import pytest
import os
from editor_plugin import findmatch

cwd = os.getcwd()
file = os.path.join(cwd, 'editor_plugin.py')
libdir = ''


config = {
    'command': 'vscodium --goto {filepath}:{line}',
    # 'match': r'([^ \t\n\r\f\v\(:]+?\.([a-zA-Z][\w]{1,20}))([ \n:]|$)([0-9]+)*([ \n:]|$)([0-9]+)*',
    # 'match': r'([^:\(\s]+?\.([a-zA-Z][\w]{1,20}))([ \n:]|$)([0-9]+)*([ \n:]|$)([0-9]+)*',
    # 'match': r'([^:\(\s]+?\.([\w]{1,20}))([\s:]|$)([0-9]+)*([\s:]|$)([0-9]+)*',
    # 'match': r'([^:\(\s]+?\.?([\w]{1,30}))([ :\n]|$)([0-9]+)*([\s:]|$)([0-9]+)*',
    # 'match': r'([^:\(\s]+([\.\w]{1,30}))([ :\n]|$)([0-9]+)*([\s:]|$)([0-9]+)*',
    'match': r'([^:\(\s]+[\.\w]+)(:([0-9]+)){0,1}(:([0-9]+)){0,1}',
    'groups': 'file _line_separator line _column_separator column',
}

@pytest.mark.parametrize('cwd, libdir, strmatch, expected', [
    (cwd, libdir, file, (file, 1, 1)),
    (cwd, libdir, file + ':', (file, 1, 1)),
    (cwd, libdir, file + ':2', (file, 2, 1)),
    (cwd, libdir, file + ':3:', (file, 3, 1)),
    (cwd, libdir, file + ':4:5', (file, 4, 5)),
    (cwd, libdir, file + ':6:7:', (file, 6, 7)),

    # # File doesn't exist
    (cwd, libdir, file + 'missing', (None, 1, 1)),
    (cwd, libdir, file + 'missing:0', (None, 0, 1)),
    (cwd, libdir, file + 'missing:9:8', (None, 9, 8)),
    (cwd, libdir, file + 'missing:7:6:', (None, 7, 6)),
    (cwd, libdir, file + 'missing:5:4::3', (None, 5, 4)),
])
def test_findmatch(cwd, libdir, strmatch, expected):
    assert findmatch(config, cwd, libdir, strmatch) == expected

