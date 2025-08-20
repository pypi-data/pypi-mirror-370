# Various utilities

# GSE Proprietary Software License
# Copyright (c) 2025 Global Satellite Engineering, LLC. All rights reserved.
# This software and associated documentation files (the "Software") are the proprietary and confidential information of Global Satellite Engineering, LLC ("GSE"). The Software is provided solely for the purpose of operating applications distributed by GSE and is subject to the following conditions:

# 1. NO RIGHTS GRANTED: This license does not grant any rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell the Software.
# 2. RESTRICTED ACCESS: You may only access the Software as part of a GSE application package and only to the extent necessary for operation of that application package.
# 3. PROHIBITION ON REVERSE ENGINEERING: You may not reverse engineer, decompile, disassemble, or attempt to derive the source code of the Software.
# 4. PROPRIETARY NOTICES: You must retain all copyright, patent, trademark, and attribution notices present in the Software.
# 5. NO WARRANTIES: The Software is provided "AS IS", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement.
# 6. LIMITATION OF LIABILITY: In no event shall GSE be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the Software or the use or other dealings in the Software.
# 7. TERMINATION: This license will terminate automatically if you fail to comply with any of the terms and conditions of this license. Upon termination, you must destroy all copies of the Software in your possession.

# THE SOFTWARE IS PROTECTED BY UNITED STATES COPYRIGHT LAW AND INTERNATIONAL TREATY. UNAUTHORIZED REPRODUCTION OR DISTRIBUTION IS SUBJECT TO CIVIL AND CRIMINAL PENALTIES.

import subprocess
import sys
import os
import configparser
try:
    from colorama import init as cl_init
    from colorama import Fore, Style
    cl_init(autoreset = True)
    colors_ok = True
except:
    colors_ok = False
import sys
import re
from pathlib import Path
import yaml
import traceback
from queue import Queue
import threading

#######################################################################################################################
# Local functions and data

with_colors = colors_ok and sys.stdout.isatty()
debug_level = 0

# Default cross compiler (mpy-cross) arguments
mpy_cross_args = ["-msmall-int-bits=31"]

# Returned the text colored with the given color, unless colors are disabled or the program is not running in a tty
def colored(text, col):
    return getattr(Fore, col) + Style.BRIGHT + text + Style.RESET_ALL if with_colors else text

def red(text):
    return colored(text, 'RED')

def yellow(text):
    return colored(text, 'YELLOW')

def blue(text):
    return colored(text, 'BLUE')

def green(text):
    return colored(text, 'GREEN')

#######################################################################################################################
# Logging

# There is a single thread that handles logging.
log_q = Queue()
# Log kinds/levels (same values)
(LOG_KIND_NONE, LOG_KIND_ERR, LOG_KIND_WARN, LOG_KIND_INFO, LOG_KIND_DEBUG, LOG_KIND_DEBUG2, LOG_KIND_DEBUG3, LOG_TOT_LEVELS) = range(8)
# Log prefixes for the levels above
log_prefixes = ("", "[ERROR]", "[WARNING]", "[INFO]", "[DEBUG]", "[DEBUG2]", '[DEBUG3]')
# Colors for the levels above
log_colors = ("", "RED", "YELLOW", "BLUE", "GREEN", "GREEN", "GREEN")
# Semaphore for local logging
log_sem = threading.Semaphore(0)

# Logging server that serializes log messages from various sources
class LogServer():
    def __init__(self, q):
        self.q = q

    # Output the given log
    def output_log(self, kind, name, text, raw, sem):
        if raw:
            msg = text
        else:
            msg = log_prefixes[kind]
            if name:
                msg += f"[{name}]"
            msg += " " + text
            if not msg.endswith("\n"):
                msg += "\n"
            if log_colors[kind]:
                msg = colored(msg, log_colors[kind])
        # Console output
        if kind in (LOG_KIND_ERR, LOG_KIND_WARN):
            sys.stderr.write(msg)
        else:
            sys.stdout.write(msg)
            sys.stdout.flush()
        if sem:
            sem.release()

    # Thread entry function
    def run(self):
        while True:
            (req, data) = self.q.get()
            if req == "log":
                self.output_log(data[0], data[1], data[2], data[3], data[4])

