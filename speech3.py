from pydub import AudioSegment
import time
import math
from playsound import playsound
import webbrowser
import subprocess
import speech_recognition as sr
import pandas as pd
import random
import pyautogui
import numpy as np
import pyaudio
import wave
import openai
import requests
import json
from IPython.display import Javascript
from base64 import b64decode

def stt(audio_file):
    st = time.time()
    headers = {
        'accept': 'application/json',
        'x-gladia-key': '9399f5c0-98fa-468e-ac22-eee3f452d1b5',
    }

    files = {
        'audio': (audio_file, open(audio_file, 'rb'), 'audio/mpeg'),
        #'audio_url': (None, 'http://files.gladia.io/example/audio-transcription/split_infinity.wav'),
        #'language': (None, 'japanese'),
        'language_behaviour': (None, 'automatic single language'),
    }

    response = requests.post(
        'https://api.gladia.io/audio/text/audio-transcription/',
        headers=headers,
        files=files)

    et = time.time()
    elapsed_time = et - st

    # Save the response to a file
    with open('response.json', 'w') as f:
        f.write(response.text)

    return response, elapsed_time
    # ファイルからiとjの値を読み込む関数
def load_values(filename):
    try:
        with open(filename, 'r') as file:
            #e_hap,v_hap,e_sad,v_sad,e_ang,v_ang,e_fea,v_fea,e_dis,v_dis,e_sur,v_sur,e_neu,v_neu = map(float, file.readline().split())
            e_hap,v_hap,e_sad,v_sad,e_ang,v_ang,e_fea,v_fea,e_dis,v_dis,e_sur,v_sur,e_neu,v_neu = map(float, file.readline().split(','))
            return e_hap,v_hap,e_sad,v_sad,e_ang,v_ang,e_fea,v_fea,e_dis,v_dis,e_sur,v_sur,e_neu,v_neu
    except FileNotFoundError:
        return None, None

# ファイルにiとjの値を保存する関数
def save_values(filename, e_hap,v_hap,e_sad,v_sad,e_ang,v_ang,e_fea,v_fea,e_dis,v_dis,e_sur,v_sur,e_neu,v_neu):
    with open(filename, 'w') as file:
        file.write(f"{e_hap},{v_hap},{e_sad},{v_sad},{e_ang},{v_ang},{e_fea},{v_fea},{e_dis},{v_dis},{e_sur},{v_sur},{e_neu},{v_neu}")




# 初回実行時、もしくはファイルが存在しない場合
"""if e_hap is None or v_hap is None or e_sad is None or v_sad is None or e_ang is None or v_ang is None or e_fea is None or v_fea is None or e_dis is None or v_dis is None or e_sur is None or v_sur is None or e_neu is None or v_neu is None:
    e_hap = 0.5
    v_hap = 0.5
    e_sad = 0.2
    v_sad = 0.2
    e_ang = 0.5
    v_ang = 0.2
    e_fea = 0.5
    v_fea = 0.2
    e_dis = 0.5
    v_dis = 0.2
    e_sur = 0.5
    v_sur = 0.5
    e_neu = 0.3
    v_neu = 0.4"""

lower_limit = 0
upper_limit = 0.7


RECORD = """
const sleep = time => new Promise(resolve => setTimeout(resolve, time))
const b2text = blob => new Promise(resolve => {
  const reader = new FileReader()
  reader.onloadend = e => resolve(e.srcElement.result)
  reader.readAsDataURL(blob)
})
var record = time => new Promise(async resolve => {
  stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  recorder = new MediaRecorder(stream)
  chunks = []
  recorder.ondataavailable = e => chunks.push(e.data)
  recorder.start()
  await sleep(time)
  recorder.onstop = async ()=>{
    blob = new Blob(chunks)
    text = await b2text(blob)
    resolve(text)
  }
  recorder.stop()
})
"""

def record(sec, filename='audio.wav'):
  display(Javascript(RECORD))
  s = output.eval_js('record(%d)' % (sec * 1000))
  b = b64decode(s.split(',')[1])
  with open(filename, 'wb+') as f:
    f.write(b)

df = pd.read_csv('output4.csv')

def jtalk(t):
    open_jtalk=['open_jtalk']
    mech=['-x','/var/lib/mecab/dic/open-jtalk/naist-jdic']
    htsvoice=['-m','/usr/share/hts-voice/mei/mei_normal.htsvoice']
    speed=['-r','1.0']#1.0
    outwav=['-ow','open_jtalk.wav']
    cmd=open_jtalk+mech+htsvoice+speed+outwav
    c = subprocess.Popen(cmd,stdin=subprocess.PIPE)
    c.stdin.write(t.encode())
    c.stdin.close()
    c.wait()
    aplay = ['aplay','-q','open_jtalk.wav']
    wr = subprocess.Popen(aplay)
    sound = AudioSegment.from_file("open_jtalk.wav", "wav")
    times = sound.duration_seconds
    print(times)
    time.sleep(math.ceil(times))
    
