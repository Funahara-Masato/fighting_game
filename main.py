import pygame
import sys
import math
from config import *
from fighter import Fighter
from select_mode import select_mode

TIMER_SECONDS = 90
HUD_H = 50


def draw_hud(win, p1, p2, timer_frames, jp_font):
    pygame.draw.rect(win, (20, 20, 20), (0, 0, WIDTH, HUD_H))

    bar_w = 280
    bar_h = 18
    pad_x = 20

    p1_ratio = max(0, p1.hp / 100)
    pygame.draw.rect(win, (60, 0, 0), (pad_x, 10, bar_w, bar_h), border_radius=4)
    if p1_ratio > 0:
        col = (220, 40, 40) if p1_ratio > 0.3 else (255, 200, 0)
        pygame.draw.rect(win, col, (pad_x, 10, int(bar_w * p1_ratio), bar_h), border_radius=4)
    pygame.draw.rect(win, (180, 180, 180), (pad_x, 10, bar_w, bar_h), 1, border_radius=4)

    for i in range(Fighter.GUARD_MAX):
        filled = i < p1.guard_hp
        pygame.draw.circle(win, (100, 180, 255) if filled else (40, 40, 60),
                           (pad_x + i * 14, 36), 5)

    label = jp_font.render("P1", True, (255, 80, 80))
    win.blit(label, (pad_x, -2))

    p2_ratio = max(0, p2.hp / 100)
    p2_x = WIDTH - pad_x - bar_w
    pygame.draw.rect(win, (0, 0, 60), (p2_x, 10, bar_w, bar_h), border_radius=4)
    if p2_ratio > 0:
        col = (60, 60, 220) if p2_ratio > 0.3 else (255, 200, 0)
        filled_w = int(bar_w * p2_ratio)
        pygame.draw.rect(win, col, (p2_x + bar_w - filled_w, 10, filled_w, bar_h), border_radius=4)
    pygame.draw.rect(win, (180, 180, 180), (p2_x, 10, bar_w, bar_h), 1, border_radius=4)

    for i in range(Fighter.GUARD_MAX):
        filled = i < p2.guard_hp
        pygame.draw.circle(win, (100, 180, 255) if filled else (40, 40, 60),
                           (WIDTH - pad_x - i * 14, 36), 5)

    label = jp_font.render("P2", True, (80, 80, 255))
    win.blit(label, (WIDTH - pad_x - label.get_width(), -2))

    secs = max(0, timer_frames // FPS)
    t_col = (255, 80, 80) if secs <= 10 else (240, 240, 240)
    t_surf = jp_font.render(str(secs), True, t_col)
    win.blit(t_surf, (WIDTH // 2 - t_surf.get_width() // 2, 8))


def draw_popup(win, fighter, font):
    if fighter.popup_timer > 0:
        alpha = min(255, fighter.popup_timer * 6)
        cy = int(fighter.y - fighter.height - 20 - (55 - fighter.popup_timer) * 0.4)
        surf = font.render(fighter.popup_text, True, (255, 220, 60))
        surf.set_alpha(alpha)
        win.blit(surf, (int(fighter.x + fighter.width // 2) - surf.get_width() // 2, cy))
        fighter.popup_timer -= 1


def show_win_screen(win, text, flash_color, jp_big, jp_small):
    for i in range(4):
        win.fill(flash_color if i % 2 == 0 else (10, 10, 10))
        pygame.display.update()
        pygame.time.delay(120)

    win.fill((10, 10, 10))
    shadow = jp_big.render(text, True, (0, 0, 0))
    main_s = jp_big.render(text, True, flash_color)
    cx = WIDTH // 2 - main_s.get_width() // 2
    cy = HEIGHT // 2 - main_s.get_height() // 2
    win.blit(shadow, (cx + 3, cy + 3))
    win.blit(main_s, (cx, cy))
    sub = jp_small.render("\u30af\u30ea\u30c3\u30af\u3057\u3066\u518d\u30d7\u30ec\u30a4", True, (160, 160, 160))
    win.blit(sub, (WIDTH // 2 - sub.get_width() // 2, cy + main_s.get_height() + 12))
    pygame.display.update()

    waiting = True
    while waiting:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                waiting = False


def main():
    clock = pygame.time.Clock()

    GAME_MODE = select_mode()

    jp_hud   = pygame.font.Font("meiryo.ttf", 18)
    jp_popup = pygame.font.Font("meiryo.ttf", 22)
    jp_big   = pygame.font.Font("meiryo.ttf", 52)
    jp_small = pygame.font.Font("meiryo.ttf", 22)

    player1 = Fighter(100, GROUND, RED)
    player2 = Fighter(600, GROUND, BLUE, facing="left")

    timer_frames = TIMER_SECONDS * FPS
    screen_flash = 0

    run = True
    while run:
        clock.tick(FPS)

        win_surf = WIN
        win_surf.blit(background_img, (0, 0))

        if screen_flash > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((255, 140, 0, min(180, screen_flash * 18)))
            win_surf.blit(flash_surf, (0, 0))
            screen_flash -= 1

        if player1.trigger_screen_flash:
            screen_flash = 8
            player1.trigger_screen_flash = False
        if player2.trigger_screen_flash:
            screen_flash = 8
            player2.trigger_screen_flash = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

        keys = pygame.key.get_pressed()
        player1.move(keys, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s,
                     guard_key=pygame.K_q, opponent=player2)

        if GAME_MODE == "AI":
            player2.move(keys, ai=True, opponent=player1)
        else:
            player2.move(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
                         guard_key=pygame.K_RSHIFT, opponent=player1, ai=False)

        player1.draw(win_surf)
        player2.draw(win_surf)

        draw_popup(win_surf, player1, jp_popup)
        draw_popup(win_surf, player2, jp_popup)

        if timer_frames > 0:
            timer_frames -= 1

        draw_hud(win_surf, player1, player2, timer_frames, jp_hud)

        winner = None
        flash_col = (220, 220, 220)
        if player1.hp <= 0:
            winner = "P2 WINS!"
            flash_col = (60, 60, 220)
        elif player2.hp <= 0:
            winner = "P1 WINS!"
            flash_col = (220, 60, 60)
        elif timer_frames <= 0:
            if player1.hp > player2.hp:
                winner = "P1 WINS!"
                flash_col = (220, 60, 60)
            elif player2.hp > player1.hp:
                winner = "P2 WINS!"
                flash_col = (60, 60, 220)
            else:
                winner = "DRAW!"
                flash_col = (180, 180, 180)

        if winner:
            pygame.display.update()
            show_win_screen(win_surf, winner, flash_col, jp_big, jp_small)
            main()
            return

        pygame.display.update()


if __name__ == "__main__":
    main()
