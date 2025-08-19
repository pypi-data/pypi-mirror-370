import os
import signal
from dataset_up.utils.concurrent_utils import interrupt_event,can_quit_event


_signal_callback = None
def register_signal_handler(callback = None):
    global _signal_callback
    _signal_callback = callback
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
def signal_handler(sig, frame):
    print("\n接收到中断信号,准备退出...\n")
    
    if _signal_callback:
        try:
            _signal_callback()
        except Exception as e:
            print(f"回调处理出错:{e}")
    interrupt_event.set()
    can_quit_event.wait(10)
    os._exit(0)
    
