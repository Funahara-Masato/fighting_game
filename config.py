import pygame

pygame.init()

WIDTH, HEIGHT = 800, 400
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ゴム人間格闘ゲーム")

FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GROUND = HEIGHT - 83

try:
    pygame.mixer.init()
    _mixer_ok = True
except Exception:
    _mixer_ok = False


class _SilentSound:
    def play(self): pass
    def set_volume(self, v): pass
    def stop(self): pass


def _make_sound_safe(arr2d):
    try:
        import pygame.sndarray
        return pygame.sndarray.make_sound(arr2d)
    except Exception:
        return _SilentSound()


# 効果音
try:
    hit_sound = pygame.mixer.Sound("assets/hit.ogg")
    hit_sound.set_volume(0.3)
except Exception:
    hit_sound = _SilentSound()

# ガード音（金属的なカキン）
try:
    import numpy as np
    _sr = 44100
    _t  = np.linspace(0, 0.07, int(_sr * 0.07), endpoint=False)
    _w  = (np.sin(2 * np.pi * 900 * _t) * np.exp(-_t * 50) * 0.55 * 32767).astype(np.int16)
    guard_sound = _make_sound_safe(np.column_stack([_w, _w]))
    guard_sound.set_volume(0.5)

    # ゴムゴムのピストル音
    _t_p   = np.linspace(0, 0.22, int(_sr * 0.22), endpoint=False)
    _noise = np.random.randn(len(_t_p))
    _bass  = np.sin(2 * np.pi * 68  * _t_p) * np.exp(-_t_p * 10)
    _crack = np.sin(2 * np.pi * 210 * _t_p) * np.exp(-_t_p * 28)
    _w_raw = _noise * 0.28 * np.exp(-_t_p * 38) + _bass * 0.56 + _crack * 0.16
    _w_p   = (_w_raw / max(abs(_w_raw).max(), 1e-6) * 0.90 * 32767).astype(np.int16)
    pistol_sound = _make_sound_safe(np.column_stack([_w_p, _w_p]))
    pistol_sound.set_volume(0.70)

    # 棘ダメージ音
    _t_sp = np.linspace(0, 0.05, int(_sr * 0.05), endpoint=False)
    _w_sp = (np.sin(2 * np.pi * 440 * _t_sp) * np.exp(-_t_sp * 60) * 0.5 * 32767).astype(np.int16)
    spike_sound = _make_sound_safe(np.column_stack([_w_sp, _w_sp]))
    spike_sound.set_volume(0.4)

    # セレクト画面BGM（C→Am→F→G コード＋アルペジオ、8秒ループ）
    _bsr  = 44100
    _bdur = 8.0
    _bn   = int(_bsr * _bdur)
    _bgm  = np.zeros(_bn)
    _chords = [
        [261.63, 329.63, 392.00],
        [220.00, 261.63, 329.63],
        [174.61, 220.00, 261.63],
        [196.00, 246.94, 293.66],
    ]
    _csec = int(_bsr * 2)
    for _ci, _freqs in enumerate(_chords):
        _st = _ci * _csec
        _en = _st + _csec
        _ct = np.arange(_en - _st) / _bsr
        _env = np.ones(len(_ct))
        _env[:int(0.03 * _bsr)] = np.linspace(0, 1, int(0.03 * _bsr))
        _env[-int(0.4 * _bsr):] = np.linspace(1, 0, int(0.4 * _bsr))
        for _f in _freqs:
            _bgm[_st:_en] += np.sin(2 * np.pi * _f * _ct) * 0.18 * _env
    _arp = [261.63, 329.63, 392.00, 523.25, 392.00, 329.63, 261.63, 220.00]
    _astep = int(_bsr * 0.25)
    for _ai in range(_bn // _astep):
        _st = _ai * _astep
        _en = min(_st + _astep, _bn)
        _at = np.arange(_en - _st) / _bsr
        _aenv = np.exp(-_at * 10) * 0.28
        _note = _arp[_ai % len(_arp)]
        _bgm[_st:_en] += np.sin(2 * np.pi * _note * _at) * _aenv
    _bgm_max = max(abs(_bgm).max(), 1e-6)
    _bgm_i   = (_bgm / _bgm_max * 0.60 * 32767).astype(np.int16)
    select_bgm_sound = _make_sound_safe(np.column_stack([_bgm_i, _bgm_i]))
    select_bgm_sound.set_volume(0.28)

except Exception:
    guard_sound = _SilentSound()
    pistol_sound = _SilentSound()
    spike_sound  = _SilentSound()
    select_bgm_sound = _SilentSound()

# 背景画像
try:
    background_img = pygame.image.load("assets/background.jpg")
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except Exception:
    background_img = pygame.Surface((WIDTH, HEIGHT))
    background_img.fill((30, 30, 50))
