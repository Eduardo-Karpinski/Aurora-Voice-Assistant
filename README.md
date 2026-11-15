# Aurora

Assistente de voz local para Windows. O microfone é transcrito na própria máquina, um modelo GGUF gera a resposta e o XTTS a fala. Nenhuma etapa chama uma API externa.

A conversa fica só na memória do processo. Ao encerrar o programa, o histórico some.

Quando a resposta precisa de um fato atual, só o texto da consulta sai para a busca, e a primeira página encontrada é lida. O áudio, a transcrição e o modelo continuam na máquina.

## Pipeline

1. O microfone captura áudio a 16 kHz.
2. O WebRTC VAD detecta o fim da fala.
3. O faster-whisper transcreve em português na GPU.
4. O Qwen3 8B, via llama.cpp com Vulkan, escreve a resposta.
5. O XTTS v2 sintetiza a fala na GPU e o sounddevice reproduz.

Whisper e XTTS usam o PyTorch ROCm, que nesta plataforma se apresenta como CUDA. O modelo de linguagem permanece no Vulkan.

## Requisitos

- Windows com uma AMD RX 7900 GRE (gfx1100).
- Python 3.11. Os wheels de ROCm para Windows existem do 3.10 ao 3.14. O Python 3.15 não instala o PyTorch ROCm.
- O arquivo `models/Qwen3-8B-Q5_K_M.gguf`.

Se o `python` do sistema for outra versão:

```powershell
winget install -e --id Python.Python.3.11
```

## Instalação

Na pasta do projeto, crie o ambiente com o Python 3.11:

```powershell
py -3.11 -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip wheel
```

O `Set-ExecutionPolicy` vale apenas para a janela atual. Sem ele, o PowerShell bloqueia o `Activate.ps1`. Também é possível pular a ativação e chamar `.\venv\Scripts\python.exe` diretamente.

Instale o PyTorch ROCm para a gfx1100:

```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1100]==2.12.0+rocm7.14.1" "torchvision[device-gfx1100]==0.27.0+rocm7.14.1" "torchaudio==2.11.0+rocm7.14.1"
```

Instale o áudio, a transcrição, a síntese e o `transformers` compatível com o XTTS:

```powershell
pip install sounddevice webrtcvad-wheels faster-whisper coqui-tts six ddgs "torchcodec==0.12.0" "transformers==4.57.6"
```

O pacote `webrtcvad` não publica wheel para Python 3.11 no Windows. Use `webrtcvad-wheels`. O XTTS desta versão usa o GPT-2 do `transformers` 4.57. A série 5 altera a geração e a fala falha.

O `faster-whisper` instala o CTranslate2 do PyPI, compilado para GPU NVIDIA. Substitua pelo wheel ROCm da [release 4.9.0](https://github.com/OpenNMT/CTranslate2/releases/tag/v4.9.0):

```powershell
Invoke-WebRequest -Uri https://github.com/OpenNMT/CTranslate2/releases/download/v4.9.0/rocm-python-wheels-Windows.zip -OutFile rocm-python-wheels-Windows.zip
Expand-Archive -Path rocm-python-wheels-Windows.zip -DestinationPath ctranslate2-rocm -Force
pip install --force-reinstall --no-deps (Get-ChildItem -Recurse .\ctranslate2-rocm -Filter "ctranslate2-*-cp311-cp311-win_amd64.whl").FullName
```

Instale o llama.cpp pelo wheel Vulkan já compilado. Sem o `--only-binary`, o pip tenta compilar o pacote e exige o Visual C++:

```powershell
pip install --only-binary=llama-cpp-python llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/vulkan
```

## Modelo de linguagem

Coloque o GGUF em `models/Qwen3-8B-Q5_K_M.gguf`. Esse caminho está em `LLMConfig.MODEL_PATH`. Se o arquivo não existir, o programa avisa e não inicia. O arquivo oficial é o `Q5_K_M` do repositório [Qwen/Qwen3-8B-GGUF](https://huggingface.co/Qwen/Qwen3-8B-GGUF).

Na primeira execução o XTTS baixa o modelo de voz. O programa aceita a licença não comercial CPML para permitir esse download: https://tts-hub.github.io/cpml

## Execução

Com o ambiente ativo:

```powershell
python main.py
```

Fale depois que o estado mudar para `LISTENING`. Ctrl+C encerra.

## Configuração

`config.py` concentra os ajustes: modelo e contexto do LLM, tamanho do Whisper, voz e idioma do XTTS, e os limites do VAD. A voz padrão é Alma María, em português.

## Solução de problemas

O Windows Smart App Control bloqueia a DLL não assinada `aotriton_v2.dll` com o erro 4551. A carga do PyTorch ROCm só segue depois que o Smart App Control é desligado em Segurança do Windows.

Se o Whisper disser que a versão do driver CUDA é insuficiente, o CTranslate2 instalado ainda é o wheel NVIDIA. Repita a instalação do wheel ROCm acima.

Se o llama.cpp pedir `nmake` ou o compilador C++, a instalação partiu para compilação local. Repita o comando com `--only-binary=llama-cpp-python`.
