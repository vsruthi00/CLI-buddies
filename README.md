# CLI Buddies

Your terminal doesn't have to be lonely. CLI Buddies are pixel art companions that live in your terminal while you code. Cats. Plants. More coming.

Pure Python. One file per buddy. Zero dependencies. No pip installs.

---

## Quick Start (5 minutes)

### Step 1: Check if you have Python

```bash
python3 --version
```

You need Python 3.8 or higher. If you don't have it, grab it from [python.org](https://python.org/downloads).

### Step 2: Download this repo

```bash
git clone https://github.com/vsruthi00/CLI-buddies.git
cd CLI-buddies
```

Or click the green **Code** button and choose **Download ZIP**, then unzip it.

### Step 3: Pick a buddy

```bash
# Cats
python3 cozy-cats/cozy-cats.py --height 32

# Plants
python3 leafy-loft/leafy-loft.py --height 32
```

**To quit any buddy:** press `Ctrl+C`.

That's it. Everything below is optional but recommended.

---

## Running Alongside Your Code (the good part)

The magic is having a buddy docked in a pane at the bottom of your terminal while you work in the top. For this you need **tmux**.

### What is tmux?

tmux is a terminal multiplexer -- it lets you split one terminal window into multiple panes. You code in the top pane, buddies live in the bottom pane.

```
+----------------------------------+
|  your code / terminal            |
|  (you work here normally)        |
|                                  |
+----------------------------------+
|  buddy pane                      |
|  (cats / plants live here)       |
+----------------------------------+
```

Click whichever pane you want to use. Click the top pane to type commands. Click the bottom pane to interact with your buddy.

### Install tmux

**macOS (with Homebrew):**
```bash
brew install tmux
```

If you don't have Homebrew, install it first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Ubuntu / Debian / WSL:**
```bash
sudo apt update && sudo apt install tmux
```

**Fedora:**
```bash
sudo dnf install tmux
```

**Verify it installed:**
```bash
tmux -V
```

### Launch a buddy with the launcher script

Each buddy has its own launcher that sets up tmux for you:

```bash
# Cats in a bottom pane
bash cozy-cats/launch.sh

# Plants in a bottom pane
bash leafy-loft/launch.sh
```

The launcher:
- Starts a tmux session (or uses your existing one)
- Creates a 32-row pane at the bottom
- Launches the buddy inside it
- Enables mouse mode so you can click between panes

**Custom height:**
```bash
bash cozy-cats/launch.sh 24    # shorter
bash leafy-loft/launch.sh 36   # taller
```

### Closing

- **Quit the buddy:** press `Ctrl+C` in the buddy pane
- **Close the tmux pane:** type `exit` after the buddy quits
- **Kill the tmux session:** `tmux kill-session -t cozy-cats` or `tmux kill-session -t leafy-loft`
- **Detach from tmux (leave it running):** press `Ctrl+B` then `D`

---

## Requirements

- **Python 3.8+** (already on most Macs and Linux machines)
- **A modern terminal** with true-color support: iTerm2, Kitty, Alacritty, WezTerm, Terminal.app (macOS), or a recent GNOME Terminal
- **Mouse support** enabled in your terminal (most are on by default)
- **tmux** (optional but recommended for the split-pane setup)

No pip installs. No virtual environments. Just Python and a terminal.

---
---

# Cozy Cats

A colony of eight pixel art cats that wander around a cozy room while you work. They have distinct personalities, opinions about food, and a lot to say about your hydration habits.

## The Cats

You start with an empty room. Click the bell icon (top right) to summon a cat, pick which one, give it a name, and watch it wander in. Up to four cats at once.

| Name | Personality | Food | Quirk |
|------|-------------|------|-------|
| Seraphine | High-maintenance princess. | Fish only | Refuses dry and wet |
| Hazel | Sweet and shy. | Wet food | May flee if petted too much |
| Kulfi | Chaos goblin. | Anything | Knocks plants over |
| Nyx | Void cat. | Wet food | Disappears into shadow |
| Arwen | Aloof and dry. | Dry food | Attention on her own terms |
| Saffron | Gentle chirper. | Wet food | Trills at random |
| Mochi | Extremely needy. | Wet food | Sits on your keyboard |
| Oreo | Chaos goblin #2. | Anything | Always hungry, also destructive |

## Controls

- **Click the bell** (top right) to summon a cat
- **Click the save icon** to save your current cats so they come back next time
- **Click the trash icon** to send a cat away
- **Click any cat** to open the action menu (dry food, wet food, fish, yarn, toy, pet, cuddle)
- **Click a knocked-over plant** to fix it
- **Ctrl+C** to quit

## Wellness Reminders

Your cats remind you to take care of yourself in their own voice:

| Reminder | Frequency | When |
|----------|-----------|------|
| Drink water | Every 20 minutes | All day |
| Stretch / take a break | Every 60 minutes | All day |
| Eat a meal | At meal times | 7-8am, 12-1pm, 6-7pm |
| Have a snack | Afternoon | 3-5pm |
| Go to sleep (gentle) | Every 30 minutes | 10:30pm - midnight |
| Go to sleep (firm) | Every 15 minutes | midnight - 1am |
| Go to sleep (aggressive) | Every 5 minutes | After 1am |