def say_datetime(emotion,emotion_value,atmo):
        filename = "values.txt"
        e_hap,v_hap,e_sad,v_sad,e_ang,v_ang,e_fea,v_fea,e_dis,v_dis,e_sur,v_sur,e_neu,v_neu = load_values(filename)
        openai.api_key = "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"
        if emotion == "neutral":
            prompt = "一文目に表情から相手が"+ atmo +"の雰囲気であると読み取ったことを言いなさい。二文目にその雰囲気を踏まえて音楽を流すことを提案しなさい。ただし相手のことは「あなた」と呼びこと。"
        else:
            prompt = "一文目に表情から相手が"+ emotion +"の感情であると読み取ったことを言いなさい。二文目にその感情を踏まえて音楽を流すことを提案しなさい。ただし相手のことは「あなた」と呼ぶこと。"
        response = openai.ChatCompletion.create(
                            model = "gpt-3.5-turbo-16k-0613",
                            messages = [
                                {"role": "system", "content": "You are the proposer, and in one sentence you always speak in about 15 words, touching on their feelings."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0
                        )
        #has a positive meaning
        # 応答の表示
        text = response['choices'][0]['message']['content']
        
        jtalk(text)

        time.sleep(4)

        r = sr.Recognizer()
        mic = sr.Microphone()
        while True:
            jtalk("なにか話してください ...")

            with mic as source:
                r.adjust_for_ambient_noise(source) #ノイズ除去
                audio = r.listen(source)

            jtalk ("認識中...")

            try:
                print("detecting...")
                detected = r.recognize_google(audio, language='ja-JP')
                print(detected)
                prompt = "You suggest playing music." + detected + "is the response to the proposal. If"+detected+ "has a positive meaning, please return '1', and if" +detected+ "has negative meaning, please return '0'.If you cannot decide, please answer '2'."
                response = openai.ChatCompletion.create(
                                    model = "gpt-3.5-turbo-16k-0613",
                                    messages = [
                                        {"role": "system", "content": "Just answer questions faithfully."},
                                        {"role": "user", "content": prompt}
                                    ],
                                    temperature=0
                                )
                #has a positive meaning
                # 応答の表示
                text = response['choices'][0]['message']['content']
                print(text)
                judge = int(text)
                #print("detecting...")
                #detected = r.recognize_google(audio, language='ja-JP')
                #print(detected)

                if judge == 0 :
                    exit()
                elif judge == 1 :
                    #jtalk("音楽を再生します")
                    #url = "https://www.youtube.com/watch?v=d6ItrROosYw&t=60s&autoplay=1"
                    #webbrowser.open(url)
                    
                    filtered_results = []
                    
                        # i と j の範囲に該当する行をフィルタリング
                    if emotion == "happy":
                        filtered_results = df[
                            (df['energy'] >= e_hap) & (df['energy'] <= e_hap + 0.4) &
                            (df['valence'] >= v_hap) & (df['valence'] <= v_hap + 0.4)
                        ]
                    elif emotion == "sad":
                        filtered_results = df[
                            (df['energy'] >= e_sad) & (df['energy'] <= e_sad + 0.4) &
                            (df['valence'] >= v_sad) & (df['valence'] <= v_sad + 0.4)
                        ]
                    elif emotion == "angry":
                        filtered_results = df[
                            (df['energy'] >= e_ang) & (df['energy'] <= e_ang + 0.4) &
                            (df['valence'] >= v_ang) & (df['valence'] <= v_ang + 0.4)
                        ]
                    elif emotion == "fear":
                        filtered_results = df[
                            (df['energy'] >= e_fea) & (df['energy'] <= e_fea + 0.4) &
                            (df['valence'] >= v_fea) & (df['valence'] <= v_fea + 0.4)
                        ]
                    elif emotion == "disgust":
                        filtered_results = df[
                            (df['energy'] >= e_dis) & (df['energy'] <= e_dis + 0.4) &
                            (df['valence'] >= v_dis) & (df['valence'] <= v_dis + 0.4)
                        ]
                    elif emotion == "surprise":
                        filtered_results = df[
                            (df['energy'] >= e_sur) & (df['energy'] <= e_sur + 0.4) &
                            (df['valence'] >= v_sur) & (df['valence'] <= v_sur + 0.4)
                        ]
                    elif emotion == "neutral":
                        filtered_results = df[
                            (df['energy'] >= e_neu) & (df['energy'] <= e_neu + 0.4) &
                            (df['valence'] >= v_neu) & (df['valence'] <= v_neu + 0.4)
                        ]
                    # ランダムに1行を選択
                    if len(filtered_results) > 0:
                        random_result = filtered_results.sample(n=1).iloc[0]
                        url = random_result['URL']
                        energy = random_result['energy']
                        valence = random_result['valence']
                        print(url)
                        webbrowser.open(url, 1)
                        time.sleep(15)
                        pyautogui.click(140, 607)
                        #pyautogui.moveTo(450,350)
                        #pyautogui.scroll(-100)
                        #time.sleep(1)
                        #pyautogui.click(170, 187)    
                        break
                    else:
                        print("can't find data")
            except sr.UnknownValueError:
                jtalk("認識できませんでした。")
            except sr.RequestError as e:
                jtalk("Could not request results from Google Speech Recognition service; {0}".format(e))
            #review = input("Please enter good if this song fits your emotion, bad if it doesn't.:")
            review = "good"
            if review == "bad":
                if emotion == "happy":        
                    if energy < e_hap + 0.15:
                        e_hap = min(e_hap + 0.1, upper_limit)
                    else:
                        e_hap = max(e_hap - 0.1, lower_limit)
                    if valence < v_hap + 0.15:
                        v_hap = min(v_hap + 0.1, upper_limit)
                    else:
                        v_hap = max(v_hap - 0.1, lower_limit)
                if emotion == "sad":        
                    if energy < e_sad + 0.15:
                        e_sad = min(e_sad + 0.1, upper_limit)
                    else:
                        e_sad = max(e_sad - 0.1, lower_limit)
                    if valence < v_sad + 0.15:
                        v_sad = min(v_sad + 0.1, upper_limit)
                    else:
                        v_sad = max(v_sad - 0.1, lower_limit)
                if emotion == "angry":        
                    if energy < e_ang + 0.15:
                        e_ang = min(e_ang + 0.1, upper_limit)
                    else:
                        e_ang = max(e_ang - 0.1, lower_limit)
                    if valence < v_ang + 0.15:
                        v_ang = min(v_ang + 0.1, upper_limit)
                    else:
                        v_ang = max(v_ang - 0.1, lower_limit)
                if emotion == "fear":        
                    if energy < e_fea + 0.15:
                        e_fea = min(e_fea + 0.1, upper_limit)
                    else:
                        e_fea = max(e_fea - 0.1, lower_limit)
                    if valence < v_fea + 0.15:
                        v_fea = min(v_fea + 0.1, upper_limit)
                    else:
                        v_fea = max(v_fea - 0.1, lower_limit)
                if emotion == "disgust":        
                    if energy < e_dis + 0.15:
                        e_dis = min(e_dis + 0.1, upper_limit)
                    else:
                        e_dis = max(e_dis - 0.1, lower_limit)
                    if valence < v_dis + 0.15:
                        v_dis = min(v_dis + 0.1, upper_limit)
                    else:
                        v_dis = max(v_dis - 0.1, lower_limit)
                if emotion == "surprise":        
                    if energy < e_sur + 0.15:
                        e_sur = min(e_sur + 0.1, upper_limit)
                    else:
                        e_sur = max(e_sur - 0.1, lower_limit)
                    if valence < v_sur + 0.15:
                        v_sur = min(v_sur + 0.1, upper_limit)
                    else:
                        v_sur = max(v_sur - 0.1, lower_limit)
                if emotion == "neutral":        
                    if energy < e_neu + 0.15:
                        e_neu = min(e_neu + 0.1, upper_limit)
                    else:
                        e_neu = max(e_neu - 0.1, lower_limit)
                    if valence < v_neu + 0.15:
                        v_neu = min(v_neu + 0.1, upper_limit)
                    else:
                        v_neu = max(v_neu - 0.1, lower_limit)
                               
                e_hap = round(min(max(e_hap, lower_limit), upper_limit),1)
                v_hap = round(min(max(v_hap, lower_limit), upper_limit),1)
                e_sad = round(min(max(e_sad, lower_limit), upper_limit),1)
                v_sad = round(min(max(v_sad, lower_limit), upper_limit),1)
                e_ang = round(min(max(e_ang, lower_limit), upper_limit),1)
                v_ang = round(min(max(v_ang, lower_limit), upper_limit),1)
                e_fea = round(min(max(e_fea, lower_limit), upper_limit),1)
                v_fea = round(min(max(v_fea, lower_limit), upper_limit),1)
                e_dis = round(min(max(e_dis, lower_limit), upper_limit),1)
                v_dis = round(min(max(v_dis, lower_limit), upper_limit),1)
                e_sur = round(min(max(e_sur, lower_limit), upper_limit),1)
                v_sur = round(min(max(v_sur, lower_limit), upper_limit),1)
                e_neu = round(min(max(e_neu, lower_limit), upper_limit),1)
                v_neu = round(min(max(v_neu, lower_limit), upper_limit),1)
                            
            # iとjの値を保存
                save_values(filename, e_hap,v_hap,e_sad,v_sad,e_ang,v_ang,e_fea,v_fea,e_dis,v_dis,e_sur,v_sur,e_neu,v_neu)
                print(f"e_hap = {e_hap}, v_hap = {v_hap}, e_sad = {e_sad}, v_sad = {v_sad}, e_ang = {e_ang}, v_ang = {v_ang}, e_fea = {e_fea}, v_fea = {v_fea}, e_dis = {e_dis}, v_dis = {v_dis}, e_sur = {e_sur}, v_sur = {v_sur}, e_neu = {e_neu}, v_neu = {v_neu},")
            else:
                print("thank you")
