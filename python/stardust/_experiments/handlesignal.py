import sys
import signal
import asyncio

from asyncio import CancelledError
import threading


# class Singleton(type):
#     _instances = {}
#     _lock: threading.Lock = threading.Lock()

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def __call__(cls, *args, **kwargs):
#         key = (cls, args, frozenset(kwargs.items()))
#         with cls._lock:
#             if key not in cls._instances:
#                 instance = super().__call__(*args, **kwargs)
#                 cls._instances[key] = instance
#         return cls._instances[key]

#     def __new__(cls, *args, **kwargs):
#         pass

#     @classmethod
#     def reset_instance(cls, *args, **kwargs):
#         key = (cls, args, frozenset(kwargs.items()))
#         with cls._lock:
#             if key in cls._instances:
#                 del cls._instances[key]


# class SignalManager(Singleton):
#     def __init__(self):
#         self._shutdown_event = asyncio.Event()

#     @property
#     def shutdown_event(self):
#         return self._shutdown_event

#     def _handle_signal(self, received_signal, frame: object) -> None:
#         self._shutdown_event.set()

#         loop = asyncio.get_running_loop()
#         try:
#             if loop.is_running():
#                 for task in asyncio.all_tasks(loop):
#                     task.cancel()

#                 for task in asyncio.all_tasks(loop):
#                     try:
#                         task.result()
#                     except Exception:
#                         pass
#         except (
#             Exception,
#             CancelledError,
#             KeyboardInterrupt,
#             SystemExit,
#         ):
#             pass
#         finally:
#             if self.is_test():
#                 sys.exit(0)

#             sys.exit(received_signal)

#     def register_shutdown_signal(self):
#         signal.signal(signal.SIGINT, self._handle_signal)
#         signal.signal(signal.SIGTERM, self._handle_signal)
#         signal.signal(signal.SIGKILL, self._handle_signal)

#     @classmethod
#     def is_shutdown_signaled(cls):
#         instance = cls()
#         return instance.shutdown_event.is_set()

#     def is_test(self):
#         return hasattr(sys, "gettrace") and sys.gettrace() is None


class SignalManager:
    def __init__(self):
        self.event_ = asyncio.Event()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    @property
    def shutdown(self):
        return self.event_
    

    async def handle_signal(self, sig):
        """Handle signals asynchronously"""
        print(f"Received signal {sig}, shutting down...")
        self.shutdown.set()

        loop = asyncio.get_running_loop()
        try:
            if loop.is_running():
                for task in asyncio.all_tasks(loop):
                    task.cancel()

                for task in asyncio.all_tasks(loop):
                    try:
                        task.result()
                    except Exception:
                        pass
        except (
            Exception,
            CancelledError,
            KeyboardInterrupt,
            SystemExit,
        ):
            pass
        finally:
            sys.exit(sig)
        # Stop the event loop
        self.loop.stop()

    def register_signals(self):
        for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT]:
            self.loop.add_signal_handler(
                sig, lambda sig_=sig: asyncio.create_task(self.handle_signal(sig_))
            )

    @classmethod
    def is_shutdown(cls):
        instance=cls()
        return instance.shutdown.is_set()

