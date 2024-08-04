import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import random
import pygame
from typing import List, Tuple, Optional

# Pygameの初期化（音声用）
pygame.mixer.init()

# 効果音の読み込み
sound_star: pygame.mixer.Sound = pygame.mixer.Sound('path_to_star_sound.wav')
sound_sun: pygame.mixer.Sound = pygame.mixer.Sound('path_to_sun_sound.wav')
sound_butterfly: pygame.mixer.Sound = pygame.mixer.Sound('path_to_butterfly_sound.wav')
sound_fish: pygame.mixer.Sound = pygame.mixer.Sound('path_to_fish_sound.wav')
sound_turtle: pygame.mixer.Sound = pygame.mixer.Sound('path_to_turtle_sound.wav')
sound_dog: pygame.mixer.Sound = pygame.mixer.Sound('path_to_dog_sound.wav')
sound_rainbow: pygame.mixer.Sound = pygame.mixer.Sound('path_to_rainbow_sound.wav')
sound_swallow: pygame.mixer.Sound = pygame.mixer.Sound('path_to_swallow_sound.wav')

class AnimatedObject:
    def __init__(self, image_path: str, x: int, y: int, speed_x: int, speed_y: int, sound: pygame.mixer.Sound):
        self.image: np.ndarray = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        self.x: int = x
        self.y: int = y
        self.speed_x: int = speed_x
        self.speed_y: int = speed_y
        self.sound: pygame.mixer.Sound = sound

    def move(self, width: int, height: int) -> None:
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x < 0 or self.x > width - self.image.shape[1]:
            self.speed_x *= -1
            self.sound.play()
        if self.y < 0 or self.y > height - self.image.shape[0]:
            self.speed_y *= -1
            self.sound.play()

    def draw(self, frame: np.ndarray) -> None:
        h, w = self.image.shape[:2]
        if self.x + w > frame.shape[1] or self.y + h > frame.shape[0]:
            return
        if self.image.shape[2] == 4:  # With alpha channel
            alpha: np.ndarray = self.image[:, :, 3] / 255.0
            for c in range(3):
                frame[self.y:self.y+h, self.x:self.x+w, c] = \
                    frame[self.y:self.y+h, self.x:self.x+w, c] * (1 - alpha) + \
                    self.image[:, :, c] * alpha
        else:
            frame[self.y:self.y+h, self.x:self.x+w] = self.image

class Rainbow:
    def __init__(self, sound: pygame.mixer.Sound):
        self.active: bool = False
        self.duration: float = 5.0  # 虹の表示時間（秒）
        self.start_time: float = 0.0
        self.sound: pygame.mixer.Sound = sound

    def activate(self) -> None:
        self.active = True
        self.start_time = time.time()
        self.sound.play()

    def draw(self, frame: np.ndarray) -> np.ndarray:
        if not self.active:
            return frame

        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2
        radius: int = min(width, height) // 2

        for r in range(radius, radius - 30, -5):
            color: Tuple[int, int, int] = self.get_rainbow_color((radius - r) / 30)
            cv2.circle(frame, (center_x, center_y), r, color, 5)

        if time.time() - self.start_time > self.duration:
            self.active = False

        return frame

    def get_rainbow_color(self, position: float) -> Tuple[int, int, int]:
        position = max(0, min(position, 1))
        hue: int = int(position * 180)  # Hue ranges from 0 to 180 in OpenCV
        hsv: np.ndarray = np.uint8([[[hue, 255, 255]]])
        rgb: np.ndarray = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0][0]
        return tuple(map(int, rgb))

class Swallow:
    def __init__(self, image_path: str, sound: pygame.mixer.Sound):
        self.image: np.ndarray = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        self.active: bool = False
        self.x: int = -100  # Start off-screen
        self.y: int = 0
        self.speed: int = 10
        self.sound: pygame.mixer.Sound = sound

    def activate(self, height: int) -> None:
        self.active = True
        self.x = -100
        self.y = random.randint(0, height - self.image.shape[0])
        self.sound.play()

    def move(self, width: int) -> None:
        if not self.active:
            return
        self.x += self.speed
        if self.x > width:
            self.active = False

    def draw(self, frame: np.ndarray) -> None:
        if not self.active:
            return
        h, w = self.image.shape[:2]
        if self.x + w > frame.shape[1] or self.y + h > frame.shape[0]:
            return
        if self.image.shape[2] == 4:  # With alpha channel
            alpha: np.ndarray = self.image[:, :, 3] / 255.0
            for c in range(3):
                frame[self.y:self.y+h, self.x:self.x+w, c] = \
                    frame[self.y:self.y+h, self.x:self.x+w, c] * (1 - alpha) + \
                    self.image[:, :, c] * alpha
        else:
            frame[self.y:self.y+h, self.x:self.x+w] = self.image

