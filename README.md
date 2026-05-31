# MK8DX Time Trial Bot (LINUX/LINUX VM ONLY)

## Setup

```bash
# Activate your venv
source ~/mariokart/bin/activate

# Install dependencies
pip install nxbt opencv-python pygame
```

## First time: pair with Switch

1. On your Switch: **System Settings → Controllers and Sensors → Change Grip/Order**
2. Run the bot — it will connect as a Pro Controller
3. Save the Switch Bluetooth address it prints into `controller.py` as `SWITCH_ADDRESS`

## Workflow

### Step 1 — Record a track

Play the track yourself using keyboard (or a gamepad plugged into your PC):

```bash
python recorder.py --track mario_kart_stadium
# or with a gamepad:
python recorder.py --track mario_kart_stadium --gamepad
```

Controls (keyboard):
- Arrow keys / WASD = steer + throttle
- Space = drift
- E = use item
- Enter = start recording
- Q = save and quit
- R = restart

### Step 2 — Run the bot

```bash
python bot.py --track mario_kart_stadium
python bot.py --track mario_kart_stadium --laps 5
```

The bot will:
1. Connect to your Switch as a Pro Controller
2. Wait 5 seconds (navigate to your track and start the time trial)
3. Replay the recorded inputs at 60fps
4. Track your personal bests and compute reward scores

### Step 3 — Improve

Re-record a track after you get better at it. The bot always saves
the fastest lap it runs as the new personal best, and rewards future
runs against that benchmark.

## All commands

```bash
# List all available tracks (all cups + all DLC)
python bot.py --list

# Show all personal bests
python bot.py --pbs

# Run with longer start delay (more time to navigate menus)
python bot.py --track rainbow_road --delay 15
```

## File structure

```
mariokart/
├── bot.py                  # main entry point
├── controller.py           # nxbt wrapper
├── recorder.py             # record your own inputs
├── reward.py               # personal best tracking + reward
├── tracks.py               # all 96 tracks registry
├── personal_bests.json     # auto-generated, stores your PBs
└── tracks/
    ├── mushroom_cup/
    │   ├── mario_kart_stadium.csv
    │   └── ...
    ├── booster_course_1/
    │   ├── paris_promenade.csv
    │   └── ...
    └── ...
```

## Track names

Use underscores and lowercase, e.g.:
- `mario_kart_stadium`
- `rainbow_road`
- `rainbow_road_n64`
- `paris_promenade`
- `ninja_hideaway`

Run `python bot.py --list` to see all 96 tracks.
