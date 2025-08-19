import logging
import os
from copy import deepcopy
from typing import TYPE_CHECKING, Dict, List, Tuple

import torch
from accelerate import init_empty_weights
from tqdm.auto import tqdm
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoTokenizer,
    Qwen2ForCausalLM,
)
from transformers.models.qwen2.modeling_qwen2 import Qwen2DecoderLayer

from fusion_bench import BaseAlgorithm, BaseModelPool
from fusion_bench.compat.modelpool import to_modelpool
from fusion_bench.mixins import SimpleProfilerMixin, auto_register_config
from fusion_bench.modelpool import CausalLMPool
from fusion_bench.models.hf_utils import (
    generate_complete_readme,
    save_pretrained_with_remote_code,
)
from fusion_bench.models.modeling_smile_qwen2 import (
    SmileQwen2Config,
    SmileQwen2ForCausalLM,
    SmileQwen2Model,
)
from fusion_bench.models.modeling_smile_qwen2.modeling_smile_qwen2 import (
    SmileQwen2DecoderLayer,
)
from fusion_bench.models.smile_moe.linear_from_hf_config import (
    ExpertNotTrainedError,
    upscale_to_smile_linear,
)
from fusion_bench.utils.dtype import parse_dtype
from fusion_bench.utils.parameters import print_parameters

log = logging.getLogger(__name__)


