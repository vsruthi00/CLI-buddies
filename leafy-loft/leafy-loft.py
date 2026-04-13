#!/usr/bin/env python3
"""
leafy-loft.py -- Your terminal plant shelf. A cozy pixel-art room where
you pick 4-5 plants, water them, and move them around. Different plants
need different amounts of water and light. Day/night cycle with sunrise
and sunset. Plants closer to the window get more light.

Pure Python stdlib. No pip installs. Runs in a tmux split pane.

CONTROLS:
  Click the grey [+]    -> add a plant (pick from menu)
  Click the save icon   -> save your garden so it reappears next launch
  Click the trash icon  -> remove a plant
  Click any plant       -> water / move / rename menu
  Ctrl+C                -> goodbye
"""

import sys, os, re, tty, termios, select, signal, time, random, math, json, atexit
from datetime import datetime
from pathlib import Path

# Import pre-converted pixel art sprites
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_data

# ══════════════════════════════════════════════════════════════════════════════
# § 1  ANSI / TERMINAL HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def fg(r, g, b):  return f'\033[38;2;{r};{g};{b}m'
def bg(r, g, b):  return f'\033[48;2;{r};{g};{b}m'
RST   = '\033[0m'
BOLD  = '\033[1m'
HIDE  = '\033[?25l'
SHOW  = '\033[?25h'
MON   = '\033[?1000h\033[?1006h'
MOFF  = '\033[?1000l\033[?1006l'

def goto(r, c): return f'\033[{r};{c}H'

def term_size():
    import shutil
    s = shutil.get_terminal_size((120, 32))
    return s.lines, s.columns

# ══════════════════════════════════════════════════════════════════════════════
# § 2  CONFIG / STATE
# ══════════════════════════════════════════════════════════════════════════════

CFG_DIR = Path(os.environ.get('XDG_CONFIG_HOME') or (Path.home() / '.config')) / 'leafy-loft'
STATE_FILE = CFG_DIR / 'state.json'

def load_state():
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text()).get('plants') or []
    except Exception:
        pass
    return []

def save_state(plants):
    try:
        CFG_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps({
            'plants': [
                {'key': p.key, 'name': p.name, 'slot': p.slot}
                for p in plants
            ]
        }, indent=2))
    except Exception:
        pass

def reset_state():
    try:
        if STATE_FILE.exists():
            STATE_FILE.unlink()
    except Exception:
        pass

def _emergency_restore():
    try:
        sys.stdout.write('\033[?1000l\033[?1006l\033[?25h\033[0m')
        sys.stdout.flush()
    except Exception:
        pass

atexit.register(_emergency_restore)

# ══════════════════════════════════════════════════════════════════════════════
# § 3  INPUT HANDLING
# ══════════════════════════════════════════════════════════════════════════════

_MOUSE_RE = re.compile(r'\x1b\[<(\d+);(\d+);(\d+)([Mm])')

def read_events():
    """Returns list of event dicts. Non-blocking. Same approach as cozy-cats."""
    if not select.select([sys.stdin], [], [], 0)[0]:
        return []
    raw = b''
    while select.select([sys.stdin], [], [], 0)[0]:
        chunk = os.read(sys.stdin.fileno(), 256)
        if not chunk:
            break
        raw += chunk
    buf = raw.decode('utf-8', errors='replace')
    events = []
    # Mouse SGR sequences
    for m in _MOUSE_RE.finditer(buf):
        btn, col, row, act = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
        if act == 'M' and btn == 0:
            events.append({'t': 'click', 'col': col, 'row': row})
    buf = _MOUSE_RE.sub('', buf)
    # Keyboard (after stripping mouse)
    i = 0
    while i < len(buf):
        ch = buf[i]
        if ch == '\x03':
            events.append({'t': 'quit'})
        elif ch == '\x1b' and i + 2 < len(buf):
            seq = buf[i:i+3]
            if   seq == '\x1b[A': events.append({'t': 'key', 'k': 'UP'});    i += 3; continue
            elif seq == '\x1b[B': events.append({'t': 'key', 'k': 'DOWN'});  i += 3; continue
            elif seq == '\x1b[C': events.append({'t': 'key', 'k': 'RIGHT'}); i += 3; continue
            elif seq == '\x1b[D': events.append({'t': 'key', 'k': 'LEFT'});  i += 3; continue
            else:                 events.append({'t': 'esc'})
        elif ch in ('\r', '\n'):
            events.append({'t': 'key', 'k': 'ENTER'})
        elif ch == '\x7f':
            events.append({'t': 'key', 'k': 'BACKSPACE'})
        elif ch.isprintable():
            events.append({'t': 'key', 'k': ch})
        i += 1
    return events

# ══════════════════════════════════════════════════════════════════════════════
# § 4  PIXEL CANVAS
# ══════════════════════════════════════════════════════════════════════════════

SKY_BLUE = (173, 223, 255)   # #aedef1 daytime sky

class Canvas:
    def __init__(self, term_h, term_w):
        self.th, self.tw = term_h, term_w
        self.ph = term_h * 2
        self.pw = term_w
        self._b = [[None]*term_w for _ in range(self.ph)]
        self.bg_color = SKY_BLUE

    def fill(self, color=None):
        c = color or self.bg_color
        for row in self._b:
            for i in range(self.pw): row[i] = c

    def put(self, py, px, color):
        if 0 <= py < self.ph and 0 <= px < self.pw:
            self._b[py][px] = color

    def rect(self, py, px, h, w, color):
        for dy in range(h):
            for dx in range(w): self.put(py+dy, px+dx, color)

    def blit(self, py, px, sprite):
        for dr, row in enumerate(sprite):
            for dc, c in enumerate(row):
                if c is not None: self.put(py+dr, px+dc, c)

    def render(self, start_row=1):
        SBG = self.bg_color
        rows = self._b
        if self.ph % 2:
            rows = rows + [[None]*self.pw]
        parts = [HIDE]
        for i in range(0, len(rows), 2):
            tr = start_row + i // 2
            top_r, bot_r = rows[i], rows[i+1]
            parts.append(f'\033[{tr};1H')
            parts.append(bg(*SBG))
            for t, b in zip(top_r, bot_r):
                t = t or SBG
                b = b or SBG
                if t == b:
                    parts.append(bg(*t) + ' ')
                else:
                    parts.append(bg(*b) + fg(*t) + '▀')
            parts.append(RST)
        return ''.join(parts)

