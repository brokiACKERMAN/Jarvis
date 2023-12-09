import queue
import sounddevice as sd
import vosk
import sys
import json
import words
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import pvporcupine
from pvrecorder import PvRecorder

porcupine = pvporcupine.create(access_key='IBLG8U7CAM+kQOHVNcjGhdg+cSso95n6diIAVKc5sFXuLAWpfxlq+g==',
                               keyword_paths=['./jarvis_en_windows_v2_2_0.ppn'])

q = queue.Queue()
model = vosk.Model("model")
device = sd.default.device = 0, 4
samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])
kaldi_rec = vosk.KaldiRecognizer(model, samplerate)


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def recognize(data, vectorizer, clf):
    trg = words.TRIGGERS.intersection(data.split())
    if not trg:
        return

    text_vector = vectorizer.transform([data]).toarray()[0]
    answer = clf.predict([text_vector])[0]
    print(answer)


def main():
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(list(words.data_set.keys()))

    clf = LogisticRegression()
    clf.fit(vectors, list(words.data_set.values()))

    del words.data_set

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

    with sd.RawInputStream(samplerate=samplerate, blocksize=4800, device=device[0],
                           dtype='int16', channels=1, callback=callback):
        while True:
            data = q.get()

            audio_frame = kaldi_rec.AcceptWaveform(data)
            keyword_index = porcupine.process(audio_frame)
            if keyword_index == 0:
                print("Yes, sir")

            if kaldi_rec.AcceptWaveform(data):
                data = json.loads(kaldi_rec.Result())['text']
                recognize(data, vectorizer, clf)
                print(data)
            # else:
            #     data = json.loads(rec.Result())['text']
            #     recognize(data, vectorizer, clf)
            #     print(data)


if __name__ == "__main__":
    main()
