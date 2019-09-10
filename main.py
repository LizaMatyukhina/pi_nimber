import threading
from multiprocessing import Process
from queue import Queue
import requests
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed


class Sequence(Process):

    def __init__(self, url="http://www.eveandersson.com/pi/digits/1000000"):
        super().__init__()
        self.main = requests.get(url)
        self.main = self.main.text
        self.now = 0
        self.end = 0

        with open('dates.txt', 'r') as f_in:
            self.birth = f_in.readlines()

    def word_processing(self):
        self.main = re.sub('\n', '', self.main)
        self.match = re.findall(r'<pre>(3\.\d+)', self.main)
        self.pi = self.match[0]

    def main_(self):
        in_ = 0
        out_ = 0
        for line in self.birth:
            line = line.replace('/', '')
            line = line.strip()
            if line in self.pi:
                in_ += 1

        print('There are', in_, 'birthdays in number Pi')
        self.end = time.time()
        print('Time for sequential execution: ',
              round(self.end - self.now, 5),
              'sec.', '\n')


    def run(self):
        self.now = time.time()
        self.word_processing()
        self.main_()


class Queues(Sequence):

    def __init__(self):
        super().__init__()
        self.in_ = 0
        self.now = 0
        self.end = 0

    def quest(self, q):
        while True:
            item = q.get()
            if item is None:
                break
            item = str(item)
            if item in self.pi:
                self.in_ += 1

        return self.in_

    def run(self):
        self.now = time.time()
        self.word_processing()

        q = Queue()
        for line in self.birth:
            line = line.replace('/', '')
            line = line.strip()
            q.put(line)
        q.put(None)
        q.put(None)
        q.put(None)

        with ThreadPoolExecutor(max_workers=3) as pool:
            results = [pool.submit(self.quest, q)]

            for future in as_completed(results):
                print('There are', future.result(), 'birthdays in number Pi')
                self.end = time.time()
                print('Time for queue: ',
                      round(self.end - self.now, 5),
                      'sec.', '\n')



class Block(Sequence):

    def __init__(self):
        super().__init__()
        self._in = 0
        self.now = 0
        self.end = 0

    def main_(self):
        lock = threading.RLock()
        for line in self.birth:
            line = line.replace('/', '')
            line = line.strip()

            if line in self.pi:
                lock.acquire()
                self._in += 1
                lock.release()

        return self._in

    def run(self):
        self.now = time.time()
        self.word_processing()

        with ThreadPoolExecutor(max_workers=3) as pool:
            results = [pool.submit(self.main_)]

            for future in as_completed(results):
                print('There are', future.result(), 'birthdays in number Pi')
                self.end = time.time()
                print('Time for execution with block: ',
                      round(self.end - self.now, 5),
                      'sec.', '\n')


if __name__ == '__main__':
    proc1 = Sequence()
    proc2 = Queues()
    proc3 = Block()
    proc1.start()
    proc2.start()
    proc3.start()
