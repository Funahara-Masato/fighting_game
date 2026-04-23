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
    GUARD_MAX = 3
    GUARD_REGEN = 180
    CHARGE_FRAMES = 42
    DASH_DURATION = 8
    DASH_SPEED = 14
    DASH_WINDOW = 14

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
        self.land_squash = 0
        self.was_on_ground = True
        self.is_guarding = False
        self.guard_hp = self.GUARD_MAX
        self.guard_regen_timer = 0
        self.guard_flash = 0
        self.guard_sparks = []
        self.dash_timer = 0
        self.dash_dir = 0
        self.dash_cooldown = 0
        self.frame = 0
        self._prev_left = False
        self._prev_right = False
        self._tap_dir = None
        self._tap_frame = 0
        self.charge_timer = 0
        self.is_charging = False
        self.is_charged_attack = False
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
            flash = self.guard_flash / 8.0
            ring_color = (
                int(120 + 135 * flash),
                int(180 + 75 * flash),
                255
            )
            pygame.draw.circle(win, ring_color, (cx, int(self.y - self.height // 2 + 5)), 38, 3)
        if self.guard_flash > 0:
            self.guard_flash -= 1

        alive = []
        for sp in self.guard_sparks:
            x, y, vx, vy, life = sp
            if life > 0:
                pygame.draw.circle(win, (180, 210, 255), (int(x), int(y)), max(1, life // 3))
                alive.append((x + vx, y + vy, vx, vy + 0.4, life - 1))
        self.guard_sparks = alive

        if self.is_charging:
            t = min(1.0, self.charge_timer / self.CHARGE_FRAMES)
            r = int(6 + 10 * t)
            glow = (255, int(160 * t), 0)
            pygame.draw.circle(win, glow, (cx, sho_y + 5), r, 2)

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

            if self.is_charged_attack:
                ua = s * (20 + 85 * ext)
                fist_glow = int(10 * ext)
            else:
                ua = s * (25 + 65 * ext)
                fist_glow = 0

            elb = _pt(*spt, UA, ua)
            hnd = _pt(*elb, LA, ua + s * 20 * ext)
            _seg(win, draw_color, spt, elb)
            _seg(win, draw_color, elb, hnd)
            if fist_glow > 0:
                pygame.draw.circle(win, (255, 140, 0),
                                   (int(hnd[0]), int(hnd[1])), fist_glow, 2)

            ua2 = -s * 20
            elb2 = _pt(*spt, UA, ua2)
            hnd2 = _pt(*elb2, LA, ua2 - s * 10)
            _seg(win, draw_color, spt, elb2)
            _seg(win, draw_color, elb2, hnd2)
        elif self.is_guarding:
            s = 1 if self.facing == "right" else -1
            for ua in [s * 38, s * 22]:
                elb = _pt(*spt, UA, ua)
                hnd = _pt(*elb, LA, ua + s * 8)
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

        bar_y = self.y - self.height - 15
        pygame.draw.rect(win, WHITE, (self.x, bar_y, self.width, 5))
        pygame.draw.rect(win, self.color,
                         (self.x, bar_y, int(self.width * self.hp / 100), 5))
        pygame.draw.rect(win, (0, 0, 0), (self.x - 1, bar_y - 1, self.width + 2, 6), 1)

        pip_y = bar_y - 8
        pip_w = (self.width - 2) // self.GUARD_MAX
        for i in range(self.GUARD_MAX):
            color = (80, 140, 255) if i < self.guard_hp else (60, 60, 60)
            pygame.draw.rect(win, color, (self.x + i * (pip_w + 1), pip_y, pip_w, 4))

        if self.hit_flash > 0:
            self.hit_flash -= 1

    def _deal_damage(self, opponent):
        reach = 100 if self.is_charged_attack else 80
        knockback = 8 if self.is_charged_attack else 5
        damage = 20 if self.is_charged_attack else 10

        if self.facing == "right":
            in_range = 0 < (opponent.x - self.x) < reach
            kb_dir = 1
        else:
            in_range = -reach < (opponent.x - self.x) < 0
            kb_dir = -1

        if not in_range:
            return

        if opponent.is_guarding and opponent.guard_hp > 0:
            opponent.guard_hp -= 1
            opponent.guard_flash = 8
            opponent.hp -= 3
            sx = int(opponent.x + opponent.width // 2 - kb_dir * 5)
            sy = int(opponent.y - 35)
            for _ in range(7):
                vx = random.uniform(-3, 3)
                vy = random.uniform(-4, -1)
                opponent.guard_sparks.append((sx, sy, vx, vy, random.randint(6, 10)))
            guard_sound.play()
            self.hit_registered = True
            if opponent.guard_hp <= 0:
                opponent.stun_timer = 25
                opponent.is_guarding = False
        else:
            opponent.hp -= damage
            opponent.hit_flash = 5
            opponent.stun_timer = 10 if not self.is_charged_attack else 18
            opponent.x += knockback * kb_dir
            opponent.attack_progress = 0
            hit_sound.play()
            self.hit_registered = True

    def move(self, keys,
             left_key=None, right_key=None, jump_key=None,
             attack_key=None, guard_key=None,
             opponent=None, ai=False):

        moved = False
        self.frame += 1

        if self.stun_timer > 0:
            self.stun_timer -= 1
            self._prev_left = False
            self._prev_right = False
            return

        if not ai:
            cur_left  = keys[left_key]
            cur_right = keys[right_key]

            self.is_guarding = bool(
                guard_key and keys[guard_key]
                and self.on_ground
                and self.charge_timer == 0
                and self.attack_progress == 0
            )

            if not self.is_guarding:
                if cur_left and not self._prev_left:
                    if self._tap_dir == "left" and (self.frame - self._tap_frame) <= self.DASH_WINDOW and self.dash_cooldown == 0:
                        self.dash_timer = self.DASH_DURATION
                        self.dash_dir = -1
                        self.dash_cooldown = 40
                        self._tap_dir = None
                    else:
                        self._tap_dir = "left"
                        self._tap_frame = self.frame

                if cur_right and not self._prev_right:
                    if self._tap_dir == "right" and (self.frame - self._tap_frame) <= self.DASH_WINDOW and self.dash_cooldown == 0:
                        self.dash_timer = self.DASH_DURATION
                        self.dash_dir = 1
                        self.dash_cooldown = 40
                        self._tap_dir = None
                    else:
                        self._tap_dir = "right"
                        self._tap_frame = self.frame

                if self.dash_timer > 0:
                    self.x += self.DASH_SPEED * self.dash_dir
                    self.facing = "right" if self.dash_dir > 0 else "left"
                    self.dash_timer -= 1
                    moved = True
                else:
                    if cur_left:
                        self.x -= self.vel_x
                        self.facing = "left"
                        moved = True
                    if cur_right:
                        self.x += self.vel_x
                        self.facing = "right"
                        moved = True

                if keys[jump_key] and self.on_ground and self.jump_cooldown == 0:
                    self.vel_y = -12
                    self.on_ground = False
                    self.jump_cooldown = 30

                if keys[attack_key] and self.attack_cooldown == 0:
                    self.charge_timer += 1
                    self.is_charging = self.charge_timer >= self.CHARGE_FRAMES
                elif not keys[attack_key] and self.charge_timer > 0 and self.attack_cooldown == 0:
                    self.is_charged_attack = self.charge_timer >= self.CHARGE_FRAMES
                    self.attack_cooldown = 60 if self.is_charged_attack else 50
                    self.attack_progress = 0.01
                    self.charge_timer = 0
                    self.is_charging = False
                elif not keys[attack_key]:
                    self.charge_timer = 0
                    self.is_charging = False
            else:
                self.charge_timer = 0
                self.is_charging = False

            if self.jump_cooldown > 0:
                self.jump_cooldown -= 1
            if self.dash_cooldown > 0:
                self.dash_cooldown -= 1

            self._prev_left  = cur_left
            self._prev_right = cur_right

        else:
            dist = opponent.x - self.x
            self.facing = "right" if dist >= 0 else "left"
            abs_dist = abs(dist)
            opp_attacking = opponent.attack_progress > 0.15

            if opp_attacking and abs_dist < 90 and self.guard_hp > 0:
                self.is_guarding = True
            else:
                self.is_guarding = False

            if not self.is_guarding:
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
                        self.is_charged_attack = False
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
            if self.dash_cooldown > 0:
                self.dash_cooldown -= 1

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
                    self._deal_damage(opponent)
            if self.attack_progress > 1.0:
                self.attack_progress = 0
                self.hit_registered = False
                self.is_charged_attack = False

        if not self.is_guarding and self.guard_hp < self.GUARD_MAX:
            self.guard_regen_timer += 1
            if self.guard_regen_timer >= self.GUARD_REGEN:
                self.guard_hp += 1
                self.guard_regen_timer = 0
        elif self.is_guarding:
            self.guard_regen_timer = 0

        if moved and self.on_ground:
            self.walk_vel = min(0.25, self.walk_vel + 0.04)
        else:
            self.walk_vel *= 0.75
        self.walk_cycle += self.walk_vel
        if self.walk_cycle > 2 * math.pi:
            self.walk_cycle -= 2 * math.pi

        self.x = max(0, min(WIDTH - self.width, self.x))
