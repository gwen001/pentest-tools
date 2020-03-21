import math
from multiprocessing import Process, Queue
import os
import os.path
import re
import sys
import time

try:
    # Python 3
    from queue import Empty as EmptyQueueException
    from queue import Full as FullQueueException
except ImportError:
    # Python 2
    from Queue import Empty as EmptyQueueException
    from Queue import Full as FullQueueException

from bs4 import BeautifulSoup
import requests


DOMAIN = "https://apkpure.com"
SEARCH_URL = DOMAIN + "/search?q=%s"

DOWNLOAD_DIR       = "./downloaded/"
PACKAGE_NAMES_FILE = "package_names.txt"
OUTPUT_CSV         = "output.csv"


CONCURRENT_DOWNLOADS  = 5
CHUNK_SIZE            = 128*1024 # 128 KiB
PROGRESS_UPDATE_DELAY = 0.25
PROCESS_TIMEOUT       = 10.0


MSG_ERROR    = -1
MSG_PAYLOAD  =  0
MSG_START    =  1
MSG_PROGRESS =  2
MSG_END      =  3


class SplitProgBar(object):
    @staticmethod
    def center(text, base):
        if len(text) <= len(base):
            left = (len(base) - len(text)) // 2
            return "%s%s%s" % (base[:left], text, base[left+len(text):])
        else:
            return base

    def __init__(self, n, width):
        self.n = n
        self.sub_width = int(float(width-(n+1))/n)
        self.width = n * (self.sub_width + 1) + 1
        self.progress = [float("NaN")] * n

    def __getitem__(self, ix):
        return self.progress[ix]

    def __setitem__(self, ix, value):
        self.progress[ix] = value

    def render(self):
        bars = []
        for prog in self.progress:
            if math.isnan(prog) or prog < 0.0:
                bars.append(" " * self.sub_width)
                continue
            bar = "=" * int(round(prog*self.sub_width))
            bar += " " * (self.sub_width-len(bar))
            bar = SplitProgBar.center(" %.2f%% " % (prog*100), bar)
            bars.append(bar)

        new_str = "|%s|" % "|".join(bars)
        sys.stdout.write("\r%s" % new_str)

    def clear(self):
        sys.stdout.write("\r%s\r" % (" " * self.width))


class Counter(object):
    def __init__(self, value = 0):
        self.value = value

    def inc(self, n = 1):
        self.value += n

    def dec(self, n = 1):
        self.value -= n

    @property
    def empty(self):
        return self.value == 0


def download_process(id_, qi, qo):
    def send_progress(progress):
        try:
            qo.put_nowait((MSG_PROGRESS, (id_, progress)))
        except FullQueueException:
            pass

    def send_error(msg):
        qo.put((MSG_ERROR, (id_, msg)))

    def send_start(pkg_name):
        qo.put((MSG_START, (id_, pkg_name)))

    def send_finished(pkg_name, app_name, size, path, already=False):
        if already:
            qo.put((MSG_END, (id_, pkg_name, app_name, size, path)))
        else:
            qo.put((MSG_PAYLOAD, (id_, pkg_name, app_name, size, path)))

    while True:
        message = qi.get()

        if message[0] == MSG_PAYLOAD:
            package_name, app_name, download_url = message[1]
        elif message[0] == MSG_END:
            break

        try:
            r = requests.get(download_url, stream=True)
        except requests.exceptions.ConnectionError:
            send_error("Connection error")
            continue

        if r.status_code != 200:
            send_error("HTTP Error %d" % r.status_code)
            r.close()
            continue

        content_disposition = r.headers.get("content-disposition", "")
        content_length = int(r.headers.get('content-length', 0))

        filename = re.search(r'filename="(.+)"', content_disposition)
        if filename and filename.groups():
            filename = filename.groups()[0]
        else:
            filename = "%s.apk" % (package_name.replace(".", "_"))

        local_path = os.path.normpath(os.path.join(DOWNLOAD_DIR, filename))

        if os.path.exists(local_path):
            if not os.path.isfile(local_path):
                # Not a file
                send_error("%s is a directory" % local_path)
                r.close()
                continue
            if os.path.getsize(local_path) == content_length:
                # File has likely already been downloaded
                send_finished(
                    package_name, app_name, content_length, local_path, True)
                r.close()
                continue

        send_start(package_name)

        size = 0
        t = time.time()
        with open(local_path, "wb+") as f:
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    size += len(chunk)
                    f.write(chunk)

                    nt = time.time()
                    if nt - t >= PROGRESS_UPDATE_DELAY:
                        send_progress(float(size) / content_length)
                        t = nt

        send_finished(package_name, app_name, size, local_path)


