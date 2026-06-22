import argparse
import sys
import os
import json
import subprocess
import itertools
import tkinter as tk
import threading
from tkinter import messagebox

APP_VERSION = "1.1.0"
PATH_APPLICATION_PATHDATA = "paths.json"
PATH_APPLICATION_GUI_ICON = "GUI_icon.png"
PARSER_BUNNER = f"""
======================================================================
_  _  _   _   ___    _      _   _  _ _  _  ___ _  _ ____ ____
\\  / / \\  |    |     |     /_\\  |  | |\\ | |    |__| |___ |__/
 \\/  \\_/  |___ |     |___ /   \\ \\__/ | \\| \\___ |  | |___ |  \\
======================================================================
Volt Launcher v{APP_VERSION}
2026 dera_develop | Licensed under the MIT License

This application launcher handles the startup of applications.
It supports execution via file path and the specification of arguments.
"""

class exception_TypeError(Exception):
    def __init__(self, variable, need_type_list: list):
        super().__init__(f'variable type error | variable type: {type(variable)}, need:{need_type_list}')

def check_exe() -> bool:
  return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

def get_path(path: str) -> str:
  if check_exe():
    base = os.path.dirname(sys.executable)
  else:
    base = os.path.dirname(os.path.abspath(__file__))
  return os.path.join(base, path)

def load_path_datas() -> dict | None:
  conf_path = get_path(PATH_APPLICATION_PATHDATA)
  if not os.path.exists(conf_path):
    try:
      with open(conf_path, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=2)
        return {}
    except:
      return None
  try:
    with open(conf_path, "r", encoding="utf-8") as f:
      return json.load(f)
  except:
    return None

def save_path_datas(datas) -> bool:
  conf_path = get_path(PATH_APPLICATION_PATHDATA)
  try:
    with open(conf_path, "w", encoding="utf-8") as f:
      json.dump(datas, f, indent=2)
    return True
  except:
    return False

def uniform_spacing_print(source: list, output_format: str, print_function=print, space=False) -> None:
  if isinstance(source, list):
    use_source = list(singleList for singleList in source)
    for y in range(len(use_source)):
      for x in range(len(use_source[y])):
        if not isinstance(use_source[y][x], str):
          use_source[y][x] = str(use_source[y][x])

    str_length = {}
    for y in range(len(use_source)):
      for x in range(len(use_source[y])):
        if not(x in str_length):
          str_length[x] = len(use_source[y][x])
        else:
          if str_length[x] < len(use_source[y][x]):
            str_length[x] = len(use_source[y][x])
    
    for y in range(len(use_source)):
      for x in range(len(use_source[y])):
        for l in range(str_length[x] - len(use_source[y][x])):
          if space:
            use_source[y][x] = f' {use_source[y][x]}'
          else:
            use_source[y][x] = f'{use_source[y][x]} '

    left_pos = 0
    left_open = False
    index_select_poss = []
    for index, fChar in enumerate(output_format):
      if fChar == '<':
        left_pos = index
        left_open = True
        continue
      if fChar == '>' and left_open:
        left_open = False
        index_select_poss.append([left_pos, index-left_pos+1, int(output_format[left_pos+1:index])])
    for singleList in use_source:
      output_line = output_format
      for i in range(len(index_select_poss)-1, -1, -1):
        if len(singleList)-1 >= index_select_poss[i][2]:
          index_contents = singleList[index_select_poss[i][2]]
        else:
          index_contents = 'N/A'
        output_line = output_line[:index_select_poss[i][0]] + index_contents + output_line[index_select_poss[i][0] + index_select_poss[i][1]:]
      print_function(output_line)

  else:
      raise exception_TypeError(source, "'list'")

def dict_to_list(dict: dict) -> list:
  use_dict = dict.copy()
  for dict_ame, dict_value in use_dict.items():
    if not isinstance(dict_value, list):
      use_dict[dict_ame] = [dict_value]
  
  return [list(itertools.chain([s_name], s_value)) for s_name, s_value in use_dict.items()]

