# Aurora Voice Assistant

Aurora é um assistente de voz inteligente que roda **100% localmente**, sem depender de serviços na nuvem.

Ele combina **reconhecimento de fala**, **processamento de linguagem natural com LLM** e **síntese de voz** para criar uma experiência conversacional natural, rápida e privada.

Todo o processamento acontece na sua própria máquina, garantindo **privacidade total**, **baixa latência** e **controle completo** sobre o sistema.

---

## Principais características

- Execução **totalmente offline**
- Reconhecimento de voz com **Whisper**
- Processamento de linguagem natural com **LLM local**
- Respostas faladas usando **Text-to-Speech**
- Detecção de **wake word**
- Arquitetura modular e extensível
- Baixa latência e resposta rápida
- Sem dependência de APIs externas

---

## Arquitetura

O Aurora segue um fluxo simples e eficiente:

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

## Tecnologias utilizadas

- **Python**
- **faster-whisper** para reconhecimento de fala
- **llama.cpp / llama-cpp-python** para LLM local
- **XTTS** para síntese de voz
- **WebRTC VAD** para detecção de atividade de voz
- **sounddevice** para captura e reprodução de áudio

---

## Objetivos do projeto

O objetivo do Aurora é ser um **assistente de voz privado, rápido e totalmente controlado pelo usuário**, servindo como base para:

- automação local
- integração com sistemas domésticos
- assistentes pessoais offline
- experimentação com IA local

---

## Status do projeto

🚧 O projeto está em desenvolvimento ativo e novas funcionalidades estão sendo adicionadas continuamente.

---

## Licença

Este projeto é open-source e pode ser usado, modificado e distribuído livremente.