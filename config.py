import pygame

pygame.init()

WIDTH, HEIGHT = 800, 400
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ゴム人間格闘ゲーム")

FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GROUND = HEIGHT - 83

# 背景音楽
pygame.mixer.init()
pygame.mixer.music.load("assets/bgm.mp3")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

# 効果音
hit_sound = pygame.mixer.Sound("assets/hit.mp3")
hit_sound.set_volume(0.3)

# ガード音（金属的なカキン）をnumpyで生成
import numpy as np
_sr = 44100
_t  = np.linspace(0, 0.07, int(_sr * 0.07), endpoint=False)
_w  = (np.sin(2 * np.pi * 900 * _t) * np.exp(-_t * 50) * 0.55 * 32767).astype(np.int16)
guard_sound = pygame.sndarray.make_sound(np.column_stack([_w, _w]))
guard_sound.set_volume(0.5)

# 背景画像
background_img = pygame.image.load("assets/background.jpg")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
