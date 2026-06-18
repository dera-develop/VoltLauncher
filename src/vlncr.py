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
    def __init__(self, variable, needTypeList: list):
        super().__init__(f'variable type error | variable type: {type(variable)}, need:{needTypeList}')

def checkEXE() -> bool:
  return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

def getPath(path: str) -> str:
  if checkEXE():
    base = os.path.dirname(sys.executable)
  else:
    base = os.path.dirname(os.path.abspath(__file__))
  return os.path.join(base, path)

def load_pathDatas() -> dict | None:
  confPath = getPath(PATH_APPLICATION_PATHDATA)
  if not os.path.exists(confPath):
    try:
      with open(confPath, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=2)
        return {}
    except:
      return None
  try:
    with open(confPath, "r", encoding="utf-8") as f:
      return json.load(f)
  except:
    return None

def save_pathDatas(datas) -> bool:
  confPath = getPath(PATH_APPLICATION_PATHDATA)
  try:
    with open(confPath, "w", encoding="utf-8") as f:
      json.dump(datas, f, indent=2)
    return True
  except:
    return False

def Uniform_Spacing_Print(source: list, outputFormat: str, printFunction=print, space=False) -> None:
  if isinstance(source, list):
    useSource = list(singleList for singleList in source)
    for y in range(len(useSource)):
      for x in range(len(useSource[y])):
        if not isinstance(useSource[y][x], str):
          useSource[y][x] = str(useSource[y][x])

    strLength = {}
    for y in range(len(useSource)):
      for x in range(len(useSource[y])):
        if not(x in strLength):
          strLength[x] = len(useSource[y][x])
        else:
          if strLength[x] < len(useSource[y][x]):
            strLength[x] = len(useSource[y][x])
    
    for y in range(len(useSource)):
      for x in range(len(useSource[y])):
        for l in range(strLength[x] - len(useSource[y][x])):
          if space:
            useSource[y][x] = f' {useSource[y][x]}'
          else:
            useSource[y][x] = f'{useSource[y][x]} '

    leftPos = 0
    leftOpen = False
    indexSelectPoss = []
    for index, fChar in enumerate(outputFormat):
      if fChar == '<':
        leftPos = index
        leftOpen = True
        continue
      if fChar == '>' and leftOpen:
        leftOpen = False
        indexSelectPoss.append([leftPos, index-leftPos+1, int(outputFormat[leftPos+1:index])])
    for singleList in useSource:
      outputLine = outputFormat
      for i in range(len(indexSelectPoss)-1, -1, -1):
        if len(singleList)-1 >= indexSelectPoss[i][2]:
          indexContents = singleList[indexSelectPoss[i][2]]
        else:
          indexContents = 'N/A'
        outputLine = outputLine[:indexSelectPoss[i][0]] + indexContents + outputLine[indexSelectPoss[i][0] + indexSelectPoss[i][1]:]
      printFunction(outputLine)


  else:
      raise exception_TypeError(source, "'list'")

def dict_to_list(dict: dict) -> list:
  useDict = dict.copy()
  for dName, dValue in useDict.items():
    if not isinstance(dValue, list):
      useDict[dName] = [dValue]
  
  return [list(itertools.chain([sName], sValue)) for sName, sValue in useDict.items()]

