#@+leo-ver=5-thin
#@+node:ekr.20241022090855.1: * @file leoJupytext.py
"""
Support for pairing .ipynb and .py files with jupytext.

https://github.com/mwouts/jupytext
"""

#@+<< leoJupytext: imports and annotations >>
#@+node:ekr.20241022093347.1: ** << leoJupytext: imports and annotations >>
from __future__ import annotations
import io
import os
from typing import Any, Dict, Tuple, TYPE_CHECKING

try:
    import jupytext  # pylint: disable=unused-import
    has_jupytext = True
except Exception:
    has_jupytext = False

from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
#@-<< leoJupytext: imports and annotations >>

#@+others
#@+node:ekr.20241022093215.1: ** class JupytextManager
class JupytextManager:

    use_sentinels = False  # True: @file, False: @clean

    #@+others
    #@+node:ekr.20241023162459.1: *3* jtm.dump_notebook
    def dump_notebook(self, nb: Any) -> None:
        """Dump a notebook (class nbformat.notebooknode.NotebookNode)"""
        g.trace(g.callers())
        # keys are 'cells', 'metadata', 'nbformat', 'nbformat_minor'.
        if 0:
            for z in nb:
                print(f"{z:>20} {nb[z]}")
        if 1:
            print('metadata...')
            d = nb['metadata']
            for z in d:
                print(f"{z}: {g.objToString(d[z])}")
        if 1:
            print('')
            print('cells...')
            for i, cell in enumerate(nb['cells']):
                print(f"cell {i}: {g.objToString(cell)}")
    #@+node:ekr.20241023152818.1: *3* jtm.full_path
    def full_path(self, c: Cmdr, p: Position) -> str:
        """
        Return the full path in effect for the `@jupytext x.ipynb` node at p.
        
        On errors, print an error message and return ''.
        """
        if not has_jupytext:
            self.warn_no_jupytext()
            return  ''
        if not p.h.startswith('@jupytext'):
            g.trace(f"Can not happen: not an @jupytext node: {p.h!r}")
            return ''
        path = p.h[len('@jupytext') :].strip()
        return path
    #@+node:ekr.20241024160108.1: *3* jtm.get_jupytext_config_file
    def get_jupytext_config_file(self) -> str:
        """
        Print the name and contents of the jupytext config file in effect.
        Call this method with this Leonine script:
        
            g.app.jupytextManager.get_jupytext_config_file()
        """
        from jupytext.config import find_jupytext_configuration_file
        import tomllib
        config_file = find_jupytext_configuration_file(os.getcwd())
        if config_file:
            with open(config_file, 'rb') as f:
                data = tomllib.load(f)
                g.printObj(data, tag=f"jupytext: contents of {config_file!r}")
        return config_file
    #@+node:ekr.20241023155136.1: *3* jtm.read
    def read(self, c: Cmdr, p: Position) -> Tuple[str, str]:  # pragma: no cover
        """
        p must be an @jupytext node describing an .ipynb file.
        Convert x.ipynb to a string s.
        Return (s, path)
        """
        path = self.full_path(c, p)
        if not path:
            # full_path has given the error.
            return '', ''
        if not os.path.exists(path):
            self.warn_bad_at_jupytext_node(p, path)
            return '', ''

        # Read the .ipynb file into contents.
        # Use jupytext.write, *not* jupytext.writes.
        fmt = c.config.getString('jupytext-fmt') or 'py:percent'
        notebook = jupytext.read(path, fmt=fmt)
        with io.StringIO() as f:
            jupytext.write(notebook, f, fmt=fmt)
            contents = f.getvalue()
        return contents, path
    #@+node:ekr.20241023073354.1: *3* jtm.update
    def update(self, c: Cmdr, p: Position, path: str) -> None:
        """
        Update the @jupytext node at p when the path has changed externally.
        """
        at = c.atFileCommands
        at.readOneAtJupytextNode(p)
        c.redraw()
    #@+node:ekr.20241023165243.1: *3* jtm.warn_bad_at_jupytext_node
    bad_paths: Dict[str, bool] = {}

    def warn_bad_at_jupytext_node(self, p: Position, path: str) -> None:
        """Warn (once) about each bad path"""
        if path not in self.bad_paths:
            key = path if path else 'None'
            self.bad_paths[key] = True
            print('')
            g.es_print(f"Bad @jupytext node: {p.h!r}", color='red')
            g.es_print(f"File not found: {path!r}", color='blue')
            print('')
    #@+node:ekr.20241023161034.1: *3* jtm.warn_no_jupytext
    warning_given = False

    def warn_no_jupytext(self) -> None:
        """Warn (once) that jupytext is not available"""
        if not self.warning_given:
            self.warning_given = True
            print('')
            g.es_print('can not import `jupytext`', color='red')
            g.es_print('`pip install jupytext`', color='blue')
            print('')
    #@+node:ekr.20241023155519.1: *3* jtm.write
    def write(self, c: Cmdr, p: Position, contents: str) -> None:
        """
        - Check that p is an @jupytext node. 
        - Write the .ipynb file corresponding to p.b
        """
        path = self.full_path(c, p)
        if not path:
            # full_path has given the error.
            return

        # Write the .ipynb file.
        # Write the paired .py file, only if fmt specifies pairing.
        # See https://jupytext.readthedocs.io/en/latest/config.html
        fmt = c.config.getString('jupytext-fmt') or 'py:percent'
        notebook = jupytext.reads(contents, fmt=fmt)
        jupytext.write(notebook, path, fmt=fmt)
    #@-others
#@-others

#@-leo
