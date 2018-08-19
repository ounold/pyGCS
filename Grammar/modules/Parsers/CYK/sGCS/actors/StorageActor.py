from collections import deque

import pykka


class StorageActor(pykka.ThreadingActor):
    def __init__(self, jobs_queue: deque):
        super(StorageActor, self).__init__()
        self.jobs_queue = jobs_queue

    def get_cell_job(self):
        try:
            return self.jobs_queue.popleft()
        except IndexError:
            return None
