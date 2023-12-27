import sys
import queue
import time
import struct
import json

import config
import tts
from fuzzywuzzy import fuzz
import datetime
# import num2t4ru import num2text
import inflect
import webbrowser
import vosk
import sounddevice as sd
import pvporcupine
from pvrecorder import PvRecorder


porcupine = pvporcupine.create(access_key='IBLG8U7CAM+kQOHVNcjGhdg+cSso95n6diIAVKc5sFXuLAWpfxlq+g==',
                               keyword_paths=['./jarvis_en/jarvis_en_windows_v3_0_0.ppn'])

model = vosk.Model("model")
samplerate = 16000
kaldi_rec = vosk.KaldiRecognizer(model, samplerate)
q = queue.Queue()

tts.speak("Hi sir, how can I halp you ... ")


def q_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def respond(voice: str):
    global recorder
    print(voice)

    cmd = recognize_cmd(filter_cmd(voice))

    if cmd['cmd'] not in config.CMD_LIST.keys():
        tts.speak("What did you say?")
    else:
        execute_cmd(cmd['cmd'])


def filter_cmd(raw_voice: str):
    cmd = raw_voice

    for x in config.ALIAS:
        cmd = cmd.replace(x, '').strip()

    for x in config.TBR:
        cmd = cmd.replace(x, '').strip()

    return cmd


def recognize_cmd(cmd: str):
    rc = {'cmd': '', 'percent': 0}

    for c, v in config.CMD_LIST.items():
        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > rc['percent']:
                rc['cmd'] = c
                rc['percent'] = vrt

    return rc


def execute_cmd(cmd: str):
    if cmd == 'help':
        pass
    elif cmd == "ctime":
        c_time = datetime.datetime.now()
        print(c_time)

        # Using inflect to convert numeric values to words
        p = inflect.engine()
        hour_text = p.number_to_words(c_time.hour)
        minute_text = p.number_to_words(c_time.minute)

        text = f"Now it's {hour_text} {minute_text}"
        tts.speak(text)
    elif cmd == 'open_browser':
        webbrowser.open('https://google.com')


recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
recorder.start()
print("Jarvis started working !)")

ltc = time.time() - 1000

while True:
    try:
        pcm = recorder.read()
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            recorder.stop()
            print("Yes, sir.")
            tts.speak("Yes sir")
            recorder.start()  # prevent self recording
            ltc = time.time()

        while time.time() - ltc <= 10:
            pcm = recorder.read()
            sp = struct.pack("h" * len(pcm), *pcm)

            if kaldi_rec.AcceptWaveform(sp):
                if respond(json.loads(kaldi_rec.Result())["text"]):
                    ltc = time.time()

                break

    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise