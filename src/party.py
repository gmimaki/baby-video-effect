import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

def create_rainbow_colors():
    return [(255,0,0), (255,127,0), (255,255,0), (0,255,0), (0,0,255), (75,0,130), (143,0,255)]

def draw_rainbow(frame, y_pos):
    height, width = frame.shape[:2]
    colors = create_rainbow_colors()
    bar_height = height // len(colors)
    for i, color in enumerate(colors):
        y = y_pos + i * bar_height
        cv2.rectangle(frame, (0, y), (width, y + bar_height), color, -1)
    return cv2.addWeighted(frame, 0.7, frame, 0.3, 0)

def apply_party_effect(frame, frame_count):
    height, width = frame.shape[:2]
    
    # 虹色のオーバーレイ
    rainbow_y = int(height * (np.sin(frame_count * 0.05) * 0.5 + 0.5))
    frame = draw_rainbow(frame, rainbow_y)
    
    # キラキラエフェクト
    for _ in range(50):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        size = np.random.randint(2, 5)
        color = (255, 255, 255)
        alpha = np.random.rand() * 0.5 + 0.5
        cv2.circle(frame, (x, y), size, color, -1)
        frame = cv2.addWeighted(frame, 1 - alpha, frame, alpha, 0)
    
    # パルス効果
    pulse = np.sin(frame_count * 0.1) * 30 + 30
    overlay = np.full(frame.shape, (0, 255, 255), dtype=np.uint8)
    frame = cv2.addWeighted(frame, 1, overlay, pulse / 255, 0)
    
    # 画面を歪ませる
    rows, cols = frame.shape[:2]
    distortion = cv2.getRotationMatrix2D((cols/2, rows/2), 0, 1 + 0.05 * np.sin(frame_count * 0.1))
    frame = cv2.warpAffine(frame, distortion, (cols, rows))
    
    # テキストアニメーション
    text = "PARTY TIME!"
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, 1, 2)[0]
    text_x = int((width - text_size[0]) / 2)
    text_y = int(height / 2 + text_size[1] / 2)
    color = (255 * np.sin(frame_count * 0.1)**2, 
             255 * np.sin(frame_count * 0.1 + np.pi/3)**2, 
             255 * np.sin(frame_count * 0.1 + 2*np.pi/3)**2)
    cv2.putText(frame, text, (text_x, text_y), font, 1, color, 2, cv2.LINE_AA)
    
    return frame

# カメラの初期化
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# カメラのウォームアップ
time.sleep(0.1)

# メインループ
frame_count = 0
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    
    # パーティーエフェクトを適用
    party_image = apply_party_effect(image, frame_count)
    
    # 結果を表示
    cv2.imshow("Baby Party Cam", party_image)
    
    # キャプチャをクリア
    rawCapture.truncate(0)
    
    # フレームカウントを更新
    frame_count += 1
    
    # 'q'キーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()