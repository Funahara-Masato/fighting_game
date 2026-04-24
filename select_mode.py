import pygame
import sys
import math
from config import *

BG       = (12, 12, 18)
ACCENT_R = (220, 50, 50)
ACCENT_B = (50, 80, 220)
PANEL    = (28, 28, 40)
TEXT_LT  = (210, 210, 220)
TEXT_DIM = (110, 110, 130)


def _glow_text(win, font, text, color, cx, cy, glow_r=3):
    s = font.render(text, True, color)
    for dx in range(-glow_r, glow_r + 1, glow_r):
        for dy in range(-glow_r, glow_r + 1, glow_r):
            if dx or dy:
                ghost = font.render(text, True,
                                    tuple(min(255, c // 2) for c in color))
                win.blit(ghost, (cx - s.get_width() // 2 + dx,
                                 cy - s.get_height() // 2 + dy))
    win.blit(s, (cx - s.get_width() // 2, cy - s.get_height() // 2))


def select_mode():
    # \u30bb\u30ec\u30af\u30c8\u753b\u9762BGM\uff08bgm_select.mp3\u304c\u3042\u308c\u3070\u4f7f\u7528\u3001\u306a\u3051\u308c\u3070bgm.mp3\u3092\u4)?\u97f3\u91cf\u3067\uff09
    try:
        pygame.mixer.music.load("assets/bgm_select.mp3")
    except Exception:
        pygame.mixer.music.load("assets/bgm.mp3")
    pygame.mixer.music.set_volume(0.12)
    pygame.mixer.music.play(-1)

    clock = pygame.time.Clock()
    run = True
    mode = None
    frame = 0

    jp_title = pygame.font.Font("meiryo.ttf", 36)
    jp_btn   = pygame.font.Font("meiryo.ttf", 22)
    jp_info  = pygame.font.Font("meiryo.ttf", 13)

    ai_rect  = pygame.Rect(WIDTH // 2 - 160, 130, 320, 56)
    pvp_rect = pygame.Rect(WIDTH // 2 - 160, 210, 320, 56)

    while run:
        clock.tick(FPS)
        frame += 1
        mx, my = pygame.mouse.get_pos()

        WIN.fill(BG)

        pulse = 0.75 + 0.25 * math.sin(frame * 0.06)
        r = int(220 * pulse)
        g = int(40 * pulse)
        title_col = (r, g, 0)
        _glow_text(WIN, jp_title, "\u30b4\u30e0\u4eba\u9593\u683c\u95d8\u30b2\u30fc\u30e0", title_col,
                   WIDTH // 2, 68, glow_r=4)

        sub = jp_info.render("RUBBER HUMAN FIGHTING GAME", True, TEXT_DIM)
        WIN.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 110))

        for rect, label, base_col in [
            (ai_rect,  "AI\u3068\u5bfe\u6226",  ACCENT_R),
            (pvp_rect, "PvP",       ACCENT_B),
        ]:
            hover = rect.collidepoint(mx, my)
            border_col = tuple(min(255, c + 60) for c in base_col) if hover else base_col
            bg_col     = tuple(c // 4 for c in base_col) if not hover else tuple(c // 3 for c in base_col)

            pygame.draw.rect(WIN, bg_col, rect, border_radius=8)
            pygame.draw.rect(WIN, border_col, rect, 2, border_radius=8)

            txt_surf = jp_btn.render(label, True, TEXT_LT if hover else TEXT_DIM)
            WIN.blit(txt_surf, (rect.centerx - txt_surf.get_width() // 2,
                                rect.centery - txt_surf.get_height() // 2))

        info_y = 295
        panel_rect = pygame.Rect(30, info_y - 8, WIDTH - 60, 100)
        pygame.draw.rect(WIN, PANEL, panel_rect, border_radius=6)
        pygame.draw.rect(WIN, (50, 50, 70), panel_rect, 1, border_radius=6)

        info_lines = [
            ("PvP \u64cd\u4f5c\u65b9\u6cd5", TEXT_LT),
            ("P1\uff08\u8d64\uff09  A/D:\u79fb\u52d5  W:\u30b8\u30e3\u30f3\u30d7  S:\u653b\u6483\uff08\u9577\u62bc\u3057=\u30d4\u30b9\u30c8\u30eb\uff09  Q:\u30ac\u30fc\u30c9", TEXT_DIM),
            ("P2\uff08\u9752\uff09  \u2190/\u2192:\u79fb\u52d5  \u2191:\u30b8\u30e3\u30f3\u30d7  \u2193:\u653b\u6483\uff08\u9577\u62bc\u3057=\u30d4\u30b9\u30c8\u30eb\uff09  RShift:\u30ac\u30fc\u30c9", TEXT_DIM),
            ("\u5171\u901a: \u540c\u65b9\u54112\u9023\u6253=\u30c0\u30c3\u30b7\u30e5  /  \u7a7a\u4e2d\u3067\u653b\u6483=\u30ad\u30c3\u30af\uff08\u5730\u4e0a\u653b\u6483\u3092\u56de\u907f\uff09", TEXT_DIM),
        ]
        for i, (line, col) in enumerate(info_lines):
            surf = jp_info.render(line, True, col)
            WIN.blit(surf, (44, info_y + i * 22))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ai_rect.collidepoint(event.pos):
                    mode = "AI";  run = False
                elif pvp_rect.collidepoint(event.pos):
                    mode = "PVP"; run = False

    return mode
