#!/usr/bin/env python3
import os
os.environ["PYTHONUTF8"] = "1"
import logging
from pathlib import Path
from file_dir import RES_PATH,up_res_path,log_file_path,parent_dir
import sys

frozen = 0
#RES_PATH = Path(__file__).parent / "Easy_Code_res"
#up_res_path =Path(__file__).parent
#log_file_path = Path(RES_PATH) / 'error_log.txt'

log_dir = os.path.dirname(log_file_path)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
with open(log_file_path, 'w') as file:
    file.close()
logging.basicConfig(filename=log_file_path, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logging.error(f"log in frozen=: {str(frozen)}", exc_info=True)
def excepthook(type, value, traceback):
    logging.error(f"An unhandled error occurred: {type.__name__}: {value}", exc_info=(type, value, traceback))
print("parent_dir=",parent_dir)
sys.path.insert(0, parent_dir)
from voice_code import main


if __name__ == "__main__":
    sys.excepthook = excepthook
    main_window = main(up_res_path)

