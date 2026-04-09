# CLI-buddies
Your terminal doesn't have to be lonely. CLI Buddies are pixel art companions that live in a tmux pane while you code, wandering around, knocking things over, reminding you to hydrate, and generally being little gremlins about it. Cats first. More creatures coming. Pure Python stdlib, one file per buddy, zero dependencies.


---

## Getting started

You don't need to be a programmer to run these. You just need Python, which is already installed on most computers.

**Check if you have Python:**
```bash
python3 --version
```
If you see a version number (3.8 or higher), you're good. If not, download it from [python.org](https://python.org).

**Download a buddy:**

Click on the file you want in this repo, then click the **Download raw file** button (top right of the file view). Save it somewhere you'll remember, like your home folder or a `~/buddies/` folder you make.

Or if you're comfortable with the terminal:
```bash
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/cli-buddies/main/cozy-cats/cat_buddy.py
```

---

## Running a buddy

Open your terminal and navigate to where you saved the file:
```bash
cd ~/wherever-you-saved-it
python3 cat_buddy.py
```

That's it. A little room will appear with furniture and a summoning bell. Click the bell to bring in your first cat.

**To quit:** press `Ctrl+C`

---

## Running alongside your code (recommended)

The real magic is having a buddy open in a split pane while you work. If you use tmux, this one command opens a pane at the bottom of your terminal and launches the buddy inside it:

```bash
tmux split-window -v -l 22 'python3 ~/path/to/cat_buddy.py'
```

If you don't use tmux, you can just open a second terminal window side by side and run it there.

---

## Requirements

- Python 3.8 or higher
- A modern terminal emulator with true-color support (iTerm2, Kitty, Alacritty, Wezterm, or a recent version of GNOME Terminal all work great)
- Mouse clicks enabled in your terminal (most are by default)
- tmux if you want the split-pane setup (optional but recommended)

No pip installs. No package.json. Nothing to configure. Just one file.

---

---

# Cozy Cats

A colony of eight pixel art cats that wander around a little room while you work. They have distinct personalities, opinions about food, and a lot to say about your hydration habits.

---

## The cats

You start with an empty room. Click the 🔔 bell to summon a cat, pick which one you want, give it a name (or keep the default), and watch it wander in. You can have up to four cats on screen at once.

| | Name | Personality | Food preference |
|--|------|-------------|-----------------|
| 🤍 | Séraphine | High-maintenance princess. Tolerates almost nothing. | Fish only |
| 🟤 | Hazel | Sweet and shy. May flee if she gets overwhelmed. | Wet food |
| 🟠 | Kulfi | Chaos goblin. Knocks things over on purpose. | Anything |
| 🖤 | Nyx | Void cat. Randomly disappears into shadow, leaving only her eyes. | Wet food |
| 🩶 | Arwen | Aloof and sassy. Gives attention strictly on her own terms. | Dry food |
| 🌈 | Saffron | Gentle chirper. Will trill at you unprompted. | Wet food |
| 👑 | Mochi | Extremely needy. The most frequent reminders. Begs constantly. | Wet food |
| 🐄 | Oreo | Chaos goblin #2. Always hungry, always begging, occasionally destructive. | Anything |

---

## Features

**Reminders that float above whoever's talking**
Each cat gives you timed reminders to drink water, take a stretch break, and keep going. They all have their own voice — Mochi will be genuinely worried about your hydration, Séraphine will make it sound like your problem, and Kulfi will just shout at you.

**Click to interact**
Click any cat to open a retro pixel-style menu. You can give them dry food, wet food, or fish, play with yarn or a feather toy, pet them, or cuddle. Each cat reacts differently based on their personality and food preferences. Séraphine will not eat dry food. Don't try.

**Cats do things on their own**
They wander, sit, loaf around, and fall asleep without any input from you. Kulfi and Oreo will knock over the orchid or fern when they feel like it (click the plant to fix it). Nyx will randomly fade out until only her eyes are visible in the dark. Mochi will walk in front of whatever you're doing.

**Name your cats**
When you summon a cat, you can give them a custom name. The defaults are there if you want them.

**Hazel might leave**
If you overwhelm her she'll slip away quietly. You can summon her again via the bell, but she'll need a moment.

---

## How it works

One Python file, ~1200 lines, zero dependencies. It uses raw ANSI escape codes and Unicode half-block characters (▀) to render pixel art directly in your terminal, two pixels per terminal row. Mouse support is handled via the SGR mouse protocol built into most modern terminals. The cats are animated with a simple state machine (walking, sitting, loafing, sleeping) and wander around on random timers.

Everything resets when you close it. No config files, no saved state, no background processes left running.

---

*More buddies coming. Suggestions welcome.*
