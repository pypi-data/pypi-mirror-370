"""
run_shareddata.py
Start the whole SharedData stack (Flask app + Gunicorn + background threads)
from a single Python script.

$ python run_shareddata.py --host 0.0.0.0 --port 8002 --workers 4 --threads 20
"""
from __future__ import annotations

import argparse
import os
import sys
import threading
import time
from gunicorn.app.base import BaseApplication

# ----------------------------------------------------------------------
# 1) Import your Flask application factory or the global `app`
# ----------------------------------------------------------------------

from SharedData.Logger import Logger
Logger.connect('SharedData.IO.ServerHttp')

from SharedData.IO.ServerAPI import app as flask_app                 # ← adjust module name

# ----------------------------------------------------------------------
# 2) “Embedded” Gunicorn class
#    Subclassing BaseApplication lets us pass config dicts programmatically
# ----------------------------------------------------------------------
class GunicornEmbedded(BaseApplication):
    """
    Run Gunicorn inside the current Python interpreter.

    Example:
        GunicornEmbedded(flask_app, {"bind": "0.0.0.0:8002", "workers": 4}).run()
    """
    def __init__(self, wsgi_app, options: dict[str, str | int]):
        self._wsgi_app = wsgi_app
        self._options = options
        super().__init__()

    # Gunicorn hooks ----------------------------------------------------
    def load_config(self):
        config = {key: value for key, value in self._options.items()
                  if value is not None}
        for key, value in config.items():
            self.cfg.set(key, value)

    def load(self):
        return self._wsgi_app


# ----------------------------------------------------------------------
# 3) Command-line parsing
# ----------------------------------------------------------------------
def parse_cli():
    p = argparse.ArgumentParser(description="Run SharedData API via Gunicorn")
    p.add_argument("--host",    default="0.0.0.0")
    p.add_argument("--port",    type=int, default=8002)
    p.add_argument("--nproc", type=int, default=4,
                   help="Number of Gunicorn worker processes")
    p.add_argument("--nthreads", type=int, default=8,
                   help="Number of request threads *per* worker (gthread)")
    p.add_argument("--timeout", type=int, default=120,
                   help="Hard kill after N seconds")
    p.add_argument("--log-level", default="warning")
    return p.parse_args()


# ----------------------------------------------------------------------
# 4) Kick-off helper threads *before* Gunicorn forks workers
# ----------------------------------------------------------------------
def send_heartbeat():    
    heartbeat_interval = 15
    time.sleep(15)
    Logger.log.info('ROUTINE STARTED!')
    while True:
        current_time = time.time()        
        # Log the heartbeat with rates
        Logger.log.debug('#heartbeat#')
        time.sleep(heartbeat_interval)
        
def start_background_threads():    
    # Thread that emits heartbeat metrics
    heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_thread.start()


# ----------------------------------------------------------------------
# 5) main()
# ----------------------------------------------------------------------
def main():
    args = parse_cli()
    
    # 5a. Launch in-process helper threads
    start_background_threads()

    # 5b. Assemble Gunicorn config
    gunicorn_opts = {
        "bind":            f"{args.host}:{args.port}",
        "workers":         args.nproc,
        "worker_class":    "gthread",      
        "threads":         args.nthreads,
        "timeout":         args.timeout,
        "graceful_timeout": 30,
        "preload_app":     False,           
        "accesslog":       None,  
        "errorlog":        "-",
        "loglevel":        args.log_level,
        "max_requests":    5000,           # recycle workers → tame leaks
        "max_requests_jitter": 500,
        "limit_request_line": 8190,       # 8190 is HTTP/1.1 spec max
    }

    # 5c. Block here; Gunicorn handles signals and will exit cleanly
    GunicornEmbedded(flask_app, gunicorn_opts).run()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Basic env-var sanity checks (just like your original Waitress entry)
    required_env = ("SHAREDDATA_SECRET_KEY", "SHAREDDATA_TOKEN")
    missing = [v for v in required_env if v not in os.environ]
    if missing:
        sys.exit(f"Missing environment variables: {', '.join(missing)}")

    main()
