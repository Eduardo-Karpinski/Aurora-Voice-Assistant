# Aurora

[![tests](https://github.com/Eduardo-Karpinski/Aurora-Voice-Assistant/actions/workflows/tests.yml/badge.svg)](https://github.com/Eduardo-Karpinski/Aurora-Voice-Assistant/actions/workflows/tests.yml)

Local voice assistant for Windows. The microphone is transcribed on the machine, a GGUF model writes the reply, and XTTS speaks it. The assistant answers in the language of the question.

The conversation lives only in the process. When the program exits, the history is gone.

When a reply needs a current fact, only the search query leaves the machine, and the first page found is read. The audio, the transcript, and the language model stay local.

The microphone stays closed while a reply is playing, so the assistant does not record its own voice.

## Pipeline

1. The microphone captures audio at 16 kHz.
2. WebRTC VAD detects the end of speech.
3. faster-whisper detects the spoken language and transcribes it on the GPU.
4. Qwen3 8B, through llama.cpp with Vulkan, writes the reply.
5. XTTS v2 synthesizes speech on the GPU and sounddevice plays it.

Whisper and XTTS use PyTorch ROCm, which shows up as CUDA on this platform. The language model stays on Vulkan.

## Requirements

This setup is tested on one machine:

| Piece | Tested setup |
| --- | --- |
| System | Windows |
| GPU | AMD RX 7900 GRE (gfx1100) |
| Python | 3.11 |

ROCm wheels for Windows exist for Python 3.10 through 3.14. Python 3.15 does not install PyTorch ROCm. This project pins 3.11.

NVIDIA, Intel, CPU-only, macOS, and Linux are outside this setup. Whisper is configured for CUDA, and the installer replaces CTranslate2 with the ROCm build.

You also need the file `models/Qwen3-8B-Q5_K_M.gguf`.

If `python` on the system is another version:

```powershell
winget install -e --id Python.Python.3.11
```

## Installation

From the project folder:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install.ps1
```

`Set-ExecutionPolicy` applies only to the current window. Without it, PowerShell refuses to run `install.ps1` and `Activate.ps1`.

The script creates a Python 3.11 virtual environment and then:

1. Installs PyTorch ROCm for gfx1100.
2. Installs the pinned packages in `requirements.txt`.
3. Replaces the NVIDIA CTranslate2 wheel that `faster-whisper` pulls with the ROCm wheel from [CTranslate2 4.9.0](https://github.com/OpenNMT/CTranslate2/releases/tag/v4.9.0).
4. Installs the prebuilt Vulkan wheel of `llama-cpp-python` 0.3.36. Without `--only-binary`, pip tries to compile it and asks for Visual C++.
5. Installs pytest.

`transformers` stays on 4.57.6 because this XTTS build uses that GPT-2 path. The 5.x generation API breaks speech. `webrtcvad` has no Windows wheel for Python 3.11, so the file uses `webrtcvad-wheels`. `ddgs` is pinned at 9.16.1 because `search.py` replaces a private constructor in that version: the library otherwise draws a mobile browser profile and the engines return HTML it cannot read.

## Language model

Put the GGUF at `models/Qwen3-8B-Q5_K_M.gguf`. That path is `LLMConfig.MODEL_PATH`. If the file is missing, the program says so and does not start. The published file is `Q5_K_M` from [Qwen/Qwen3-8B-GGUF](https://huggingface.co/Qwen/Qwen3-8B-GGUF).

The first run downloads the XTTS voice. The program sets `COQUI_TOS_AGREED` so that download can proceed. The weights are under the non-commercial CPML: https://tts-hub.github.io/cpml. See `NOTICE`.

## Running

With the environment active:

```powershell
.\venv\Scripts\Activate.ps1
python main.py
```

You can skip activation and call `.\venv\Scripts\python.exe main.py`.

Speak after the state changes to `LISTENING`. Start with the wake word, then the question: "Aurora, what time is it?" A phrase without it is ignored. Ctrl+C exits. A failed turn is printed and the assistant goes back to listening.

Set `AURORA_BENCHMARK=1` to print how long init, transcription, the reply, and speech take. Timing is off unless that variable is set.

## Configuration

`config.py` holds the knobs: the language model and its context, the Whisper size, the XTTS voice, the wake word, the VAD limits, and the search region. `WakeWordConfig.WORD` is `aurora`. Set it to an empty string to listen to every phrase. Whisper detects the language of each question, and the reply is spoken in that language. Alma María is the voice. Portuguese is the fallback when the language is unclear. The search region is `br-pt`.

## Tests

Unit tests cover memory, transcript cleanup, speech chunking, the spoken language, tool-call parsing, and search formatting. They do not load the GPU.

```powershell
.\venv\Scripts\python.exe -m pytest
```

Scripts that hit the network, the language model, or the speaker live in `scripts/`:

```powershell
.\venv\Scripts\python.exe scripts\try_search.py current dollar to real exchange rate
.\venv\Scripts\python.exe scripts\try_llm.py What is the temperature on the surface of the Moon?
.\venv\Scripts\python.exe scripts\try_tts.py
```

## License

The code is MIT. See `LICENSE`. XTTS v2 weights are not, and they are not included in this repository. See `NOTICE` before you use the voice model for anything other than a personal project.

## Troubleshooting

Windows Smart App Control blocks the unsigned `aotriton_v2.dll` with error 4551. PyTorch ROCm loads only after Smart App Control is turned off in Windows Security.

If Whisper says the CUDA driver version is insufficient, the installed CTranslate2 is still the NVIDIA wheel. Run `install.ps1` again, or repeat the ROCm wheel step from that script.

If llama.cpp asks for `nmake` or a C++ compiler, pip tried to build it locally. Repeat the install with `--only-binary=llama-cpp-python` and the Vulkan index, as `install.ps1` does.
