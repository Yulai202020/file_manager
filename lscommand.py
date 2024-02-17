from rich.console import Console
from rich.table import Table
import os, stat, magic, math
from os import listdir
from os.path import isfile, join
from pathlib import Path
from rich.style import Style
import logging, time

logging.basicConfig(filemode="a",filename="log.txt",level=logging.DEBUG)

cursor_id = 0

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

console = Console()
directory = os.getcwd()
onlyfiles = []
onlydirs = []

def get_folder_size(folder_path):
    metadata = []

    for root, dirs, files in os.walk(folder_path):
        for name in files + dirs:
            full_path = os.path.join(root, name)
            stat_info = os.stat(full_path)

            metadata.append({
                'name': name,
                'path': full_path,
                'size': stat_info.st_size,
                'created_at': time.ctime(stat_info.st_ctime),
                'modified_at': time.ctime(stat_info.st_mtime),
                'accessed_at': time.ctime(stat_info.st_atime),
            })
    return metadata

def get_stuff_from_dir(path):
    global onlyfiles, onlydirs
    onlyfiles = [f for f in listdir(directory) if isfile(join(path, f))]
    onlydirs = [folder for folder in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder))]
    onlydirs.extend(onlyfiles)

get_stuff_from_dir(directory)

def print_Table(files_dirs):
    global directory
    table = Table()
    
    table.add_column("Perms", style="")
    table.add_column("File Ownership", style="")
    table.add_column("Size", style="cyan")
    table.add_column("File name", style="bold green")
    table.add_column("Real Type", style="")
    
    table.add_row("", "", "", "..", "")

    for i in files_dirs:
        # get onwer
        path = Path(directory + "/" + i)
        onwer = path.owner()
        
        # get perms
        file_stat = os.stat(directory + "/" + i)
        status = stat.filemode(file_stat.st_mode)

        if os.path.isdir(directory + "/" + i):
            try:
                nbytes = sum(d.stat().st_size for d in os.scandir(directory+"/"+i) if d.is_file())
                nbytes = convert_size(nbytes)                
            except:
                nbytes = "permission denied"
            table.add_row(status,onwer, str(nbytes), i , "folder")

        else:
            # get file size
            file_size = os.stat( directory + "/" + i).st_size
            file_size = convert_size(file_size)

            # get real type
            tmp = magic.from_file(directory + "/" + i, mime=True)    

            table.add_row(status, onwer, str(file_size), i, tmp)
    
    return table

with console.screen():
    table1 = print_Table(onlydirs)
    console.print(table1)

    import threading, time
    from pynput import keyboard

    def on_key_press(key):
        global directory, get_stuff_from_dir, onlydirs, print_Table
        try:
            global table1, cursor_id
            if key.char == "a":
                
                console.clear() 
                if cursor_id > len(table1.rows)-1:
                    cursor_id = 0
                elif cursor_id > 0:
                    table1.rows[cursor_id-1].style = None
                if cursor_id == 0:
                    table1.rows[-1].style = None

                table1.rows[cursor_id].style = "red"

                console.print(table1)
                cursor_id+=1

        except:
            if str(key) == "Key.enter":
                if cursor_id == 1:
                    console.clear()
                    directory = "/".join(directory.split("/")[:-1])
                    directory = os.path.split(directory)[0] + "/"
                    get_stuff_from_dir(directory)
                    table1 = print_Table(onlydirs)
                    console.print(table1)
                                      
                    cursor_id = 0

                elif os.path.isdir(directory + "/" + onlydirs[cursor_id-2]):
                    
                    console.clear()
                    directory = directory + "/" + onlydirs[cursor_id-2]
                    
                    get_stuff_from_dir(directory)
                    table1 = print_Table(onlydirs)
                    console.print(table1)
                    
                    cursor_id = 0

                else: pass

    def background_task():
        # Simulate some long-running task
        while True:
            time.sleep(100)

    with keyboard.Listener(on_press=on_key_press) as listener:
        # Start the background task in a separate thread
        thread = threading.Thread(target=background_task)
        thread.start()
    
        # Wait for the thread to finish
        thread.join()

        # Stop the listener
        listener.stop()
        listener.join()

    console.input("Press enter for exit ")