@auto_register_config
class SmileQwen2UpscalingAlgorithm(BaseAlgorithm, SimpleProfilerMixin):
    R"""
    SmileQwen2UpscalingAlgorithm is a model fusion algorithm designed to upscale
    a pretrained Qwen2 model using a set of fine-tuned expert models. The algorithm
    leverages Singular Value Decomposition (SVD) to merge the weights of the pretrained
    model and the expert models into a new upscaled model.

    Methods:
        run(modelpool: BaseModelPool) -> SmileQwen2ForCausalLM:
            Executes the upscaling process and returns the upscaled model.

        merge(pretrained_model: Qwen2ForCausalLM, finetuned_models: List[Qwen2ForCausalLM]) -> SmileQwen2ForCausalLM:
            Merges the pretrained model with the fine-tuned models to create an upscaled model.
    """

    modelpool: CausalLMPool

    def __init__(
        self,
        device,
        accelerator,
        model_path,
        model_dtype,
        num_experts_per_tok,
        rank_of_router,
        rank_of_expert,
        save_with_remote_code: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)

    @torch.no_grad()
    def run(self, modelpool) -> SmileQwen2ForCausalLM:
        """
        Executes the upscaling process.

        Args:
            modelpool (ModelPool): The pool of models to be used for upscaling.

        Returns:
            SmileQwen2ForCausalLM: The upscaled model.
        """
        self.modelpool = modelpool = to_modelpool(modelpool)
        config = self.config

        # load model from path if provided and return directly
        if config.model_path is not None and os.path.exists(config.model_path):
            log.info(f"Loading model from {config.model_path}")
            model = AutoModelForCausalLM.from_pretrained(config.model_path)
            print_parameters(model)
            return model

        with self.profile("load pretrained model"):
            pretrained_model = modelpool.load_pretrained_model()
        with self.profile("load fine-tuned model"):
            finetuned_models = [
                m for m in tqdm(modelpool.models(), total=len(modelpool.model_names))
            ]

        if config.device == "cuda" and torch.cuda.is_available():
            pretrained_model = pretrained_model.cuda()
            print("parameter count of pretrained model:")
            print_parameters(pretrained_model)
            finetuned_models = [m.cuda() for m in finetuned_models]

        with self.profile("merge model"):
            model = self.merge(pretrained_model, finetuned_models)

        self.print_profile_summary()
        print("parameter count of upscaled MoE model:")
        print_parameters(model)
        print(model)

        if config.model_dtype is not None:
            model.to(dtype=parse_dtype(config.model_dtype))

        if config.model_path is not None:
            if os.path.dirname(config.model_path):
                os.makedirs(os.path.dirname(config.model_path), exist_ok=True)
            log.info(f"Saving model to {config.model_path}")
            tokenizer = self.modelpool.load_tokenizer()
            tokenizer.save_pretrained(config.model_path)
            if not self.save_with_remote_code:
                model.save_pretrained(config.model_path)
            else:
                save_pretrained_with_remote_code(
                    model,
                    auto_map={
                        "AutoConfig": SmileQwen2Config,
                        "AutoModel": SmileQwen2Model,
                        "AutoModelForCausalLM": SmileQwen2ForCausalLM,
                    },
                    save_directory=config.model_path,
                )

            # save readme
            complete_readme = generate_complete_readme(
                algorithm=self,
                modelpool=modelpool,
                models=[modelpool.get_model_path(m) for m in modelpool.all_model_names],
            )
            with open(os.path.join(config.model_path, "README.md"), "w") as f:
                f.write(complete_readme)

        return model

    def merge(
        self,
        pretrained_model: Qwen2ForCausalLM,
        finetuned_models: List[Qwen2ForCausalLM],
    ):
        """
        Merges the pretrained model with the fine-tuned models to create an upscaled model.

        Args:
            pretrained_model (Qwen2ForCausalLM): The pretrained model.
            finetuned_models (List[Qwen2ForCausalLM]): A list of fine-tuned models.

        Returns:
            SmileQwen2ForCausalLM: The upscaled model.
        """
        config = self.config

        with init_empty_weights():
            pretrained_model_config = self.modelpool.get_model_config("_pretrained_")
            if isinstance(pretrained_model_config, str):
                pretrained_path = pretrained_model_config
            else:
                pretrained_path = pretrained_model_config.get(
                    "path", pretrained_model_config["pretrained_model_name_or_path"]
                )
            base_config = AutoConfig.from_pretrained(pretrained_path)
            model_config = SmileQwen2Config(
                num_experts_per_tok=config.num_experts_per_tok,
                rank_of_router=config.rank_of_router,
                rank_of_expert=config.rank_of_expert,
                num_local_experts=len(finetuned_models),
                **base_config.to_dict(),
            )
            model = SmileQwen2ForCausalLM(model_config)

        model.to(dtype=pretrained_model.dtype).to_empty(device="cpu")

        # copy pretrained model weights
        state_dict = model.state_dict()
        pretrained_state_dict = dict(pretrained_model.state_dict())
        for key in list(pretrained_state_dict.keys()):
            if key not in state_dict:
                pretrained_state_dict.pop(key)
        model.load_state_dict(pretrained_state_dict, strict=False)

        # upscale model
        for layer_idx in tqdm(
            range(len(pretrained_model.model.layers)),
            "Upscaling Modules (layer)",
            dynamic_ncols=True,
        ):
            pretrained_layer: Qwen2DecoderLayer = pretrained_model.model.layers[
                layer_idx
            ]
            finetuned_layers: List[Qwen2DecoderLayer] = [
                m.model.layers[layer_idx] for m in finetuned_models
            ]

            target_layer: SmileQwen2DecoderLayer = model.model.layers[layer_idx]

            for n in ["q_proj", "k_proj", "v_proj", "o_proj"]:
                try:
                    upscale_to_smile_linear(
                        base=getattr(pretrained_layer.self_attn, n),
                        experts=[getattr(m.self_attn, n) for m in finetuned_layers],
                        target=getattr(target_layer.self_attn, n),
                        accelerator=config.accelerator,
                    )
                except ExpertNotTrainedError:
                    setattr(
                        target_layer.self_attn,
                        n,
                        getattr(pretrained_layer.self_attn, n),
                    )

            for n in ["gate_proj", "up_proj", "down_proj"]:
                try:
                    upscale_to_smile_linear(
                        base=getattr(pretrained_layer.mlp, n),
                        experts=[getattr(m.mlp, n) for m in finetuned_layers],
                        target=getattr(target_layer.mlp, n),
                        accelerator=config.accelerator,
                    )
                except ExpertNotTrainedError:
                    setattr(
                        target_layer.mlp,
                        n,
                        getattr(pretrained_layer.mlp, n),
                    )

        return model
