import cv2
import numpy as np
import time
import random

def create_rainbow_colors():
    return [(255,0,0), (255,127,0), (255,255,0), (0,255,0), (0,0,255), (75,0,130), (143,0,255)]

def draw_rainbow(frame, y_pos, opacity=0.2):
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
    
    return cv2.add(bubble_layer, frame)

def apply_sparkle_effect(frame, frame_count):
    height, width = frame.shape[:2]
    sparkle_layer = np.zeros_like(frame)
    
    for _ in range(50):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        size = np.random.randint(2, 5)
        color = (255, 255, 255)
        cv2.circle(sparkle_layer, (x, y), size, color, -1)
    
    return cv2.add(sparkle_layer, frame)

def apply_star_twinkle_effect(frame, frame_count):
    height, width = frame.shape[:2]
    star_layer = np.zeros_like(frame)
    
    for _ in range(30):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        size = np.random.randint(10, 20)
        color = (255, 255, np.random.randint(200, 255))
        
        for i in range(5):
            pt1 = (int(x + size * np.cos(2 * np.pi * i / 5)), 
                   int(y + size * np.sin(2 * np.pi * i / 5)))
            pt2 = (int(x + size * np.cos(2 * np.pi * (i + 2) / 5)), 
                   int(y + size * np.sin(2 * np.pi * (i + 2) / 5)))
            cv2.line(star_layer, pt1, pt2, color, 2)
        
        if frame_count % 30 > 15:
            cv2.circle(star_layer, (x, y), size // 4, color, -1)
    
    return cv2.add(star_layer, frame)

def apply_baby_magic_mirror_effect(frame, frame_count):
    height, width = frame.shape[:2]
    
    # レインボーエフェクト
    rainbow_y = int(height * (np.sin(frame_count * 0.05) * 0.5 + 0.5))
    frame = draw_rainbow(frame, rainbow_y, opacity=0.2)
    
    # バブルエフェクト
    frame = apply_bubble_effect(frame, frame_count)
    
    # キラキラエフェクト
    frame = apply_sparkle_effect(frame, frame_count)

    # 星のキラキラエフェクト
    frame = apply_star_twinkle_effect(frame, frame_count)
    
    # テキストアニメーション
    texts = ["Party Time!", "Make Some Noise!"]
    text = texts[(frame_count // 100) % 2]
    
    beat = 1.0 + 0.2 * np.sin(frame_count * 0.3)
    vibrate = 1.0 + 0.05 * np.sin(frame_count * 3.0)
    scale = beat * vibrate
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1 * scale
    text_size = cv2.getTextSize(text, font, font_scale, 2)[0]
    text_x = int((width - text_size[0]) / 2)
    text_y = int(height / 2 + text_size[1] / 2)
    color = (int(255 * np.sin(frame_count * 0.1)**2), 
             int(255 * np.sin(frame_count * 0.1 + np.pi/3)**2), 
             int(255 * np.sin(frame_count * 0.1 + 2*np.pi/3)**2))
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, 2, cv2.LINE_AA)
    
    return frame

# ウィンドウを作成して全画面表示モードに設定
cv2.namedWindow("Baby Magic Mirror", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Baby Magic Mirror", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# メインループ
frame_count = 0
try:
    while True:
        # 背景フレームの作成（白い背景）
        frame = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
        
        # ベビーマジックミラーエフェクトを適用
        magic_mirror_frame = apply_baby_magic_mirror_effect(frame, frame_count)
        
        # 結果を表示
        cv2.imshow("Baby Magic Mirror", magic_mirror_frame)
        
        # フレームカウントを更新
        frame_count += 1
        
        # 'q'キーで終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # フレームレートを制御（約30FPS）
        time.sleep(1/30)

finally:
    cv2.destroyAllWindows()