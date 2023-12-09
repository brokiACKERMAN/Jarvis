import pvporcupine
from pvrecorder import PvRecorder

porcupine = pvporcupine.create(access_key='IBLG8U7CAM+kQOHVNcjGhdg+cSso95n6diIAVKc5sFXuLAWpfxlq+g==',
                               keyword_paths=['./jarvis_en/jarvis_en_windows_v2_2_0.ppn'])
recoder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

try:
    recoder.start()

    while True:
        keyword_index = porcupine.process(recoder.read())
        if keyword_index == 0:
            print("HI")

except KeyboardInterrupt:
    recoder.stop()
finally:
    porcupine.delete()
    recoder.delete()
