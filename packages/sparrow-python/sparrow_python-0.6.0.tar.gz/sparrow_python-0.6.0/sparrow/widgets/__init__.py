import time
from collections import deque
from sparrow.string.color_string import rgb_string
from sparrow.color.constant import TEAL, GREEN


def timer(dt=0.01):
    """A simple timer.
    Press `space` to start and suspend.
    press `q` to quit.
    """
    try:
        import keyboard
    except ImportError as e:
        raise ImportError("import `keyboard` error, use pip to install: `pip install keyboard`")
    print(
        rgb_string("Press <Space> to start and suspend.", color=TEAL),
    )
    q = deque(maxlen=1)
    q.append(True)
    keyboard.add_hotkey("space", lambda: q.append(not q[0]))
    keyboard.wait("space")
    t0 = time.time()
    suspend_start = None

    while True:
        time.sleep(dt)
        ct = time.time()
        if q[0]:
            if suspend_start is None:
                suspend_start = time.time()
        else:
            if suspend_start:
                t0 += ct - suspend_start
                suspend_start = None

            current_time = ct - t0
            print(rgb_string(f"\r{current_time:.3f} secs", color=GREEN), end="")
        if keyboard.is_pressed("q"):
            break

