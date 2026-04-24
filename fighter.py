import math
import random
import pygame
from config import *


def _bezier(win, color, p0, p2, sag=0, w=4):
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
    DODGE_HEIGHT  = 50

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
        self.is_aerial_attack = False
        self.ai_state = "APPROACH"
        self.ai_state_timer = 0
        self.wobble_timer = 0
        self.bounce_count = 0
        self.charge_sparks = []
        self._prev_atk = False
        self.spike_cooldown = 0
        self.popup_text = ""
        self.popup_timer = 0
        self.trigger_screen_flash = False

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
            pygame.draw.circle(win,
                               (int(120 + 135*flash), int(180 + 75*flash), 255),
                               (cx, int(self.y - self.height // 2 + 5)), 38, 3)
        if self.guard_flash > 0:
            self.guard_flash -= 1

        alive = []
        for x, y, vx, vy, life in self.guard_sparks:
            if life > 0:
                pygame.draw.circle(win, (180, 210, 255), (int(x), int(y)), max(1, life // 3))
                alive.append((x+vx, y+vy, vx, vy+0.4, life-1))
        self.guard_sparks = alive

        alive_c = []
        for x, y, vx, vy, life in self.charge_sparks:
            if life > 0:
                col = (255, max(0, int(140 * life / 14)), 0)
                pygame.draw.circle(win, col, (int(x), int(y)), max(2, life // 3))
                alive_c.append((x+vx, y+vy, vx, vy+0.3, life-1))
        self.charge_sparks = alive_c

        # \u6e9c\u3081\u4e2d\u30aa\u30fc\u30e9\uff08charge_timer > 0 \u304b\u3089\u5f90\u3005\u306b\u6210\u9577\uff09
        if self.charge_timer > 0:
            t     = min(1.0, self.charge_timer / self.CHARGE_FRAMES)
            ready = self.is_charging
            pulse = 0.85 + 0.15 * math.sin(self.frame * (0.40 if ready else 0.15))

            aura_r = int((14 + 34 * t) * pulse)
            sz = aura_r * 2 + 10
            aura_surf = pygame.Surface((sz, sz), pygame.SRCALPHA)
            ac = sz // 2
            for i in range(10, 0, -1):
                r = max(1, int(aura_r * i / 10))
                if ready:
                    alpha = min(200, int(90 * (i / 10) * pulse))
                    col = (255, int(180 + 75 * (i / 10)), int(20 * (1 - i / 10)), alpha)
                else:
                    alpha = min(150, int(55 * t * (i / 10)))
                    col = (255, int(55 * t * (i / 10)), 0, alpha)
                pygame.draw.circle(aura_surf, col, (ac, ac), r)
            win.blit(aura_surf, (cx - aura_r - 5, sho_y - aura_r + 4))

            interval = 2 if ready else max(3, 6 - int(4 * t))
            if self.frame % interval == 0:
                ang  = random.uniform(0, 2 * math.pi)
                dist = aura_r * random.uniform(0.55, 0.95)
                sx   = cx + int(dist * math.cos(ang))
                sy   = (sho_y + 4) + int(dist * 0.65 * math.sin(ang))
                spd  = 3.0 if ready else 1.5 * t + 0.5
                life = random.randint(6, 14) if ready else random.randint(3, 7)
                self.charge_sparks.append(
                    (sx, sy, random.uniform(-spd, spd),
                     random.uniform(-spd, 0), life))

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

        if self.is_aerial_attack and self.attack_progress > 0:
            t = self.attack_progress
            ext = (t / 0.5) if t < 0.5 else max(0.0, 1 - (t - 0.5) / 0.5)
            s = 1 if self.facing == "right" else -1

            knee_x = int(cx + s * 38 * ext)
            knee_y = int(hip_y + 4)
            foot_x = int(knee_x + s * 32 * ext)
            foot_y = int(knee_y + 12 + 12 * ext)
            _seg(win, draw_color, (cx, hip_y), (knee_x, knee_y))
            _seg(win, draw_color, (knee_x, knee_y), (foot_x, foot_y), w=5)

            tk_x = int(cx - s * 10)
            tk_y = hip_y - 12
            _seg(win, draw_color, (cx, hip_y), (tk_x, tk_y))
            _seg(win, draw_color, (tk_x, tk_y), (cx - s * 5, hip_y + 5))

        elif not self.on_ground:
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

        if self.is_aerial_attack and self.attack_progress > 0:
            s = 1 if self.facing == "right" else -1
            for arm_s, ang, sg in [(1, s*75, -4), (-1, -s*65, 3)]:
                ep = _pt(*sho_pt, UA + LA * 0.8, ang)
                _bezier(win, draw_color, sho_pt, (int(ep[0]), int(ep[1])), sag=sg, w=3)

        elif self.attack_progress > 0:
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
                    sag = 14 * math.sin(fwd * math.pi)
                else:
                    snap = (t - 0.60) / 0.40
                    ext = max(0, 1 - snap * 1.4) + 0.22 * math.sin(snap * math.pi * 2.5) * (1 - snap)
                    sag = 8 * math.sin(snap * math.pi * 3) * (1 - snap)
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
            arm_w = 6 if self.is_charged_attack else 4
            _bezier(win, draw_color, sho_pt, (arm_x, arm_y), sag=sag, w=arm_w)

            if self.is_charged_attack and ext > 0:
                for i, (size, col) in enumerate([
                    (int(12 * max(0, ext)), (255, 80, 0)),
                    (int(8  * max(0, ext)), (255, 180, 0)),
                    (int(4  * max(0, ext)), (255, 255, 150)),
                ]):
                    if size > 0:
                        pygame.draw.circle(win, col, (arm_x, arm_y), size)

            back_x = int(cx - s * 18)
            _bezier(win, draw_color, sho_pt, (back_x, sho_y + 18), sag=4, w=3)

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

        if self.hit_flash > 0:
            self.hit_flash -= 1

    def _deal_damage(self, opponent):
        if self.is_aerial_attack:
            reach, knockback, damage = 90, 8, 15
        elif self.is_charged_attack:
            reach, knockback, damage = 220, 10, 20
        else:
            reach, knockback, damage = 140, 6, 10

        if self.facing == "right":
            in_range = 0 < (opponent.x - self.x) < reach
            kb_dir   = 1
        else:
            in_range = -reach < (opponent.x - self.x) < 0
            kb_dir   = -1

        if not in_range:
            return

        if not self.is_aerial_attack and self.on_ground:
            air_height = opponent.ground_y - opponent.y
            if not opponent.on_ground and air_height > self.DODGE_HEIGHT:
                self.hit_registered = True
                return

        if opponent.is_guarding and opponent.guard_hp > 0:
            opponent.guard_hp -= 1
            opponent.guard_flash = 8
            opponent.hp -= 3
            sx = int(opponent.x + opponent.width // 2 - kb_dir * 5)
            sy = int(opponent.y - 35)
            for _ in range(7):
                opponent.guard_sparks.append(
                    (sx, sy, random.uniform(-3, 3),
                     random.uniform(-4, -1), random.randint(6, 10)))
            guard_sound.play()
            self.hit_registered = True
            if opponent.guard_hp <= 0:
                opponent.stun_timer = 25
                opponent.is_guarding = False
        else:
            opponent.hp          -= damage
            opponent.hit_flash    = 5
            opponent.stun_timer   = 18 if self.is_charged_attack else (12 if self.is_aerial_attack else 10)
            opponent.x            += knockback * kb_dir
            opponent.attack_progress = 0
            opponent.wobble_timer = 15
            if self.is_charged_attack:
                pistol_sound.play()
            else:
                hit_sound.play()
            self.hit_registered = True

            if self.is_charged_attack:
                opponent.popup_text  = "PISTOL !"
                opponent.popup_timer = 55
                self.trigger_screen_flash = True
                sx = int(opponent.x + opponent.width // 2)
                sy = int(opponent.y - 35)
                for _ in range(14):
                    opponent.charge_sparks.append(
                        (sx, sy, random.uniform(-5, 5),
                         random.uniform(-5, 1), random.randint(8, 14)))

            elif self.is_aerial_attack:
                opponent.popup_text  = "KICK !"
                opponent.popup_timer = 40

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
                and self.guard_hp > 0
            )

            if not self.is_guarding:
                if cur_left and not self._prev_left:
                    if (self._tap_dir == "left"
                            and (self.frame - self._tap_frame) <= self.DASH_WINDOW
                            and self.dash_cooldown == 0):
                        self.dash_timer, self.dash_dir, self.dash_cooldown = self.DASH_DURATION, -1, 40
                        self._tap_dir = None
                    else:
                        self._tap_dir, self._tap_frame = "left", self.frame

                if cur_right and not self._prev_right:
                    if (self._tap_dir == "right"
                            and (self.frame - self._tap_frame) <= self.DASH_WINDOW
                            and self.dash_cooldown == 0):
                        self.dash_timer, self.dash_dir, self.dash_cooldown = self.DASH_DURATION, 1, 40
                        self._tap_dir = None
                    else:
                        self._tap_dir, self._tap_frame = "right", self.frame

                if self.dash_timer > 0:
                    self.x += self.DASH_SPEED * self.dash_dir
                    self.facing = "right" if self.dash_dir > 0 else "left"
                    self.dash_timer -= 1
                    moved = True
                else:
                    if cur_left:
                        self.x -= self.vel_x; self.facing = "left"; moved = True
                    if cur_right:
                        self.x += self.vel_x; self.facing = "right"; moved = True

                if keys[jump_key] and self.on_ground and self.jump_cooldown == 0:
                    self.vel_y = -13
                    self.on_ground = False
                    self.jump_cooldown = 30

                if not self.on_ground and attack_key and keys[attack_key]:
                    if not self._prev_atk and self.attack_cooldown == 0:
                        self.attack_cooldown = 40
                        self.attack_progress = 0.01
                        self.is_aerial_attack = True
                        self.is_charged_attack = False
                        self.charge_timer = 0
                    self._prev_atk = True
                else:
                    if self.on_ground:
                        if attack_key and keys[attack_key] and self.attack_cooldown == 0:
                            self.charge_timer += 1
                            self.is_charging = self.charge_timer >= self.CHARGE_FRAMES
                        elif attack_key and not keys[attack_key] and self.charge_timer > 0 and self.attack_cooldown == 0:
                            self.is_charged_attack = self.charge_timer >= self.CHARGE_FRAMES
                            self.is_aerial_attack = False
                            self.attack_cooldown = 65 if self.is_charged_attack else 50
                            self.attack_progress = 0.01
                            self.charge_timer = 0
                            self.is_charging = False
                        elif attack_key and not keys[attack_key]:
                            self.charge_timer = 0
                            self.is_charging = False
                    self._prev_atk = False
            else:
                self.charge_timer = 0
                self.is_charging = False

            if self.jump_cooldown > 0: self.jump_cooldown -= 1
            if self.dash_cooldown > 0:  self.dash_cooldown -= 1

            self._prev_left  = cur_left
            self._prev_right = cur_right

        else:
            dist     = opponent.x - self.x
            abs_dist = abs(dist)
            self.facing = "right" if dist >= 0 else "left"
            opp_atk  = opponent.attack_progress > 0.15

            self.is_guarding = opp_atk and abs_dist < 90 and self.guard_hp > 0

            if not self.is_guarding:
                if self.ai_state == "APPROACH":
                    if abs_dist > 88:
                        self.x += self.vel_x if dist > 0 else -self.vel_x; moved = True
                    else:
                        self.ai_state = "IDLE"
                        self.ai_state_timer = random.randint(15, 35)

                elif self.ai_state == "IDLE":
                    if opp_atk and abs_dist < 100:
                        self.x -= self.vel_x if dist > 0 else -self.vel_x; moved = True
                    self.ai_state_timer -= 1
                    if self.ai_state_timer <= 0:
                        self.ai_state = "ATTACK" if (self.attack_cooldown == 0 and abs_dist < 90) else "APPROACH"

                elif self.ai_state == "ATTACK":
                    if self.attack_cooldown == 0 and abs_dist < 90:
                        self.attack_cooldown = 40
                        self.attack_progress = 0.01
                        self.is_charged_attack = False
                        self.is_aerial_attack = False
                    self.ai_state = "RETREAT"
                    self.ai_state_timer = random.randint(20, 40)

                elif self.ai_state == "RETREAT":
                    self.x -= self.vel_x if dist > 0 else -self.vel_x; moved = True
                    self.ai_state_timer -= 1
                    if self.ai_state_timer <= 0:
                        self.ai_state = "APPROACH"

            if self.jump_cooldown > 0: self.jump_cooldown -= 1
            if self.dash_cooldown > 0:  self.dash_cooldown -= 1

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
                    self.y, self.vel_y = self.ground_y, 0
                    self.on_ground = True
                    self.land_squash = 12
                    self.bounce_count = 0
        self.was_on_ground = self.on_ground

        if self.attack_progress > 0:
            self.attack_progress += 0.1

            if self.is_charged_attack:
                hit_active = 0.50 <= self.attack_progress <= 0.72
            elif self.is_aerial_attack:
                hit_active = 0.30 <= self.attack_progress <= 0.65
            else:
                hit_active = 0.30 <= self.attack_progress <= 0.62

            if hit_active and not self.hit_registered and opponent:
                self._deal_damage(opponent)

            if self.attack_progress > 1.0:
                self.attack_progress = 0
                self.hit_registered = False
                self.is_charged_attack = False
                self.is_aerial_attack = False

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

        # \u68d8\u58c1\u30c0\u30e1\u30fc\u30b8\uff08\u7aef\u306e22px\u4ee5\u5185\uff09
        if self.spike_cooldown > 0:
            self.spike_cooldown -= 1
        elif self.spike_cooldown == 0:
            in_left  = self.x < 22
            in_right = self.x > WIDTH - self.width - 22
            if in_left or in_right:
                self.hp          -= 4
                self.hit_flash    = 6
                self.wobble_timer = 10
                self.stun_timer   = 8
                self.x           += 28 if in_left else -28
                self.spike_cooldown = 55
                spike_sound.play()
