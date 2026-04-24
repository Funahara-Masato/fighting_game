import pygame

pygame.init()

WIDTH, HEIGHT = 800, 400
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("\u30b4\u30e0\u4eba\u9593\u683c\u95d8\u30b2\u30fc\u30e0")

FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GROUND = HEIGHT - 83

pygame.mixer.init()  # BGM\u518d\u751f\u306f\u5404\u753b\u9762\u3067\u884c\u3046

# \u52b9\u679c\u97f3
hit_sound = pygame.mixer.Sound("assets/hit.mp3")
hit_sound.set_volume(0.3)

# \u30ac\u30fc\u30c9\u97f3\uff08\u91d1\u5c5e\u7684\u306a\u30ab\u30ad\u30f3\uff09\u3092numpy\u3067\u751f\u6210
import numpy as np
_sr = 44100
_t  = np.linspace(0, 0.07, int(_sr * 0.07), endpoint=False)
_w  = (np.sin(2 * np.pi * 900 * _t) * np.exp(-_t * 50) * 0.55 * 32767).astype(np.int16)
guard_sound = pygame.sndarray.make_sound(np.column_stack([_w, _w]))
guard_sound.set_volume(0.5)

# \u30b4\u30e0\u30b4\u30e0\u306e\u30d4\u30b9\u30c8\u30eb\u97f3\uff08\u4)?\u97f3\uff0b\u30ce\u30a4\u30ba\u6253\u6483\uff09
_t_p    = np.linspace(0, 0.22, int(_sr * 0.22), endpoint=False)
_noise  = np.random.randn(len(_t_p))
_bass   = np.sin(2 * np.pi * 68  * _t_p) * np.exp(-_t_p * 10)
_crack  = np.sin(2 * np.pi * 210 * _t_p) * np.exp(-_t_p * 28)
_w_raw  = _noise * 0.28 * np.exp(-_t_p * 38) + _bass * 0.56 + _crack * 0.16
_w_p    = (_w_raw / max(abs(_w_raw).max(), 1e-6) * 0.90 * 32767).astype(np.int16)
pistol_sound = pygame.sndarray.make_sound(np.column_stack([_w_p, _w_p]))
pistol_sound.set_volume(0.70)

# \u68d8\u30c0\u30e1\u30fc\u30b8\u97f3\uff08\u77ed\u304f\u30d3\u30ea\u30c3\u3068\uff09
_t_sp = np.linspace(0, 0.05, int(_sr * 0.05), endpoint=False)
_w_sp = (np.sin(2 * np.pi * 440 * _t_sp) * np.exp(-_t_sp * 60) * 0.5 * 32767).astype(np.int16)
spike_sound = pygame.sndarray.make_sound(np.column_stack([_w_sp, _w_sp]))
spike_sound.set_volume(0.4)

# \u80cc\u666f\u753b\u50cf
background_img = pygame.image.load("assets/background.jpg")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
