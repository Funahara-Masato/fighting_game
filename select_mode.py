import pygame
import sys
from config import *

def select_mode():
    clock = pygame.time.Clock()
    run = True
    mode = None

    jp_font = pygame.font.Font("meiryo.ttf", 30)
    jp_small = pygame.font.Font("meiryo.ttf", 20)

    while run:
        clock.tick(FPS)
        WIN.fill(WHITE)

        # タイトル
        title_text = jp_font.render("ゲームモード選択", True, (0,0,0))
        WIN.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 30))

        # AIモードボタン
        ai_text = jp_small.render("AIと対戦", True, WHITE)
        ai_rect = pygame.Rect(WIDTH//2 - 150, 120, 300, 50)
        pygame.draw.rect(WIN, BLUE, ai_rect)
        WIN.blit(ai_text, (ai_rect.x + ai_rect.width//2 - ai_text.get_width()//2,
                           ai_rect.y + ai_rect.height//2 - ai_text.get_height()//2))

        # PVPモードボタン
        pvp_text = jp_small.render("PvP", True, WHITE)
        pvp_rect = pygame.Rect(WIDTH//2 - 150, 200, 300, 50)
        pygame.draw.rect(WIN, RED, pvp_rect)
        WIN.blit(pvp_text, (pvp_rect.x + pvp_rect.width//2 - pvp_text.get_width()//2,
                            pvp_rect.y + pvp_rect.height//2 - pvp_text.get_height()//2))

        # PVP操作説明
        info_lines = [
            "PvP操作方法：",
            "　プレイヤー1（赤）: 移動 A/D, ジャンプ W, 攻撃 S",
            "　プレイヤー2（青）: 移動 ←/→, ジャンプ ↑, 攻撃 ↓"
        ]
        for i, line in enumerate(info_lines):
            info_text = jp_small.render(line, True, (0,0,0))
            WIN.blit(info_text, (50, 270 + i*30))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ai_rect.collidepoint(event.pos):
                    mode = "AI"
                    run = False
                elif pvp_rect.collidepoint(event.pos):
                    mode = "PVP"
                    run = False

    return mode