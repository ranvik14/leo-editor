#@+leo-ver=5-thin
#@+node:ekr.20241030151621.1: * @file ../modes/jupytext.py
#@@language python
"""
leo/modes/jupytext.py, Leo's colorizer for @language jupytext.
"""
#@+<< jupytext.py: imports >>
#@+node:ekr.20241031140333.1: ** << jupytext.py: imports >>
from __future__ import annotations

from leo.core import leoGlobals as g
assert g
#@-<< jupytext.py: imports >>
#@+<< jupytext.py: rules >>
#@+node:ekr.20241031024909.1: ** << jupytext.py: rules >>

# n > 0: success.
# n == 0: temporary failure.
# n < 0: total failure, skip n chars.

#@+others
#@+node:ekr.20241031024939.2: *3* jupytext_comment
def jupytext_comment(colorer, s, i) -> int:
    """
    Color a *single line* in the appropriate state.
    
    Return: n > 1 if n characters match, otherwise -1.
    """
    if 1:
        print('')
        g.trace(repr(s))
        print('')
    assert s[i] == '#'
    marker = '# %%'  # Matches the start of Python and Markdown modes.

    # Colorize *this* line.
    colorer.match_line(s, i, kind='comment1')

    line = s.strip()

    if line.startswith(marker):
        # Colorize the *next* lines until the predicate matches.

        def predicate(s: str) -> bool:
            return s.strip().startswith(marker)

        delegate = (
            'md:md_main' if line.startswith('# %% [markdown]')
            else 'python:python_main'
        )
        colorer.match_span_delegated_lines(s, i,
            delegate=delegate, predicate=predicate)

    return -1  # This line has been completely handled.
#@+node:ekr.20241031024936.1: *3* jupytext_keyword
def jupytext_keyword(colorer, s, i):
    return colorer.match_keywords(s, i)

#@-others

#@-<< jupytext.py: rules >>
#@+<< jupytext.py: interface dicts >>
#@+node:ekr.20241101031846.1: ** << jupytext.py: interface dicts >>
properties = {}

jupytext_rules_dict = {
    '@': [jupytext_keyword],
    '#': [jupytext_comment],
}

rulesDictDict = {
    "jupytext_main": jupytext_rules_dict,
}
#@-<< jupytext.py: interface dicts >>
#@-leo