####################################
# GUI
####################################
class applicationFrameClass:
  def __init__(self, root: tk.Tk, app_name: str, app_path: str):
    self.root = root
    self.app_name = app_name
    self.app_path = app_path

  def create(self):
    self.frame_main = tk.Frame(self.root, bg="#ffffff")
    self.frame_main.pack(side="top", fill="both", padx=6, pady=6)
    inner_frame = tk.Frame(self.frame_main, bg="#ffffff")
    inner_frame.pack(side="top", fill="both", padx=4, pady=4)
    frame_info  = tk.Frame(inner_frame, bg="#ffffff")
    frame_info.pack(side="top", fill="both")
    flame_lavel = tk.Frame(frame_info, bg="#ffffff")
    flame_lavel.pack(side="left", fill="y")
    tk.Label(flame_lavel,   text="Application: ", anchor="w", bg="#ffffff").pack(anchor="w")
    tk.Label(flame_lavel,   text="Path :",        anchor="w", bg="#ffffff").pack(anchor="w")
    tk.Label(frame_info,    text=self.app_name,   anchor="w", bg="#ffffff").pack(anchor="w")
    tk.Label(frame_info,    text=self.app_path,   anchor="w", bg="#ffffff").pack(anchor="w")
    tk.Button(inner_frame,  text="Run",       relief="groove", bd=2, command=self.execution).pack(side="left", fill="both", padx=2, pady=2, expand=True)
    tk.Button(inner_frame,  text=" Delete ",  relief="groove", bd=2, command=self.delete   ).pack(side="left",              padx=2, pady=2)
  
  def run_subThreads(self):
    try:
      subprocess.run([self.app_path])
    except FileNotFoundError:
      messagebox.showerror("ERROR", f"Executable file not found. \n= = = = = = = = = =\nPath: {self.app_path}")
    except PermissionError:
      messagebox.showerror("ERROR", f"Permission denied. \n= = = = = = = = = =\nPath: {self.app_path}")
    except Exception as e:
      messagebox.showerror("ERROr", f"Application Error.\n{str(e)}")

  def execution(self):
    threading.Thread(target=self.run_subThreads, daemon=True).start()
  
  def delete(self):
    if messagebox.askokcancel("info", f"Do you want to remove the application '{self.app_name}' from your registration?"):
      datas = load_path_datas()
      if datas is None:
        messagebox.showerror("ERROR", "Failed to load data file.")
        sys.exit()
      
      if self.app_name in datas:
        datas.pop(self.app_name)
      
      res = save_path_datas(datas)
      if not res:
        messagebox.showerror("ERROR", "Failed to save data file.")
      self.frame_main.destroy()

####################################
####################################