def error(text, name="", raw=False, sync=log_sem):
    log_q.put(("log", (LOG_KIND_ERR, name, text, raw, sync)))
    if sync:
        sync.acquire()

def warning(text, name="", raw=False, sync=log_sem):
    log_q.put(("log", (LOG_KIND_WARN, name, text, raw, sync)))
    if sync:
        sync.acquire()

def info(text, name="", raw=False, sync=log_sem):
    log_q.put(("log", (LOG_KIND_INFO, name, text, raw, sync)))
    if sync:
        sync.acquire()

def debug(text, name="", raw=False, sync=log_sem):
    if debug_level >= 1:
        log_q.put(("log", (LOG_KIND_DEBUG, name, text, raw, sync)))
        if sync:
            sync.acquire()

def debug2(text, name="", raw=False, sync=log_sem):
    if debug_level >= 2:
        log_q.put(("log", (LOG_KIND_DEBUG2, name, text, raw, sync)))
        if sync:
            sync.acquire()

def debug3(text, name="", raw=False, sync=log_sem):
    if debug_level >= 3:
        log_q.put(("log", (LOG_KIND_DEBUG3, name, text, raw, sync)))
        if sync:
            sync.acquire()

def set_debug_level(level):
    global debug_level
    debug_level = level

def get_debug_level():
    return debug_level

def fatal(text, code=1):
    error(text)
    sys.exit(code)

# Enable or disable colors in logs
def enable_log_colors(enable):
    global with_colors
    with_colors = colors_ok and enable

# Logger class with custom level
class Logger:
    def __init__(self, name, level=LOG_KIND_DEBUG3):
        self.name = name
        self.level = level

    def set_level(self, level):
        self.level = level

    def error(self, text):
        if self.level >= LOG_KIND_ERR:
            error(text, name=self.name)

    def warning(self, text):
        if self.level >= LOG_KIND_WARN:
            warning(text, name=self.name)

    def info(self, text):
        if self.level >= LOG_KIND_INFO:
            info(text, name=self.name)

    def debug(self, text):
        if self.level >= LOG_KIND_DEBUG:
            debug(text, name=self.name)

    def debug2(self, text):
        if self.level >= LOG_KIND_DEBUG2:
            debug2(text, name=self.name)

    def debug3(self, text):
        if self.level >= LOG_KIND_DEBUG3:
            debug3(text, name=self.name)

    def fatal(self, text, code=1):
        error(text, name=self.name)
        sys.exit(code)

########################################################################################################################
# Other functions

# Run the given command (either a string or an array)
# If "must_succeed" is True, the program exits with error if the command fails
# If 'silent' is True, the output of the command is not displayed
# If 'show_cmd' is given, display the command line
# If 'abbrev_cmd' is True, display only the command name instead of the whole command line
def run_command(cmd, must_succeed=True, silent=True, show_cmd=True, abbrev_cmd=False):
    res, res_stdout, res_stderr = 0, None, None
    cmd_as_str = cmd if isinstance(cmd, str) else " ".join(cmd)
    if show_cmd:
        s = cmd_as_str.split(' ')[0] if abbrev_cmd else cmd_as_str
        info("Running '{}'".format(s))
    if isinstance(cmd, str):
        cmd = cmd.split(' ')
    try:
        if silent:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            p = subprocess.Popen(cmd, stdout=sys.stdout.fileno(), stderr=sys.stderr.fileno())
    except:
        if must_succeed:
            fatal("Error creating subprocess, exiting")
        else:
            res = 255
    if res == 0:
        res_stdout, res_stderr = p.communicate()
        if p.returncode != 0 and must_succeed:
            error("'{0}' exited with error code {1:d}".format(cmd, p.returncode))
            fatal(res_stderr.decode("ascii") if silent else "Exiting")
        else:
            res = p.returncode
    return (res, res_stdout, res_stderr)

