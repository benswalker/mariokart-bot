"""
bot.py — Mario Kart 8 Deluxe time trial bot

Loads pre-recorded input data for a track and replays it via nxbt.
Tracks personal bests and improves over time by saving better runs.

Usage:
    python bot.py --track mario_kart_stadium
    python bot.py --track rainbow_road --laps 3
    python bot.py --list
"""

import argparse
import csv
import os
import sys
import time

from tracks import get_track_path, list_tracks, TRACKS
from controller import MKController
from reward import PersonalBestTracker, LapTimer, RewardComputer

FRAME_RATE = 60
FRAME_TIME = 1.0 / FRAME_RATE

# How many seconds to wait after connecting before starting
# (gives you time to navigate to the track and start the race)
RACE_START_DELAY = 5.0


def load_track(path: str) -> list:
    """Load a track CSV into a list of frame dicts."""
    if not os.path.exists(path):
        return None
    with open(path) as f:
        reader = csv.DictReader(f)
        frames = []
        for row in reader:
            frames.append({
                "frame":    int(row["frame"]),
                "time":     float(row["time"]),
                "steer":    float(row["steer"]),
                "throttle": bool(int(row["throttle"])),
                "brake":    bool(int(row["brake"])),
                "drift":    bool(int(row["drift"])),
                "item":     bool(int(row["item"])),
            })
    return frames


def run_lap(controller: MKController, frames: list, lap_num: int) -> float:
    """
    Replay one lap of recorded frames.
    Returns the actual elapsed wall-clock time of the lap.
    """
    print(f"\n  Lap {lap_num} starting...")
    timer = LapTimer()
    timer.start()

    next_frame_time = time.perf_counter()

    for i, frame in enumerate(frames):
        controller.send(
            steer=frame["steer"],
            throttle=frame["throttle"],
            brake=frame["brake"],
            drift=frame["drift"],
            item=frame["item"],
        )

        # Pace the loop to 60fps
        next_frame_time += FRAME_TIME
        sleep_time = next_frame_time - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)

        # Print progress every 5 seconds
        if i % (FRAME_RATE * 5) == 0 and i > 0:
            elapsed = timer.lap()
            print(f"    {elapsed:.1f}s elapsed ({i}/{len(frames)} frames)")

    lap_time = timer.lap()
    controller.neutral()
    return lap_time


def main():
    parser = argparse.ArgumentParser(description="MK8DX time trial bot")
    parser.add_argument("--track", help="Track name e.g. mario_kart_stadium")
    parser.add_argument("--laps", type=int, default=3, help="Number of laps to run (default: 3)")
    parser.add_argument("--list", action="store_true", help="List all available tracks")
    parser.add_argument("--pbs", action="store_true", help="Show all personal bests")
    parser.add_argument("--delay", type=float, default=RACE_START_DELAY,
                        help="Seconds to wait after connecting before starting (default: 5)")
    args = parser.parse_args()

    pb_tracker = PersonalBestTracker()

    if args.list:
        print("\nAll MK8DX tracks (including DLC):\n")
        list_tracks()
        return

    if args.pbs:
        pb_tracker.summary()
        return

    if not args.track:
        parser.print_help()
        return

    # Resolve track
    try:
        track_path = get_track_path(args.track)
    except ValueError as e:
        print(e)
        print("\nAvailable tracks:")
        list_tracks()
        sys.exit(1)

    # Load track data
    frames = load_track(track_path)
    if frames is None:
        print(f"\nNo recorded data found for '{args.track}'.")
        print(f"Expected file: {track_path}")
        print(f"\nRecord it first with:")
        print(f"  python recorder.py --track {args.track}")
        sys.exit(1)

    duration = len(frames) / FRAME_RATE
    print(f"\nTrack:    {args.track}")
    print(f"Data:     {len(frames)} frames ({duration:.1f}s per lap)")
    print(f"Laps:     {args.laps}")
    print(f"PB:       {pb_tracker.get_pb(args.track):.3f}s" 
          if pb_tracker.get_pb(args.track) != float('inf') 
          else "PB:       none yet")

    # Connect controller
    controller = MKController()
    controller.wait_for_connection()

    print(f"\nConnected! Starting in {args.delay:.0f}s...")
    print("Navigate to your track and start the time trial now.")

    # Keepalive while waiting
    start = time.time()
    while time.time() - start < args.delay:
        controller.keepalive()
        time.sleep(0.5)

    # Run laps
    reward_computer = RewardComputer(pb_tracker, args.track)
    lap_times = []
    total_reward = 0.0

    for lap in range(1, args.laps + 1):
        lap_time = run_lap(controller, frames, lap)
        lap_times.append(lap_time)
        reward = reward_computer.on_lap_complete(lap_time)
        total_reward += reward
        print(f"  Lap {lap} time: {lap_time:.3f}s | reward: {reward:+.2f}")

        # Small pause between laps
        if lap < args.laps:
            time.sleep(2.0)

    controller.neutral()

    # Summary
    best_lap = min(lap_times)
    avg_lap = sum(lap_times) / len(lap_times)
    print(f"\n{'='*40}")
    print(f"Session summary for {args.track}")
    print(f"  Best lap:    {best_lap:.3f}s")
    print(f"  Average lap: {avg_lap:.3f}s")
    print(f"  Total reward: {total_reward:+.2f}")
    print(f"  PB:          {pb_tracker.get_pb(args.track):.3f}s")
    print(f"{'='*40}\n")


if __name__ == "__main__":
    main()
