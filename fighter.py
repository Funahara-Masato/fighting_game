from config import *
import math

class Fighter:
    def __init__(self, x, y, color, facing="right"):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 60
        self.ground_y = y
        self.color = color
        self.vel_x = 5
        self.vel_y = 0
        self.jump = False
        self.on_ground = True
        self.hp = 100
        self.attack_cooldown = 0
        self.hit_flash = 0
        self.attack_progress = 0
        self.hit_registered = False
        self.facing = facing
        self.walk_cycle = 0
        self.jump_cooldown = 0
        self.stun_timer = 0
        self.attack_pressed = False

    # def draw(self, win):
    #     draw_color = YELLOW if self.hit_flash > 0 else self.color
    #     # （元のdraw処理そのまま）
    #     # ...

    # def move(self, keys, left_key=None, right_key=None, jump_key=None, attack_key=None, opponent=None, ai=False):
    #     # （元のmove処理そのまま）
    #     # ...
    #     pass

    def draw(self, win):
        draw_color = YELLOW if self.hit_flash > 0 else self.color
        foot_swing = 10  # 足の前後の振れ幅
        hand_swing = 5   # 腕の前後の振れ幅

        # 頭
        head_center = (self.x + self.width // 2, self.y - self.height + 10)
        pygame.draw.circle(win, draw_color, head_center, 10)

        # 顔向きの目
        eye_offset = 4 if self.facing == "right" else -4
        pygame.draw.circle(win, (0, 0, 0),
                        (head_center[0] + eye_offset, head_center[1] - 2), 2)

        # 胴体を角丸長方形に変更
        body_width = 13
        body_height = 33
        body_rect = pygame.Rect(
            self.x + self.width // 2 - body_width // 2,  # 左上のx
            self.y - self.height + 20,                   # 左上のy
            body_width,
            body_height
        )
        pygame.draw.rect(win, draw_color, body_rect, border_radius=4)

        # 手の前後振り
        hand_offset = int(hand_swing * math.sin(self.walk_cycle))
        left_hand_x = self.x + self.width // 2 - 15 + (
            -hand_offset if self.facing == "right" else hand_offset
        )
        left_hand_y = self.y - self.height + 40
        right_hand_y = self.y - self.height + 30

        # 攻撃時は向きの手を前に伸ばす
        if self.attack_progress > 0:
            attack_length = 15 + int(65 * self.attack_progress)
            if self.facing == "right":
                pygame.draw.line(
                    win, draw_color,
                    (self.x + self.width // 2, right_hand_y),
                    (self.x + self.width // 2 + attack_length, right_hand_y + 10),
                    4
                )
            else:
                pygame.draw.line(
                    win, draw_color,
                    (self.x + self.width // 2, right_hand_y),
                    (self.x + self.width // 2 - attack_length, right_hand_y + 10),
                    4
                )

            # 反対側の手も少し振る
            pygame.draw.line(
                win, draw_color,
                (self.x + self.width // 2, right_hand_y),
                (left_hand_x, left_hand_y), 4
            )
        else:
            # 通常歩行時は左右の手を交互に振る
            left_hand_x = self.x + self.width // 2 - 15 - hand_offset
            right_hand_x = self.x + self.width // 2 + 15 + hand_offset

            pygame.draw.line(
                win, draw_color,
                (self.x + self.width // 2, right_hand_y),
                (right_hand_x, right_hand_y + 10), 4
            )
            pygame.draw.line(
                win, draw_color,
                (self.x + self.width // 2, right_hand_y),
                (left_hand_x, left_hand_y), 4
            )

        # 足（左右対称、交互）
        foot_offset = int(foot_swing * math.sin(self.walk_cycle))
        pygame.draw.line(
            win, draw_color,
            (self.x + self.width // 2, self.y - 10),
            (self.x + self.width // 2 - 10, self.y + foot_offset), 4
        )
        pygame.draw.line(
            win, draw_color,
            (self.x + self.width // 2, self.y - 10),
            (self.x + self.width // 2 + 10, self.y - foot_offset), 4
        )

        # HPバーの背景（減った分を白で表示）
        pygame.draw.rect(win, WHITE,
                        (self.x, self.y - self.height - 15, self.width, 5))

        # HPバー本体（残っている分を体色で表示）
        pygame.draw.rect(win, self.color,
                        (self.x, self.y - self.height - 15,
                        self.width * self.hp / 100, 5))

        # （任意）枠線を黒で描くと見やすい
        pygame.draw.rect(win, (0, 0, 0),
                        (self.x - 1, self.y - self.height - 16,
                        self.width + 2, 6), 1)

        if self.hit_flash > 0:
            self.hit_flash -= 1


    def move(self, keys,
            left_key=None, right_key=None, jump_key=None, attack_key=None,
            opponent=None, ai=False):

        moved = False  # 歩行アニメーション用フラグ

        if self.stun_timer > 0:
            self.stun_timer -= 1
            return  # 硬直中は他の処理をしない

        if not ai:
            # 地上の左右移動
            if self.on_ground:
                if keys[left_key]:
                    self.x -= self.vel_x
                    self.facing = "left"
                    moved = True
                if keys[right_key]:
                    self.x += self.vel_x
                    self.facing = "right"
                    moved = True
            # 空中の左右移動（地上の30％の速度）
            else:
                if keys[left_key]:
                    self.x -= self.vel_x * 1.0
                    self.facing = "left"
                    moved = True
                if keys[right_key]:
                    self.x += self.vel_x * 1.0
                    self.facing = "right"
                    moved = True

            # ジャンプ（地上かつクールダウンなし）
            if keys[jump_key] and self.on_ground and self.jump_cooldown == 0:
                self.vel_y = -12
                self.on_ground = False
                self.jump_cooldown = 30

            # 攻撃
            if keys[attack_key]:
                if not self.attack_pressed and self.attack_cooldown == 0:
                    self.attack_cooldown = 50
                    self.attack_progress = 0.01
                    self.attack_pressed = True  # 攻撃したことを記録
            else:
                self.attack_pressed = False  # キーを離したらフラグリセット

            # ジャンプクールダウン更新
            if self.jump_cooldown > 0:
                self.jump_cooldown -= 1

        else:
            # AI制御
            dist = opponent.x - self.x
            self.facing = "right" if dist >= 0 else "left"

            if abs(dist) > 79:
                self.x += self.vel_x if dist > 0 else -self.vel_x
                moved = True
            elif abs(dist) <= 79 and self.attack_cooldown == 0 and self.on_ground:
                self.attack_cooldown = 40
                self.attack_progress = 0.01

            # ジャンプクールダウン更新
            if self.jump_cooldown > 0:
                self.jump_cooldown -= 1

        # 攻撃クールダウン更新
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # 落下処理
        if not self.on_ground:
            self.vel_y += 1
            self.y += self.vel_y
            if self.y >= GROUND:
                self.y = GROUND
                self.vel_y = 0
                self.on_ground = True

        # 攻撃アニメーション進行
        if self.attack_progress > 0:
            self.attack_progress += 0.1

            # 当たり判定が有効な時間
            if 0.3 <= self.attack_progress <= 0.5 and not self.hit_registered:
                if opponent:
                    max_hit_height = 50
                    if opponent.y >= opponent.ground_y - max_hit_height:
                        if self.facing == "right" and 0 < (opponent.x - self.x) < 80:
                            # 攻撃範囲
                            opponent.hp -= 10
                            opponent.hit_flash = 5
                            opponent.stun_timer = 10  # 15フレーム硬直
                            opponent.x += 5  # 少しのけぞり（後退）
                            opponent.attack_progress = 0  # 攻撃状態をリセット
                            hit_sound.play()  # 効果音
                            self.hit_registered = True
                        elif self.facing == "left" and -80 < (opponent.x - self.x) < 0:
                            opponent.hp -= 10
                            opponent.hit_flash = 5
                            opponent.stun_timer = 10
                            opponent.x -= 5
                            opponent.attack_progress = 0  # 攻撃状態をリセット
                            hit_sound.play()
                            self.hit_registered = True

            # アニメーション終了（一定時間経過後リセット）
            if self.attack_progress > 1.0:
                self.attack_progress = 0
                self.hit_registered = False

        # 歩行アニメーション更新
        if moved and self.on_ground:
            self.walk_cycle += 0.2
            if self.walk_cycle > 2 * math.pi:
                self.walk_cycle -= 2 * math.pi
        else:
            self.walk_cycle = 0

        # 画面端で止める
        self.x = max(0, min(WIDTH - self.width, self.x))