def search_process(qi, qo):
    def send_error(msg):
        qo.put((MSG_ERROR, msg))

    def send_payload(pkg_name, app_name, dl_url):
        qo.put((MSG_PAYLOAD, (pkg_name, app_name, dl_url)))

    while True:
        message = qi.get()

        if message[0] == MSG_PAYLOAD:
            package_name = message[1]
        elif message[0] == MSG_END:
            break

        # Search page
        # url = SEARCH_URL % package_name
        # try:
        #     r = requests.get(url)
        # except requests.exceptions.ConnectionError:
        #     send_error("Connection error")
        #     continue

        # if r.status_code != 200:
        #     send_error("Could not get search page for %s" % package_name)
        #     continue

        # soup = BeautifulSoup(r.text, "html.parser")

        # first_result = soup.find("dl", class_="search-dl")
        # if first_result is None:
        #     send_error("Could not find %s" % package_name)
        #     continue

        # search_title = first_result.find("p", class_="search-title")
        # search_title_a = search_title.find("a")

        # app_name = search_title.text.strip()
        # app_url = search_title_a.attrs["href"]

        app_url = '/aaaaaaaaaaaaa/' + package_name

        # App page
        url = DOMAIN + app_url
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            send_error("Connection error")
            continue

        if r.status_code != 200:
            send_error("Could not get app page for %s" % package_name)
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        app_name = package_name
        # app_name = search_title.text.strip()

        download_button = soup.find("a", {"class":"da"})
        if download_button is None:
            send_error("%s is a paid app. Could not download" % package_name)
            continue

        download_url = download_button.attrs["href"]

        # Download app page
        url = DOMAIN + download_url
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            send_error("Connection error")
            continue

        if r.status_code != 200:
            send_error("Could not get app download page for %s" % package_name)
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        download_link = soup.find("a", {"id":"download_link"})
        
        if download_link is None:
            send_error("%s is a paid or region app. Could not download" % package_name)
            continue

        download_apk_url = download_link.attrs["href"]

        send_payload(package_name, app_name, download_apk_url)


def main():
    # Create the download directory
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    elif not os.path.isdir(DOWNLOAD_DIR):
        print("%s is not a directory" % DOWNLOAD_DIR)
        return -1


    # Read the package names
    if not os.path.isfile(PACKAGE_NAMES_FILE):
        print("Could not find %s" % PACKAGE_NAMES_FILE)
        return -1

    with open(PACKAGE_NAMES_FILE, "r") as f:
        package_names = [line.strip() for line in f.readlines()]


    # CSV file header
    with open(OUTPUT_CSV, "w+") as csv:
        csv.write("App name,Package name,Size,Location\n")


    # Message-passing queues
    search_qi = Queue()
    search_qo = Queue()

    download_qi = Queue()
    download_qo = Queue()


    # Search Process
    search_proc = Process(target=search_process, args=(search_qo, search_qi))
    search_proc.start()


    # Download Processes
    download_procs = []
    for i in range(CONCURRENT_DOWNLOADS):
        download_proc = Process(target=download_process,
                                args=(i, download_qo, download_qi))
        download_procs.append(download_proc)
        download_proc.start()


    active_tasks = Counter()
    def new_search_query():
        if package_names:
            search_qo.put((MSG_PAYLOAD, package_names.pop(0)))
            active_tasks.inc()
            return True
        return False

    # Send some queries to the search process
    for _ in range(CONCURRENT_DOWNLOADS + 1):
        new_search_query()


    prog_bars = SplitProgBar(CONCURRENT_DOWNLOADS, 80)

    def log(msg, pb=True):
        prog_bars.clear()
        print(msg)
        if pb:
            prog_bars.render()
        sys.stdout.flush()

    last_message_time = time.time()
    while True:
        if active_tasks.empty:
            log("Done!", False)
            break

        no_message = True

        try:
            # Messages from the search process
            message = search_qi.get(block=False)
            last_message_time = time.time()
            no_message = False

            if message[0] == MSG_PAYLOAD:
                # Donwload URL found => Start a download
                download_qo.put(message)
                log("  Found app for %s" % message[1][0])

            elif message[0] == MSG_ERROR:
                # Error with search query
                log("!!" + message[1])
                active_tasks.dec()

                # Search for another app
                new_search_query()
        except EmptyQueueException:
            pass

        try:
            # Messages from the download processes
            message = download_qi.get(block=False)
            last_message_time = time.time()
            no_message = False

            if message[0] == MSG_PAYLOAD or message[0] == MSG_END:
                # Download finished
                id_, package_name, app_name, size, location = message[1]
                prog_bars[id_] = float("NaN")

                if message[0] == MSG_PAYLOAD:
                    log("  Finished downloading %s" % package_name)
                elif message[0] == MSG_END:
                    log("  File already downloaded for %s" % package_name)

                # Add row to CSV file
                # with open(OUTPUT_CSV, "a") as csv:
                #     csv.write(",".join([
                #         '"%s"' % app_name.replace('"', '""'),
                #         '"%s"' % package_name.replace('"', '""'),
                #         "%d" % size,
                #         '"%s"' % location.replace('"', '""')]))
                #     csv.write("\n")

                active_tasks.dec()

                # Search for another app
                new_search_query()

            elif message[0] == MSG_START:
                # Download started
                id_, package_name = message[1]
                prog_bars[id_] = 0.0
                log("  Started downloading %s" % package_name)

            elif message[0] == MSG_PROGRESS:
                # Download progress
                id_, progress = message[1]
                prog_bars[id_] = progress
                prog_bars.render()

            elif message[0] == MSG_ERROR:
                # Error during download
                id_, msg = message[1]
                log("!!" + msg)
                prog_bars[id_] = 0.0

                active_tasks.dec()

                # Search for another app
                new_search_query()
        except EmptyQueueException:
            pass

        if no_message:
            if time.time() - last_message_time > PROCESS_TIMEOUT:
                log("!!Timed out after %.2f seconds" % (PROCESS_TIMEOUT), False)
                break
            time.sleep(PROGRESS_UPDATE_DELAY / 2.0)

    # End processes
    search_qo.put((MSG_END, ))
    for _ in range(CONCURRENT_DOWNLOADS):
        download_qo.put((MSG_END, ))

    search_proc.join()
    for download_proc in download_procs:
        download_proc.join()

    return 0


if __name__ == '__main__':
    sys.exit(main())