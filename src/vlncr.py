import argparse
import sys
import os
import json
import subprocess
import itertools

APP_VERSION = "1.2.0-CLI"
PATH_APPLICATION_PATHDATA = "paths.json"
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

class Exception_TypeError(Exception):
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

def load_path_datas() -> dict:
  conf_path = get_path(PATH_APPLICATION_PATHDATA)
  if not os.path.exists(conf_path):
    with open(conf_path, "w", encoding="utf-8") as f:
      json.dump({}, f, indent=2)
      return {}
  else:
    with open(conf_path, "r", encoding="utf-8") as f:
      return json.load(f)

def save_path_datas(datas):
  conf_path = get_path(PATH_APPLICATION_PATHDATA)
  with open(conf_path, "w", encoding="utf-8") as f:
    json.dump(datas, f, indent=2)

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
    for index, format_chr in enumerate(output_format):
      if format_chr == '<':
        left_pos = index
        left_open = True
        continue
      if format_chr == '>' and left_open:
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
      raise Exception_TypeError(source, "'list'")

def dict_to_list(target_dict: dict) -> list:
  use_dict = target_dict.copy()
  for dict_name, dict_value in use_dict.items():
    if not isinstance(dict_value, list):
      use_dict[dict_name] = [dict_value]
  
  return [list(itertools.chain([s_name], s_value)) for s_name, s_value in use_dict.items()]


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

  args = parser.parse_args()

  if args.command is None:
    parser.print_help()

  ########## add(registration) ##########
  elif args.command == "add":
    try:
      datas = load_path_datas()
    except Exception as e:
      print(f"ERROR: Failed to load data file. ({str(e)})")
      sys.exit()

    if (not args.overwrite) and (args.app_name in datas):
      print("ERROR: Application is already registered.")
      sys.exit()

    if args.overwrite and (not args.app_name in datas):
      print("ERROR: Application is not registered.")
      sys.exit()
    
    if not os.path.isabs(args.app_path):
      print("ERROR: The path is not an absolute path.")
      sys.exit()
    
    if not os.path.isfile(args.app_path):
      print(f"ERROR: The file does not exist. | Path: {args.app_path}")
      sys.exit()

    datas[args.app_name] = args.app_path

    try:
      save_path_datas(datas)
    except Exception as e:
      print(f"ERROR: Failed to save data file. ({str(e)})")

  ########## delete ##########
  elif args.command == "del":
    try:
      datas = load_path_datas()
    except Exception as e:
      print(f"ERROR: Failed to load data file. ({str(e)})")
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
    try:
      save_path_datas(datas)
    except Exception as e:
      print(f"ERROR: Failed to save data file. ({str(e)})")

  ########## run(execution) ##########
  elif args.command == "run":
    try:
      datas = load_path_datas()
    except Exception as e:
      print(f"ERROR: Failed to load data file. ({str(e)})")
      sys.exit()
    
    if not args.app_name in datas:
      print("ERROR: This is an unregistered application.")
      sys.exit()
    
    if not os.path.isabs(datas.get(args.app_name)):
      print(f"ERROR: The path format is invalid.\n= = = = = = = = = =\nPath: {datas.get(args.app_name)}")
      sys.exit()

    if not os.path.isfile(datas.get(args.app_name)):
      print(f"ERROR: Executable file not found. \n= = = = = = = = = =\nPath: {datas.get(args.app_name)}")
      sys.exit()

    exe_app_args = [datas.get(args.app_name)] + [str(arg) for arg in args.app_args]

    try:
      subprocess.run(args=exe_app_args)
    except Exception as e:
      print(f"ERROR: Execution application Error\n{str(e)}")

  ########## lsit ##########
  elif args.command == "list":
    try:
      datas = load_path_datas()
    except Exception as e:
      print(f"ERROR: Failed to load data file. ({str(e)})")
      sys.exit()
    
    print("================================================================")
    print("application : path")
    print("----------------------------------------------------------------") 
    uniform_spacing_print(dict_to_list(datas), "<0> : <1>")
    print("----------------------------------------------------------------") 
    print(f"Total: {len(datas)}")




if __name__ == "__main__":
   main()