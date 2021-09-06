# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210901140718.1: * @file ../unittests/test_syntax.py
#@@first
"""Syntax tests, including a check that Leo will continue to load!"""
# pylint: disable=no-member
import glob
import os
import subprocess
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20210901140855.1: ** class TestSyntax(LeoUnitTest)
class TestSyntax(LeoUnitTest):
    """Unit tests checking syntax of Leo files."""
    #@+others
    #@+node:ekr.20210901140645.1: *3* TestSyntax.tests...
    #@+node:ekr.20210901140645.21: *4* TestSyntax.test_syntax_of_all_files
    def test_syntax_of_all_files(self):
        c = self.c
        failed,n = [],0
        skip_tuples = (
            ('extensions','asciidoc.py'),
        )
        join = g.os_path_finalize_join
        skip_list = [join(g.app.loadDir,'..',a,b) for a,b in skip_tuples]
        for theDir in ('core', 'external', 'extensions', 'plugins', 'scripts', 'test'):
            path = g.os_path_finalize_join(g.app.loadDir,'..',theDir)
            assert g.os_path_exists(path),path
            aList = glob.glob(g.os_path_join(path,'*.py'))
            if g.isWindows:
                aList = [z.replace('\\','/') for z in aList]
            for z in aList:
                if z in skip_list:
                    pass # print('%s: skipped: %s' % (p.h,z))
                else:
                    n += 1
                    fn = g.shortFileName(z)
                    s,e = g.readFileIntoString(z)
                    if not c.testManager.checkFileSyntax(fn,s,reraise=False,suppress=False):
                        failed.append(z)
        assert not failed,'failed %s\n' % g.listToString(failed)
    #@+node:ekr.20210901140645.22: *4* TestSyntax.test_syntax_of_setup_py
    def test_syntax_of_setup_py(self):
        c = self.c
        fn = g.os_path_finalize_join(g.app.loadDir, '..', '..', 'setup.py')
        # Only run this test if setup.py exists: it may not in the actual distribution.
        if not g.os_path_exists(fn):
            self.skipTest('setup.py not found')
        s, e = g.readFileIntoString(fn)
        c.testManager.checkFileSyntax(fn, s, reraise=True, suppress=False)
    #@+node:ekr.20210906062410.1: *4* TestSyntax.test_load_leo_file
    def test_load_leo_file(self):
        # Make sure that Leo can still load!
        trace = False
        test_dot_leo = g.os_path_finalize_join(g.app.loadDir, '..', 'test', 'test.leo')
        assert os.path.exists(test_dot_leo)
        gui = 'null' #, 'Qt'
        trace = '--trace=startup' if trace else ''
        # --quit suppresses the loading of settings files for greater speed.
        command = f"leo {test_dot_leo} --quit --gui={gui} --no-plugins --silent {trace}"
        proc = subprocess.Popen(command, stdout=subprocess.DEVNULL, shell=True)
        proc.communicate()
    #@-others
#@-others
#@-leo
