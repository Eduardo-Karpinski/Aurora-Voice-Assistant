import recorder
import transcription
import llm
import tts
import wakeword

def main():
    transcription.init()
    tts.init()
    llm.init()
    
    while True:
        audio = recorder.record_until_silence()
        text = transcription.transcribe(audio)
        if wakeword.validate(text):
            answer = llm.ask(text)
            tts.speak(answer)

if __name__ == "__main__":
    try:
        print('START SYSTEM')
        main()
    except KeyboardInterrupt:
        print('BYE')