import sys, time, threading, itertools

class RainbowDots:
    def __init__(self, prefix="처리 중", interval=0.12, max_dots=10):
        self.prefix = prefix
        self.interval = interval
        self.max_dots = max_dots
        self._running = False
        self._thread = None
        self._tty = sys.stdout.isatty()
        self._colors = ["31", "33", "32", "36", "34", "35"]

    def _color_dot(self, idx: int) -> str:
        return f"\033[{self._colors[idx % len(self._colors)]}m.\033[0m"

    def _loop(self):
        pad_len = self.max_dots + len(self.prefix) + 1
        for n in itertools.cycle(range(1, self.max_dots + 1)):
            if not self._running:
                break
            if self._tty:
                dots = "".join(self._color_dot(i) for i in range(n))
                line = f"\r{self.prefix} {dots}{' ' * (self.max_dots - n)}"
                sys.stdout.write(line); sys.stdout.flush()
            time.sleep(self.interval)
        if self._tty:
            sys.stdout.write("\r" + " " * pad_len + "\r"); sys.stdout.flush()

    def start(self):
        if not self._tty:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self, final_message: str | None = None):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        if final_message and self._tty:
            sys.stdout.write(final_message + "\n"); sys.stdout.flush()
