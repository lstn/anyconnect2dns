
import asyncio
import toml
import os
import signal
import sys
from pprint import pprint as pp
from munch import Munch

import ac2dns
def main():
    conf = toml.load(os.path.join(os.path.abspath(__file__), "..", "anyconnect2dns.toml"), Munch)
    pp(conf)
    vpn_log_dir = conf.anyconnect.vpn_log_dir
    refresh_interval = conf.anyconnect.refresh_interval
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ac2dns.watch_vpn_logs(vpn_log_dir, refresh_interval, conf))    

def sysexit(arg1, arg2):
    sys.exit(f"Got signal to interrupt, exiting. ![{arg1}  -- {arg2}]!")

for sig in ('TERM', 'HUP', 'INT'):
        signal.signal(getattr(signal, 'SIG'+sig) if hasattr(signal, 'SIG'+sig) else getattr(signal, 'SIGTERM'), sysexit)

main()