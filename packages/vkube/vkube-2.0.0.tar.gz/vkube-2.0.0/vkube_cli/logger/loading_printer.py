import itertools
import sys
import time
import threading

class LoadingPrinter:
    def __init__(self):
        self.line = ""
        self.done = False
        self.thread = None
        self.lock = threading.Lock()

    def loading(self, line):
        for c in itertools.cycle(['|', '/', '-', '\\']):
            with self.lock:
                if self.done:
                    self.done = False
                    # use white space to overwrite value of c
                    sys.stdout.write('\r' + line + '  \n')
                    sys.stdout.flush()
                    break
            sys.stdout.write('\r' + line + ' ' + c)
            sys.stdout.flush()
            time.sleep(0.1)
    
    def print(self, message = ""):
        if message == "":
            return
        start_thread = False
        stop_thread = False
        with self.lock:
            if self.line != message:
                if self.thread is not None:
                    self.done = True
                    stop_thread = True
                else:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                self.line = message
            elif self.thread is None:
                start_thread = True
        if stop_thread:
            # Stop the current loading thread if it exists
            self.thread.join()
            self.thread = None

        if start_thread:
            # Overwrite the current line, fill with spaces, then return to the beginning of the line
            self.thread = threading.Thread(target=self.loading, args=(message,))
            self.thread.daemon = True
            self.thread.start()
        else:
            sys.stdout.write("\r" + message)
            sys.stdout.flush()

    def stop(self):
        with self.lock:
            self.done = True
        if self.thread is not None:
            self.thread.join()
            self.thread = None
        
