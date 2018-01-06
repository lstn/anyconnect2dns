import watchgod
import os
import time
from random import randint
from enum import Enum

class _OS(Enum):
    WIN = ("WIN", os.name == 'nt')

    def __init__(self, os_name, is_os):
        self.os_name = os_name
        self.is_os = is_os

if _OS.WIN.is_os:
    import win32ui
    def WindowExists(classname=None, windowname=None):
        try:
            win32ui.FindWindow(None, windowname) if windowname else win32ui.FindWindow(classname, None) if classname else None
            return True
        except win32ui.error:
            try:
                win32ui.FindWindow(classname, None) if classname else win32ui.FindWindow(None, windowname) if windowname else None
                return True
            except:
                return False
            return False

def getfn_if_WIN_else(win_fn, notwin_fn):
    return win_fn if _OS.WIN.is_os else notwin_fn

class FileSizeWatcher(watchgod.watcher.DefaultDirWatcher):
    
    def should_watch_file(self, entry):
        return entry.name.endswith(('.txt',))

    def _win_walk(self, dir_path, changes, new_files):
        if WindowExists("Cisco AnyConnect", "Cisco AnyConnect Secure Mobility Client"):
            for entry in os.scandir(dir_path):
                if entry.is_dir():
                    self._walk(entry.path, changes, new_files) if self.should_watch_dir(entry) else None

                elif self.should_watch_file(entry):
                    _entry_stat = entry.stat()
                    mtime = _entry_stat.st_mtime
                    fsize = _entry_stat.st_size

                    new_files[entry.path] = (mtime, fsize)

                    _old_entry = self.files.get(entry.path) 
                    old_mtime = _old_entry[0] if _old_entry else None
                    old_fsize = _old_entry[1] if _old_entry else None
                    # print(f"old mtime: {old_mtime}  ... old fsize: {old_fsize}")

                    if not old_mtime or not old_fsize:
                        changes.add((watchgod.watcher.Change.added, entry.path))
                    elif old_mtime != mtime or old_fsize != fsize:
                        changes.add((watchgod.watcher.Change.modified, entry.path))
                    # windows hack here, rand 1,7 is completely arbitrary
                    elif randint(1,7) == randint(1,7):
                        print("Refreshing windows file metadata in a really hacky way...")
                        os.stat(entry.path)
        else:
            print("AnyConnect is not open.")
            _fifteensec_repeat = 1#4
            for i in range(1,_fifteensec_repeat+1):
                print(f"Checking again in {_fifteensec_repeat*15-i*15+15} seconds.")
                time.sleep(15)
    
    def _unix_walk(self, dir_path, changes, new_files):
        print("Currently only available for Windows.")
        return None
        
    def _walk(self, dir_path, changes, new_files):
        getfn_if_WIN_else(self._win_walk, self._unix_walk)(dir_path, changes, new_files)

async def watch_vpn_logs(vpn_log_dir, refresh_interval, conf):
    async for changes in watchgod.awatch(vpn_log_dir, min_sleep=refresh_interval+750, watcher_cls=FileSizeWatcher):
        print(changes)