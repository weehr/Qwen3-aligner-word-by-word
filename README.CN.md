# Qwen3 强制对齐 —— 音文对齐与词/字级 SRT 字幕

[English](README.md) | **简体中文**

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-6.5.1-FF7C00?logo=gradio&logoColor=white)
![CUDA](https://img.shields.io/badge/CUDA-12.6-76B900?logo=nvidia&logoColor=white)
![License](https://img.shields.io/badge/License-Apache--2.0-blue)

一个本地运行的 Gradio 网页应用。用户上传音频并粘贴与音频对应的文本后，程序使用 [Qwen3-ForcedAligner-0.6B](https://huggingface.co/Qwen/Qwen3-ForcedAligner-0.6B) 进行强制对齐，并导出**逐词或逐字**的 SRT 字幕。

项目支持 Windows、NVIDIA GPU 加速和 CPU 回退，并通过 90 秒分段处理任意长度的音频。

## 功能特性

- **逐词 SRT**：适用于英语、德语、法语等有空格分隔的语言。
- **逐字 SRT**：适用于汉语、日语、泰语等字词之间无空格的语言。
- **59 种语种选项**：自动区分有空格语言和无空格语言。
- **GPU / CPU 双模式**：自动检测 CUDA，不可用时回退到 CPU。
- **长音频支持**：按 90 秒分段处理，并按顺序逐步对齐文本。
- **时间戳修复**：避免字幕时间重叠或零长度。
- **UTF-8 SRT 输出**：毫秒级时间戳，文件保存在 `outputs/`。
- **网页操作**：上传音频、粘贴文本、查看时间戳预览、下载 SRT。

## 环境要求

| 组件 | 要求 |
|---|---|
| Python | 3.13（本项目环境版本） |
| 操作系统 | Windows（已验证）；Linux/macOS 需安装对应平台的 PyTorch |
| FFmpeg | 必需，且已加入 `PATH` |
| GPU | 可选 |
| 内存 | 需容纳完整音频和模型；音频越长占用越高 |
| 磁盘 | 模型与依赖约 2 GB |

检查环境：

```powershell
python --version
ffmpeg -version
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

## 下载模型

模型需要放在以下目录：

```text
Qwen/Qwen3-ForcedAligner-0.6B/
```

### 使用 Hugging Face

```powershell
python -m pip install -U "huggingface_hub[cli]"
huggingface-cli download Qwen/Qwen3-ForcedAligner-0.6B --local-dir Qwen/Qwen3-ForcedAligner-0.6B
```

如果无法直连 Hugging Face，可先设置镜像：

```powershell
$env:HF_ENDPOINT = "https://hf-mirror.com"
```

### 使用 ModelScope

```powershell
python -m pip install -U modelscope
modelscope download --model Qwen/Qwen3-ForcedAligner-0.6B --local_dir Qwen/Qwen3-ForcedAligner-0.6B
```

### 自动加载顺序

如果本地模型目录不存在，程序会依次尝试：

1. 从 Hugging Face 加载 `Qwen/Qwen3-ForcedAligner-0.6B`，成功后保存到 `Qwen/`。
2. 从 ModelScope 下载并直接保存到 `Qwen/`。

`modelscope` 未包含在 `requirements.txt` 中，如需该回退方式，请手动安装。离线或受限网络环境建议提前下载模型，并放入 `Qwen/Qwen3-ForcedAligner-0.6B/`。

模型目录中至少需要以下文件：

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

`Qwen/` 已写入 `.gitignore`，因为模型权重约 1.75 GB，不应提交到 GitHub。

## 安装

```powershell
git clone https://github.com/weehr/Qwen3-aligner-word-by-word.git
cd Qwen3-aligner-word-by-word
python -m pip install -r requirements.txt
```

Windows 也可以直接使用附带的脚本：

```powershell
.\install.bat
.\run.bat
```

`requirements.txt` 会从 CUDA 12.6 的 PyTorch 源安装 GPU 版本。如果安装后仍无法使用 GPU，可手动重装：

```powershell
python -m pip install --force-reinstall torch==2.12.1 --index-url https://download.pytorch.org/whl/cu126
```

项目也支持纯 CPU 运行，但对齐速度会明显变慢。

## 启动

```powershell
python app_gradio.py
```

默认访问地址为 `http://127.0.0.1:7860`，程序会自动打开浏览器。

可选环境变量：

```powershell
$env:GRADIO_SERVER_NAME = "127.0.0.1"   # 改为 0.0.0.0 可供局域网访问
$env:GRADIO_SERVER_PORT = "7860"
$env:QWEN3_MODELS_DIR = "D:\models\Qwen"  # 自定义模型根目录
```

## 使用方法

1. 在 **音频文件** 中上传音频（WAV、MP3、FLAC、OGG、M4A，以及其他 FFmpeg 支持的格式）。
2. 在 **语种** 下拉框中选择文本对应的语言。
3. 在 **对应文本** 中粘贴与音频对应的文本。
4. 保持 **使用 GPU（CUDA）** 勾选；如需强制使用 CPU，可取消勾选。
5. 点击 **开始对齐**。
6. 查看时间戳预览，并下载生成的 `.words.srt` 文件。

注意事项：

- 文本必须与音频内容对应，本项目不包含语音识别功能。
- 有空格分隔的语言按正常单词间距粘贴文本。
- 汉语、日语、泰语等无空格语言直接粘贴正常文本，无需手动加空格；程序会在内部插入分隔符进行对齐。
- 标点会保留在 SRT 中，并归入相邻的词或字。
- 预览表格最多显示 200 条，完整内容以 SRT 文件为准。
- SRT 同时保存在 `outputs/`，文件名包含原音频名和时间戳。

## 输出示例

英语逐词示例：

```srt
1
00:00:00,120 --> 00:00:00,480
Hello

2
00:00:00,480 --> 00:00:00,920
world
```

汉语逐字示例：

```srt
1
00:00:00,120 --> 00:00:00,320
你

2
00:00:00,320 --> 00:00:00,560
好
```

## 支持的语种

模型官方训练语种为 11 种：汉语、英语、粤语、法语、德语、意大利语、日语、韩语、葡萄牙语、俄语、西班牙语。

界面提供以下 59 种选项。非官方语种会使用字/词切分进行对齐，精度可能低于官方语种。

### 字词之间无空格（逐字输出）

汉语、日语、泰语、老挝语、高棉语（柬埔寨语）、缅甸语、彝语（诺苏彝语）、巴厘语、爪哇语、纳西语、切罗基语、傣那语。

### 字词之间有空格（逐词输出）

英语、德语、荷兰语、瑞典语、丹麦语、挪威语、冰岛语、阿非利坎语、法语、西班牙语、葡萄牙语、意大利语、罗马尼亚语、加泰罗尼亚语、俄语、乌克兰语、白俄罗斯语、波兰语、捷克语、克罗地亚语、塞尔维亚语、立陶宛语、拉脱维亚语、威尔士语、爱尔兰语、现代希腊语、波斯语、库尔德语、印地语、乌尔都语、孟加拉语、泰米尔语、卡纳达语、芬兰语、匈牙利语、爱沙尼亚语、土耳其语、维吾尔语、哈萨克语、蒙古语、阿拉伯语、希伯来语、印尼语/马来语、越南语、格鲁吉亚语、韩语/朝鲜语、斯瓦希里语。

韩语使用模型自带分词器，并按字级匹配规则处理。

## 项目结构

```text
.
├── app_gradio.py
├── requirements.txt
├── install.bat
├── run.bat
├── .gitignore
├── LICENSE
├── README.md
├── Qwen3-aligner/
│   ├── abbreviations.json
│   ├── LICENSE
│   ├── NOTICE
│   └── qwen3_aligner/
│       ├── __init__.py
│       ├── aligner.py
│       ├── audio_utils.py
│       ├── languages.py
│       ├── model_loader.py
│       ├── srt_utils.py
│       └── text_utils.py
├── Qwen
```



## 常见问题

### 无法使用 CUDA

```powershell
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

如果输出为 `False`，请安装与显卡驱动匹配的 CUDA 版 PyTorch，然后重启程序。

### 找不到 FFmpeg

```powershell
ffmpeg -version
```

如果命令无法识别，请安装 FFmpeg，并将其 `bin` 目录加入 `PATH`，然后重新打开终端。

### 模型加载失败

- 确认 `Qwen/Qwen3-ForcedAligner-0.6B/model.safetensors` 存在。
- 将 `QWEN3_MODELS_DIR` 指向包含 `Qwen3-ForcedAligner-0.6B` 的目录。
- 网络受限时请手动下载模型，不要依赖自动下载。

### 显存不足

- 取消勾选 **使用 GPU（CUDA）**，改用 CPU。
- 关闭其他占用 GPU 的程序。
- 先截取较短片段验证流程。

### 对齐效果不佳

- 尽量保证文本与音频逐字对应。
- 选择正确的语种。
- 优先使用官方支持的 11 种语言。
- 检查文本是否缺少或多余大段内容。

## 已知限制

- 不包含语音识别，必须提供文本。
- 长音频会完整载入内存，并按 90 秒切块，内存占用随音频时长增长。
- 分段边界可能对少量边界词的时间戳产生轻微影响。
- 非官方语种属于尽力而为模式，时间戳精度可能较低。
- 网页界面与提示信息当前为中文。

## 许可证

本项目采用 Apache License 2.0，详见 [LICENSE](LICENSE) 与 [NOTICE](Qwen3-aligner/NOTICE)。

Qwen3-ForcedAligner-0.6B 由阿里云提供，采用 Apache License 2.0。对齐实现基于 [surfincanoy/Qwen3-aligner](https://github.com/surfincanoy/Qwen3-aligner) 项目。
