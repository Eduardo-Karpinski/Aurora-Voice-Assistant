import queue
import collections
import numpy as np
import sounddevice as sd
import webrtcvad
from config import RecorderConfig

SAMPLE_RATE = RecorderConfig.SAMPLE_RATE
FRAME_MS = RecorderConfig.FRAME_MS
FRAME_SIZE = int(SAMPLE_RATE * FRAME_MS / 1000)
VAD_MODE = RecorderConfig.VAD_MODE
START_VOICE_FRAMES = RecorderConfig.START_VOICE_FRAMES
SILENCE_FRAMES_TO_STOP = RecorderConfig.SILENCE_FRAMES_TO_STOP
PRE_ROLL_FRAMES = RecorderConfig.PRE_ROLL_FRAMES

def record_until_silence():
    vad = webrtcvad.Vad(VAD_MODE)
    q = queue.Queue()

    def callback(indata, frames, time_info, status):
        q.put(indata.copy())

    def is_speech(frame_f32: np.ndarray) -> bool:
        pcm16 = np.clip(frame_f32.squeeze() * 32768, -32768, 32767).astype(np.int16)
        return vad.is_speech(pcm16.tobytes(), SAMPLE_RATE)

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=FRAME_SIZE,
        callback=callback,
    )
    stream.start()

    recording = False
    frames = []
    pre_roll = collections.deque(maxlen=PRE_ROLL_FRAMES)
    voice_run = 0
    silence_run = 0
    print("Ouvindo...")
    try:
        while True:
            frame = q.get()
            speech = is_speech(frame)

            if not recording:
                pre_roll.append(frame)
                voice_run = voice_run + 1 if speech else 0

                if voice_run >= START_VOICE_FRAMES:
                    recording = True
                    frames = list(pre_roll)
                    pre_roll.clear()
                    silence_run = 0
                    print("Gravando...")
            else:
                frames.append(frame)
                silence_run = 0 if speech else silence_run + 1

                if silence_run >= SILENCE_FRAMES_TO_STOP:
                    audio = np.concatenate(frames, axis=0).squeeze().astype(np.float32)
                    print("Parou.\n")
                    return audio

    finally:
        stream.stop()
        stream.close()