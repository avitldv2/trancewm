import subprocess
import sys
import os

WM = os.path.join(os.path.dirname(__file__), 'wm.py')


def launch_wm():
    try:
        proc = subprocess.Popen([sys.executable, WM])
        proc.wait()
    except Exception as e:
        print(f"Failed to launch wm: {e}")
        sys.exit(1)


def main():
    launch_wm()


if __name__ == "__main__":
    main()
