"""
Terminator plugin to open a file using a chosen editor.

Author: michele.silva@gmail.com
License: GPLv2
Site: https://github.com/mchelem/terminator-editor-plugin
"""
import inspect
import os
import re
import shlex
import subprocess
from terminatorlib import plugin, config
from typing import Optional
from pprint import pprint

AVAILABLE = ["EditorPlugin"]

DEFAULT_COMMAND = "gvim --remote-silent +{line} {filepath}"
DEFAULT_REGEX = r"([^ \t\n\r\f\v:]+?):([0-9]+)"
DEFAULT_GROUPS = "file line"
DEFAULT_OPEN_IN_CURRENT_TERM = False


def to_bool(val):
    return val == "True"


class EditorPlugin(plugin.URLHandler):
    """Process URLs returned by commands."""

    capabilities = ["url_handler"]
    handler_name = "editorurl"
    nameopen = "Open File"
    namecopy = "Copy Open Command"

    def __init__(self):
        self.plugin_name = self.__class__.__name__
        self.config = config.Config()
        self.check_config()
        self.match = self.config.plugin_get(self.plugin_name, "match")
        if hasattr(self.match, "decode"):
            self.match = self.match.decode("string_escape")

    def check_config(self):
        config = {
            "command": DEFAULT_COMMAND,
            "match": DEFAULT_REGEX,
            "groups": DEFAULT_GROUPS,
            "open_in_current_term": DEFAULT_OPEN_IN_CURRENT_TERM,
        }
        saved_config = self.config.plugin_get_config(self.plugin_name)
        if saved_config is not None:
            config.update(saved_config)
        config["open_in_current_term"] = to_bool(config["open_in_current_term"])
        self.config.plugin_set_config(self.plugin_name, config)
        self.config.save()

    def get_terminal(self):
        # HACK: Because the current working directory is not available to
        # plugins, we need to use the inspect module to climb up the stack to
        # the Terminal object and call get_cwd() from there.
        for frameinfo in inspect.stack():
            frameobj = frameinfo[0].f_locals.get("self")
            if frameobj and frameobj.__class__.__name__ == "Terminal":
                return frameobj

    def get_cwd(self):
        """Return current working directory."""
        term = self.get_terminal()
        if term:
            return term.get_cwd()

    def open_url(self):
        """Return True if we should open the file."""
        # HACK: Because the plugin doesn't tell us we should open or copy
        # the command, we need to climb the stack to see how we got here.
        return inspect.stack()[3][3] == "open_url"

    def callback(self, strmatch):
        cwd = self.get_cwd()
        libdir = self.config.plugin_get(self.plugin_name, "libdir")
        config = self.config.plugin_get_config(self.plugin_name)

        filepath, line, column = findmatch(config, cwd, libdir, strmatch)

        if filepath:
            command = self.config.plugin_get(self.plugin_name, "command")
            command = command.replace("{filepath}", filepath)
            command = command.replace("{line}", str(line))
            command = command.replace("{column}", str(column))
            if self.open_url():
                if self.config.plugin_get(self.plugin_name, "open_in_current_term"):
                    self.get_terminal().feed(command + "\n")
                else:
                    subprocess.call(shlex.split(command))
                return "--version"
            return command


def search_filepath_in_libdir(libdir: Optional[str], filepart: str):
    filename = filepart.split("/")[-1]

    for dirpath, dirnames, filenames in os.walk(os.path.expanduser(libdir)):
        for name in filenames:
            if name == filename:
                return os.path.join(dirpath, name)


def search_filepath(cwd: str, libdir: Optional[str], filepart: str):
    if os.path.exists(filepart):
        return (filepart, True)

    cwd_filepath = os.path.join(cwd, filepart)
    if os.path.exists(cwd_filepath):
        return (cwd_filepath, True)

    if libdir:
        libdir_filepath = search_filepath_in_libdir(libdir, filepart)
        if os.path.exists(libdir_filepath):
            return (libdir_filepath, True)

    return (None, False)


def findmatch(config, cwd: str, libdir: Optional[str], io_line: str):
    regex = config["match"]
    group_names = config["groups"].split()

    # print("io_line")
    # print(io_line)
    # print()

    result = {
        "match": None,
        "file": None,
        "line": 1,
        "column": 1,
        "exists": False,
    }

    match = re.match(regex, io_line)

    # print("match")
    # print(match)
    # print()

    if match is None:
        return result

    groups = [group for group in match.groups() if group is not None]

    # print("groups")
    # pprint(groups)
    # print()

    for group_value, group_name in zip(groups, group_names):
        if group_name == "file":
            (filepath, exists) = search_filepath(cwd, libdir, group_value)
            result["match"] = group_value
            result["file"] = filepath
            result["exists"] = exists

        elif group_name == "line":
            line = group_value.replace(":", "")
            if line.isdigit():
                result["line"] = int(line)

        elif group_name == "column":
            column = group_value.replace(":", "")
            if column.isdigit():
                result["column"] = int(column)
    return result
