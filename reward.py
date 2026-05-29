"""
reward.py — personal best tracking and reward computation

Since we're on native Switch with no RAM access, rewards are computed
from timing alone. The bot tracks its own best lap times per track
and rewards improvement over those bests.
"""

import json
import os
import time

PB_FILE = "personal_bests.json"


class PersonalBestTracker:
    def __init__(self, pb_file=PB_FILE):
        self.pb_file = pb_file
        self.pbs = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.pb_file):
            with open(self.pb_file) as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(self.pb_file, "w") as f:
            json.dump(self.pbs, f, indent=2)

    def get_pb(self, track: str) -> float:
        return self.pbs.get(track, float("inf"))

    def update(self, track: str, lap_time: float) -> float:
        """
        Submit a lap time. Returns the improvement over PB (positive = better).
        Updates PB if this is a new best.
        """
        pb = self.get_pb(track)
        delta = pb - lap_time  # positive means faster than PB

        if lap_time < pb:
            print(f"  New PB on {track}: {lap_time:.3f}s (was {pb:.3f}s, improved by {delta:.3f}s)")
            self.pbs[track] = lap_time
            self._save()
        else:
            print(f"  Lap: {lap_time:.3f}s | PB: {pb:.3f}s | Delta: {delta:+.3f}s")

        return delta

    def summary(self):
        if not self.pbs:
            print("No personal bests recorded yet.")
            return
        print("\nPersonal Bests:")
        for track, t in sorted(self.pbs.items()):
            mins = int(t // 60)
            secs = t % 60
            print(f"  {track:<35} {mins}:{secs:06.3f}")


class LapTimer:
    """Simple lap timer using wall clock — you trigger start/end manually."""
    def __init__(self):
        self._start = None
        self._splits = []

    def start(self):
        self._start = time.time()
        self._splits = []

    def split(self) -> float:
        """Record a sector split. Returns sector time."""
        now = time.time()
        if not self._splits:
            sector_time = now - self._start
        else:
            sector_time = now - (self._start + sum(self._splits))
        self._splits.append(sector_time)
        return sector_time

    def lap(self) -> float:
        """End the lap. Returns total lap time."""
        if self._start is None:
            return 0.0
        return time.time() - self._start

    def reset(self):
        self._start = None
        self._splits = []


class RewardComputer:
    """
    Computes reward signal from timing data.
    Used during training to evaluate run quality.
    """
    def __init__(self, pb_tracker: PersonalBestTracker, track: str):
        self.pb_tracker = pb_tracker
        self.track = track
        self.pb = pb_tracker.get_pb(track)

    def on_lap_complete(self, lap_time: float) -> float:
        delta = self.pb_tracker.update(self.track, lap_time)
        self.pb = self.pb_tracker.get_pb(self.track)

        # Reward: large bonus for PB, smaller for close, penalty for way off
        if delta > 0:
            reward = 10.0 + delta * 50   # beat PB — big reward
        elif delta > -1.0:
            reward = 2.0 + delta * 2     # within 1 second
        elif delta > -3.0:
            reward = delta               # 1-3 seconds off
        else:
            reward = -5.0                # way off pace

        return reward

    def on_sector(self, sector_idx: int, sector_time: float, sector_pb: float) -> float:
        delta = sector_pb - sector_time
        if delta > 0:
            return 3.0 + delta * 10
        return delta * 2