# Try to convert the given variable to an integer, returning its value or None for error
def to_int(n):
    if isinstance(n, str):
        # Is this a hex number
        if re.fullmatch(r"[\+\-]?0[xX][0-9a-fA-F]+", n):
            return int(n, base=16)
        elif re.fullmatch(r"[\+\-]?[0-9]+", n):
            return int(n, base=10)
        else:
            return None
    else: # not sure that this branch is actually needed
        try:
            return int(n)
        except (ValueError, TypeError):
            return None

# Try to convert the given variable to a floating point number, returning its value or None for error
def to_float(n):
    if isinstance(n, str):
        try:
            n = float(n)
        except ValueError:
            return None
    return n

# Return True if the given argument is an integer or can be converted to an integer, False otherwise
def is_int(n):
    return to_int(n) != None

# Return the final path of the configuration file, given the user provided argument in command line
# First, check if cfg_arg contains a valid path (if not None).
# If not, try the GSE_TOOLS_CONFIG_FILE environment variable (if not None)
# If not, try standard paths
def get_config_file_path(cfg_arg, must_exist=False):
    # Try the command line argument first
    config_path = cfg_arg
    # Then look in the environment
    if config_path == None:
        config_path = os.environ.get("GSE_TOOLS_CONFIG_FILE", default=None)
    # Look in the standard paths
    if config_path == None:
        config_path = os.environ.get('APPDATA') or os.environ.get('XDG_CONFIG_HOME') or os.path.join(os.environ['HOME'],
            '.config')
        config_path = os.path.join(config_path, "gse_tools.ini")
    if must_exist and not os.path.isfile(config_path):
        fatal("Config file {} not found or not a regular file".format(config_path))
    debug2("Configuration file path is {}".format(config_path))
    return config_path

# Read the configuration, given the user provided argument in command line
# Returns the configuration parser instance for success or None for error
def read_config(cfg_arg=None, must_exist=False):
    config_path = get_config_file_path(cfg_arg, must_exist)
    config, config_ok, res = configparser.ConfigParser(), False, {}
    if os.path.isfile(config_path):
        try:
            config_ok = len(config.read(config_path)) == 1
        except:
            pass
    if not config_ok:
        warning("Config file {} not found or invalid".format(config_path))
        return res
    debug("Read configuration from {}".format(config_path))
    return {s:dict(config.items(s)) for s in config.sections()}

# Return the config entry in the given section
# If not found in the configuration file, the entry is looked up in the environment
# Returns the config entry value or None if not found
def get_config_entry(cfg, section, name, must_exist=False):
    res = None
    if section in cfg and name in cfg[section]:
        res = cfg[section][name]
    if res == None: # check for the entry in the environment
        entry_name = f"GSE_CONFIG_{section.upper()}_{name.upper()}"
        res = os.environ.get(entry_name, None)
    if must_exist and res == None:
        fatal(f"Required configuration key {name} in section {section} not found")
    return res

# Find and return the full path to the mpy-cross executable
def find_mpy_cross():
    res = None
    # Try to run directly first. If that succeeds, we're good to go
    (ok, _, _) = run_command("mpy-cross --version", must_succeed=False, silent=True, show_cmd=False)
    if ok == 0:
        info("Using 'mpy-cross' in $PATH")
        res = "mpy-cross"
    elif (mpy_cc := os.environ.get("GSEMGR_MPY_CC", None)) != None:
        (ok, _, _) = run_command([mpy_cc, "--version"], must_succeed=False, silent=True, show_cmd=False)
        if ok == 0:
            info(f"Using 'mpy-cross' from {mpy_cc}")
            res = mpy_cc
    return res

# Cross-compile the given Pyrhon source file
# Return the path to the cross-compiled file
def cross_compile(src_path, out_path=".", mpy_cross=None):
    if mpy_cross == None:
        mpy_cross = find_mpy_cross()
    # We are cross-compiling and we found a Python file, so cross-compile it now
    actual_f = Path(out_path) / Path(src_path).with_suffix(".mpy").name
    info(f"Cross-compiling {src_path} to {actual_f}")
    # If the environment variable GSE_MPY_BASE_DIR is set, make all the names relative to that directory
    extra_args = []
    if (base_dir := os.environ.get("GSE_MPY_BASE_DIR", None)) != None and os.path.isdir(base_dir):
        full_norm = os.path.normpath(os.path.abspath(src_path))
        rel_norm = os.path.normpath(os.path.abspath(base_dir))
        try:
            extra_args = ["-s", os.path.relpath(full_norm, rel_norm)]
        except: # apparently this can happen in Windows
            pass
    run_command([mpy_cross] + mpy_cross_args + extra_args + ["-o", str(actual_f), src_path], must_succeed=True,
        silent=True, show_cmd=False)
    return str(actual_f)