def add_baby_effects(frame: np.ndarray, objects: List[AnimatedObject], rainbow: Rainbow, swallow: Swallow) -> np.ndarray:
    # エフェクト1: 明るい色を強調
    hsv: np.ndarray = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv[:,:,1] = hsv[:,:,1] * 1.5  # 彩度を上げる
    hsv[:,:,2] = np.clip(hsv[:,:,2] * 1.2, 0, 255)  # 明度を上げる
    frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # エフェクト2: ふわふわした縁を追加
    blurred: np.ndarray = cv2.GaussianBlur(frame, (21, 21), 0)
    frame = cv2.addWeighted(frame, 0.7, blurred, 0.3, 0)

    # エフェクト3: アニメーションオブジェクトを描画
    for obj in objects:
        obj.move(frame.shape[1], frame.shape[0])
        obj.draw(frame)

    # エフェクト4: 虹を描画
    frame = rainbow.draw(frame)

    # エフェクト5: ツバメを描画
    swallow.move(frame.shape[1])
    swallow.draw(frame)

    return frame

def main() -> None:
    # カメラの初期化
    camera: PiCamera = PiCamera()
    camera.resolution = (1920, 1080)
    camera.framerate = 32
    rawCapture: PiRGBArray = PiRGBArray(camera, size=(1920, 1080))

    # カメラのウォームアップ時間
    time.sleep(0.1)

    # アニメーションオブジェクトの初期化
    objects: List[AnimatedObject] = [
        AnimatedObject('path_to_star.png', random.randint(0, 639), random.randint(0, 479), random.randint(1, 3), random.randint(1, 3), sound_star),
        AnimatedObject('path_to_sun.png', random.randint(0, 639), random.randint(0, 479), random.randint(1, 2), random.randint(1, 2), sound_sun),
        AnimatedObject('path_to_butterfly.png', random.randint(0, 639), random.randint(0, 479), random.randint(2, 4), random.randint(2, 4), sound_butterfly),
        AnimatedObject('path_to_fish.png', random.randint(0, 639), random.randint(0, 479), random.randint(3, 5), random.randint(3, 5), sound_fish),
        AnimatedObject('path_to_turtle.png', random.randint(0, 639), random.randint(0, 479), random.randint(1, 2), random.randint(1, 2), sound_turtle),
        AnimatedObject('path_to_dog.png', random.randint(0, 639), random.randint(0, 479), random.randint(4, 6), random.randint(4, 6), sound_dog),
    ]

    # 虹とツバメの初期化
    rainbow: Rainbow = Rainbow(sound_rainbow)
    swallow: Swallow = Swallow('path_to_swallow.png', sound_swallow)

    # タイミング制御用の変数
    last_rainbow_time: float = time.time()
    last_swallow_time: float = time.time()
    rainbow_interval: float = 30.0  # 虹が現れる間隔（秒）
    swallow_interval: float = 45.0  # ツバメが現れる間隔（秒）

    # メインループ
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image: np.ndarray = frame.array

        # 虹の出現チェック
        current_time: float = time.time()
        if current_time - last_rainbow_time > rainbow_interval and not rainbow.active:
            rainbow.activate()
            last_rainbow_time = current_time

        # ツバメの出現チェック
        if current_time - last_swallow_time > swallow_interval and not swallow.active:
            swallow.activate(image.shape[0])
            last_swallow_time = current_time

        # エフェクトを適用
        output: np.ndarray = add_baby_effects(image, objects, rainbow, swallow)

        # 結果を表示
        cv2.imshow("Baby Camera", output)

        # キャプチャをクリア
        rawCapture.truncate(0)

        # 'q'キーが押されたらループを抜ける
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # クリーンアップ
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()