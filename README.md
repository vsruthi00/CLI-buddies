# CLI Buddies

Your terminal doesn't have to be lonely. CLI Buddies are pixel art companions that live in your terminal while you code -- wandering around, knocking things over, reminding you to hydrate, and generally being little gremlins about it. Cats first. More creatures coming.

Pure Python. One file per buddy. Zero dependencies. No pip installs.

---

## Quick Start (5 minutes)

### Step 1: Check if you have Python

Open your terminal and type:

```bash
python3 --version
```

If you see a version number (3.8 or higher), you're good. If not, download Python from [python.org](https://python.org/downloads).

### Step 2: Download this repo

```bash
git clone https://github.com/vsruthi00/CLI-buddies.git
cd CLI-buddies
```

Or click the green **Code** button on this page and choose **Download ZIP**, then unzip it.

### Step 3: Run cozy-cats

```bash
python3 cozy-cats/cozy-cats.py --height 32
```

A little room will appear with furniture, cats, and a bell. Click the bell to summon your first cat.

**To quit:** press `Ctrl+C`

That's it. You're done. Everything below is optional but recommended.

---

## Running Alongside Your Code (the good part)

The real magic is having cats in a pane at the bottom of your terminal while you work in the top. For this you need **tmux**.

### What is tmux?

tmux is a terminal multiplexer. It lets you split one terminal window into multiple panes. Think of it like having two terminals stacked on top of each other in the same window. You code in the top pane, cats live in the bottom pane.

```
+----------------------------------+
|  your code / terminal            |
|  (you work here normally)        |
|                                  |
+----------------------------------+
|  cozy-cats pane                  |
|  (cats wander around here)       |
+----------------------------------+
```

You click on whichever pane you want to use. Click the top pane to type commands. Click the bottom pane to interact with your cats.

### Install tmux

**macOS (using Homebrew):**
```bash
brew install tmux
```

