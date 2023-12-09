import config
import stt
import tts
from fuzzywuzzy import fuzz
import datetime
# import num2t4ru import num2text
import webbrowser
import random

tts.speak("Hi sir, how can I halp you.")


def respond(voice: str):
    print(voice)

    if voice.startswith(config.ALIAS):
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
        text = "Now it's" + str(c_time.hour) + " " + str(c_time.minute)
        tts.speak(text)
    elif cmd == 'open_browser':
        webbrowser.open('https://google.com')


stt.listen(respond)
