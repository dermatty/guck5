# -*- mode: python-ts-mode; lexical-binding: t; -*-
import gunicorn
import multiprocessing as mp
from threading import Thread
import time, sys
from fastapi import FastAPI
import gunicorn.app.base
import uvicorn
import signal, os

TERMINATED = False
FINISHED = False

class SigHandler:
    def __init__(self, p: mp.Process, t: Thread)-> None:
        self.p = p
        self.t = t
        pass

    def sighandler(self, signum, frame)-> None:
        print("PRESSED ...")
        os.kill(self.p.pid, signal.SIGFPE)
        global TERMINATED
        global FINISHED
        TERMINATED = True        
        while not FINISHED:
            time.sleep(0.1)
        self.t.join()
        print("AUS - SIGHANDLER")

# def start_server():
#     sys.argv = [  # ugly hack
#         "gunicorn",
#         "-b", "0.0.0.0:8000",
#         # "-w", str((multiprocessing.cpu_count() * 2) + 1),
#         "-k", "uvicorn.workers.UvicornWorker",
#         # "--reload",
#         "guck5.app.api:app"
#     ]
#     gunicorn.app.wsgiapp.run()

def start_uvicorn() -> None:
    uvicorn.run("guck5.app.api:app", reload=True, port=8000, log_level="info")

def start_gunicorn():
    options = {
             'bind': '%s:%s' % ('0.0.0.0', '8000'),
             'workers': 4,
             # 'reload': True,
             'worker_class': "uvicorn.workers.UvicornWorker"
         }
    StandaloneApplication("guck5.app.api:app", options).run()

class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

# ----------------------------------------------------------------------------------------------
# this is the main loop
def main():
    global TERMINATED
    global FINISHED
    
    while not TERMINATED:
        time.sleep(1)
        print(time.time())  # heartbeat
    print("AUS - MAIN")
    FINISHED = True

# ----------------------------------------------------------------------------------------------
# this call by the script "uv run guck5 dev/prod"
#   it starts uvicorn (dev) or gunicorn (prod) and then runs main() above
def start():
    global TERMINATED
    global FINISHED
    print(sys.argv[1])
    
    if len(sys.argv) > 1:
        environment = sys.argv[1].upper() if sys.argv[1].upper() in ["DEV", "PROD"] else "DEV"
    else:
        environment = "DEV"

    print("Starting Guck5 in environment " + environment)

    if environment == "DEV":
        t = Thread(target=main, daemon=True)
        t.start()
        start_uvicorn()
        TERMINATED = True
        t.join()
        print("AUS - ALLES")
    else:
        p = mp.Process(target=start_gunicorn)
        p.start()
        t = Thread(target=main, daemon=True)
        t.start()
        sh = SigHandler(p, t)
        signal.signal(signal.SIGINT, sh.sighandler)
        signal.signal(signal.SIGTERM, sh.sighandler)

        
    
    