# ══════════════════════════════════════════════════════════════════════════════
# § 5  DAY/NIGHT CYCLE
# ══════════════════════════════════════════════════════════════════════════════
#
# Sky color interpolates through: night -> dawn -> day -> dusk -> night
# Based on the hour of day from the system clock.

NIGHT_SKY = (58, 78, 118)     # dusky blue (not too dark)
DAWN_SKY  = (255, 188, 148)   # warm peach
DAY_SKY   = (173, 223, 255)   # #aedef1 light sky blue
DUSK_SKY  = (238, 160, 168)   # warm rose

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def sky_at(hour):
    """Return (top_color, bot_color, light_level 0.0-1.0) for the given hour."""
    # Hour is float 0-24
    h = hour % 24

    if 5.0 <= h < 6.5:          # dawn
        t = (h - 5.0) / 1.5
        top = lerp(NIGHT_SKY, DAWN_SKY, t)
        bot = lerp(NIGHT_SKY, DAWN_SKY, min(1.0, t * 1.3))
        light = t * 0.5
    elif 6.5 <= h < 8.0:        # dawn -> day
        t = (h - 6.5) / 1.5
        top = lerp(DAWN_SKY, DAY_SKY, t)
        bot = lerp(DAWN_SKY, DAY_SKY, t)
        light = 0.5 + t * 0.5
    elif 8.0 <= h < 17.0:       # day
        top = DAY_SKY
        bot = DAY_SKY
        light = 1.0
    elif 17.0 <= h < 18.5:      # day -> dusk
        t = (h - 17.0) / 1.5
        top = lerp(DAY_SKY, DUSK_SKY, t)
        bot = lerp(DAY_SKY, DUSK_SKY, t)
        light = 1.0 - t * 0.4
    elif 18.5 <= h < 20.0:      # dusk -> night
        t = (h - 18.5) / 1.5
        top = lerp(DUSK_SKY, NIGHT_SKY, t)
        bot = lerp(DUSK_SKY, NIGHT_SKY, min(1.0, t * 1.3))
        light = 0.6 - t * 0.6
    else:                        # night (20:00 - 5:00)
        top = NIGHT_SKY
        bot = NIGHT_SKY
        light = 0.0

    return top, bot, light


def sun_position(hour, pw, ph):
    """Return (px, py) for the sun/moon. None if not visible."""
    h = hour % 24
    # Sun visible roughly 5am to 8pm, moon the rest
    # Map visible portion to an arc across the sky
    if 5.5 <= h < 19.5:
        # Sun path
        t = (h - 5.5) / 14.0  # 0 at sunrise, 1 at sunset
        px = int(pw * 0.1 + (pw * 0.8) * t)
        # Arc: y = ph*0.05 at noon (t=0.5), ph*0.35 at horizon
        arc = 1 - 4 * (t - 0.5) ** 2  # 0 at edges, 1 at middle
        py = int(ph * 0.32 - arc * ph * 0.25)
        return (px, py, 'sun')
    else:
        # Moon path (20:00 -> 5:00, crosses midnight)
        if h >= 20.0:
            t = (h - 20.0) / 9.0
        else:
            t = (h + 4.0) / 9.0
        px = int(pw * 0.1 + (pw * 0.8) * t)
        arc = 1 - 4 * (t - 0.5) ** 2
        py = int(ph * 0.32 - arc * ph * 0.2)
        return (px, py, 'moon')


def draw_sun(cv, px, py):
    SUN = (255, 226, 118)
    SHINE = (255, 248, 190)
    # 5x5 sun
    for dy in range(5):
        for dx in range(5):
            # Roundish
            d2 = (dx - 2) ** 2 + (dy - 2) ** 2
            if d2 <= 5:
                cv.put(py + dy, px + dx, SUN)
    cv.put(py + 1, px + 1, SHINE)
    cv.put(py + 1, px + 2, SHINE)
    cv.put(py + 2, px + 1, SHINE)


def draw_moon(cv, px, py):
    MOON = (232, 232, 240)
    SHADOW = (178, 178, 198)
    for dy in range(5):
        for dx in range(5):
            d2 = (dx - 2) ** 2 + (dy - 2) ** 2
            if d2 <= 5:
                cv.put(py + dy, px + dx, MOON)
    # Crater shadow on right
    cv.put(py + 2, px + 3, SHADOW)
    cv.put(py + 3, px + 3, SHADOW)

# ══════════════════════════════════════════════════════════════════════════════
# § 6  SCENE BACKGROUND (walls, floor, sun/moon)
# ══════════════════════════════════════════════════════════════════════════════

FLOOR_H = 8

# Floor colors (wood)
FL_A     = (158, 118, 72)
FL_B     = (140, 100, 58)
FL_BOARD = (112, 78, 42)