Sleep reminders escalate -- Mochi gets genuinely worried by 2am, Seraphine will threaten to sit on your face, Nyx invokes the void.

## CLI Flags

```bash
python3 cozy-cats/cozy-cats.py --height 32      # set pane height
python3 cozy-cats/cozy-cats.py --no-sound       # disable terminal bell
python3 cozy-cats/cozy-cats.py --no-restore     # don't reload saved cats
python3 cozy-cats/cozy-cats.py --reset-state    # wipe saved cats
python3 cozy-cats/cozy-cats.py --smoke-test     # headless validation
```

---
---

# Leafy Loft

A sunny pixel-art plant room where you pick 4-5 plants, water them, move them around, and keep them alive. Plants have different watering needs, different light preferences, and react to your care.

## The Room

- **Light blue sky-wall** that shifts color from dawn through day to dusk to night based on your system clock
- **Window** above the stool (plants closer to the window get more light)
- **Wall shelf** with pre-drawn decorations (just for atmosphere)
- **Stool** on the floor (one plant slot sits right on top)
- **Floor bookshelf** (decorative)

## Plant Slots

There are 5 spots where you can put plants:

1. Floor, left of the stool
2. On top of the stool
3. Floor, right of the stool (slot 1)
4. Floor, right of the stool (slot 2)
5. Floor, right of the stool (slot 3)

## Controls

Three icons in the top-right corner:

| Icon | What it does |
|------|--------------|
| Grey plus (+) | Open the add-plant menu (57 species to choose from) |
| Floppy disk | Save your current garden so it reappears next launch |
| Trash can | Remove a plant |

In the scene:

- **Click a plant** to open its menu: water, move to a different slot, rename, or cancel
- **Arrow keys** scroll the plant menu (57 species, shown 10 at a time)
- **Enter** to confirm, **Esc** to cancel
- **Ctrl+C** to quit

## Plants

57 plants to choose from. Each has its own watering schedule and light needs:

| Type | Water needed | Light |
|------|--------------|-------|
| Cactus, succulents, jade, ZZ plant | Every 3-4 hours | High (direct sun) |
| Rubber plant, monstera, money tree, pothos | Every 45-90 minutes | Medium |
| Parlor palm, calathea, peace lily, prayer plant, orchid | Every 20-45 minutes | Low (shade) |
| All flowers (sunflower, rose, tulip, etc.) | Every 10-20 minutes | Medium |

Plants that aren't getting enough water **wilt** -- they turn yellowish at 50% thirst, brownish at 80%, show "thirsty..." at 70%, and "dying..." at 90%.

Plants that aren't getting enough light pale out to a duller green.

Flowers come without pots. When you add one, a terracotta pot is drawn under it automatically.

## Day / Night Cycle

The scene follows the real-world clock:

| Time | Sky |
|------|-----|
| 5:00 - 8:00 | Dawn fade (orange-peach into light blue) |
| 8:00 - 17:00 | Bright sky blue (full light) |
| 17:00 - 20:00 | Dusk fade (rose into dusky blue) |
| 20:00 - 5:00 | Night (no light -- plants stop photosynthesizing) |

At night, plants don't get any light regardless of slot, so their light meter drifts toward the "not enough" side.

## Wellness Reminders

Leafy Loft has the same wellness reminders as Cozy Cats:

| Reminder | Frequency | When |
|----------|-----------|------|
| Drink water | Every 20 minutes | All day |
| Stretch / take a break | Every 60 minutes | All day |
| Eat a meal | At meal times | 7-8am, 12-1pm, 6-7pm |
| Have a snack | Afternoon | 3-5pm |
| Go to sleep (gentle) | Every 30 minutes | 10:30pm - midnight |
| Go to sleep (firm) | Every 15 minutes | midnight - 1am |
| Go to sleep (aggressive) | Every 5 minutes | After 1am |

Reminders appear as a peach-colored bubble above a plant (or as a banner at the top if you have no plants yet), and the terminal bell rings.

## CLI Flags

```bash
python3 leafy-loft/leafy-loft.py --height 32       # set pane height
python3 leafy-loft/leafy-loft.py --no-restore      # don't reload saved garden
python3 leafy-loft/leafy-loft.py --reset-state     # wipe saved garden
python3 leafy-loft/leafy-loft.py --smoke-test      # headless validation
```

---

## Troubleshooting

**Terminal looks broken after a crash:**
```bash
printf '\033[?1000l\033[?1006l\033[?25h'; stty sane
```

**Colors look washed out:**
Make sure your terminal supports true color:
```bash
echo $COLORTERM
```
It should say `truecolor` or `24bit`.

**Scene doesn't fit / looks cramped:**
Use a taller pane: `bash cozy-cats/launch.sh 36` or `bash leafy-loft/launch.sh 36`

**Can't click inside tmux:**
Enable tmux mouse mode (the launcher does this, but you can run it manually):
```bash
tmux set-option -g mouse on
```

**tmux command not found:**
Install tmux first -- see the Install tmux section above.

**Nothing happens when I click icons:**
Click the buddy's pane first to give it focus, then click the icon.

---

*More buddies coming.*
