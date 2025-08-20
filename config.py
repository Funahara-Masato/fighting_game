import pygame

pygame.init()

WIDTH, HEIGHT = 800, 400
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("棒人間格闘ゲーム - AI対戦")

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

# 背景画像
background_img = pygame.image.load("assets/background.jpg")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
