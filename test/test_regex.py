import pytest
import os
from editor_plugin import findmatch

cwd = os.getcwd()
file = os.path.join(cwd, "editor_plugin.py")
libdir = ""


config = {
    "command": "vscodium --goto {filepath}:{line}",
    # 'match': r'([^ \t\n\r\f\v\(:]+?\.([a-zA-Z][\w]{1,20}))([ \n:]|$)([0-9]+)*([ \n:]|$)([0-9]+)*',
    # 'match': r'([^:\(\s]+?\.([a-zA-Z][\w]{1,20}))([ \n:]|$)([0-9]+)*([ \n:]|$)([0-9]+)*',
    # 'match': r'([^:\(\s]+?\.([\w]{1,20}))([\s:]|$)([0-9]+)*([\s:]|$)([0-9]+)*',
    # 'match': r'([^:\(\s]+?\.?([\w]{1,30}))([ :\n]|$)([0-9]+)*([\s:]|$)([0-9]+)*',
    # 'match': r'([^:\(\s]+([\.\w]{1,30}))([ :\n]|$)([0-9]+)*([\s:]|$)([0-9]+)*',
    # 'match': r'[\(: \n]?([~\/a-zA-Z][^:\(\s]+[\.\w]+)(:([0-9]+)){0,1}(:([0-9]+)){0,1}',
    # 'match': r'([~\/a-zA-Z][^:\(\s]+[\.\w]+)(:([0-9]+)){0,1}(:([0-9]+)){0,1}',
    # 'match': r'([^:\(\s]+[\.\w]+)(:([0-9]+)){0,1}(:([0-9]+)){0,1}',
    # "match": r"([^:\(\s]+[\w\-.]+)(:([0-9]+)){0,1}(:([0-9]+)){0,1}",
    # "match": r"([^:\(\s]*[\w\-.]+)(:([0-9]+)){0,1}(:([0-9]+)){0,1}",
    # "match": r"(([^ !$`&*()+]|(\[ !$`&*()+]))+)(:([0-9]+)){0,1}(:([0-9]+)){0,1}",
    "match": r"[^a-zA-Z/]*([^\0\t\n\r\f\v\(:'\")]+)(:[0-9]+)?(:[0-9]+)?[^a-zA-Z/]*",
    "groups": "file line column",
    # "match": r"(((?=\/)|\.|\.\.)(\/(?=[^/\0])[^/\0]+)*\/?)(:([0-9]+)){0,1}(:([0-9]+)){0,1}",
    # "match": r"((?:[a-zA-Z]\:){0,1}(?:[\\/][\w.]+){1,})",
    # "match": r"([^ \t\n\r\f\v:]+?)(:([0-9]+)){0,1}(:([0-9]+)){0,1}",
    # "match": r"([^ \t\n\r\f\v:]+)(:([0-9]+)){0,1}(:([0-9]+)){0,1}",
}


@pytest.mark.parametrize(
    "cwd, libdir, strmatch, expected",
    [
        (cwd, libdir, file, (file, file, 1, 1)),
        (cwd, libdir, file + ":", (file, file, 1, 1)),
        (cwd, libdir, file + ":2", (file, file, 2, 1)),
        (cwd, libdir, file + ":3:", (file, file, 3, 1)),
        (cwd, libdir, file + ":4:5", (file, file, 4, 5)),
        (cwd, libdir, file + ":6:7:", (file, file, 6, 7)),
        (cwd, libdir, file + ":6:7:", (file, file, 6, 7)),
    ],
)
def test_findmatch_for_existing_file(cwd, libdir, strmatch, expected):
    assert findmatch(config, cwd, libdir, strmatch) == {
        "match": expected[0],
        "file": expected[1],
        "line": expected[2],
        "column": expected[3],
        "exists": True,
    }


@pytest.mark.parametrize(
    "cwd, libdir, strmatch, expected",
    [
        (cwd, libdir, file + "missing", (file + "missing", None, 1, 1)),
        (cwd, libdir, file + "missing:0", (file + "missing", None, 0, 1)),
        (cwd, libdir, file + "missing:9:8", (file + "missing", None, 9, 8)),
        (cwd, libdir, file + "missing:7:6:", (file + "missing", None, 7, 6)),
        (cwd, libdir, file + "missing:5:4::3", (file + "missing", None, 5, 4)),
    ],
)
def test_findmatch_for_non_existing_file(cwd, libdir, strmatch, expected):
    assert findmatch(config, cwd, libdir, strmatch) == {
        "match": expected[0],
        "file": expected[1],
        "line": expected[2],
        "column": expected[3],
        "exists": False,
    }


def test_mix_test():
    cwd = "/home/sitch/sites/chainapi/chainapi-api"
    line = "       test/chainapi/domains/apis/schemas/endpoint_parameter_test.exs:32: (test)\n"

    assert findmatch(config, cwd, libdir, line) == {
        "match": "test/chainapi/domains/apis/schemas/endpoint_parameter_test.exs",
        "file": "/home/sitch/sites/chainapi/chainapi-api/test/chainapi/domains/apis/schemas/endpoint_parameter_test.exs",
        "line": 32,
        "column": 1,
        "exists": True,
    }


def test_mix_string_console_output():
    cwd = "/home/sitch/sites/chainapi/chainapi-api"
    line = '"/home/sitch/sites/chainapi/chainapi-api/_build/dev/lib/chainapi/.mix"'
    assert findmatch(config, cwd, libdir, line) == {
        "match": "/home/sitch/sites/chainapi/chainapi-api/_build/dev/lib/chainapi/.mix",
        "file": "/home/sitch/sites/chainapi/chainapi-api/_build/dev/lib/chainapi/.mix",
        "line": 1,
        "column": 1,
        "exists": True,
    }


def test_pytest_test():
    cwd = "/home/sitch/sites/chainapi/chainapi-api"
    line = "test/test_regex.py::test_findmatch[/home/sitch/sites/terminator-editor-plugin--/home/sitch/sites/terminator-editor-plugin/editor_plugin.pymissing:0-expected7] ✓73%\n"
    assert findmatch(config, cwd, libdir, line) == {
        "match": "test/test_regex.py",
        "file": "test/test_regex.py",
        "line": 1,
        "column": 1,
        "exists": True,
    }
