import cv2
import matplotlib.pyplot as plt
from deepface import DeepFace
import speech3
import gpt4v_test

#カメラを開く
cap = cv2.VideoCapture(0)

#画像をキャプチャする
ret, frame = cap.read()

#画像を保存する
cv2.imwrite("./Pictures/image.jpg", frame)

#カメラを閉じる
cap.release()
img = cv2.imread('./Pictures/image.jpg')#26972965_s.jpg#26951174_s.jpg
img_path = './Pictures/image.jpg'
#plt.imshow(img[:,:,::-1])

plt.show()

result = DeepFace.analyze(img_path = img_path, actions = ['emotion'])

# 結果の最初の要素（ここでは顔データ）を取得
first_result = result[0]

# 感情の値を取得
dominant_emotion = first_result['dominant_emotion']
dominant_emotion_value = first_result["emotion"][dominant_emotion]

print("Dominant emotion: ",dominant_emotion, "\nEmotion score: ", dominant_emotion_value)

emotion = dominant_emotion
emotion_value = dominant_emotion_value
#if emotion == "neutral":
atmo = gpt4v_test.main_gpt(img_path)
#else:
speech3.say_datetime(emotion,emotion_value,atmo)
