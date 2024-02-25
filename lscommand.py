from rich.console import Console
from rich.table import Table
from rich.style import Style

from pathlib import Path

from pynput import keyboard

from os.path import isfile, join

import os, stat, magic, math, logging

logging.basicConfig(filemode="a", filename="log.txt",l evel=logging.DEBUG)

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
directory = os.getcwd()+"/"
dir_entries = []

def get_entries(path):
    try:
        all_items = os.listdir(path)
    except:
        all_items = ["permission denied"]
    
    get_folders = [i for i in all_items if os.path.isdir(os.path.join(path, i))]
    get_files = [i for i in all_items if os.path.isfile(os.path.join(path, i))]
    
    dir_entries = get_folders + get_files
    if len(dir_entries) > 60:
        dir_entries = dir_entries[0:60] 
    return dir_entries

dir_entries = get_entries(directory)

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
            try:
                tmp = magic.from_file(directory + "/" + i, mime=True)
            except:
                tmp = "permission denied"

            table.add_row(status, onwer, str(file_size), i, tmp)

    if len(files_dirs) < 60:
        a  = len(files_dirs)
        for i in range(50-a):
            table.add_row("","","","","")

    return table

with console.screen():
    table_entry = print_Table(dir_entries)
    console.print(table_entry)

    def on_key_press(key):
        global directory, get_entries, dir_entries, print_Table

        if key == keyboard.Key.esc:
            return False

        try:
            global table_entry, cursor_id
            
            if key.char == "q":
                return False
                    
        except:
            logging.info(str(str(key)=="Key.down"))
            logging.info(str(str(key)=="Key.up"))
            if str(key) == "Key.enter":
                if cursor_id == 1:
                    console.clear()

                    directory = "/".join(directory.split("/")[:-1])
                    directory = os.path.split(directory)[0] + "/"

                    dir_entries = get_entries(directory)

                    table_entry = print_Table(dir_entries)
                    console.print(table_entry)

                    cursor_id = 0

                elif os.path.isdir(directory + dir_entries[cursor_id-2]):
                    
                    console.clear()

                    directory = directory + dir_entries[cursor_id-2] + "/"
                    dir_entries = get_entries(directory)

                    table_entry = print_Table(dir_entries)

                    console.print(table_entry)
                    
                    cursor_id = 0

                elif os.path.isfile(directory+dir_entries[cursor_id-2]):
                    with open(directory+dir_entries[cursor_id-2],"r") as file:
                        for i in range(5):
                           console.print(file.readline())

                else: pass
            
            elif str(key) == "Key.down" and cursor_id <= len(dir_entries):
                console.clear()
                if cursor_id > len(table_entry.rows)-1:
                    cursor_id = 0
                elif cursor_id > 0:
                    table_entry.rows[cursor_id-1].style = None

                table_entry.rows[cursor_id].style = "red"
    
                console.print(table_entry)
                cursor_id+=1

            elif str(key) == "Key.up"and cursor_id > 1:
                logging.info(cursor_id)
                cursor_id-=1
                console.clear() 
                if cursor_id > len(table_entry.rows)-1:
                    cursor_id = 0
                elif cursor_id > 0:
                    table_entry.rows[cursor_id].style = None

                table_entry.rows[cursor_id-1].style = "red"

                console.print(table_entry)

    listener = keyboard.Listener(on_press=on_key_press)
    listener.start() 
    listener.join() 