####################################
# Main
####################################
def main():
  parser = argparse.ArgumentParser(
    prog="vlncr",
    usage="",
    formatter_class=argparse.RawTextHelpFormatter,
    description=PARSER_BUNNER,
    epilog="",
    add_help=True
  )

  parser_sub = parser.add_subparsers(dest="command", title="Available Commands", required=False)

  parser_command_add = parser_sub.add_parser("add", help="Add application")
  parser_command_add.add_argument("app_name", help="Identifier of the app to register")
  parser_command_add.add_argument("app_path", help="Absolute path of the application")
  parser_command_add.add_argument("-o", "--overwrite", help="This will override the path of the specified app.", action="store_true")

  parser_command_del = parser_sub.add_parser("del", help="Delete application")
  parser_command_del.add_argument("app_name", help="Identifier of the app to delete")
  parser_command_del.add_argument("-f", "--forced", help="Execute without confirmation", action="store_true")

  parser_command_run = parser_sub.add_parser("run", help="Run application")
  parser_command_run.add_argument("app_name", help="Identifier of the app to execute")
  parser_command_run.add_argument("app_args",  nargs=argparse.REMAINDER,  help="Arguments passed directly to the target application")

  parser_sub.add_parser("list", help="Print all application information")
  parser_sub.add_parser("gui", help="Start in GUI mode")

  args = parser.parse_args()

  if args.command is None:
    parser.print_help()

  ########## add(registration) ##########
  elif args.command == "add":
    datas = load_path_datas()
    if datas is None:
      print("ERROR: Failed to load data file.")
      sys.exit()

    if (not args.overwrite) and (args.app_name in datas):
      print("ERROR: Application is already registered.")
      sys.exit()

    if args.overwrite and (not args.app_name in datas):
      print("ERROR: Application is not registered.")
      sys.exit()

    datas[args.app_name] = args.app_path

    if not save_path_datas(datas):
      print("ERROR: Failed to save data file.")

  ########## delete ##########
  elif args.command == "del":
    datas = load_path_datas()
    if datas is None:
      print("ERROR: Failed to load data file.")
      sys.exit()

    if not args.app_name in datas:
      print("ERROR: This is an unregistered application.")
      sys.exit()

    if not args.forced:
      print(f"Do you want to delete application '{args.app_name}'? This action cannot be undone.(y/other)")
      if input("> ") != "y":
        print("canceled.")
        sys.exit()

    datas.pop(args.app_name)
    if not save_path_datas(datas):
      print("ERROR: Failed to save data file.")

  ########## run(execution) ##########
  elif args.command == "run":
    datas = load_path_datas()
    if datas is None:
      print("ERROR: Failed to load data file.")
      sys.exit()
    
    if not args.app_name in datas:
      print("ERROR: This is an unregistered application.")
      sys.exit()

    exe_app_args = [datas.get(args.app_name)] + args.app_args
    
    try:
      subprocess.run(args=exe_app_args)
    except FileNotFoundError:
      print(f"ERROR: Executable file not found. ({datas.get(args.app_name)})")
    except PermissionError:
      print(f"ERROR: Permission denied. ({datas.get(args.app_name)})")
    except Exception as e:
      print(f"ERROR: Application Error\n{str(e)}")

  ########## lsit ##########
  elif args.command == "list":
    datas = load_path_datas()
    if datas is None:
      print("ERROR: Failed to load data file.")
      sys.exit()
    
    print("================================================================")
    print("application : path")
    print("----------------------------------------------------------------") 
    uniform_spacing_print(dict_to_list(datas), "<0> : <1>")
    print("----------------------------------------------------------------") 
    print(f"Total: {len(datas)}")
  
  ########## GUI mode ##########
  elif args.command == "gui":
    window_root = tk.Tk()
    window_root.geometry("300x500")
    window_root.title(f"Volt Launcher v{APP_VERSION}")
    try:
      icon = tk.PhotoImage(file=get_path(PATH_APPLICATION_GUI_ICON))
    except:
      print("ERROR: Failed to load icon file")
      sys.exit()
    
    window_root.iconphoto(True, icon)

    frame_app_list = tk.Frame(window_root)
    frame_app_list.pack(side="top", fill="both", expand=True)
    frame_app_add = tk.Frame(window_root)
    frame_app_add.pack(side="bottom", fill="both", expand=False)

    scrollbar_app_list = tk.Scrollbar(frame_app_list, orient="vertical")
    scrollbar_app_list.pack(side="right", fill="y")
    canvas_app_list = tk.Canvas(frame_app_list, highlightthickness=0)
    canvas_app_list.pack(side="left", fill="both", expand=True)
    scrollbar_app_list.configure(command=canvas_app_list.yview)
    canvas_app_list.configure(yscrollcommand=scrollbar_app_list.set)
    frame_inner_app_list = tk.Frame(canvas_app_list)
    frame_inner_app_list_window = canvas_app_list.create_window((0, 0), window=frame_inner_app_list, anchor="nw")
    def scroll(event):
      canvas_app_list.configure(scrollregion=canvas_app_list.bbox("all"))
    frame_inner_app_list.bind("<Configure>", scroll)
    def resize(event):
      canvas_app_list.itemconfig(frame_inner_app_list_window, width=event.width)
    canvas_app_list.bind("<Configure>", resize)

    frame_inner_app_add = tk.Frame(frame_app_add)
    frame_inner_app_add.pack(side="top", fill="both", padx=4, pady=4)
    tk.Frame(frame_inner_app_add, height=1, bg="#000000").pack(side="top", fill="both", expand=False, padx=2)
    tk.Label(frame_inner_app_add, text="Registration application", anchor="w").pack(side="top", anchor="w")
    frame_label = tk.Frame(frame_inner_app_add)
    frame_label.pack(side="left", fill="y", expand=False)
    frame_entry = tk.Frame(frame_inner_app_add)
    frame_entry.pack(side="left", fill="both", expand=True)
    tk.Label(frame_label, text="NAME: ").pack(pady=2, padx=2)
    tk.Label(frame_label, text="PATH: ").pack(pady=2, padx=2)
    entry_name = tk.Entry(frame_entry)
    entry_name.pack(side="top", fill="x", padx=2, pady=2, expand=True)
    entry_path = tk.Entry(frame_entry)
    entry_path.pack(side="top", fill="x", padx=2, pady=2, expand=True)
    def app_add():
      if entry_name.get() == "" or entry_path.get() == "":
        messagebox.showerror("ERROR", "Registration requires specifying a name and an absolute path.")
        return

      datas = load_path_datas()
      if datas is None:
        messagebox.showerror("ERROR", "Failed to load data file.")
        return

      if entry_name.get() in datas:
        messagebox.showerror("ERROR", "Application is already registered.")
        return
      
      datas[entry_name.get()] = entry_path.get()
      
      if not save_path_datas(datas):
        messagebox.showerror("ERROR", "Failed to save data file.")
        return
      
      messagebox.showinfo("Info", f"Application registered.\nName : {entry_name.get()}\nPath : {entry_path.get()}")
      app_info = applicationFrameClass(frame_inner_app_list, entry_name.get(), entry_path.get())
      app_info.create()
      entry_name.delete("0", "end")
      entry_path.delete("0", "end")


    tk.Button(frame_app_add, text="Registration", command=app_add).pack(side="top", fill="both", padx=4, pady=4)

    datas = load_path_datas()
    if datas is None:
      print("ERROR: Failed to load data file.")
      sys.exit()
    
    for app_name, app_path in datas.items():
      app_info = applicationFrameClass(frame_inner_app_list, app_name, app_path)
      app_info.create()
    
    window_root.mainloop()





if __name__ == "__main__":
   main()