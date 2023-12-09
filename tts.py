import torch
import sounddevice as sd
import time

language = 'en'
model_id = 'v3_en'
sample_rate = 48000
speaker = 'en_5'  # voice | sexy voice is 'en_0'
device = torch.device('cpu')

model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                     model='silero_tts',
                                     language=language,
                                     speaker=model_id)

model.to(device)  # gpu or cpu


def speak(what: str):
    audio = model.apply_tts(text=what,
                            speaker=speaker,
                            sample_rate=sample_rate,
                            put_accent=True,
                            put_yo=True)

    sd.play(audio, sample_rate)
    sd.wait()
    sd.stop()
