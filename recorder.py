"""
recorder.py — record your own inputs to generate track data

Since we can't read Switch controller input directly, this recorder
uses keyboard input as a proxy while you call out what you're doing,
OR you can run it alongside a gamepad connected to the PC and read
its inputs via pygame to log them in real time.

Usage:
    python recorder.py --track mario_kart_stadium

Controls during recording:
    Arrow keys / WASD  = steer + throttle
    Space              = drift
    E                  = use item
    Q                  = quit and save
    R                  = restart (discard current recording)
"""

import argparse
import csv
import os
import time
import sys
from tracks import get_track_path, TRACKS

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

FRAME_RATE = 60
FRAME_TIME = 1.0 / FRAME_RATE


def record_keyboard(track_name: str, output_path: str):
    """Record inputs from keyboard via pygame."""
    if not PYGAME_AVAILABLE:
        print("pygame not installed. Run: pip install pygame")
        sys.exit(1)

    pygame.init()
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption(f"Recording: {track_name} — Q to save, R to restart")
    font = pygame.font.SysFont(None, 28)

    def draw(recording, frame_count):
        screen.fill((30, 30, 30))
        status = f"{'● REC' if recording else 'READY'}  frames: {frame_count}"
        text = font.render(status, True, (220, 60, 60) if recording else (180, 180, 180))
        screen.blit(text, (20, 80))
        hint = font.render("SPACE=drift  E=item  Q=save  R=restart", True, (120, 120, 120))
        screen.blit(hint, (20, 120))
        pygame.display.flip()

    frames = []
    recording = False
    clock = pygame.time.Clock()
    frame_count = 0
    start_time = None

    print(f"Recording for: {track_name}")
    print("Press ENTER in the pygame window to start recording, Q to save.")

    running = True
    while running:
        clock.tick(FRAME_RATE)

        steer = 0.0
        throttle = False
        brake = False
        drift = False
        item = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and not recording:
                    recording = True
                    start_time = time.time()
                    frames = []
                    frame_count = 0
                    print("Recording started!")
                if event.key == pygame.K_q and recording:
                    running = False
                if event.key == pygame.K_r:
                    recording = False
                    frames = []
                    frame_count = 0
                    print("Restarted.")

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            steer = -1.0
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            steer = 1.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            throttle = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            brake = True
        if keys[pygame.K_SPACE]:
            drift = True
        if keys[pygame.K_e]:
            item = True

        if recording:
            elapsed = time.time() - start_time
            frames.append({
                "frame": frame_count,
                "time": round(elapsed, 4),
                "steer": round(steer, 3),
                "throttle": int(throttle),
                "brake": int(brake),
                "drift": int(drift),
                "item": int(item),
            })
            frame_count += 1

        draw(recording, frame_count)

    pygame.quit()

    if frames:
        save_recording(frames, output_path, track_name)
    else:
        print("Nothing recorded.")


def record_gamepad(track_name: str, output_path: str):
    """Record inputs from a physical gamepad connected to the PC."""
    if not PYGAME_AVAILABLE:
        print("pygame not installed. Run: pip install pygame")
        sys.exit(1)

    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No gamepad detected. Falling back to keyboard recording.")
        record_keyboard(track_name, output_path)
        return

    joy = pygame.joystick.Joystick(0)
    joy.init()
    print(f"Using gamepad: {joy.get_name()}")

    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption(f"Recording: {track_name} — gamepad mode")
    font = pygame.font.SysFont(None, 28)

    frames = []
    recording = False
    clock = pygame.time.Clock()
    frame_count = 0
    start_time = None

    print("Press START on your gamepad to begin, SELECT to save.")

    running = True
    while running:
        clock.tick(FRAME_RATE)
        pygame.event.pump()

        # Xbox-style mapping (adjust indices for your controller)
        steer = joy.get_axis(0)          # left stick X
        throttle_axis = joy.get_axis(5)  # right trigger
        brake_axis = joy.get_axis(4)     # left trigger
        throttle = throttle_axis > 0.1
        brake = brake_axis > 0.1
        drift = joy.get_button(4)        # LB
        item = joy.get_button(5)         # RB
        start_btn = joy.get_button(7)
        select_btn = joy.get_button(6)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 7 and not recording:
                    recording = True
                    start_time = time.time()
                    frames = []
                    frame_count = 0
                    print("Recording started!")
                if event.button == 6 and recording:
                    running = False

        screen.fill((30, 30, 30))
        status = f"{'● REC' if recording else 'READY — press START'}  frames: {frame_count}"
        text = font.render(status, True, (220, 60, 60) if recording else (180, 180, 180))
        screen.blit(text, (20, 80))
        pygame.display.flip()

        if recording:
            elapsed = time.time() - start_time
            frames.append({
                "frame": frame_count,
                "time": round(elapsed, 4),
                "steer": round(steer, 3),
                "throttle": int(throttle),
                "brake": int(brake),
                "drift": int(drift),
                "item": int(item),
            })
            frame_count += 1

    pygame.quit()

    if frames:
        save_recording(frames, output_path, track_name)
    else:
        print("Nothing recorded.")


def save_recording(frames: list, output_path: str, track_name: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["frame", "time", "steer", "throttle", "brake", "drift", "item"])
        writer.writeheader()
        writer.writerows(frames)
    print(f"Saved {len(frames)} frames ({len(frames)/FRAME_RATE:.1f}s) to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record MK8DX inputs for a track")
    parser.add_argument("--track", required=True, help="Track name e.g. mario_kart_stadium")
    parser.add_argument("--gamepad", action="store_true", help="Use a connected gamepad instead of keyboard")
    args = parser.parse_args()

    try:
        path = get_track_path(args.track)
    except ValueError as e:
        print(e)
        print("\nAvailable tracks:")
        from tracks import list_tracks
        list_tracks()
        sys.exit(1)

    print(f"Track: {args.track} → {path}")

    if args.gamepad:
        record_gamepad(args.track, path)
    else:
        record_keyboard(args.track, path)
