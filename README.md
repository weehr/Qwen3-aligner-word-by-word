# Qwen3 Forced Aligner — Audio-Text Alignment with Word/Character-Level SRT

**English** | [简体中文](README.CN.md)

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-6.5.1-FF7C00?logo=gradio&logoColor=white)
![CUDA](https://img.shields.io/badge/CUDA-12.6-76B900?logo=nvidia&logoColor=white)
![License](https://img.shields.io/badge/License-Apache--2.0-blue)

A local Gradio web application that aligns a **known transcript** with an audio file and exports **word-level or character-level SRT subtitles** using [Qwen3-ForcedAligner-0.6B](https://huggingface.co/Qwen/Qwen3-ForcedAligner-0.6B).

The app runs on Windows, supports NVIDIA GPU acceleration with automatic CPU fallback, and processes audio of any length by splitting it into 90-second chunks.

## Features

- **Word-level SRT** for space-separated languages (English, German, French, etc.).
- **Character-level SRT** for languages without word spacing (Chinese, Japanese, Thai, etc.).
- **59 language options** with automatic word/character splitting rules.
- **GPU or CPU** execution; CUDA is detected automatically and CPU is used as a fallback.
- **Long audio support** through 90-second chunking and progressive transcript consumption.
- **Timestamp cleanup** to prevent overlapping or zero-length subtitle cues.
- **UTF-8 SRT output** with millisecond precision, saved under `outputs/`.
- **Browser UI** for drag-and-drop audio upload, pasted transcript, preview table, and SRT download.

## Requirements

| Component | Requirement |
|---|---|
| Python | 3.13 (the tested and pinned configuration) |
| OS | Windows (tested); Linux/macOS should work with matching PyTorch wheels |
| FFmpeg | Required, must be available on `PATH` |
| GPU | Optional NVIDIA GPU |
| RAM | Enough memory for the loaded audio and model; longer audio uses more RAM |
| Disk | About 2 GB for the model and dependencies |

Verify the environment:

```powershell
python --version
ffmpeg -version
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

## Model Download

The model must be placed at:

```text
Qwen/Qwen3-ForcedAligner-0.6B/
```

### Hugging Face

```powershell
python -m pip install -U "huggingface_hub[cli]"
huggingface-cli download Qwen/Qwen3-ForcedAligner-0.6B --local-dir Qwen/Qwen3-ForcedAligner-0.6B
```

If Hugging Face is not directly reachable, set a mirror before downloading:

```powershell
$env:HF_ENDPOINT = "https://hf-mirror.com"
```

### ModelScope

```powershell
python -m pip install -U modelscope
modelscope download --model Qwen/Qwen3-ForcedAligner-0.6B --local_dir Qwen/Qwen3-ForcedAligner-0.6B
```

### Automatic loading order

If the local model directory is missing, the loader tries:

1. Hugging Face (`Qwen/Qwen3-ForcedAligner-0.6B`), then saves the model into `Qwen/`.
2. ModelScope, downloaded directly into `Qwen/`.

`modelscope` is not included in `requirements.txt`; install it manually if you want the ModelScope fallback. For offline or restricted networks, download the model first and place it in `Qwen/Qwen3-ForcedAligner-0.6B/`.

Required model files include:

```text
config.json
model.safetensors
tokenizer_config.json
preprocessor_config.json
generation_config.json
vocab.json
merges.txt
chat_template.json
```

The `Qwen/` directory is excluded by `.gitignore` because the weights are about 1.75 GB.

## Installation

```powershell
git clone https://github.com/weehr/Qwen3-aligner-word-by-word.git
cd Qwen3-aligner-word-by-word
python -m pip install -r requirements.txt
```

On Windows, the included scripts can be used instead:

```powershell
.\install.bat
.\run.bat
```

`requirements.txt` installs PyTorch from the CUDA 12.6 wheel index. If GPU support is unavailable after installation, reinstall PyTorch explicitly:

```powershell
python -m pip install --force-reinstall torch==2.12.1 --index-url https://download.pytorch.org/whl/cu126
```

The application also runs on CPU, but alignment is significantly slower.

## Run

```powershell
python app_gradio.py
```

The app starts at `http://127.0.0.1:7860` and opens the browser automatically.

Optional environment variables:

```powershell
$env:GRADIO_SERVER_NAME = "127.0.0.1"   # use 0.0.0.0 for LAN access
$env:GRADIO_SERVER_PORT = "7860"
$env:QWEN3_MODELS_DIR = "D:\models\Qwen"  # custom model base directory
```

## Usage

1. Upload audio in the **音频文件** field (WAV, MP3, FLAC, OGG, M4A, and other formats supported by FFmpeg).
2. Choose the language in the **语种** dropdown.
3. Paste the transcript into **对应文本**.
4. Leave the **使用 GPU（CUDA）** checkbox checked unless you want to force CPU mode.
5. Click **开始对齐** (Start Alignment).
6. Review the timestamp preview and download the generated `.words.srt` file.

Notes:

- The transcript must match the spoken content; the app does not perform speech recognition.
- For space-separated languages, use normal word spacing.
- For languages without word spacing (Chinese, Japanese, Thai, etc.), paste normal text without adding spaces; the app inserts internal separators for alignment.
- Punctuation is retained in the SRT and attached to the neighboring word or character.
- The preview table shows up to 200 cues; the downloaded SRT contains all cues.
- The SRT is also saved under `outputs/` with the audio filename and a timestamp.

## Output

English word-level example:

```srt
1
00:00:00,120 --> 00:00:00,480
Hello

2
00:00:00,480 --> 00:00:00,920
world
```

Chinese character-level example:

```srt
1
00:00:00,120 --> 00:00:00,320
你

2
00:00:00,320 --> 00:00:00,560
好
```

## Supported Languages

The aligner was officially trained on 11 languages: Chinese, English, Cantonese, French, German, Italian, Japanese, Korean, Portuguese, Russian, and Spanish.

The UI exposes the following 59 options. Languages outside the official set use character/word splitting and may have lower accuracy.

### No word spacing (character-level output)

Chinese, Japanese, Thai, Lao, Khmer, Burmese, Yi, Balinese, Javanese, Naxi, Cherokee, Tai Nua.

### Space-separated (word-level output)

English, German, Dutch, Swedish, Danish, Norwegian, Icelandic, Afrikaans, French, Spanish, Portuguese, Italian, Romanian, Catalan, Russian, Ukrainian, Belarusian, Polish, Czech, Croatian, Serbian, Lithuanian, Latvian, Welsh, Irish, Greek, Persian, Kurdish, Hindi, Urdu, Bengali, Tamil, Kannada, Finnish, Hungarian, Estonian, Turkish, Uyghur, Kazakh, Mongolian, Arabic, Hebrew, Indonesian/Malay, Vietnamese, Georgian, Korean, Swahili.

Korean uses the model's built-in tokenizer and character-matching rules.

## Project Structure

```text
.
├── app_gradio.py                 # Gradio UI and SRT export
├── requirements.txt              # Python dependencies
├── install.bat                   # Windows install helper
├── run.bat                       # Windows launch helper
├── .gitignore
├── LICENSE                       # Apache License 2.0
├── README.md                     # English documentation
├── README_cn.md                  # Chinese documentation
├── Qwen3-aligner/
│   ├── abbreviations.json        # English abbreviation handling
│   ├── LICENSE
│   ├── NOTICE
│   └── qwen3_aligner/
│       ├── __init__.py
│       ├── aligner.py            # Alignment and long-audio chunking
│       ├── audio_utils.py        # Audio loading, FFmpeg conversion, memory cleanup
│       ├── languages.py          # Language rules and display labels
│       ├── model_loader.py       # Local model resolution and GPU/CPU loading
│       ├── srt_utils.py          # Timestamp repair and SRT generation
│       └── text_utils.py         # Sentence splitting and abbreviation handling
├── Qwen/
│   └── Qwen3-ForcedAligner-0.6B/ # Model weights, git-ignored
└── outputs/                      # Generated SRT files, git-ignored
```

## How It Works

1. The transcript is normalized and split into sentences.
2. Audio longer than 90 seconds is processed in chunks, consuming transcript segments progressively.
3. The model returns word/character timestamps for each chunk.
4. Timestamps are mapped back to the original text, preserving punctuation.
5. Cues are clamped to be monotonic and at least 50 ms long.
6. The result is written as a UTF-8 SRT file and shown in the preview table.

## Troubleshooting

### CUDA is not available

```powershell
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

If this prints `False`, install a CUDA-enabled PyTorch build that matches your driver, then restart the app.

### FFmpeg not found

```powershell
ffmpeg -version
```

If the command is not recognized, install FFmpeg and add its `bin` directory to `PATH`, then reopen the terminal.

### Model fails to load

- Confirm that `Qwen/Qwen3-ForcedAligner-0.6B/model.safetensors` exists.
- Set `QWEN3_MODELS_DIR` to the directory that contains `Qwen3-ForcedAligner-0.6B`.
- For restricted networks, download the model manually instead of relying on the automatic fallback.

### Out of memory

- Uncheck the **使用 GPU（CUDA）** checkbox to run on CPU.
- Close other GPU applications.
- Process a shorter excerpt first to confirm the setup.

### Poor alignment quality

- Make the transcript match the audio as closely as possible.
- Use the correct language option.
- Prefer one of the 11 officially supported languages.
- Check that the transcript is not missing or adding large sections of text.

## Limitations

- Speech recognition is not included; a transcript is required.
- Very long audio is loaded into memory and processed in 90-second chunks, so memory usage grows with duration.
- Chunk boundaries can slightly affect a small number of words near the boundary.
- Non-official languages run in best-effort mode and may produce less accurate timestamps.
- The UI labels and status messages are currently in Chinese.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](Qwen3-aligner/NOTICE).

Qwen3-ForcedAligner-0.6B is provided by Alibaba Cloud under the Apache License 2.0. The alignment implementation is based on the surfincanoy/Qwen3-aligner project. 
