# CLI Buddies

Your terminal doesn't have to be lonely. CLI Buddies are pixel art companions that live in your terminal while you code -- wandering around, knocking things over, reminding you to hydrate, eat, stretch, and sleep, and generally being little gremlins about it. Cats first. More creatures coming.

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

A little room will appear with furniture, plants, and a bell. Click the bell to summon your first cat.

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
python3 cozy-cats/cozy-cats.py --height 32
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

A colony of eight pixel art cats that wander around a cozy room while you work. They have distinct personalities, opinions about food, and a lot to say about your hydration habits, meal times, stretch breaks, and bedtime.

## The Cats

You start with an empty room. Click the bell icon (top right) to summon a cat. Pick which one you want, give it a name (or keep the default), and watch it wander in. Up to four cats on screen at once.

| Name | Personality | Food preference | Special behavior |
|------|-------------|-----------------|------------------|
| Seraphine | High-maintenance princess. Tolerates almost nothing. | Fish only | Refuses dry and wet food |
| Hazel | Sweet and shy. Easily overwhelmed. | Wet food | May flee if you pet her too much |
| Kulfi | Chaos goblin. Loud. Affectionate. Destructive. | Anything | Knocks over plants when she walks past them |
| Nyx | Void cat. Speaks from the shadows. | Wet food | Randomly disappears, leaving only her glowing eyes |
| Arwen | Aloof and sassy. Dignified. | Dry food | Gives attention strictly on her own terms |
| Saffron | Gentle chirper. Full-body happiness. | Wet food | Trills and chirps at random intervals |
| Mochi | Extremely needy. Constantly worried about you. | Wet food | Sits on your keyboard when she gets the chance |
| Oreo | Chaos goblin #2. Always hungry. Also destructive. | Anything | Begs AND knocks plants over |

## The Room

The scene includes:

- **Cat tower** on the left (cats can sit on the top or middle perch)
- **Cat bed** on the floor (cats curl up inside it to sleep)
- **Desk and chair** where cats can loaf on the desk surface
- **Shelf** hanging on the wall (cats can sit there too)
- **Window** on the wall when the pane is wide enough
- **Plants** (orchid and parlor palm) on the floor -- knockable by Kulfi and Oreo
- **Lavender wall** gradient and warm brown wood floor

## Controls

All interaction is via mouse click. The top-right corner of the scene has three icons:

| Icon | What it does |
|------|--------------|
| Bell | Opens the summon menu. Pick a cat to bring in (up to 4). |
| Save | Saves your current colony so the same cats come back next launch. |
| Trash | Opens the dismiss menu. Pick a cat to send away. |

In the scene:

- **Click any cat** to open the interaction menu (dry food, wet food, fish, yarn, feather toy, pet, cuddle)
- **Click a knocked-over plant** to fix it
- **Ctrl+C** to quit

Keyboard shortcuts in menus: arrow keys navigate, Enter selects, Esc closes.

## Wellness Reminders

Your cats remind you to take care of yourself throughout the day. Each cat delivers reminders in their own voice -- Mochi will be genuinely worried, Seraphine will make it sound like your problem, Kulfi will just shout.

| Reminder | Frequency | When it fires |
|----------|-----------|---------------|
| Drink water | Every 20 minutes | All day |
| Stretch / take a break | Every 60 minutes | All day |
| Eat a meal | Around meal times | 7-8am, 12-1pm, 6-7pm |
| Have a snack | Afternoon | 3-5pm |
| Motivational nudges | Varies by cat | Throughout the day |
| **Go to sleep (gentle)** | Every 30 minutes | 10:30pm to midnight |
| **Go to sleep (firm)** | Every 15 minutes | Midnight to 1am |
| **Go to sleep (aggressive)** | Every 5 minutes | After 1am |

The sleep reminders escalate. At 10:30pm, Mochi politely suggests bedtime. By 2am, she is aggressively begging. Seraphine will threaten to sit on your face. Nyx will invoke the void.

## Features

