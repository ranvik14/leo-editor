#@+leo-ver=5-thin
#@+node:ekr.20211209153303.1: * @file ../plugins/importers/python.py
"""The new, tokenize based, @auto importer for Python."""
from __future__ import annotations
import re
from typing import List, TYPE_CHECKING
import leo.core.leoGlobals as g
from leo.plugins.importers.linescanner import Block, Importer
if TYPE_CHECKING:
    assert g
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
#@+others
#@+node:ekr.20220720043557.1: ** class Python_Importer
class Python_Importer(Importer):
    """Leo's Python importer"""
    
    string_list = ['"""', "'''", '"', "'"]  # longest first.
    
    # The default patterns. Overridden in the Cython_Importer class.
    async_def_pat = re.compile(r'\s*async\s+def\s*(\w+)\s*\(')
    def_pat = re.compile(r'\s*def\s*(\w+)\s*\(')
    class_pat = re.compile(r'\s*class\s*(\w+)')
    block_patterns = (
        ('class', class_pat),
        ('async def', async_def_pat),
        ('def', def_pat),
    )

    def __init__(self, c: Cmdr, language: str = 'python') -> None:
        """Py_Importer.ctor."""
        super().__init__(c, language=language, strict=True)

    #@+others
    #@+node:ekr.20230514140918.1: *3* python_i.find_blocks & helper (override)
    def find_blocks(self, i1: int, i2: int) -> List[Block]:
        """
        Python_Importer.find_blocks: override Importer.find_blocks.

        Find all blocks in the given range of *guide* lines from which blanks
        and tabs have been deleted.

        Return a list of Blocks, that is, tuples(name, start, start_body, end).
        """
        i, prev_i, result = i1, i1, []
        while i < i2:
            s = self.guide_lines[i]
            # g.trace(repr(s))
            i += 1
            for kind, pattern in self.block_patterns:
                m = pattern.match(s)
                if m:
                    name = m.group(1).strip()  # cython may include trailing whitespace.
                    end = self.find_end_of_block(i, i2)
                    assert i1 + 1 <= end <= i2, (i1, end, i2)
                    result.append((kind, name, prev_i, i, end))
                    i = prev_i = end
                    break
        # g.printObj(result, tag=f"python_i.findblocks: {i1}:{i2}")
        return result
    #@+node:ekr.20230514140918.4: *4* python_i.find_end_of_block
    def find_end_of_block(self, i: int, i2: int) -> int:
        """
        i is the index of the class/def line (within the *guide* lines).

        Return the index of the line *following* the entire class/def
        """
        def lws_n(s: str) -> int:
            """Return the length of the leading whitespace for s."""
            return len(s) - len(s.lstrip())

        prev_line = self.guide_lines[i-1]
        assert any(z in prev_line for z in ('class', 'def')), (i, repr(prev_line))
        if i < i2:
            lws1 = lws_n(prev_line)
            while i < i2:
                s = self.guide_lines[i]
                i += 1
                if s.strip() and lws_n(s) <= lws1:
                    return i - 1
        return i2
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for python."""
    Python_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.py', '.pyw', '.pyi', '.codon'],  # mypy uses .pyi extension.
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
