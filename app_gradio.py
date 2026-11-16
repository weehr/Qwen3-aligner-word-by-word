"""Qwen3 强制对齐 Gradio 应用。

功能：
- 上传任意时长音频并粘贴对应文本；
- 选择语种（自动区分字词间是否有空格）；
- 支持 GPU / CPU；
- 输出逐词（空格语言）或逐字（无空格语言）SRT 字幕。
"""

import os
import sys
import threading
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(PROJECT_DIR, "Qwen3-aligner")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "outputs")

sys.path.insert(0, SOURCE_DIR)

import gradio as gr
import torch

from qwen3_aligner.aligner import Aligner
from qwen3_aligner.languages import LANGUAGE_CHOICES, LANGUAGE_LABELS
from qwen3_aligner.srt_utils import sentences_to_word_srt

os.makedirs(OUTPUT_DIR, exist_ok=True)

_aligner = None
_aligner_key = None
_aligner_lock = threading.Lock()
MAX_PREVIEW_ROWS = 200


def _get_aligner(language: str, use_gpu: bool) -> Aligner:
    global _aligner, _aligner_key
    key = (language, use_gpu)
    with _aligner_lock:
        if _aligner is not None and _aligner_key != key:
            _aligner._unload_model()
            _aligner = None
        if _aligner is None:
            _aligner = Aligner(language=language, use_gpu=use_gpu)
            _aligner_key = key
        return _aligner


def _resolve_language(label: str) -> str:
    return LANGUAGE_LABELS.get(label, label)


def _resolve_audio_path(audio_file) -> str:
    if isinstance(audio_file, str):
        return audio_file
    return getattr(audio_file, "name", None)


def _device_text(use_gpu: bool) -> str:
    if use_gpu and torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        return f"GPU（{name}）"
    if use_gpu:
        return "CPU（未检测到可用的 CUDA，已自动回退）"
    return "CPU"


def _safe_stem(path: str) -> str:
    stem = os.path.splitext(os.path.basename(path))[0]
    return "".join(ch for ch in stem if ch.isalnum() or ch in "-_") or "subtitle"


def run_alignment(audio_file, text, language_label, use_gpu):
    audio_path = _resolve_audio_path(audio_file)
    if not audio_path or not os.path.isfile(audio_path):
        return "请先上传音频文件。", [], None
    text = (text or "").lstrip("\ufeff").strip()
    if not text:
        return "请粘贴与音频对应的文本。", [], None

    language = _resolve_language(language_label)

    try:
        aligner = _get_aligner(language, bool(use_gpu))
        sentences = aligner.align(audio_path, text)
    except Exception as exc:
        return f"对齐失败：{exc}", [], None

    if not sentences:
        return "对齐失败：没有得到有效的时间戳。", [], None

    word_srt = sentences_to_word_srt(sentences, language)
    stem = _safe_stem(audio_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    srt_path = os.path.join(OUTPUT_DIR, f"{stem}_{timestamp}.words.srt")
    with open(srt_path, "w", encoding="utf-8") as handle:
        handle.write(word_srt)

    rows = []
    for sent in sentences:
        for word in sent.get("words", []):
            rows.append(
                [
                    len(rows) + 1,
                    f"{word['start_time']:.3f}",
                    f"{word['end_time']:.3f}",
                    word["text"],
                ]
            )
    preview = rows[:MAX_PREVIEW_ROWS]
    total_duration = max(
        (sent.get("end_time", 0.0) for sent in sentences), default=0.0
    )

    note = ""
    if len(rows) > MAX_PREVIEW_ROWS:
        note = f"\n（预览仅显示前 {MAX_PREVIEW_ROWS} 条，完整内容见 SRT 文件）"

    status = (
        f"### 对齐完成\n"
        f"- 语种：{language_label}\n"
        f"- 设备：{_device_text(bool(use_gpu))}\n"
        f"- 句子数：{len(sentences)}\n"
        f"- 字幕条数：{len(rows)}（逐词/逐字）\n"
        f"- 覆盖时长：{total_duration:.2f} 秒\n"
        f"- SRT 文件：{os.path.basename(srt_path)}{note}"
    )
    return status, preview, srt_path


def build_demo() -> gr.Blocks:
    default_language = "英语 (English)"
    with gr.Blocks(title="Qwen3 音文对齐") as demo:
        gr.Markdown(
            "# Qwen3 音文对齐\n"
            "上传音频并粘贴对应文本，选择语种后生成逐词/逐字 SRT 字幕。"
            "支持长音频自动分段。"
        )
        with gr.Row():
            with gr.Column(scale=1):
                audio_input = gr.File(
                    label="音频文件",
                    file_types=["audio"],
                    type="filepath",
                )
                language_input = gr.Dropdown(
                    label="语种",
                    choices=LANGUAGE_CHOICES,
                    value=default_language,
                    info=(
                        "模型官方训练语种为 11 种；其余语种会按字/词切分对齐，"
                        "精度可能低于官方语种。"
                    ),
                )
                gpu_input = gr.Checkbox(
                    label="使用 GPU（CUDA）",
                    value=torch.cuda.is_available(),
                )
                text_input = gr.Textbox(
                    label="对应文本",
                    placeholder="请粘贴与音频逐字对应的文本……",
                    lines=14,
                )
                run_button = gr.Button("开始对齐", variant="primary")
            with gr.Column(scale=1):
                status_output = gr.Markdown("等待对齐……")
                preview_output = gr.Dataframe(
                    headers=["#", "开始(秒)", "结束(秒)", "字幕文本"],
                    label="逐词/逐字时间戳预览",
                    interactive=False,
                    wrap=True,
                )
                srt_output = gr.File(label="下载逐词/逐字 SRT")

        run_button.click(
            fn=run_alignment,
            inputs=[audio_input, text_input, language_input, gpu_input],
            outputs=[status_output, preview_output, srt_output],
        )
    return demo


def main():
    demo = build_demo()
    demo.queue(default_concurrency_limit=1, max_size=10).launch(
        server_name=os.environ.get("GRADIO_SERVER_NAME", "127.0.0.1"),
        server_port=int(os.environ.get("GRADIO_SERVER_PORT", "7860")),
        inbrowser=True,
        show_error=True,
    )


if __name__ == "__main__":
    main()
