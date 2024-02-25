from rich.console import Console
from rich.table import Table
from rich.style import Style

from pathlib import Path

from pynput import keyboard

from os.path import isfile, join

import os, stat, magic, math, logging

logging.basicConfig(filemode="a", filename="log.txt", level=logging.DEBUG)

def patch_path(path):
    path = os.path.normpath(path)
    path = path.replace("//","/")
    return path

def convert_size(size_bytes):
    if size_bytes == 0:
       return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def get_entries(path):
    all_items = []
    try:
        logging.info(os.listdir(path))
        all_items = os.listdir(path)
    except:
        # all_items = []
        err = "permission denied"
    
    get_folders = [i for i in all_items if os.path.isdir(os.path.join(path, i))]
    get_files = [i for i in all_items if os.path.isfile(os.path.join(path, i))]
    
    dir_entries = get_folders + get_files
    if len(dir_entries) > 60:
        dir_entries = dir_entries[0:60] 
    return dir_entries

def print_Table(files_dirs):
    global directory, err
    table = Table()
    
    table.add_column("Perms", style="")
    table.add_column("File Ownership", style="")
    table.add_column("Size", style="cyan")
    table.add_column("File name", style="bold green")
    table.add_column("Real Type", style="")
    
    table.add_row("", "", "", "..", "")

    for i in files_dirs:
        # get onwer
        path = Path(patch_path(directory + "/" + i))
        onwer = path.owner()
        
        # get perms
        file_stat = os.stat(directory + "/" + i)
        status = stat.filemode(file_stat.st_mode)

        if os.path.isdir(directory + "/" + i):
            try:
                nbytes = sum(d.stat().st_size for d in os.scandir(patch_path(directory+"/"+i)) if d.is_file())
                nbytes = convert_size(nbytes)                
            except:
                err = f"[ERR] Cannot get {patch_path(directory+"/"+i)}'s metdata : Permission denied"
                nbytes = 0
            table.add_row(status,onwer, str(nbytes), i , "folder")

        else:
            # get file size
            file_size = os.stat(directory + "/" + i).st_size
            file_size = convert_size(file_size)

            # get real type
            try:
                tmp = magic.from_file(directory + "/" + i, mime=True)
            except:
                tmp = "file"
                err = f"[ERR] Cannot get {os.path.normpath(directory+"/"+i)} file type : Permission denied"

            table.add_row(status, onwer, str(file_size), i, tmp)

    if len(files_dirs) < 60:
        a  = len(files_dirs)
        for i in range(49-a):
            table.add_row("","","","","")

    return table

console = Console()
err = ""
directory = os.getcwd()
dir_entries = get_entries(directory)

cursor_id = 0

with console.screen():
    table_entry = print_Table(dir_entries)
    console.print(table_entry)

    def on_key_press(key):
        global directory, get_entries, dir_entries, print_Table, cursor_id, table_entry

        if key == keyboard.Key.esc:
            return False

        try:           
            if key.char == "q":
                return False

        except:

            if str(key) == "Key.enter":
                # cd ..
                if cursor_id == 1:
                    # clear screen
                    console.clear()

                    # get all path without lastest dir
                    path = os.path.normpath(directory)
                    dir_splited = path.split(os.sep)
                    dir_splited.pop()

                    # join
                    directory = os.path.join(os.path.sep, *dir_splited)

                    # get entries from new dir
                    dir_entries = get_entries(directory)

                    # print new table
                    table_entry = print_Table(dir_entries)
                    console.print(table_entry)
                    console.print(err)

                    cursor_id = 0

                # cd dir
                elif os.path.isdir(directory + "/" + dir_entries[cursor_id-2]):
                    # clear screen
                    console.clear()

                    # 
                    directory = directory + "/" + dir_entries[cursor_id-2]
                    dir_entries = get_entries(directory)
                    
                    # print new table
                    table_entry = print_Table(dir_entries)

                    console.print(table_entry)
                    console.print(err)

                    # set cursor to deafult
                    cursor_id = 0

                # like cat file_name
                #elif os.path.isfile(directory + "/" + dir_entries[cursor_id-2]):
                    #with open(directory + "/" + dir_entries[cursor_id-2],"r") as file:
                        #for i in range(5):
                           #console.print(file.readline())
            
            # move cursor down
            elif str(key) == "Key.down" and cursor_id <= len(dir_entries):
                console.clear()

                if cursor_id > len(table_entry.rows)-1:
                    cursor_id = 0

                elif cursor_id > 0:
                    table_entry.rows[cursor_id-1].style = None

                table_entry.rows[cursor_id].style = "red"
    
                console.print(table_entry)
                console.print(err)
                cursor_id+=1

            # move cursor up
            elif str(key) == "Key.up" and cursor_id > 1:
                cursor_id-=1

                console.clear() 

                if cursor_id > len(table_entry.rows)-1:
                    cursor_id = 0

                elif cursor_id > 0:
                    table_entry.rows[cursor_id].style = None

                table_entry.rows[cursor_id-1].style = "red"

                console.print(table_entry)
                console.print(err)

    # listen keyboard
    listener = keyboard.Listener(on_press=on_key_press)
    listener.start() 
    listener.join() 