# Write to the given file only if it doesn't exist or its content is different from "data"
# Returns true if the file was written, False otherwise
def write_if_changed(fname, data):
    crt, res = None, False
    if os.path.isfile(fname):
        with open(fname, "rt") as f:
            crt = f.read()
    if crt != data:
        with open(fname, "wt") as f:
            f.write(data)
        info(f"Wrote {fname}")
        res = True
    else:
        debug(f"{fname} unchanged (not written)")
    return res

# Read and return the content of the given file
# Returns None if the file is not found and must_exist is False
def read_file(fname, binary=False, must_exist=True):
    if not os.path.isfile(fname):
        if must_exist:
            fatal(f"{fname} not found or not a regular file")
        else:
            return None
    else:
        with open(fname, "rb" if binary else "rt") as f:
            return f.read()

# Ensure that the given argument is a file, exit with a fatal error if it isn't
def must_be_file(fname):
    if not os.path.isfile(fname):
        fatal(f"{fname} not found or not a regular file")

# Ensure that the given argument is a directory, exit with a fatal error if it isn't
def must_be_dir(dname):
    if not os.path.isdir(dname):
        fatal(f"{dname} not found or not a directory")

# Parse the given file, looking for a #define <macro_name> <data>, where macro_name is an element of the "names" array
# Returns a ({macro_name: value} dictionary, n_found) where n_found is the number of found macros
# Returns None, 0 if the file is not found and must_exist is False
def search_macros_in_file(fname, names, must_exist=True):
    if (data := read_file(fname, must_exist=must_exist)) == None:
        return None, 0
    values, cnt = {}, 0
    for l in data.split("\n"):
        l = l.replace("\n", "").replace("\r", "")
        l = re.sub(r"\s+", " ", l) # replace multiple spaces with a single space
        l = re.sub(r"//.*$", "", l).strip().split(" ") # split using space as a delimiter
        if len(l) == 3 and l[0] == "#define" and l[1] in names: # this is a macro definition of interest
            if l[1] in values:
                fatal(f"Macro {l[1]} defined multiple times in {fname}")
            values[l[1]] = l[2]
            cnt += 1
            if cnt == len(names):
                break
    return values, cnt

# Reads and returns YAML data from the given file. Errors are treated as fatal
def read_yaml(fname):
    must_be_file(fname)
    try:
        with open(fname) as f:
            res = yaml.load(f, Loader=yaml.FullLoader)
    except:
        fatal(f"Unable to read YAML data from {fname}")
    return res

# Check if the given dictionary has only the keys in "allowed" and also the mandatory keys
def check_dict_keys(d, allowed, mandatory=None, source=None):
    d_set = set(list(d.keys()))
    a_set = set(allowed)
    m_set = set(mandatory) if mandatory != None else set()
    source_str = f"{source}: " if source != None else ""
    foreign = d_set - a_set
    if foreign:
        fatal(f"{source_str}Found unknown key(s) {','.join(foreign)}")
    absent = m_set - d_set
    if absent:
        fatal(f"{source_str}Required key(s) {','.join(absent)} not found")

# Write the current exception info as log messages
# If "ret" is not 0, also exit the process with the code "ret"
def handle_exc(header=None, ret=0):
    exc_info = traceback.format_exc()
    if header:
        error(header)
    for l in exc_info.split("\n"):
        error(l)
    if ret != 0:
        fatal("Aborting", ret)

# Apply escape sequences to the given string
def unescape(s):
    return s.encode().decode("unicode-escape")

# Start the loggin server on first import
log_server = LogServer(log_q)
threading.Thread(target=log_server.run, daemon=True).start()