def draw_background(cv, hour):
    ph, pw = cv.ph, cv.pw
    top_sky, bot_sky, light = sky_at(hour)
    cv.bg_color = top_sky
    floor_top = ph - FLOOR_H

    # Sky gradient
    for py in range(floor_top):
        t = py / max(1, floor_top)
        shade = lerp(top_sky, bot_sky, t)
        for px in range(pw):
            cv.put(py, px, shade)

    # (Sun/moon sprite removed — the sky gradient carries the time-of-day)

    # Floor (wood)
    for py in range(floor_top, ph):
        for px in range(pw):
            col = FL_A if ((px // 6 + py // 4) % 2 == 0) else FL_B
            cv.put(py, px, col)
    # Floor board line
    for py in range(floor_top, floor_top + 2):
        for px in range(pw):
            cv.put(py, px, FL_BOARD)

    return light

# ══════════════════════════════════════════════════════════════════════════════
# § 7  PLANT CLASS
# ══════════════════════════════════════════════════════════════════════════════

# Slots: where a plant can be placed
# 5 slots total: left of stool, on stool, and three on the right of the stool
SLOT_FLOOR_L  = 'floor_l'    # left of stool
SLOT_STOOL    = 'stool'      # on the stool
SLOT_FLOOR_R1 = 'floor_r1'   # right of stool, slot 1
SLOT_FLOOR_R2 = 'floor_r2'   # right of stool, slot 2
SLOT_FLOOR_R3 = 'floor_r3'   # right of stool, slot 3

SLOT_NAMES = {
    SLOT_FLOOR_L:  'Floor (left of stool)',
    SLOT_STOOL:    'On the stool',
    SLOT_FLOOR_R1: 'Floor (right 1)',
    SLOT_FLOOR_R2: 'Floor (right 2)',
    SLOT_FLOOR_R3: 'Floor (right 3)',
}

ALL_SLOTS = [SLOT_FLOOR_L, SLOT_STOOL, SLOT_FLOOR_R1, SLOT_FLOOR_R2, SLOT_FLOOR_R3]


def pretty_plant_name(key):
    return key.replace('_', ' ').title()


class Plant:
    def __init__(self, key, name, slot):
        self.key  = key
        self.name = name
        self.slot = slot
        self.sprite = sprite_data.get_plant_sprite(key)
        self.w, self.h = sprite_data.get_plant_size(key)
        # Water need in minutes
        wn = sprite_data.WATER_NEEDS.get(key, (60, 90))
        self.water_min = random.uniform(wn[0], wn[1])
        self.light_need = sprite_data.LIGHT_NEEDS.get(key, 'med')
        # Thirst 0-100, rises over time. 100 = dead.
        self.thirst = 0.0
        self.last_water_t = time.time()
        # Light accumulation (sunshine deficit/surplus)
        self.light_balance = 0.0  # neg = needs more, pos = happy
        # Sad state when thirsty or wrong light
        self.sad_bubble = None
        self._bub_t = 0

    def update(self, dt, light_here):
        # Thirst rises linearly: reaches 100 at water_min minutes
        rise_per_sec = 100.0 / (self.water_min * 60.0)
        self.thirst = min(100.0, self.thirst + rise_per_sec * dt)

        # Light balance: positive if matching need, negative if not
        # light_here is 0-1 from sun + proximity to window
        need_map = {'low': 0.2, 'med': 0.5, 'high': 0.9}
        needed = need_map.get(self.light_need, 0.5)
        # Drift toward balance
        delta = (light_here - needed) * dt * 0.05
        self.light_balance = max(-100, min(100, self.light_balance + delta))

        # Clear bubble
        if self.sad_bubble and time.time() >= self._bub_t:
            self.sad_bubble = None

    def water(self):
        self.thirst = 0.0
        self.last_water_t = time.time()
        self.sad_bubble = random.choice([
            "ahh, thank you",
            "refreshing!",
            "*happy rustle*",
            "yum",
            "needed that",
        ])
        self._bub_t = time.time() + 3.0

    def status_color(self):
        """Return a tint color based on how happy the plant is."""
        if self.thirst > 80:
            return (150, 100, 80)  # wilted brown
        if self.thirst > 50:
            return (180, 160, 100)  # yellowish
        if self.light_balance < -20:
            return (120, 140, 100)  # pale green (not enough light)
        return None  # healthy, no tint

    def urgency(self):
        """How urgently does this plant need something? 0-100."""
        return max(self.thirst, max(0, -self.light_balance))

# ══════════════════════════════════════════════════════════════════════════════
# § 8  SCENE
# ══════════════════════════════════════════════════════════════════════════════

class Scene:
    def __init__(self, cv):
        self.cv = cv
        pw, ph = cv.pw, cv.ph
        self.floor_py = ph - FLOOR_H

        def _fitx(x, w):
            return max(2, min(x, pw - w - 2))

        def _fity(y, min_y=2):
            return max(min_y, y)

        # Room sprite sizes
        self.window_w, self.window_h = sprite_data.get_room_size('glass_window')
        self.shelf_w,  self.shelf_h  = sprite_data.get_room_size('shelf')
        self.shelf2_w, self.shelf2_h = sprite_data.get_room_size('shelf_2')
        self.stool_w,  self.stool_h  = sprite_data.get_room_size('stool')

        # Menu icons top-right: [+] [save] [trash] — set first so shelf
        # positioning can avoid them.
        plus_w, plus_h     = sprite_data.get_icon_size('plus')
        save_w, save_h     = sprite_data.get_icon_size('save')
        trash_w, trash_h   = sprite_data.get_icon_size('trash')
        self.plus_w, self.plus_h   = plus_w, plus_h
        self.save_w, self.save_h   = save_w, save_h
        self.trash_w, self.trash_h = trash_w, trash_h

        gap = 3
        self.trash_px = _fitx(pw - trash_w - 4, trash_w)
        self.trash_py = 2
        self.save_px  = _fitx(self.trash_px - save_w - gap, save_w)
        self.save_py  = 2
        self.plus_px  = _fitx(self.save_px - plus_w - gap, plus_w)
        self.plus_py  = 2

        # Stool on the floor, ~25% from the left (this anchors the window above)
        self.stool_px = _fitx(pw // 4, self.stool_w)
        self.stool_py = self.floor_py - self.stool_h

        # Window on the wall directly above the stool
        self.window_px = _fitx(self.stool_px + self.stool_w // 2 - self.window_w // 2, self.window_w)
        self.window_py = _fity(2, 2)

        # Wall shelf: decorative (pre-drawn plants on it). Positioned to
        # the LEFT of the menu icons so they don't overlap.
        # Icons start at self.plus_px. Shelf must end before that (with margin).
        shelf_left_margin = self.window_px + self.window_w + 6  # right of window
        shelf_right_margin = self.plus_px - 4                    # left of icons
        # Prefer centering between window and icons
        shelf_space = shelf_right_margin - shelf_left_margin
        if shelf_space >= self.shelf_w:
            self.shelf_px = shelf_left_margin + (shelf_space - self.shelf_w) // 2
        else:
            # Not enough room between window and icons; place left of window
            self.shelf_px = _fitx(self.window_px - self.shelf_w - 4, self.shelf_w)
        self.shelf_py = _fity(2, 2)

        # Floor shelf (side bookshelf) on the floor, far-right
        self.shelf2_px = _fitx(pw - self.shelf2_w - 6, self.shelf2_w)
        self.shelf2_py = self.floor_py - self.shelf2_h

        # Plant slot positions (top-left of the plant sprite).
        # Layout: [floor_l] [stool] [floor_r1] [floor_r2] [floor_r3]
        # Floor plants render at the bottom of the scene; the wall shelf is
        # at the top of the scene. Vertical separation means no visual overlap.
        plant_slot_w = 22
        right_start = self.stool_px + self.stool_w + 2
        self.slot_pos = {
            SLOT_FLOOR_L:  (max(4, self.stool_px - plant_slot_w - 2),  'floor'),
            SLOT_STOOL:    (self.stool_px + self.stool_w // 2,         'stool'),
            SLOT_FLOOR_R1: (right_start,                                'floor'),
            SLOT_FLOOR_R2: (right_start + plant_slot_w,                 'floor'),
            SLOT_FLOOR_R3: (right_start + plant_slot_w * 2,             'floor'),
        }

        # Click regions (term coords) -- set immediately so first click works
        self._plus_r  = self._treg(self.plus_px,  self.plus_py,  self.plus_w,  self.plus_h)
        self._save_r  = self._treg(self.save_px,  self.save_py,  self.save_w,  self.save_h)
        self._trash_r = self._treg(self.trash_px, self.trash_py, self.trash_w, self.trash_h)

    def _treg(self, px, py, w, h):
        return (px + 1, py // 2 + 1, px + w, (py + h) // 2 + 1)

    def slot_render_pos(self, slot, plant_w, plant_h):
        """Return (px, py) to render a plant of given size in the given slot."""
        spec = self.slot_pos.get(slot)
        if not spec:
            return (0, 0)
        base_x, kind = spec
        if kind == 'floor':
            # Center the plant horizontally around the slot x
            px = base_x
            py = self.floor_py - plant_h
        elif kind == 'stool':
            # Plant bottom sits flush with the stool seat top (row 1 of sprite)
            px = self.stool_px + (self.stool_w - plant_w) // 2
            py = self.stool_py + 1 - plant_h
        else:
            px, py = base_x, self.floor_py - plant_h
        return (px, py)

    def light_at_slot(self, slot, daylight):
        """Compute how much light reaches a plant in this slot.
        daylight: 0-1 from sun cycle.
        Return: 0-1 effective light."""
        if daylight <= 0:
            return 0.0
        # Light spreads from window. Distance from window center to slot center.
        win_cx = self.window_px + self.window_w // 2
        win_cy = self.window_py + self.window_h // 2
        spec = self.slot_pos.get(slot)
        if not spec:
            return daylight * 0.5
        base_x, kind = spec
        if kind == 'floor':
            sx, sy = base_x + 12, self.floor_py - 10
        elif kind == 'stool':
            sx, sy = self.stool_px + self.stool_w // 2, self.stool_py + 5
        else:
            sx, sy = base_x, self.floor_py - 10
        dist = math.hypot(sx - win_cx, sy - win_cy)
        falloff = max(0.3, 1.0 - dist / 80.0)
        return daylight * falloff

    def draw(self, hour):
        cv = self.cv
        daylight = draw_background(cv, hour)
        # Window
        sp = sprite_data.get_room_sprite('glass_window')
        if sp: cv.blit(self.window_py, self.window_px, sp)
        # Wall shelf (decorative, plants in the sprite itself)
        sp = sprite_data.get_room_sprite('shelf')
        if sp: cv.blit(self.shelf_py, self.shelf_px, sp)
        # Floor shelf (side bookshelf)
        sp = sprite_data.get_room_sprite('shelf_2')
        if sp: cv.blit(self.shelf2_py, self.shelf2_px, sp)
        # Stool
        sp = sprite_data.get_room_sprite('stool')
        if sp: cv.blit(self.stool_py, self.stool_px, sp)
        # Icons
        for name, px, py in [
            ('plus',  self.plus_px,  self.plus_py),
            ('save',  self.save_px,  self.save_py),
            ('trash', self.trash_px, self.trash_py),
        ]:
            icn = sprite_data.get_icon(name)
            if icn:
                cv.blit(py, px, icn)
        # Click regions
        self._plus_r  = self._treg(self.plus_px,  self.plus_py,  self.plus_w,  self.plus_h)
        self._save_r  = self._treg(self.save_px,  self.save_py,  self.save_w,  self.save_h)
        self._trash_r = self._treg(self.trash_px, self.trash_py, self.trash_w, self.trash_h)
        return daylight

    def in_region(self, reg, tc, tr):
        if not reg: return False
        x1, y1, x2, y2 = reg
        return x1 <= tc <= x2 and y1 <= tr <= y2

    def in_plus(self, tc, tr):  return self.in_region(self._plus_r, tc, tr)
    def in_save(self, tc, tr):  return self.in_region(self._save_r, tc, tr)
    def in_trash(self, tc, tr): return self.in_region(self._trash_r, tc, tr)


# ══════════════════════════════════════════════════════════════════════════════
# § 9  MENUS
# ══════════════════════════════════════════════════════════════════════════════

MAX_MENU_ROWS = 10   # max visible rows for scrollable menus

def menu_box(title, options, sel, tw, width=42, max_rows=MAX_MENU_ROWS):
    """Return list of ANSI strings for a bordered menu with scrolling.

    If len(options) > max_rows, only max_rows are shown at a time and the
    visible window scrolls to keep `sel` in view.
    """
    PC = fg(86, 142, 68)
    AC = fg(188, 224, 178)
    DC = fg(118, 132, 102)
    BG = bg(28, 58, 38)
    RST_ = RST + bg(173, 223, 255)

    w = width
    n = len(options)
    visible = min(n, max_rows)

    # Scroll window so sel is visible
    if n <= visible:
        start = 0
    else:
        start = max(0, min(sel - visible // 2, n - visible))
    end = start + visible
    shown = options[start:end]

    lines = []
    # Top border
    lines.append(BG + PC + '╔' + '═' * (w - 2) + '╗' + RST_)
    # Title
    t = title[:w - 4]
    pad = (w - 4 - len(t)) // 2
    lines.append(BG + PC + '║' + ' ' + ' ' * pad + AC + t + PC + ' ' * (w - 4 - pad - len(t)) + ' ' + PC + '║' + RST_)
    # Separator
    lines.append(BG + PC + '╠' + '═' * (w - 2) + '╣' + RST_)
    # Options with scroll indicators
    for i, (_, label) in enumerate(shown):
        global_i = start + i
        marker = '>' if global_i == sel else ' '
        color = AC if global_i == sel else DC
        l = label[:w - 6]
        lines.append(BG + PC + '║ ' + color + marker + ' ' + l + ' ' * (w - 5 - len(l)) + PC + '║' + RST_)
    # Scroll hint row
    if n > visible:
        frac = (sel + 1) / n
        hint = f'  {sel+1}/{n}  '
        if start > 0: hint = '^ ' + hint
        else:         hint = '  ' + hint
        if end < n:   hint += ' v'
        else:         hint += '  '
        hpad = (w - 4 - len(hint)) // 2
        lines.append(BG + PC + '║ ' + DC + ' ' * hpad + hint + ' ' * (w - 5 - hpad - len(hint)) + PC + '║' + RST_)
    # Bottom border
    lines.append(BG + PC + '╚' + '═' * (w - 2) + '╝' + RST_)
    return lines


def name_box(plant_key, buf, tw, tr_center):
    """Input box for naming a plant."""
    w = 42
    PC = fg(86, 142, 68)
    AC = fg(188, 224, 178)
    BG = bg(28, 58, 38)
    RST_ = RST + bg(142, 198, 232)
    placeholder = pretty_plant_name(plant_key)
    shown = buf if buf else f'({placeholder})'
    shown = shown[:w - 6]
    ml = tr_center - 2
    mc = max(1, tw // 2 - w // 2)
    lines = []
    lines.append(f'\033[{ml};{mc}H' + BG + PC + '╔' + '═' * (w - 2) + '╗' + RST_)
    title = f' name your {placeholder[:20]} '
    pad = (w - 2 - len(title)) // 2
    lines.append(f'\033[{ml+1};{mc}H' + BG + PC + '║' + ' ' * pad + AC + title + PC + ' ' * (w - 2 - pad - len(title)) + '║' + RST_)
    lines.append(f'\033[{ml+2};{mc}H' + BG + PC + '╠' + '═' * (w - 2) + '╣' + RST_)
    cursor = '_' if int(time.time() * 2) % 2 == 0 else ' '
    input_line = f' > {shown}{cursor}'
    lines.append(f'\033[{ml+3};{mc}H' + BG + PC + '║' + AC + input_line + ' ' * (w - 2 - len(input_line)) + PC + '║' + RST_)
    lines.append(f'\033[{ml+4};{mc}H' + BG + PC + '║' + ' ' * (w - 2) + '║' + RST_)
    lines.append(f'\033[{ml+5};{mc}H' + BG + PC + '║' + fg(158, 184, 144) + '    [Enter] to confirm  [Esc] to cancel  ' + ' ' * (w - 2 - 42) + PC + '║' + RST_)
    lines.append(f'\033[{ml+6};{mc}H' + BG + PC + '╚' + '═' * (w - 2) + '╝' + RST_)
    return lines


def bubble_lines(text, tc, tr, accent=(188, 224, 178)):
    if not text: return []
    ac = fg(*accent)
    tc_c = fg(40, 60, 30)
    BG_ = bg(255, 255, 255)
    t = text[:36]
    w = len(t) + 4
    ml = max(1, tr - 2)
    mc = max(1, tc - w // 2)
    return [
        f'\033[{ml};{mc}H' + BG_ + ac + '╭' + '─' * (w - 2) + '╮' + RST,
        f'\033[{ml+1};{mc}H' + BG_ + ac + '│ ' + tc_c + t + ac + ' │' + RST,
        f'\033[{ml+2};{mc}H' + BG_ + ac + '╰' + '─' * (w - 2) + '╯' + RST,
    ]


class Menu:
    NONE = 'none'
    ADD = 'add'           # pick plant species
    NAME = 'name'         # name the new plant
    SLOT = 'slot'         # pick which slot to place in
    ACTION = 'action'     # water / move / rename / cancel
    MOVE = 'move'         # pick new slot for existing plant
    DISMISS = 'dismiss'   # pick plant to remove

    def __init__(self):
        self.mode = Menu.NONE
        self.sel = 0
        self.pending_key = None
        self.pending_name = ''
        self.pending_plant = None
        self.name_buf = ''
        self._plant_list = []  # cached for add menu
        self._slot_options = []

    def open_add(self, taken_slots, max_plants=5):
        if len(taken_slots) >= max_plants:
            return False
        self._plant_list = sorted(sprite_data.get_plant_names())
        self.mode = Menu.ADD
        self.sel = 0
        return True

    def open_name(self, key):
        self.pending_key = key
        self.name_buf = ''
        self.mode = Menu.NAME

    def open_slot(self, taken_slots):
        self._slot_options = [(s, SLOT_NAMES[s]) for s in ALL_SLOTS if s not in taken_slots]
        if not self._slot_options:
            return False
        self.mode = Menu.SLOT
        self.sel = 0
        return True

    def open_action(self, plant):
        self.pending_plant = plant
        self.mode = Menu.ACTION
        self.sel = 0

    def open_move(self, plant, taken_slots):
        self.pending_plant = plant
        # Can move to any slot not taken by another plant (plant's current slot is fine)
        self._slot_options = [(s, SLOT_NAMES[s]) for s in ALL_SLOTS if s not in taken_slots or s == plant.slot]
        if not self._slot_options:
            return False
        self.mode = Menu.MOVE
        self.sel = 0
        return True

    def open_dismiss(self, plants):
        if not plants:
            return False
        self._plant_list = [(p, p.name) for p in plants]
        self.mode = Menu.DISMISS
        self.sel = 0
        return True

    def close(self):
        self.mode = Menu.NONE
        self.pending_key = None
        self.pending_plant = None
        self.name_buf = ''
        self.sel = 0

    def add_opts(self):
        return [(k, pretty_plant_name(k)) for k in self._plant_list]

    def slot_opts(self):
        return self._slot_options

    def dismiss_opts(self):
        return [(p, name) for p, name in self._plant_list]


# ══════════════════════════════════════════════════════════════════════════════
# § 10  MAIN LOOP
# ══════════════════════════════════════════════════════════════════════════════

def get_sim_hour():
    """Current simulated hour (0-24) based on system clock."""
    now = datetime.now()
    return now.hour + now.minute / 60.0 + now.second / 3600.0


def beep():
    try:
        sys.stdout.write('\a')
        sys.stdout.flush()
    except Exception:
        pass


WATER_MSGS = [
    "drink some water!",
    "hydration check",
    "water break!",
    "time to sip",
]
STRETCH_MSGS = [
    "stand up & stretch!",
    "take a quick walking break",
    "stretch your legs",
]
FOOD_MSGS = [
    "time to eat a meal",
    "meal break!",
    "go get some food",
]
SNACK_MSGS = [
    "afternoon snack time",
    "snack break!",
    "grab a small snack",
]
SLEEP_GENTLE = [
    "getting late -- think about sleep",
    "bedtime is soon",
    "maybe start winding down",
]
SLEEP_FIRM = [
    "past midnight -- please sleep",
    "go to bed now",
    "it's really late, sleep",
]
SLEEP_URGENT = [
    "GO TO BED. NOW.",
    "SLEEP. PLEASE.",
    "this is absurd, sleep",
    "it is WAY too late",
]


class Reminders:
    """Track wellness reminder timers and decide when to surface a bubble."""
    def __init__(self):
        now = time.time()
        self._water_t   = now + 20 * 60       # every 20 min
        self._stretch_t = now + 60 * 60       # every 60 min
        self._food_t    = now + random.uniform(5, 15) * 60
        self._sleep_t   = now + random.uniform(1, 5) * 60
        self.msg = None
        self.msg_t = 0

    def update(self, now):
        # Clear old message
        if self.msg and now >= self.msg_t:
            self.msg = None
        if self.msg:
            return

        hour = get_sim_hour()
        picked = None

        if now >= self._water_t:
            picked = random.choice(WATER_MSGS)
            self._water_t = now + 20 * 60
        elif now >= self._stretch_t:
            picked = random.choice(STRETCH_MSGS)
            self._stretch_t = now + 60 * 60
        elif now >= self._food_t:
            h = int(hour)
            if h in (7, 8, 12, 13, 18, 19):
                picked = random.choice(FOOD_MSGS)
            elif 15 <= h <= 17:
                picked = random.choice(SNACK_MSGS)
            self._food_t = now + 45 * 60
        elif now >= self._sleep_t:
            t = hour
            if t >= 22.5 or t < 5:
                if t >= 1 and t < 5:
                    picked = random.choice(SLEEP_URGENT)
                    self._sleep_t = now + 5 * 60
                elif t >= 0 and t < 1:
                    picked = random.choice(SLEEP_FIRM)
                    self._sleep_t = now + 15 * 60
                else:  # 22.5 - 24
                    picked = random.choice(SLEEP_GENTLE)
                    self._sleep_t = now + 30 * 60
            else:
                self._sleep_t = now + 30 * 60

        if picked:
            self.msg = picked
            self.msg_t = now + 9.0
            beep()


def run_smoke_test():
    errors = []
    def check(cond, msg):
        if cond:
            print(f"  ok:   {msg}")
        else:
            errors.append(msg)
            print(f"  FAIL: {msg}")

    print("leafy-loft smoke test")
    cv = Canvas(32, 120)
    scene = Scene(cv)
    check(cv.pw == 120 and cv.ph == 64, f"Canvas 120x64 (got {cv.pw}x{cv.ph})")

    # Test sky at various hours
    for h in [0, 6, 12, 18, 22]:
        t, b, l = sky_at(h)
        check(0 <= l <= 1, f"sky at {h}h: light={l:.2f}")

    # Test plants
    names = sprite_data.get_plant_names()
    check(len(names) > 20, f"plants available: {len(names)}")

    # Create test plants in each slot
    slots = list(ALL_SLOTS)
    plants = []
    for i, slot in enumerate(slots):
        key = names[i % len(names)]
        p = Plant(key, f'test_{slot}', slot)
        plants.append(p)
        check(p.sprite is not None, f"plant {key}: sprite loads")

    # Render scene
    cv.fill()
    daylight = scene.draw(12.0)  # noon
    for p in plants:
        px, py = scene.slot_render_pos(p.slot, p.w, p.h)
        cv.blit(py, px, p.sprite)
    out = cv.render(start_row=1)
    check(len(out) > 500, f"scene render: {len(out)} bytes")

    # Test light at slots
    for slot in slots:
        light = scene.light_at_slot(slot, 1.0)
        check(0 <= light <= 1, f"light at {slot}: {light:.2f}")

    # Test update
    for p in plants:
        p.update(10.0, 0.5)
    check(all(p.thirst >= 0 for p in plants), "plants update without error")

    # Test water action
    p = plants[0]
    p.thirst = 50.0
    p.water()
    check(p.thirst == 0.0, "water resets thirst")

    # State save/load
    global STATE_FILE
    import tempfile
    old = STATE_FILE
    with tempfile.TemporaryDirectory() as td:
        STATE_FILE = Path(td) / 'state.json'
        save_state(plants)
        loaded = load_state()
        check(len(loaded) == len(plants), f"state save/load: {len(loaded)}/{len(plants)}")
        reset_state()
    STATE_FILE = old

    # Menu render
    m = Menu()
    m.open_add(set())
    opts = m.add_opts()
    check(len(opts) > 0, f"add menu: {len(opts)} options")
    mlines = menu_box('Add a plant', opts[:6], 0, 120)
    check(len(mlines) > 0, "menu box renders")

    print()
    if errors:
        print(f"SMOKE TEST FAILED ({len(errors)} errors)")
        for e in errors: print(f"  - {e}")
        sys.exit(1)
    print("SMOKE TEST PASSED")


def run():
    import argparse
    ap = argparse.ArgumentParser(description='leafy-loft -- terminal plant shelf')
    ap.add_argument('--height', type=int, default=0, help='Pane height override')
    ap.add_argument('--no-restore', action='store_true', help='Do not restore saved garden')
    ap.add_argument('--reset-state', action='store_true', help='Wipe saved state before launch')
    ap.add_argument('--smoke-test', action='store_true', help='Headless validation')
    args = ap.parse_args()

    if args.reset_state:
        reset_state()
    if args.smoke_test:
        run_smoke_test()
        return

    th, tw = term_size()
    ph = args.height if args.height > 0 else th
    ph = max(16, min(ph, 60))
    row_offset = max(0, th - ph)

    cv = Canvas(ph, tw)
    scene = Scene(cv)
    plants: list = []
    menu = Menu()
    reminders = Reminders()

    # Restore previously saved garden
    if not args.no_restore:
        for entry in load_state()[:5]:
            key = entry.get('key')
            name = entry.get('name') or pretty_plant_name(key or '')
            slot = entry.get('slot')
            if not key or not slot:
                continue
            if key not in sprite_data.get_plant_names():
                continue
            plants.append(Plant(key, name, slot))

    # Require a real TTY
    try:
        old_settings = termios.tcgetattr(sys.stdin)
    except termios.error:
        sys.stderr.write(
            "\nleafy-loft needs a real interactive terminal (TTY).\n"
            "Open a fresh terminal and run:\n"
            f"  python3 {os.path.abspath(__file__)}\n\n"
            "For headless validation: --smoke-test\n"
        )
        sys.exit(1)

    def cleanup(sig=None, _=None):
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        except Exception:
            pass
        sys.stdout.write(MOFF + SHOW + RST + '\033[2J\033[H')
        sys.stdout.flush()
        print(f'\n  {fg(188, 224, 178)}Your plants will miss you~ {RST}\n')
        os._exit(0)

    signal.signal(signal.SIGINT,  cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGWINCH, signal.SIG_IGN)

    try:
        tty.setraw(sys.stdin.fileno())
        sys.stdout.write(HIDE + MON)
        sys.stdout.flush()

        FPS = 10
        dt = 1.0 / FPS
        last_f = 0.0
        last_update = time.time()
        prev_count = len(plants)

        while True:
            now = time.time()

            # ── events ────────────────────────────────────────────
            for evt in read_events():
                t = evt['t']
                if t == 'quit': cleanup()
                elif t == 'esc': menu.close()
                elif t == 'key':
                    k = evt['k']
                    if menu.mode in (Menu.ADD, Menu.SLOT, Menu.ACTION, Menu.MOVE, Menu.DISMISS):
                        if menu.mode == Menu.ADD:
                            opts_n = len(menu._plant_list)
                        elif menu.mode == Menu.SLOT or menu.mode == Menu.MOVE:
                            opts_n = len(menu._slot_options)
                        elif menu.mode == Menu.ACTION:
                            opts_n = 4  # water / move / rename / cancel
                        else:  # DISMISS
                            opts_n = len(menu._plant_list)
                        if k == 'UP':   menu.sel = (menu.sel - 1) % max(1, opts_n)
                        elif k == 'DOWN': menu.sel = (menu.sel + 1) % max(1, opts_n)
                        elif k == 'ENTER':
                            if menu.mode == Menu.ADD:
                                key = menu._plant_list[menu.sel]
                                menu.open_name(key)
                            elif menu.mode == Menu.SLOT:
                                slot, _ = menu._slot_options[menu.sel]
                                name = menu.pending_name or pretty_plant_name(menu.pending_key)
                                p = Plant(menu.pending_key, name, slot)
                                plants.append(p)
                                save_state(plants)
                                menu.close()
                            elif menu.mode == Menu.ACTION:
                                act = ['water', 'move', 'rename', 'cancel'][menu.sel]
                                p = menu.pending_plant
                                if act == 'water':
                                    p.water()
                                    menu.close()
                                elif act == 'move':
                                    taken = {pp.slot for pp in plants}
                                    menu.open_move(p, taken)
                                elif act == 'rename':
                                    menu.pending_key = p.key
                                    menu.name_buf = p.name
                                    menu.mode = Menu.NAME
                                else:
                                    menu.close()
                            elif menu.mode == Menu.MOVE:
                                slot, _ = menu._slot_options[menu.sel]
                                menu.pending_plant.slot = slot
                                save_state(plants)
                                menu.close()
                            elif menu.mode == Menu.DISMISS:
                                p, _ = menu._plant_list[menu.sel]
                                if p in plants:
                                    plants.remove(p)
                                    save_state(plants)
                                menu.close()
                    elif menu.mode == Menu.NAME:
                        if k == 'ENTER':
                            name = menu.name_buf.strip() or pretty_plant_name(menu.pending_key)
                            # If we're renaming an existing plant
                            if menu.pending_plant:
                                menu.pending_plant.name = name
                                save_state(plants)
                                menu.close()
                            else:
                                menu.pending_name = name
                                taken = {p.slot for p in plants}
                                menu.open_slot(taken)
                        elif k == 'BACKSPACE':
                            menu.name_buf = menu.name_buf[:-1]
                        elif len(k) == 1 and k.isprintable() and len(menu.name_buf) < 20:
                            menu.name_buf += k

                elif t == 'click':
                    tc = evt['col']
                    tr = evt['row'] - row_offset
                    if tr < 1: continue

                    # Menu click handling
                    if menu.mode == Menu.ADD:
                        opts = menu.add_opts()
                        n = len(opts)
                        visible = min(n, MAX_MENU_ROWS)
                        start = 0 if n <= visible else max(0, min(menu.sel - visible // 2, n - visible))
                        # mlines length = 4 (border+title+sep+bottom) + visible + (1 if scroll hint)
                        has_hint = 1 if n > visible else 0
                        total_rows = 4 + visible + has_hint
                        ml = ph // 2 - total_rows // 2
                        mc = max(1, tw // 2 - 21)
                        rel = tr - ml - 3  # 3 = top border + title + sep
                        if 0 <= rel < visible and mc <= tc <= mc + 42:
                            key = menu._plant_list[start + rel]
                            menu.open_name(key)
                        elif tr < ml or tr > ml + total_rows + 1:
                            menu.close()
                        continue
                    if menu.mode == Menu.SLOT:
                        opts = menu._slot_options
                        ml = ph // 2 - (len(opts) + 6) // 2
                        mc = max(1, tw // 2 - 21)
                        rel = tr - ml - 3
                        if 0 <= rel < len(opts) and mc <= tc <= mc + 42:
                            slot, _ = opts[rel]
                            name = menu.pending_name or pretty_plant_name(menu.pending_key)
                            plants.append(Plant(menu.pending_key, name, slot))
                            save_state(plants)
                            menu.close()
                        elif tr < ml or tr > ml + len(opts) + 5:
                            menu.close()
                        continue
                    if menu.mode == Menu.ACTION:
                        ml = ph // 2 - 5
                        mc = max(1, tw // 2 - 21)
                        rel = tr - ml - 3
                        if 0 <= rel < 4 and mc <= tc <= mc + 42:
                            act = ['water', 'move', 'rename', 'cancel'][rel]
                            p = menu.pending_plant
                            if act == 'water': p.water(); menu.close()
                            elif act == 'move':
                                menu.open_move(p, {pp.slot for pp in plants})
                            elif act == 'rename':
                                menu.pending_key = p.key
                                menu.name_buf = p.name
                                menu.mode = Menu.NAME
                            else: menu.close()
                        elif tr < ml or tr > ml + 10:
                            menu.close()
                        continue
                    if menu.mode == Menu.MOVE:
                        opts = menu._slot_options
                        ml = ph // 2 - (len(opts) + 6) // 2
                        mc = max(1, tw // 2 - 21)
                        rel = tr - ml - 3
                        if 0 <= rel < len(opts) and mc <= tc <= mc + 42:
                            slot, _ = opts[rel]
                            menu.pending_plant.slot = slot
                            save_state(plants)
                            menu.close()
                        elif tr < ml or tr > ml + len(opts) + 5:
                            menu.close()
                        continue
                    if menu.mode == Menu.DISMISS:
                        opts = menu._plant_list
                        ml = ph // 2 - (len(opts) + 6) // 2
                        mc = max(1, tw // 2 - 21)
                        rel = tr - ml - 3
                        if 0 <= rel < len(opts) and mc <= tc <= mc + 42:
                            p, _ = opts[rel]
                            if p in plants:
                                plants.remove(p)
                                save_state(plants)
                            menu.close()
                        elif tr < ml or tr > ml + len(opts) + 5:
                            menu.close()
                        continue
                    if menu.mode == Menu.NAME:
                        menu.close(); continue

                    # Scene clicks
                    if scene.in_plus(tc, tr):
                        if len(plants) < 5:
                            menu.open_add({p.slot for p in plants})
                        continue
                    if scene.in_save(tc, tr):
                        save_state(plants)
                        if plants and not plants[0].sad_bubble:
                            plants[0].sad_bubble = "saved!"
                            plants[0]._bub_t = time.time() + 2.0
                        continue
                    if scene.in_trash(tc, tr):
                        if plants:
                            menu.open_dismiss(plants)
                        continue
                    # Click on a plant?
                    for p in plants:
                        px, py = scene.slot_render_pos(p.slot, p.w, p.h)
                        if px <= tc - 1 < px + p.w and py // 2 <= tr - 1 < (py + p.h + 1) // 2:
                            menu.open_action(p)
                            break

            # ── update plants ────────────────────────────────────
            upd_dt = now - last_update
            last_update = now
            hour = get_sim_hour()
            top_sky, bot_sky, daylight = sky_at(hour)
            for p in plants:
                light = scene.light_at_slot(p.slot, daylight)
                p.update(upd_dt, light)
            if len(plants) != prev_count:
                save_state(plants)
                prev_count = len(plants)

            # ── update reminders ─────────────────────────────────
            reminders.update(now)

            # ── render ───────────────────────────────────────────
            if now - last_f < dt:
                time.sleep(0.01)
                continue
            last_f = now

            cv.fill()
            daylight_now = scene.draw(hour)

            # Draw plants
            for p in plants:
                px, py = scene.slot_render_pos(p.slot, p.w, p.h)
                sp = p.sprite
                if sp:
                    # Tint if unhappy
                    tint = p.status_color()
                    if tint:
                        # Darken the sprite pixels
                        tinted = [[tint if c is not None else None for c in row] for row in sp]
                        # But only tint every 3rd pixel so the plant is still recognizable
                        tinted_full = []
                        for dr, row in enumerate(sp):
                            new_row = []
                            for dc, c in enumerate(row):
                                if c is None:
                                    new_row.append(None)
                                elif (dr + dc) % 3 == 0:
                                    new_row.append(tint)
                                else:
                                    new_row.append(c)
                            tinted_full.append(new_row)
                        cv.blit(py, px, tinted_full)
                    else:
                        cv.blit(py, px, sp)

            out = [cv.render(start_row=1 + row_offset)]

            # Speech bubbles
            for p in plants:
                if p.sad_bubble:
                    px, py = scene.slot_render_pos(p.slot, p.w, p.h)
                    tc = px + p.w // 2
                    tr = py // 2 + row_offset
                    out.extend(bubble_lines(p.sad_bubble, tc, tr))

            # Thirst warning bubbles
            for p in plants:
                if p.thirst > 70 and not p.sad_bubble:
                    px, py = scene.slot_render_pos(p.slot, p.w, p.h)
                    tc = px + p.w // 2
                    tr = py // 2 + row_offset
                    msg = "thirsty..." if p.thirst < 90 else "dying..."
                    out.extend(bubble_lines(msg, tc, tr, (200, 160, 80)))

            # Wellness reminder bubble (water / stretch / food / sleep)
            if reminders.msg:
                if plants:
                    # Show above a random plant so it feels in-scene
                    p = plants[hash(reminders.msg) % len(plants)]
                    px, py = scene.slot_render_pos(p.slot, p.w, p.h)
                    tc = px + p.w // 2
                    tr = py // 2 + row_offset
                else:
                    # Banner at top-center if there are no plants yet
                    tc = tw // 2
                    tr = 3 + row_offset
                out.extend(bubble_lines(reminders.msg, tc, tr, (250, 188, 120)))

            # Menu overlays
            if menu.mode == Menu.ADD:
                opts = menu.add_opts()
                mlines = menu_box('Add a plant', opts, menu.sel, tw)
                ml = ph // 2 - len(mlines) // 2 + row_offset
                mc = max(1, tw // 2 - 21)
                for i, ln in enumerate(mlines):
                    out.append(f'\033[{ml+i};{mc}H{ln}')
            elif menu.mode == Menu.SLOT:
                mlines = menu_box('Where should it go?', menu._slot_options, menu.sel, tw)
                ml = ph // 2 - len(mlines) // 2 + row_offset
                mc = max(1, tw // 2 - 21)
                for i, ln in enumerate(mlines):
                    out.append(f'\033[{ml+i};{mc}H{ln}')
            elif menu.mode == Menu.ACTION:
                p = menu.pending_plant
                thirst = int(p.thirst)
                light_need = p.light_need
                title = f'{p.name}  (thirst: {thirst}%  light: {light_need})'
                action_opts = [
                    ('water',  'Water'),
                    ('move',   'Move to another spot'),
                    ('rename', 'Rename'),
                    ('cancel', 'Cancel'),
                ]
                mlines = menu_box(title, action_opts, menu.sel, tw, width=48)
                ml = ph // 2 - len(mlines) // 2 + row_offset
                mc = max(1, tw // 2 - 24)
                for i, ln in enumerate(mlines):
                    out.append(f'\033[{ml+i};{mc}H{ln}')
            elif menu.mode == Menu.MOVE:
                mlines = menu_box(f'Move {menu.pending_plant.name} to...', menu._slot_options, menu.sel, tw)
                ml = ph // 2 - len(mlines) // 2 + row_offset
                mc = max(1, tw // 2 - 21)
                for i, ln in enumerate(mlines):
                    out.append(f'\033[{ml+i};{mc}H{ln}')
            elif menu.mode == Menu.DISMISS:
                opts = [(None, name) for _, name in menu._plant_list]
                mlines = menu_box('Remove a plant', opts, menu.sel, tw)
                ml = ph // 2 - len(mlines) // 2 + row_offset
                mc = max(1, tw // 2 - 21)
                for i, ln in enumerate(mlines):
                    out.append(f'\033[{ml+i};{mc}H{ln}')
            elif menu.mode == Menu.NAME:
                nlines = name_box(menu.pending_key or '', menu.name_buf, tw, ph // 2 + row_offset)
                out.extend(nlines)

            # Status bar
            hint = fg(60, 100, 70)
            hl   = fg(120, 180, 110)
            time_str = f'{int(hour):02d}:{int((hour % 1) * 60):02d}'
            out.append(f'\033[{ph + row_offset};1H{hint}  {hl}[+]{hint}=add  |  {hl}[save]{hint}  |  {hl}[del]{hint}  |  {hl}click plant{hint}=water  |  {hl}{time_str}{hint}  |  {hl}{len(plants)}/5 plants{RST}')

            sys.stdout.write(''.join(out))
            sys.stdout.flush()

    except Exception:
        cleanup()
        raise


if __name__ == '__main__':
    run()
