# Copyright 2026 Alibaba Cloud (Qwen3-ASR)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import gc
import os

import torch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)


def _get_device(use_gpu: bool = True) -> str:
    if use_gpu and torch.cuda.is_available():
        return "cuda:0"
    return "cpu"


def _clear_cache(use_gpu: bool = True):
    gc.collect()
    if use_gpu and torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


def _resolve_models_dir(models_base_dir: str = None) -> str:
    """依次查找模型目录，兼容源码目录和便携版目录结构。"""
    candidates = [
        models_base_dir,
        os.environ.get("QWEN3_MODELS_DIR"),
        os.path.join(PROJECT_DIR, "Qwen"),
        os.path.join(os.path.dirname(PROJECT_DIR), "Qwen"),
    ]
    for base_dir in candidates:
        if base_dir and os.path.isdir(
            os.path.join(base_dir, "Qwen3-ForcedAligner-0.6B")
        ):
            return base_dir
    for base_dir in candidates:
        if base_dir and os.path.isdir(base_dir):
            return base_dir
    return os.path.join(PROJECT_DIR, "Qwen")


def load_aligner_model(
    attn_implementation: str = None,
    models_base_dir: str = None,
    use_gpu: bool = True,
):
    from qwen_asr import Qwen3ForcedAligner

    _clear_cache(use_gpu)
    device = _get_device(use_gpu)
    print(f"Using device: {device}")
    dtype = torch.bfloat16 if device.startswith("cuda") else torch.float32
    load_kwargs = dict(dtype=dtype, device_map=device)
    if attn_implementation:
        load_kwargs["attn_implementation"] = attn_implementation

    local_model_dir = os.path.join(
        _resolve_models_dir(models_base_dir), "Qwen3-ForcedAligner-0.6B"
    )

    if os.path.isdir(local_model_dir):
        print(f"Loading local aligner: {local_model_dir}")
        try:
            model = Qwen3ForcedAligner.from_pretrained(local_model_dir, **load_kwargs)
            print("Local aligner loaded")
            return model
        except Exception as e:
            print(f"Local aligner load failed: {e}")

    hf_model_id = "Qwen/Qwen3-ForcedAligner-0.6B"
    try:
        print(f"Downloading aligner from HuggingFace: {hf_model_id}")
        model = Qwen3ForcedAligner.from_pretrained(hf_model_id, **load_kwargs)
        print("HuggingFace aligner loaded")
        print(f"Saving aligner to local: {local_model_dir}")
        model.save_pretrained(local_model_dir)
        return model
    except Exception as e:
        print(f"HuggingFace aligner failed: {e}")

    try:
        from modelscope import snapshot_download

        print("Downloading aligner from ModelScope...")
        snapshot_download("qwen/Qwen3-ForcedAligner-0.6B", local_dir=local_model_dir)
        model = Qwen3ForcedAligner.from_pretrained(local_model_dir, **load_kwargs)
        print("ModelScope aligner loaded")
        return model
    except ImportError:
        print("modelscope not installed")
    except Exception as e:
        print(f"ModelScope aligner failed: {e}")

    raise RuntimeError("All aligner model loading methods failed")
