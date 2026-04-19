import asyncio
import inspect
from typing import List, Tuple, Callable, Optional

class StepPlayer:
    """Play a sequence of steps (r,c,val) using asyncio. Provide play/pause/step/stop and speed control.

    Supports two modes:
      - history mode: set_steps / set_event_steps (existing behavior)
      - streaming mode: push_event(step_tuple) to push live events. Player can be paused/resumed.
    """
    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._pause_event = asyncio.Event()
        self._stop_event = asyncio.Event()
        self._steps: List[tuple] = []
        self._index = 0
        self._delay = 0.25
        self._callback: Optional[Callable] = None
        self._streaming = False
        self._stream_queue: List[tuple] = []
        self._user_paused = False

    def set_steps(self, steps: List[tuple], callback: Callable):
        self._streaming = False
        self._steps = list(steps)
        self._index = 0
        self._callback = callback
        self._stop_event.clear()
        self._pause_event.set()  # default to running when started

    def set_event_steps(self, steps: List[tuple], callback: Callable):
        self.set_steps(steps, callback)

    async def start_streaming(self, callback: Callable, delay: float = 0.1):
        """Start streaming mode: events are pushed via push_event and processed by the internal loop."""
        self._streaming = True
        self._callback = callback
        self._delay = delay
        self._stop_event.clear()
        self._pause_event.set()
        
        if self._task and not self._task.done():
            return
        
        self._task = asyncio.create_task(self._run())

    async def run_streaming(self, callback: Callable, delay: float = 0.1):
        """Structured version of start_streaming for TaskGroup."""
        self._streaming = True
        self._callback = callback
        self._delay = delay
        self._stop_event.clear()
        self._pause_event.set()
        await self._run()

    def push_event(self, step: tuple):
        """Push a single step tuple into the streaming queue."""
        self._stream_queue.append(step)
        # only unpause if not explicitly paused by user
        if not self._user_paused:
            self._pause_event.set()

    async def _run(self):
        while not self._stop_event.is_set():
            # wait if paused
            await self._pause_event.wait()
            
            if self._stop_event.is_set():
                break

            step = None
            if self._streaming:
                if not self._stream_queue:
                    # queue is empty, auto-pause until new item
                    self._pause_event.clear()
                    await asyncio.sleep(0.01)
                    continue
                step = self._stream_queue.pop(0)
            else:
                if self._index >= len(self._steps):
                    break
                step = self._steps[self._index]
                self._index += 1

            if step is not None:
                # execute step
                try:
                    if self._callback:
                        if inspect.iscoroutinefunction(self._callback):
                            await self._callback(*step)
                        else:
                            self._callback(*step)
                except Exception:
                    pass
            
            await asyncio.sleep(self._delay)

    async def start_auto(self, delay: float = 0.25):
        self._delay = delay
        self._user_paused = False
        self._pause_event.set()
        self._stop_event.clear()
        
        if self._task and not self._task.done():
            return
            
        self._task = asyncio.create_task(self._run())

    async def run_auto(self, delay: float = 0.25):
        """Structured version of start_auto for TaskGroup."""
        self._delay = delay
        self._user_paused = False
        self._pause_event.set()
        self._stop_event.clear()
        await self._run()

    def pause(self):
        self._user_paused = True
        self._pause_event.clear()

    def resume(self):
        self._user_paused = False
        self._pause_event.set()

    async def step_once(self):
        step = None
        if self._streaming:
            if not self._stream_queue:
                return
            step = self._stream_queue.pop(0)
        else:
            if self._index >= len(self._steps):
                return
            step = self._steps[self._index]
            self._index += 1
            
        if step is not None and self._callback:
            try:
                if inspect.iscoroutinefunction(self._callback):
                    await self._callback(*step)
                else:
                    self._callback(*step)
            except Exception:
                pass

    async def stop(self):
        self._stop_event.set()
        self._pause_event.set() # wake up to finish
        if self._task:
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._index = 0
        self._stream_queue = []
        self._streaming = False

    def is_running(self) -> bool:
        return self._task is not None and not self._task.done() and self._pause_event.is_set()

    def is_paused(self) -> bool:
        return self._task is not None and not self._task.done() and not self._pause_event.is_set()
