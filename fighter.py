import math
import random
import pygame
from config import *


def _bezier(win, color, p0, p2, sag=0, w=4):
    """ゴム腕: 二次ベジェ曲線で描く。sag>0で下にたわむ"""
    mx = (p0[0] + p2[0]) / 2
    my = (p0[1] + p2[1]) / 2 + sag
    pts = []
    for i in range(12):
        t = i / 11
        x = (1-t)**2*p0[0] + 2*(1-t)*t*mx + t**2*p2[0]
        y = (1-t)**2*p0[1] + 2*(1-t)*t*my + t**2*p2[1]
        pts.append((int(x), int(y)))
    pygame.draw.lines(win, color, False, pts, w)
    pygame.draw.circle(win, color, pts[-1], 6)


def _seg(win, color, p1, p2, w=4):
    pygame.draw.line(win, color,
                     (int(p1[0]), int(p1[1])),
                     (int(p2[0]), int(p2[1])), w)


def _pt(ox, oy, length, angle_deg):
    r = math.radians(angle_deg)
    return (ox + length * math.sin(r), oy + length * math.cos(r))


class Fighter:
    GUARD_MAX     = 3
    GUARD_REGEN   = 180
    CHARGE_FRAMES = 42
    DASH_DURATION = 8
    DASH_SPEED    = 14
    DASH_WINDOW   = 14

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
        self.wobble_timer = 0
        self.bounce_count = 0

    def draw(self, win):
        draw_color = YELLOW if self.hit_flash > 0 else self.color
        cx = int(self.x + self.width // 2)

        if self.wobble_timer > 0:
            cx += int(6 * math.sin(self.wobble_timer * 1.3) * (self.wobble_timer / 15))
            self.wobble_timer -= 1

        if self.land_squash > 0:
            self.land_squash -= 1
        sq = self.land_squash / 12.0

        head_y = int(self.y - self.height * (1.0 - sq * 0.20) + 10)
        sho_y  = head_y + 12
        hip_y  = int(self.y - 12 + sq * 7)

        head_cx = cx - self.dash_dir * 7 if self.dash_timer > 0 else cx

        if self.is_guarding:
            flash = self.guard_flash / 8.0
            ring_color = (int(120 + 135*flash), int(180 + 75*flash), 255)
            pygame.draw.circle(win, ring_color,
                               (cx, int(self.y - self.height // 2 + 5)), 38, 3)
        if self.guard_flash > 0:
            self.guard_flash -= 1

        alive = []
        for sp in self.guard_sparks:
            x, y, vx, vy, life = sp
            if life > 0:
                pygame.draw.circle(win, (180, 210, 255), (int(x), int(y)), max(1, life // 3))
                alive.append((x+vx, y+vy, vx, vy+0.4, life-1))
        self.guard_sparks = alive

        if self.is_charging:
            t = min(1.0, self.charge_timer / self.CHARGE_FRAMES)
            pygame.draw.circle(win, (255, int(160*t), 0),
                               (cx, sho_y + 5), int(6 + 10*t), 2)

        pygame.draw.circle(win, draw_color, (head_cx, head_y), 10)
        ex = 4 if self.facing == "right" else -4
        pygame.draw.circle(win, (0, 0, 0), (head_cx + ex, head_y - 2), 2)

        if self.dash_timer > 0 and head_cx != cx:
            _bezier(win, draw_color, (head_cx, head_y + 10), (cx, sho_y),
                    sag=self.dash_dir * -4, w=3)

        body_h = max(hip_y - sho_y + 2, 8)
        pygame.draw.rect(win, draw_color,
                         pygame.Rect(cx - 6, sho_y, 13, body_h),
                         border_radius=3)

        UL, LL = 16, 16
        UA, LA = 13, 12
        c = self.walk_cycle
        sho_pt = (cx, sho_y + 4)

        SWING = 35
        if not self.on_ground:
            for ls in [-1, 1]:
                knee = _pt(cx, hip_y, UL, ls * 35)
                foot = _pt(*knee, LL, ls * 55)
                _seg(win, draw_color, (cx, hip_y), knee)
                _seg(win, draw_color, knee, foot)
        else:
            for phase in [0, math.pi]:
                thigh_a = SWING * math.sin(c + phase)
                knee_extra = max(0, -thigh_a) * 0.8 + 5
                knee_a = thigh_a + knee_extra
                knee = _pt(cx, hip_y, UL, thigh_a)
                foot = _pt(*knee, LL, knee_a)
                _seg(win, draw_color, (cx, hip_y), knee)
                _seg(win, draw_color, knee, foot)

        if self.attack_progress > 0:
            t = self.attack_progress
            s = 1 if self.facing == "right" else -1

            if self.is_charged_attack:
                MAX = 220
                if t < 0.20:
                    ext = -t / 0.20 * 0.35
                    sag = 0
                elif t < 0.60:
                    fwd = (t - 0.20) / 0.40
                    ext = fwd
                    sag = 12 * math.sin(fwd * math.pi)
                else:
                    snap = (t - 0.60) / 0.40
                    ext = max(0, 1 - snap * 1.4) + 0.20 * math.sin(snap * math.pi * 2.5) * (1 - snap)
                    sag = 7 * math.sin(snap * math.pi * 3) * (1 - snap)
            else:
                MAX = 140
                if t < 0.40:
                    ext = t / 0.40
                    sag = 8 * math.sin(t * math.pi / 0.40)
                elif t < 0.60:
                    ext = 1.0
                    sag = 3
                else:
                    snap = (t - 0.60) / 0.40
                    ext = max(0, 1 - snap) + 0.12 * math.sin(snap * math.pi * 2.5) * (1 - snap)
                    sag = 5 * math.sin(snap * math.pi * 3) * (1 - snap)

            arm_x = int(cx + s * MAX * ext)
            arm_y = int(sho_y + 8 + 6 * max(0, ext))
            _bezier(win, draw_color, sho_pt, (arm_x, arm_y), sag=sag)

            back_x = int(cx - s * 18)
            _bezier(win, draw_color, sho_pt, (back_x, sho_y + 18), sag=4, w=3)

            if self.is_charged_attack:
                glow_r = int(10 * max(0, ext))
                if glow_r > 0:
                    pygame.draw.circle(win, (255, 140, 0), (arm_x, arm_y), glow_r, 2)

        elif self.is_guarding:
            s = 1 if self.facing == "right" else -1
            for ua in [s * 38, s * 22]:
                elb = _pt(*sho_pt, UA, ua)
                hnd = _pt(*elb, LA, ua + s * 8)
                _seg(win, draw_color, sho_pt, elb)
                _seg(win, draw_color, elb, hnd)
        else:
            ARM = 22
            for phase in [math.pi, 0]:
                ua = ARM * math.sin(c + phase)
                bend = abs(ua) * 0.3
                ea = ua + (bend if ua >= 0 else -bend)
                elb = _pt(*sho_pt, UA, ua)
                hnd = _pt(*elb, LA, ea)
                _seg(win, draw_color, sho_pt, elb)
                _seg(win, draw_color, elb, hnd)

        bar_y = self.y - self.height - 15
        pygame.draw.rect(win, WHITE,      (self.x, bar_y, self.width, 5))
        pygame.draw.rect(win, self.color, (self.x, bar_y, int(self.width * self.hp / 100), 5))
        pygame.draw.rect(win, (0, 0, 0),  (self.x - 1, bar_y - 1, self.width + 2, 6), 1)

        pip_y = bar_y - 8
        pip_w = (self.width - 2) // self.GUARD_MAX
        for i in range(self.GUARD_MAX):
            c2 = (80, 140, 255) if i < self.guard_hp else (60, 60, 60)
            pygame.draw.rect(win, c2, (self.x + i * (pip_w + 1), pip_y, pip_w, 4))

        if self.hit_flash > 0:
            self.hit_flash -= 1

    def _deal_damage(self, opponent):
        reach     = 220 if self.is_charged_attack else 140
        knockback = 10  if self.is_charged_attack else 6
        damage    = 20  if self.is_charged_attack else 10

        if self.facing == "right":
            in_range = 0 < (opponent.x - self.x) < reach
            kb_dir   = 1
        else:
            in_range = -reach < (opponent.x - self.x) < 0
            kb_dir   = -1

        if not in_range:
            return

        if opponent.is_guarding and opponent.guard_hp > 0:
            opponent.guard_hp -= 1
            opponent.guard_flash = 8
            opponent.hp -= 3
            sx = int(opponent.x + opponent.width // 2 - kb_dir * 5)
            sy = int(opponent.y - 35)
            for _ in range(7):
                opponent.guard_sparks.append(
                    (sx, sy, random.uniform(-3, 3), random.uniform(-4, -1),
                     random.randint(6, 10)))
            guard_sound.play()
            self.hit_registered = True
            if opponent.guard_hp <= 0:
                opponent.stun_timer = 25
                opponent.is_guarding = False
        else:
            opponent.hp       -= damage
            opponent.hit_flash = 5
            opponent.stun_timer = 18 if self.is_charged_attack else 10
            opponent.x         += knockback * kb_dir
            opponent.attack_progress = 0
            opponent.wobble_timer = 15
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
                    if (self._tap_dir == "left"
                            and (self.frame - self._tap_frame) <= self.DASH_WINDOW
                            and self.dash_cooldown == 0):
                        self.dash_timer = self.DASH_DURATION
                        self.dash_dir   = -1
                        self.dash_cooldown = 40
                        self._tap_dir = None
                    else:
                        self._tap_dir   = "left"
                        self._tap_frame = self.frame

                if cur_right and not self._prev_right:
                    if (self._tap_dir == "right"
                            and (self.frame - self._tap_frame) <= self.DASH_WINDOW
                            and self.dash_cooldown == 0):
                        self.dash_timer = self.DASH_DURATION
                        self.dash_dir   = 1
                        self.dash_cooldown = 40
                        self._tap_dir = None
                    else:
                        self._tap_dir   = "right"
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
                    self.vel_y = -13
                    self.on_ground = False
                    self.jump_cooldown = 30

                if keys[attack_key] and self.attack_cooldown == 0:
                    self.charge_timer += 1
                    self.is_charging = self.charge_timer >= self.CHARGE_FRAMES
                elif not keys[attack_key] and self.charge_timer > 0 and self.attack_cooldown == 0:
                    self.is_charged_attack = self.charge_timer >= self.CHARGE_FRAMES
                    self.attack_cooldown = 65 if self.is_charged_attack else 50
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
            dist     = opponent.x - self.x
            abs_dist = abs(dist)
            self.facing = "right" if dist >= 0 else "left"
            opp_atk = opponent.attack_progress > 0.15

            if opp_atk and abs_dist < 90 and self.guard_hp > 0:
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
                    if opp_atk and abs_dist < 100:
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
                if self.bounce_count < 2 and self.vel_y >= 7:
                    self.vel_y = -int(self.vel_y * 0.38)
                    self.y = self.ground_y
                    self.land_squash = 7
                    self.bounce_count += 1
                else:
                    self.y = self.ground_y
                    self.vel_y = 0
                    self.on_ground = True
                    self.land_squash = 12
                    self.bounce_count = 0
        else:
            self.was_on_ground = True

        self.was_on_ground = self.on_ground

        if self.attack_progress > 0:
            self.attack_progress += 0.1

            if self.is_charged_attack:
                hit_active = 0.50 <= self.attack_progress <= 0.72
            else:
                hit_active = 0.30 <= self.attack_progress <= 0.62

            if hit_active and not self.hit_registered and opponent:
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
            self.walk_vel = min(0.28, self.walk_vel + 0.05)
        else:
            self.walk_vel *= 0.72
        self.walk_cycle += self.walk_vel
        if self.walk_cycle > 2 * math.pi:
            self.walk_cycle -= 2 * math.pi

        self.x = max(0, min(WIDTH - self.width, self.x))
