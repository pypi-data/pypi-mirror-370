import json
import queue
import sys
import time
from threading import Thread
from typing import TextIO


class AsyncLogger:
    def __init__(self):
        self.max_queue_size = 10000  # ~ 250QPS * 10logs/s * 5s queue buffer
        self.log_drop_threshold = self.max_queue_size * 0.8
        self.log_queue = queue.Queue(maxsize=self.max_queue_size)
        self.original_stdout = sys.__stdout__
        self.initial_backoff = 0.1
        self.max_backoff = 5
        self.log_thread = Thread(target=self._log_writer, daemon=True)
        self.log_thread.start()

    def log(self, log_record):
        """Enqueue log messages instead of writing synchronously."""
        if self.log_queue.qsize() > self.log_drop_threshold:
            self.original_stdout.flush()
        self.log_queue.put(log_record)

    def _log_writer(self):
        """Background thread to process logs asynchronously."""
        initial_backoff = self.initial_backoff
        backoff = initial_backoff
        while True:
            try:
                log_record = self.log_queue.get(timeout=backoff)
                self.original_stdout.write(json.dumps(log_record) + "\n")
                self.original_stdout.flush()
                backoff = initial_backoff

            except queue.Empty:
                backoff = min(backoff * 2, self.max_backoff)


class JSONStdoutWrapper(TextIO):
    def __init__(self, logger):
        self.logger = logger

    def write(self, message):
        stripped_message = message.strip()
        if stripped_message:
            log_record = {"MESSAGE": stripped_message, "@timestamp": time.time()}
            self.logger.log(log_record)

    def flush(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    @property
    def buffer(self):
        msg = "buffer is not implemented"
        raise NotImplementedError(msg)

    @property
    def encoding(self):
        return "utf-8"

    @property
    def errors(self):
        return None

    @property
    def line_buffering(self):
        return False

    @property
    def newlines(self):
        return None