### Cat AI
- Cats wander around, sit, loaf, sleep, and claim furniture rest spots on their own
- State machine handles idle, walking, sleeping, loafing, and hidden (Nyx only)
- Cats walk at a calm pace (about 4 pixels per second)
- Each cat has a unique voice and 6-8 message categories per personality

### Personality-driven interactions
- Every cat reacts differently to food, pets, cuddles, and toys
- Seraphine refuses anything but fish
- Hazel may flee if overwhelmed and needs to be re-summoned
- Kulfi and Oreo are destructive and loud
- Nyx is haunting and sparse
- Saffron chirps randomly

### Physics-based plant knocking
- Kulfi and Oreo only knock plants over when they actually walk near them
- Click a knocked plant to fix it
- Other cats will never knock plants over

### Rest spot system
- Six rest spots: cat bed, desk surface, tower top, tower middle, shelf, Mochi-only keyboard
- Cats walk to their chosen spot and settle in
- Cats sit inside the bed, not floating above it
- Mochi has her own dedicated keyboard spot that only appears when she claims it

### Heart popup
- A heart appears above any cat you pet or cuddle for 2 seconds
- Does not fire when Hazel flees

### Colony persistence
- Click the save icon to write your current colony to disk
- Next launch automatically restores the same cats by default
- Use `--no-restore` to skip the restore, or `--reset-state` to wipe saved cats

### Dismiss cat
- Click the trash icon to open a menu listing your active cats
- Pick one to send away (useful if you want to change the lineup)

### Nyx void mechanic
- Nyx randomly fades into the shadows
- While hidden, only her two glowing eyes are visible
- She reappears on her own schedule

### Mochi keyboard gag
- Mochi occasionally climbs onto a little pixel keyboard that appears in the scene
- The keyboard only renders while she is sitting on it
- Other cats cannot claim this spot

### Sound
- Terminal bell rings on wellness reminders and cat summons
- Disable with `--no-sound` or in the config file

### Config file
- Located at `~/.config/cozy-cats/config.json`
- Override reminder intervals per cat
- Append custom messages to any category (additive, won't replace the defaults)
- Override scene layout positions (bell, tower, bed, plants, etc.)
- Set custom FPS if you see flicker

### State file
- Located at `~/.config/cozy-cats/state.json`
- Stores the current colony (cat keys + names)
- Auto-updates on summon and dismiss

### Auto-sizing
- Scene adapts to your pane size on launch
- Use `--height N` to override
- Below 24 rows, sprites automatically downscale to stay readable

## CLI Flags

```bash
python3 cozy-cats/cozy-cats.py --height 32      # set pane height
python3 cozy-cats/cozy-cats.py --no-sound       # disable terminal bell on reminders
python3 cozy-cats/cozy-cats.py --no-restore     # don't reload saved cats
python3 cozy-cats/cozy-cats.py --reset-state    # wipe saved cats and start fresh
python3 cozy-cats/cozy-cats.py --no-kitty       # force half-block rendering in Kitty terminal
python3 cozy-cats/cozy-cats.py --smoke-test     # headless validation (no terminal needed)
```

## How It Works

Two Python files, zero runtime dependencies:

- **`cozy-cats.py`** handles rendering, input, cat AI, menus, state machine, reminders, and the main loop.
- **`sprite_data.py`** contains pre-converted pixel art sprites as base64-encoded RGBA data. Decoded at runtime using only the standard library.

The renderer uses ANSI escape codes and Unicode half-block characters to draw pixel art directly in your terminal, two pixels per terminal row. Mouse support uses the SGR mouse protocol built into modern terminals.

If you run inside Kitty terminal (outside of tmux), cozy-cats will automatically use the Kitty graphics protocol for a sharper image. Inside tmux or any other terminal, it falls back to half-block rendering which works everywhere.

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

**tmux command not found:**
Install tmux first -- see the Install tmux section above.

**Nothing happens when I click the bell:**
Make sure you clicked the cozy-cats pane first (to give it focus) and that your terminal has mouse support enabled.

---

*More buddies coming. Suggestions welcome.*
