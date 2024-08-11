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

def apply_kaleidoscope(frame, frame_count):
    height, width = frame.shape[:2]
    center_x, center_y = width // 2, height // 2
    angle = frame_count * 0.1
    scale = 1 + 0.1 * np.sin(frame_count * 0.05)
    
    segments = 8
    kaleidoscope_layer = np.zeros_like(frame)
    for i in range(segments):
        rot = cv2.getRotationMatrix2D((center_x, center_y), angle + i * (360 / segments), scale)
        rot_frame = cv2.warpAffine(frame, rot, (width, height))
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.ellipse(mask, (center_x, center_y), (width, height), 0, i * (360 / segments), (i + 1) * (360 / segments), 255, -1)
        kaleidoscope_layer = cv2.add(kaleidoscope_layer, cv2.bitwise_and(rot_frame, rot_frame, mask=mask))
    
    return cv2.addWeighted(frame, 0.7, kaleidoscope_layer, 0.3, 0)

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
    
    return cv2.addWeighted(frame, 1, star_layer, 0.5, 0)

def apply_text_animation(frame, frame_count):
    height, width = frame.shape[:2]

    # 一定時間ごとにテキストを切り替える
    if (frame_count // 100) % 2 == 0:
        text = "Party Time!"
    else:
        text = "Make Some Noise!"

    font = cv2.FONT_HERSHEY_SIMPLEX

    # テキストサイズを膨らませたり縮めたりする
    scale = 1 + 0.5 * np.sin(frame_count * 0.1)
    
    # ビートに合わせて振動するような効果
    jitter_x = int(5 * np.sin(frame_count * 0.3))
    jitter_y = int(5 * np.cos(frame_count * 0.3))

    text_size = cv2.getTextSize(text, font, scale, 2)[0]
    text_x = int((width - text_size[0]) / 2) + jitter_x
    text_y = int(height / 2 + text_size[1] / 2) + jitter_y

    color = (int(255 * np.sin(frame_count * 0.1)**2), 
             int(255 * np.sin(frame_count * 0.1 + np.pi/3)**2), 
             int(255 * np.sin(frame_count * 0.1 + 2*np.pi/3)**2))
    
    cv2.putText(frame, text, (text_x, text_y), font, scale, color, 2, cv2.LINE_AA)
    
    return frame

def apply_baby_magic_mirror_effect(frame, frame_count):
    height, width = frame.shape[:2]
    
    rainbow_y = int(height * (np.sin(frame_count * 0.05) * 0.5 + 0.5))
    frame = draw_rainbow(frame, rainbow_y, opacity=0.2)
    frame = apply_bubble_effect(frame, frame_count)
    frame = apply_sparkle_effect(frame, frame_count)
    frame = apply_star_twinkle_effect(frame, frame_count)

    pulse = np.sin(frame_count * 0.1) * 15 + 15
    overlay = np.full(frame.shape, (0, 255, 255), dtype=np.uint8)
    frame = cv2.addWeighted(frame, 1, overlay, pulse / 255 * 0.2, 0)

    # テキストアニメーションを適用
    frame = apply_text_animation(frame, frame_count)
    
    return frame

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": 'RGB888', "size": (1280, 960)})
picam2.configure(config)
picam2.start()

frame_count = 0
try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        magic_mirror_frame = apply_baby_magic_mirror_effect(frame, frame_count)
        cv2.imshow("Baby Magic Mirror", magic_mirror_frame)
        frame_count += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cv2.destroyAllWindows()
    picam2.stop()