####################################
# GUI
####################################
class ApplicationFrame:
  def __init__(self, root: tk.Tk, app_name: str, app_path: str):
    self.root = root
    self.appName = app_name
    self.appPath = app_path

  def create(self):
    self.mainFrame = tk.Frame(self.root, bg="#ffffff")
    self.mainFrame.pack(side="top", fill="both", padx=6, pady=6)
    innerFrame = tk.Frame(self.mainFrame, bg="#ffffff")
    innerFrame.pack(side="top", fill="both", padx=4, pady=4)
    infoFrame = tk.Frame(innerFrame, bg="#ffffff")
    infoFrame.pack(side="top", fill="both")
    lavelFrame = tk.Frame(infoFrame, bg="#ffffff")
    lavelFrame.pack(side="left", fill="y")
    tk.Label(lavelFrame, text="Application: ", anchor="w", bg="#ffffff").pack(anchor="w")
    tk.Label(lavelFrame, text="Path :", anchor="w", bg="#ffffff").pack(anchor="w")
    tk.Label(infoFrame, text=self.appName, anchor="w", bg="#ffffff").pack(anchor="w")
    tk.Label(infoFrame, text=self.appPath, anchor="w", bg="#ffffff").pack(anchor="w")
    tk.Button(innerFrame, text="Run", relief="groove", bd=2, command=self.execution).pack(side="left", fill="both", padx=2, pady=2, expand=True)
    tk.Button(innerFrame, text=" Delete ", relief="groove", bd=2, command=self.delete).pack(side="left", padx=2, pady=2)
  
  def run_subThreads(self):
    try:
      subprocess.run([self.appPath])
    except FileNotFoundError:
      messagebox.showerror("ERROR", f"Executable file not found. \n= = = = = = = = = =\nPath: {self.appPath}")
    except PermissionError:
      messagebox.showerror("ERROR", f"Permission denied. \n= = = = = = = = = =\nPath: {self.appPath}")
    except:
      import traceback
      print(traceback.format_exc())
      messagebox.showerror("ERROr", f"Unknown error.")

  def execution(self):
    threading.Thread(target=self.run_subThreads, daemon=True).start()
  
  def delete(self):
    if messagebox.askokcancel("info", f"Do you want to remove the application '{self.appName}' from your registration?"):
      datas = load_pathDatas()
      if datas is None:
        messagebox.showerror("ERROR", "Failed to load data file.")
        sys.exit()
      
      if self.appName in datas:
        datas.pop(self.appName)
      
      res = save_pathDatas(datas)
      if not res:
        messagebox.showerror("ERROR", "Failed to save data file.")
      self.mainFrame.destroy()

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
    datas = load_pathDatas()
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
    
    if not save_pathDatas(datas):
      print("ERROR: Failed to save data file.")

  ########## delete ##########
  elif args.command == "del":
    datas = load_pathDatas()
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
    if not save_pathDatas(datas):
      print("ERROR: Failed to save data file.")

  ########## run(execution) ##########
  elif args.command == "run":
    datas = load_pathDatas()
    if datas is None:
      print("ERROR: Failed to load data file.")
      sys.exit()
    
    if not args.app_name in datas:
      print("ERROR: This is an unregistered application.")
      sys.exit()

    exeAppArgs = [datas.get(args.app_name)] + args.app_args
    
    try:
      subprocess.run(args=exeAppArgs)
    except FileNotFoundError:
      print(f"ERROR: Executable file not found. ({datas.get(args.app_name)})")
    except PermissionError:
      print(f"ERROR: Permission denied. ({datas.get(args.app_name)})")
    except:
      print("ERROR: Unknown error.")

  ########## lsit ##########
  elif args.command == "list":
    datas = load_pathDatas()
    if datas is None:
      print("ERROR: Failed to load data file.")
      sys.exit()
    
    print("================================================================")
    print("application : path")
    print("----------------------------------------------------------------") 
    Uniform_Spacing_Print(dict_to_list(datas), "<0> : <1>")
    print("----------------------------------------------------------------") 
    print(f"Total: {len(datas)}")
  
  ########## GUI mode ##########
  elif args.command == "gui":
    windowR = tk.Tk()
    windowR.geometry("300x500")
    windowR.title(f"Volt Launcher v{APP_VERSION}")
    try:
      icon = tk.PhotoImage(file=getPath(PATH_APPLICATION_GUI_ICON))
    except:
      print("ERROR: Failed to load icon file")
      sys.exit()
    
    windowR.iconphoto(True, icon)


    appListFrame = tk.Frame(windowR)
    appListFrame.pack(side="top", fill="both", expand=True)
    dataAddFrame = tk.Frame(windowR)
    dataAddFrame.pack(side="bottom", fill="both", expand=False)

    appListScrollbar = tk.Scrollbar(appListFrame, orient="vertical")
    appListScrollbar.pack(side="right", fill="y")
    appListCanvas = tk.Canvas(appListFrame, highlightthickness=0)
    appListCanvas.pack(side="left", fill="both", expand=True)
    appListScrollbar.configure(command=appListCanvas.yview)
    appListCanvas.configure(yscrollcommand=appListScrollbar.set)
    appListInnerFrame = tk.Frame(appListCanvas)
    appListInnerFrame_window = appListCanvas.create_window((0, 0), window=appListInnerFrame, anchor="nw")
    def scroll(event):
      appListCanvas.configure(scrollregion=appListCanvas.bbox("all"))
    appListInnerFrame.bind("<Configure>", scroll)
    def resize(event):
      appListCanvas.itemconfig(appListInnerFrame_window, width=event.width)
    appListCanvas.bind("<Configure>", resize)

    dataAddInnerFrame = tk.Frame(dataAddFrame)
    dataAddInnerFrame.pack(side="top", fill="both", padx=4, pady=4)
    tk.Frame(dataAddInnerFrame, height=1, bg="#000000").pack(side="top", fill="both", expand=False, padx=2)
    tk.Label(dataAddInnerFrame, text="Registration application", anchor="w").pack(side="top", anchor="w")
    labelFrame = tk.Frame(dataAddInnerFrame)
    labelFrame.pack(side="left", fill="y", expand=False)
    entryFrame = tk.Frame(dataAddInnerFrame)
    entryFrame.pack(side="left", fill="both", expand=True)
    tk.Label(labelFrame, text="NAME: ").pack(pady=2, padx=2)
    tk.Label(labelFrame, text="PATH: ").pack(pady=2, padx=2)
    nameEntry = tk.Entry(entryFrame)
    nameEntry.pack(side="top", fill="x", padx=2, pady=2, expand=True)
    pathEntry = tk.Entry(entryFrame)
    pathEntry.pack(side="top", fill="x", padx=2, pady=2, expand=True)
    def app_add():
      if nameEntry.get() == "" or pathEntry.get() == "":
        messagebox.showerror("ERROR", "Registration requires specifying a name and an absolute path.")
        return

      datas = load_pathDatas()
      if datas is None:
        messagebox.showerror("ERROR", "Failed to load data file.")
        return

      if nameEntry.get() in datas:
        messagebox.showerror("ERROR", "Application is already registered.")
        return
      
      datas[nameEntry.get()] = pathEntry.get()
      
      if not save_pathDatas(datas):
        messagebox.showerror("ERROR", "Failed to save data file.")
        return
      
      messagebox.showinfo("Info", f"Application registered.\nName : {nameEntry.get()}\nPath : {pathEntry.get()}")
      appInfo = ApplicationFrame(appListInnerFrame, nameEntry.get(), pathEntry.get())
      appInfo.create()
      nameEntry.delete("0", "end")
      pathEntry.delete("0", "end")


    tk.Button(dataAddFrame, text="Registration", command=app_add).pack(side="top", fill="both", padx=4, pady=4)

    datas = load_pathDatas()
    if datas is None:
      print("ERROR: Failed to load data file.")
      sys.exit()
    
    for appName, appPath in datas.items():
      appInfo = ApplicationFrame(appListInnerFrame, appName, appPath)
      appInfo.create()
    
    windowR.mainloop()





if __name__ == "__main__":
   main()