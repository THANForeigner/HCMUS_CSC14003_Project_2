import threading
import time
from typing import List, Tuple, Callable, Optional

class StepPlayer:
    """Play a sequence of steps (r,c,val). Provide play/pause/step/stop and speed control.

    Usage:
      player = StepPlayer()
      player.set_steps(steps, step_callback)
      player.start_auto(delay)
      player.pause()
      player.step_once()
      player.stop()

    Supports two modes:
      - history mode: set_steps / set_event_steps (existing behavior)
      - streaming mode: push_event(step_tuple) to push live events. Player can be paused/resumed.
    """
    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._pause_event = threading.Event()
        self._stop_event = threading.Event()
        self._steps: List[Tuple[int,int,int]] = []
        self._index = 0
        self._delay = 0.25
        self._callback: Optional[Callable] = None
        self._lock = threading.Lock()
        self._streaming = False
        self._stream_queue: List[tuple] = []

    def set_steps(self, steps: List[Tuple[int,int,int]], callback: Callable[[int,int,int], None]):
        with self._lock:
            self._streaming = False
            self._steps = list(steps)
            self._index = 0
            self._callback = callback
            self._stop_event.clear()
            self._pause_event.set()  # default to running when started

    def set_event_steps(self, steps: List[tuple], callback: Callable):
        """Accept steps as arbitrary tuples and a callback that accepts the tuple unpacked.

        Example step: ('assign', r, c, val)
        The callback must accept the tuple as separate args: callback(action, r, c, val)
        """
        with self._lock:
            self._streaming = False
            self._steps = list(steps)
            self._index = 0
            self._callback = callback
            self._stop_event.clear()
            self._pause_event.set()

    def start_streaming(self, callback: Callable, delay: float = 0.1):
        """Start streaming mode: events are pushed via push_event and processed by the internal loop calling callback(*step).

        callback: function accepting step tuple unpacked, e.g., callback(action, r, c, val)
        """
        with self._lock:
            self._streaming = True
            self._callback = callback
            self._stop_event.clear()
            self._pause_event.set()
            if self._thread and self._thread.is_alive():
                return
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def push_event(self, step: tuple):
        """Push a single step tuple into the streaming queue."""
        with self._lock:
            self._stream_queue.append(step)
            # ensure player un-paused so events are consumed
            self._pause_event.set()

    def _run(self):
        while True:
            with self._lock:
                if self._stop_event.is_set():
                    break
                if self._streaming:
                    if not self._stream_queue:
                        step = None
                    else:
                        step = self._stream_queue.pop(0)
                else:
                    if self._index >= len(self._steps):
                        break
                    step = self._steps[self._index]
            # wait if paused
            self._pause_event.wait()
            if self._stop_event.is_set():
                break
            if step is None:
                time.sleep(0.01)
                continue
            # execute step
            try:
                if self._callback:
                    # history mode: step is tuple of (r,c,val) or event tuples
                    if self._streaming:
                        self._callback(*step)
                    else:
                        self._callback(*step)
            except Exception:
                pass
            with self._lock:
                if not self._streaming:
                    self._index += 1
            time.sleep(self._delay)

    def start_auto(self, delay: float = 0.25):
        with self._lock:
            self._delay = delay
            self._pause_event.set()
            self._stop_event.clear()
            if self._thread and self._thread.is_alive():
                return
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def start_auto(self, delay: float = 0.25):
        with self._lock:
            self._delay = delay
            self._pause_event.set()
            self._stop_event.clear()
            if self._thread and self._thread.is_alive():
                return
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def pause(self):
        self._pause_event.clear()

    def resume(self):
        self._pause_event.set()

    def step_once(self):
        with self._lock:
            if self._index >= len(self._steps):
                return
            step = self._steps[self._index]
            self._index += 1
        if self._callback:
            try:
                self._callback(*step)
            except Exception:
                pass

    def stop(self):
        self._stop_event.set()
        self._pause_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.1)
        with self._lock:
            self._index = 0
            self._stream_queue = []
            self._streaming = False

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive() and self._pause_event.is_set()

    def is_paused(self) -> bool:
        return self._thread is not None and self._thread.is_alive() and not self._pause_event.is_set()
