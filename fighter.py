import math
import random
import pygame
from config import *


def _pt(ox, oy, length, angle_deg):
    r = math.radians(angle_deg)
    return (ox + length * math.sin(r), oy + length * math.cos(r))


def _seg(win, color, p1, p2, w=4):
    pygame.draw.line(win, color,
                     (int(p1[0]), int(p1[1])),
                     (int(p2[0]), int(p2[1])), w)


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
        self.on_ground = True
        self.hp = 100
        self.attack_cooldown = 0
        self.hit_flash = 0
        self.attack_progress = 0
        self.hit_registered = False
        self.facing = facing
        self.walk_cycle = 0.0
        self.walk_vel = 0.0
        self.jump_cooldown = 0
        self.stun_timer = 0
        self.attack_pressed = False
        self.land_squash = 0
        self.was_on_ground = True
        self.is_guarding = False
        self.ai_state = "APPROACH"
        self.ai_state_timer = 0

    def draw(self, win):
        draw_color = YELLOW if self.hit_flash > 0 else self.color
        cx = int(self.x + self.width // 2)

        if self.land_squash > 0:
            self.land_squash -= 1
        sq = self.land_squash / 8.0

        head_y = int(self.y - self.height * (1.0 - sq * 0.15) + 10)
        sho_y  = head_y + 12
        hip_y  = int(self.y - 12 + sq * 5)

        if self.is_guarding:
            pygame.draw.circle(win, (120, 180, 255),
                               (cx, int(self.y - self.height // 2 + 5)), 38, 3)

        pygame.draw.circle(win, draw_color, (cx, head_y), 10)
        ex = 4 if self.facing == "right" else -4
        pygame.draw.circle(win, (0, 0, 0), (cx + ex, head_y - 2), 2)

        body_h = max(hip_y - sho_y + 2, 8)
        pygame.draw.rect(win, draw_color,
                         pygame.Rect(cx - 6, sho_y, 13, body_h),
                         border_radius=3)

        UL, LL = 16, 16
        UA, LA = 13, 12
        c = self.walk_cycle
        spt = (cx, sho_y + 5)

        if not self.on_ground:
            for ls in [-1, 1]:
                knee = _pt(cx, hip_y, UL, ls * 35)
                foot = _pt(*knee, LL, ls * 55)
                _seg(win, draw_color, (cx, hip_y), knee)
                _seg(win, draw_color, knee, foot)
        else:
            SWING = 28
            for phase in [0, math.pi]:
                thigh_a = SWING * math.sin(c + phase)
                knee_extra = max(0, -thigh_a) * 0.7 + 4
                knee_a = thigh_a + knee_extra
                knee = _pt(cx, hip_y, UL, thigh_a)
                foot = _pt(*knee, LL, knee_a)
                _seg(win, draw_color, (cx, hip_y), knee)
                _seg(win, draw_color, knee, foot)

        if self.attack_progress > 0:
            t = self.attack_progress
            ext = (t / 0.4) if t < 0.4 else max(0.0, (1.0 - t) / 0.6)
            s = 1 if self.facing == "right" else -1

            ua = s * (25 + 65 * ext)
            elb = _pt(*spt, UA, ua)
            hnd = _pt(*elb, LA, ua + s * 20 * ext)
            _seg(win, draw_color, spt, elb)
            _seg(win, draw_color, elb, hnd)

            ua2 = -s * 20
            elb2 = _pt(*spt, UA, ua2)
            hnd2 = _pt(*elb2, LA, ua2 - s * 10)
            _seg(win, draw_color, spt, elb2)
            _seg(win, draw_color, elb2, hnd2)
        elif self.is_guarding:
            s = 1 if self.facing == "right" else -1
            for ua in [s * 35, s * 20]:
                elb = _pt(*spt, UA, ua)
                hnd = _pt(*elb, LA, ua + s * 10 * (1 if ua > 0 else -1))
                _seg(win, draw_color, spt, elb)
                _seg(win, draw_color, elb, hnd)
        else:
            ARM = 20
            for phase in [math.pi, 0]:
                ua = ARM * math.sin(c + phase)
                bend = abs(ua) * 0.25
                ea = ua + (bend if ua >= 0 else -bend)
                elb = _pt(*spt, UA, ua)
                hnd = _pt(*elb, LA, ea)
                _seg(win, draw_color, spt, elb)
                _seg(win, draw_color, elb, hnd)

        pygame.draw.rect(win, WHITE,
                         (self.x, self.y - self.height - 15, self.width, 5))
        pygame.draw.rect(win, self.color,
                         (self.x, self.y - self.height - 15,
                          int(self.width * self.hp / 100), 5))
        pygame.draw.rect(win, (0, 0, 0),
                         (self.x - 1, self.y - self.height - 16,
                          self.width + 2, 6), 1)

        if self.hit_flash > 0:
            self.hit_flash -= 1

    def _deal_damage(self, opponent):
        if opponent.is_guarding:
            opponent.hp -= 3
            opponent.hit_flash = 2
        else:
            opponent.hp -= 10
            opponent.hit_flash = 5
            opponent.stun_timer = 10
            opponent.x += 5 if self.facing == "right" else -5
            opponent.attack_progress = 0
        hit_sound.play()
        self.hit_registered = True

    def move(self, keys,
             left_key=None, right_key=None, jump_key=None,
             attack_key=None, guard_key=None,
             opponent=None, ai=False):

        moved = False

        if self.stun_timer > 0:
            self.stun_timer -= 1
            return

        if not ai:
            self.is_guarding = bool(
                guard_key and keys[guard_key]
                and self.on_ground
                and self.attack_progress == 0
            )

            if not self.is_guarding:
                if keys[left_key]:
                    self.x -= self.vel_x
                    self.facing = "left"
                    moved = True
                if keys[right_key]:
                    self.x += self.vel_x
                    self.facing = "right"
                    moved = True

                if keys[jump_key] and self.on_ground and self.jump_cooldown == 0:
                    self.vel_y = -12
                    self.on_ground = False
                    self.jump_cooldown = 30

                if keys[attack_key]:
                    if not self.attack_pressed and self.attack_cooldown == 0:
                        self.attack_cooldown = 50
                        self.attack_progress = 0.01
                        self.attack_pressed = True
                else:
                    self.attack_pressed = False
            else:
                self.attack_pressed = False

            if self.jump_cooldown > 0:
                self.jump_cooldown -= 1

        else:
            self.is_guarding = False
            dist = opponent.x - self.x
            self.facing = "right" if dist >= 0 else "left"
            abs_dist = abs(dist)
            opp_attacking = opponent.attack_progress > 0.15

            if self.ai_state == "APPROACH":
                if abs_dist > 88:
                    self.x += self.vel_x if dist > 0 else -self.vel_x
                    moved = True
                else:
                    self.ai_state = "IDLE"
                    self.ai_state_timer = random.randint(15, 35)

            elif self.ai_state == "IDLE":
                if opp_attacking and abs_dist < 100:
                    self.x -= self.vel_x if dist > 0 else -self.vel_x
                    moved = True
                self.ai_state_timer -= 1
                if self.ai_state_timer <= 0:
                    if self.attack_cooldown == 0 and abs_dist < 90:
                        self.ai_state = "ATTACK"
                    else:
                        self.ai_state = "APPROACH"

            elif self.ai_state == "ATTACK":
                if self.attack_cooldown == 0 and abs_dist < 90:
                    self.attack_cooldown = 40
                    self.attack_progress = 0.01
                self.ai_state = "RETREAT"
                self.ai_state_timer = random.randint(20, 40)

            elif self.ai_state == "RETREAT":
                self.x -= self.vel_x if dist > 0 else -self.vel_x
                moved = True
                self.ai_state_timer -= 1
                if self.ai_state_timer <= 0:
                    self.ai_state = "APPROACH"

            if self.jump_cooldown > 0:
                self.jump_cooldown -= 1

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if not self.on_ground:
            self.vel_y += 1
            self.y += self.vel_y
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.vel_y = 0
                self.on_ground = True

        if not self.was_on_ground and self.on_ground:
            self.land_squash = 8
        self.was_on_ground = self.on_ground

        if self.attack_progress > 0:
            self.attack_progress += 0.1

            if 0.3 <= self.attack_progress <= 0.5 and not self.hit_registered:
                if opponent:
                    if self.facing == "right" and 0 < (opponent.x - self.x) < 80:
                        self._deal_damage(opponent)
                    elif self.facing == "left" and -80 < (opponent.x - self.x) < 0:
                        self._deal_damage(opponent)

            if self.attack_progress > 1.0:
                self.attack_progress = 0
                self.hit_registered = False

        if moved and self.on_ground:
            self.walk_vel = min(0.25, self.walk_vel + 0.04)
        else:
            self.walk_vel *= 0.75

        self.walk_cycle += self.walk_vel
        if self.walk_cycle > 2 * math.pi:
            self.walk_cycle -= 2 * math.pi

        self.x = max(0, min(WIDTH - self.width, self.x))
