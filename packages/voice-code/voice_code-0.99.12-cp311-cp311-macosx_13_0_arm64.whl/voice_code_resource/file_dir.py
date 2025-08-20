#!/usr/bin/env python3
import os
os.environ["PYTHONUTF8"] = "1"
import logging
from pathlib import Path
import sys

frozen = 0
RES_PATH = Path(__file__).parent / "Easy_Code_res"
up_res_path =Path(__file__).parent
log_file_path = Path(RES_PATH) / 'error_log.txt'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))


