# Aurora Voice Assistant

**Aurora** é um assistente de voz inteligente que roda **100% localmente**, sem dependência de serviços na nuvem.

Ele combina **reconhecimento de fala**, **processamento de linguagem natural com LLM** e **síntese de voz** para criar uma experiência conversacional natural, rápida e privada.

Todo o processamento acontece **na própria máquina do usuário**, garantindo:

-   **Privacidade total**
-   **Baixa latência**
-   **Processamento com IA local**
-   **Controle completo sobre o sistema**

------------------------------------------------------------------------

# Principais características

-   Execução **totalmente offline**
-   Reconhecimento de fala com **Whisper**
-   Processamento de linguagem natural com **LLM local**
-   Respostas faladas usando **Text-to-Speech**
-   Detecção de **atividade de voz (VAD)**
-   Arquitetura **modular e extensível**
-   **Baixa latência** de resposta
-   Nenhuma dependência de **APIs externas**

------------------------------------------------------------------------

# Arquitetura

O Aurora segue um pipeline simples e eficiente para processar interações
de voz:

Microfone
↓
Detecção de fala (VAD)
↓
Reconhecimento de voz (Speech-to-Text)
↓
Processamento de linguagem natural (LLM)
↓
Síntese de voz (Text-to-Speech)
↓
Resposta falada

------------------------------------------------------------------------

# Tecnologias utilizadas

-   **Python 3.11.9**
-   **faster-whisper** --- reconhecimento de fala
-   **llama.cpp / llama-cpp-python** --- LLM local
-   **XTTS (Coqui TTS)** --- síntese de voz
-   **WebRTC VAD** --- detecção de atividade de voz
-   **sounddevice** --- captura e reprodução de áudio
-   **DirectML / Vulkan** --- aceleração por GPU

------------------------------------------------------------------------

------------------------------------------------------------------------

# Instalação

Crie e ative um ambiente virtual:

``` powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Atualize ferramentas básicas:

``` powershell
python -m pip install --upgrade pip wheel
pip install "setuptools<81"
```

Instale as dependências principais:

``` powershell
pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 torch-directml==0.2.5.dev240914
pip install sounddevice webrtcvad faster-whisper
pip install coqui-tts
pip install transformers==4.57.6
```

Instale o backend de LLM local com suporte a Vulkan:

``` powershell
$env:CMAKE_ARGS="-DGGML_VULKAN=on"
pip install llama-cpp-python --no-cache-dir
```

------------------------------------------------------------------------

# Execução

Após instalar todas as dependências, execute o assistente com:

``` powershell
python main.py
```

------------------------------------------------------------------------

# Objetivos do projeto

O Aurora foi projetado para ser um **assistente de voz privado, rápido e
totalmente controlado pelo usuário**, servindo como base para:

-   automação local
-   integração com sistemas domésticos
-   assistentes pessoais offline
-   experimentação com IA local
-   pesquisa e desenvolvimento em interfaces de voz

------------------------------------------------------------------------

# Licença

Este projeto é **open-source** e pode ser utilizado, modificado e
distribuído livremente.
