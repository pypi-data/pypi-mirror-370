import time
import os
import argparse
import pathlib

def load_animation(file_path):
    """Loads animation frames from the given file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    frames = content.split("!--FRAME--!")
    return [frame.strip() for frame in frames if frame.strip()]

def clear():
    """Clears the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")

def animate(frames, delay=0.1, loops=-1):
    """Animates frames across the terminal with scrolling effect."""
    width = os.get_terminal_size().columns
    count = 0
    while loops == -1 or count < loops:
        for i in range(width - 10):
            for frame in frames:
                clear()
                lines = frame.split('\n')
                for line in lines:
                    print(" " * i + line)
                time.sleep(delay)
        count += 1

def main():
    parser = argparse.ArgumentParser(description="Your own terminal mantis!")
    parser.add_argument("-delay", type=float, default=0.1, help="Frame delay in seconds")
    parser.add_argument("-loops", type=int, default=-1, help="Number of loops (-1 for infinite)")
    parser.add_argument("-animation", type=str, help="Path to animation file (default: bundled mantis.animation)")
    
    args = parser.parse_args()
    
    if args.animation:
        animation_path = args.animation
    else:
        animation_path = pathlib.Path(__file__).parent / "animations" / "mantis.animation"
    
    if not os.path.exists(animation_path):
        print(f"Animation file not found: {animation_path}")
        return
    
    frames = load_animation(animation_path)
    animate(frames, delay=args.delay, loops=args.loops)

if __name__ == "__main__":
    main()