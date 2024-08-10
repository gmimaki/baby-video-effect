import cv2
import numpy as np
from picamera2 import Picamera2
import time
import random

def create_rainbow_colors():
    return [(255,0,0), (255,127,0), (255,255,0), (0,255,0), (0,0,255), (75,0,130), (143,0,255)]

def draw_rainbow(frame, y_pos, opacity=0.3):
    height, width = frame.shape[:2]
    colors = create_rainbow_colors()
    bar_height = height // len(colors)
    rainbow_layer = np.zeros_like(frame)
    for i, color in enumerate(colors):
        y = y_pos + i * bar_height
        cv2.rectangle(rainbow_layer, (0, y), (width, y + bar_height), color, -1)
    return cv2.addWeighted(frame, 1 - opacity, rainbow_layer, opacity, 0)

def apply_bubble_effect(frame, frame_count):
    height, width = frame.shape[:2]
    bubble_layer = np.zeros_like(frame)
    
    for _ in range(20):
        x = int(width * (0.5 + 0.4 * np.sin(frame_count * 0.01 + _ * 0.5)))
        y = int(height * (0.5 + 0.4 * np.cos(frame_count * 0.01 + _ * 0.5)))
        radius = int(20 + 10 * np.sin(frame_count * 0.1 + _ * 0.5))
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        cv2.circle(bubble_layer, (x, y), radius, color, -1)
    
    return cv2.addWeighted(frame, 0.7, bubble_layer, 0.3, 0)

def apply_sparkle_effect(frame, frame_count):
    height, width = frame.shape[:2]
    sparkle_layer = np.zeros_like(frame)
    
    for _ in range(50):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        size = np.random.randint(2, 5)
        color = (255, 255, 255)
        alpha = np.random.rand() * 0.5 + 0.5
        cv2.circle(sparkle_layer, (x, y), size, color, -1)
    
    return cv2.addWeighted(frame, 1, sparkle_layer, 0.3, 0)

def apply_mosaic_effect(frame, block_size=10):
    height, width = frame.shape[:2]
    mosaic_frame = cv2.resize(frame, (width // block_size, height // block_size), interpolation=cv2.INTER_LINEAR)
    mosaic_frame = cv2.resize(mosaic_frame, (width, height), interpolation=cv2.INTER_NEAREST)
    return mosaic_frame

def apply_swirl_effect(frame, frame_count):
    height, width = frame.shape[:2]
    swirl_layer = np.zeros_like(frame)
    center_x, center_y = width // 2, height // 2
    max_radius = np.sqrt(center_x**2 + center_y**2)
    
    for y in range(height):
        for x in range(width):
            offset_x = x - center_x
            offset_y = y - center_y
            radius = np.sqrt(offset_x**2 + offset_y**2)
            theta = np.arctan2(offset_y, offset_x) + (frame_count * 0.02) * (max_radius - radius) / max_radius
            new_x = int(center_x + radius * np.cos(theta))
            new_y = int(center_y + radius * np.sin(theta))
            
            if 0 <= new_x < width and 0 <= new_y < height:
                swirl_layer[y, x] = frame[new_y, new_x]
            else:
                swirl_layer[y, x] = 0
    
    return cv2.addWeighted(frame, 0.5, swirl_layer, 0.5, 0)

def apply_baby_magic_mirror_effect(frame, frame_count):
    height, width = frame.shape[:2]
    
    # 画面全体の明るさを調整
    frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=30)  # alphaはコントラスト、betaは明るさを調整
    
    # レインボー、バブル、キラキラのエフェクトを適用
    rainbow_y = int(height * (np.sin(frame_count * 0.05) * 0.5 + 0.5))
    frame = draw_rainbow(frame, rainbow_y, opacity=0.2)
    frame = apply_bubble_effect(frame, frame_count)
    frame = apply_sparkle_effect(frame, frame_count)
    
    # 時間経過によるエフェクト切り替え
    effect_selector = (frame_count // 1000) % 3
    
    if effect_selector == 0:
        # モザイクエフェクト
        frame = apply_mosaic_effect(frame, block_size=20)
    elif effect_selector == 1:
        # スワールエフェクト
        frame = apply_swirl_effect(frame, frame_count)
    # 既存のエフェクト（何も追加しない）

    # テキストアニメーション
    text = "Party Time!"
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, 1, 2)[0]
    text_x = int((width - text_size[0]) / 2)
    text_y = int(height / 2 + text_size[1] / 2)
    color = (int(255 * np.sin(frame_count * 0.1)**2), 
             int(255 * np.sin(frame_count * 0.1 + np.pi/3)**2), 
             int(255 * np.sin(frame_count * 0.1 + 2*np.pi/3)**2))
    cv2.putText(frame, text, (text_x, text_y), font, 1, color, 2, cv2.LINE_AA)
    
    return frame

# カメラの初期化
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)})
picam2.configure(config)
picam2.start()

# メインループ
frame_count = 0
try:
    while True:
        # フレームの取得
        frame = picam2.capture_array()
        
        # BGR形式に変換（OpenCVはBGR形式を使用）
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # ベビーマジックミラーエフェクトを適用
        magic_mirror_frame = apply_baby_magic_mirror_effect(frame, frame_count)
        
        # 結果を表示
        cv2.imshow("Baby Magic Mirror", magic_mirror_frame)
        
        # フレームカウントを更新
        frame_count += 1
        
        # 'q'キーで終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cv2.destroyAllWindows()
    picam2.stop()
