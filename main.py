import pygame
import sys
from config import *
from fighter import Fighter
from select_mode import select_mode

def main():
    clock = pygame.time.Clock()
    run = True

    # ゲームモードを選択
    GAME_MODE = select_mode()

    player1 = Fighter(100, GROUND, RED)
    player2 = Fighter(600, GROUND, BLUE)

    while run:
        clock.tick(FPS)
        WIN.blit(background_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player1.move(keys, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, opponent=player2)

        if GAME_MODE == "AI":
            player2.move(keys, ai=True, opponent=player1)
        else:
            player2.move(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, opponent=player1, ai=False)

        player1.draw(WIN)
        player2.draw(WIN)

        # 勝敗判定
        font = pygame.font.SysFont(None, 60)
        if player1.hp <= 0:
            text = font.render("BLUE WINS!", True, (0,0,0))
            WIN.blit(text, (WIDTH//2 - 150, HEIGHT//2 - 30))
            pygame.display.update()
            pygame.time.delay(3000)
            main()

        if player2.hp <= 0:
            text = font.render("RED WINS!", True, (0,0,0))
            WIN.blit(text, (WIDTH//2 - 150, HEIGHT//2 - 30))
            pygame.display.update()
            pygame.time.delay(3000)
            main()

        pygame.display.update()

if __name__ == "__main__":
    main()
