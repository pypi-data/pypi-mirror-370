""" ThreadedExecutor class for running tasks in multiple threads """
import concurrent.futures


class ThreadedExecutor:
    """ThreadedExecutor class for running tasks in multiple threads"""

    def __init__(self, max_workers: int):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []

    def submit(self, fn, *args, **kwargs):
        self.futures.append(self.executor.submit(fn, *args, **kwargs))

    def get_results(self):
        return [future.result() for future in concurrent.futures.as_completed(self.futures)]

    def shutdown(self):
        self.executor.shutdown(wait=True)
