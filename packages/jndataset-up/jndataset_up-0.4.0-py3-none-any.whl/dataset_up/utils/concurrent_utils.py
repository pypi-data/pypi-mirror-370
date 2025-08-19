from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
import threading
from threading import Event
import time
from typing import Callable
from typing import Iterable


error_event = Event()
parse_filelist_to_tasklist_event = Event()
upload_files_event = Event()
interrupt_event = Event()
can_quit_event = Event()


def wait_result(futures: list, results: list,event: Event):
    try:
        for future in as_completed(futures):
            if future.exception() is not None:
                raise Exception(future.exception())
            results.append(future.result())
        event.set()
    except Exception as e:
        error_event.set()
        raise e

def concurrent_submit(func: Callable, workers: int,event: Event, *args):
    def wrapper(*args):
        try:
            return func(*args)
        except Exception as e:
            error_event.set()
            raise Exception(f"An error occurred: {e}")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(wrapper, *args) for _ in range(workers)]
        results = []

        threading.Thread(target=wait_result, args=[futures, results, event], daemon=True).start()
        while not event.is_set():
            if(error_event.is_set() or interrupt_event.is_set()):
                if error_event.is_set():
                    time.sleep(7)
                executor.shutdown(wait=False)
                break
            time.sleep(1)

        return results