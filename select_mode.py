import pygame
import sys
import math
import asyncio
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


async def select_mode():
    select_bgm_sound.play(loops=-1)

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

        # タイトルグロー（脈動）
        pulse = 0.75 + 0.25 * math.sin(frame * 0.06)
        r = int(220 * pulse)
        g = int(40 * pulse)
        title_col = (r, g, 0)
        _glow_text(WIN, jp_title, "ゴム人間格闘ゲーム", title_col,
                   WIDTH // 2, 68, glow_r=4)

        # サブタイトル
        sub = jp_info.render("RUBBER HUMAN FIGHTING GAME", True, TEXT_DIM)
        WIN.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 110))

        # ボタン描画
        for rect, label, base_col in [
            (ai_rect,  "AIと対戦",  ACCENT_R),
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

        # 操作説明パネル
        info_y = 295
        panel_rect = pygame.Rect(30, info_y - 8, WIDTH - 60, 108)
        pygame.draw.rect(WIN, PANEL, panel_rect, border_radius=6)
        pygame.draw.rect(WIN, (50, 50, 70), panel_rect, 1, border_radius=6)

        info_lines = [
            ("PvP 操作方法", TEXT_LT),
            ("P1（赤）  A/D:移動  W:ジャンプ  S:攻撃（長押し=ピストル）  Q:ガード", TEXT_DIM),
            ("P2（青）  ←/→:移動  ↑:ジャンプ  ↓:攻撃（長押し=ピストル）  RShift:ガード", TEXT_DIM),
            ("共通: 同方向2連打=ダッシュ  /  空中で攻撃=キック（地上攻撃を回避）", TEXT_DIM),
        ]
        for i, (line, col) in enumerate(info_lines):
            surf = jp_info.render(line, True, col)
            WIN.blit(surf, (44, info_y + i * 22))

        pygame.display.update()
        await asyncio.sleep(0)

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

    select_bgm_sound.stop()
    return mode