If you don't have Homebrew, install it first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Then run `brew install tmux`.

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt install tmux
```

**Fedora:**
```bash
sudo dnf install tmux
```

**Windows (WSL):**
```bash
sudo apt install tmux
```

**Verify it installed:**
```bash
tmux -V
```

You should see something like `tmux 3.4`.

### Launch cozy-cats with the launcher script

Once tmux is installed, use the included launcher:

```bash
bash cozy-cats/launch.sh
```

This does everything for you:
- Starts a tmux session (or uses your existing one)
- Creates a 32-row pane at the bottom
- Launches cozy-cats inside it
- Enables mouse mode so you can click between panes

You'll see your normal terminal on top and the cat room on the bottom. Click the bottom pane to interact with cats, click the top pane to go back to coding.

**Custom height:**
```bash
bash cozy-cats/launch.sh 24    # shorter pane
bash cozy-cats/launch.sh 36    # taller pane
```

### Launch manually (if you prefer)

If you're already inside tmux:
```bash
tmux split-window -v -l 32 'python3 /full/path/to/CLI-buddies/cozy-cats/cozy-cats.py --height 32'
```

Or just open a second terminal window and run:
```bash
python3 cozy-cats/cozy-cats.py
```

### Closing

- **Quit the cats:** press `Ctrl+C` in the cat pane
- **Close the tmux pane:** type `exit` in the pane after the cats quit
- **Kill the whole tmux session:** `tmux kill-session -t cozy-cats`
- **Detach from tmux (leave it running in background):** press `Ctrl+B` then `D`

---

## Requirements

- **Python 3.8+** (already on most Macs and Linux machines)
- **A modern terminal** with true-color support: iTerm2, Kitty, Alacritty, WezTerm, Terminal.app (macOS), or a recent GNOME Terminal all work
- **Mouse support** enabled in your terminal (most are by default)
- **tmux** for the split-pane setup (optional but recommended)

No pip installs. No virtual environments. No package managers. Just Python and a terminal.

---

---

# Cozy Cats

A colony of eight pixel art cats that wander around a cozy room while you work. They have distinct personalities, opinions about food, and a lot to say about your hydration habits.

## The Cats

You start with an empty room. Click the bell icon (top right) to summon a cat. Pick which one you want, give it a name (or keep the default), and watch it wander in. Up to four cats on screen at once.

| Name | Personality | Food preference |
|------|-------------|-----------------|
| Seraphine | High-maintenance princess. Tolerates almost nothing. | Fish only |
| Hazel | Sweet and shy. May flee if overwhelmed. | Wet food |
| Kulfi | Chaos goblin. Knocks things over on purpose. | Anything |
| Nyx | Void cat. Disappears into shadow, leaving only glowing eyes. | Wet food |
| Arwen | Aloof and dry. Gives attention on her own terms. | Dry food |
| Saffron | Gentle chirper. Trills at you unprompted. | Wet food |
| Mochi | Extremely needy. Begs constantly. Sits on your keyboard. | Wet food |
| Oreo | Chaos goblin #2. Always hungry, always begging, occasionally destructive. | Anything |

## Controls

- **Click the bell** (top right) to summon a cat
- **Click the save icon** (top right) to save your current cats so they reappear next time
- **Click the trash icon** (top right) to send a cat away
- **Click any cat** to open the interaction menu (feed, pet, play, cuddle)
- **Click a knocked-over plant** to fix it (Kulfi and Oreo knock them over)
- **Ctrl+C** to quit

## Reminders

Your cats remind you to take care of yourself:

| Reminder | Frequency | When |
|----------|-----------|------|
| Drink water | Every 20 minutes | Always |
| Stretch / take a break | Every 60 minutes | Always |
| Eat a meal | At mealtimes | 7-8am, 12-1pm, 6-7pm |
| Have a snack | Afternoon | 3-5pm |
| Motivational messages | Varies by cat | Throughout the day |

Each cat delivers reminders in their own voice. Mochi will be genuinely worried about your hydration. Seraphine will make it sound like your problem. Kulfi will just shout.

## Features

- **Pixel art room** with desk, chair, cat tower, cat bed, shelf, window, and plants
- **Cat AI** -- cats wander, sit, loaf, sleep, claim furniture spots, and do cat things on their own
- **Personality-driven interactions** -- each cat reacts differently to food, pets, and cuddles
- **Kulfi and Oreo knock over plants** -- click to fix them
- **Nyx disappears** into shadow and reappears when she feels like it
- **Hazel may flee** if you pet her too much -- she'll come back if you summon her again
- **Mochi sits on your keyboard** (a dedicated animation spot just for her)
- **Heart popup** appears when you pet or cuddle a cat
- **Colony saves** -- click save to preserve your cats between sessions
- **Config file** at `~/.config/cozy-cats/config.json` for customizing reminder intervals, messages, and scene layout

## CLI Flags

```bash
python3 cozy-cats/cozy-cats.py --height 32      # set pane height
python3 cozy-cats/cozy-cats.py --no-sound        # disable terminal bell on reminders
python3 cozy-cats/cozy-cats.py --no-restore      # don't reload saved cats
python3 cozy-cats/cozy-cats.py --reset-state     # wipe saved cats and start fresh
python3 cozy-cats/cozy-cats.py --smoke-test      # headless validation (no terminal needed)
```

## How It Works

Two Python files, zero dependencies. `cozy-cats.py` handles rendering, input, cat AI, and the main loop. `sprite_data.py` contains pre-converted pixel art sprites (base64-encoded RGBA data decoded at runtime using only the standard library).

The renderer uses ANSI escape codes and Unicode half-block characters to draw pixel art directly in your terminal, two pixels per terminal row. Mouse support uses the SGR mouse protocol built into modern terminals.

## Troubleshooting

**Terminal looks broken after a crash:**
```bash
printf '\033[?1000l\033[?1006l\033[?25h'; stty sane
```

**Colors look washed out:**
Make sure your terminal supports true color. Check with:
```bash
echo $COLORTERM
```
It should say `truecolor` or `24bit`.

**Cats are too small / scene doesn't fit:**
Try a taller pane: `bash cozy-cats/launch.sh 36`

**Can't click on cats in tmux:**
Make sure tmux mouse mode is on. The launcher does this automatically, but you can also run:
```bash
tmux set-option -g mouse on
```

---

*More buddies coming. Suggestions welcome.*
