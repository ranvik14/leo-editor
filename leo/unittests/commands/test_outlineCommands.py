#@+leo-ver=5-thin
#@+node:ekr.20221113062857.1: * @file ../unittests/commands/test_outlineCommands.py
"""
New unit tests for Leo's outline commands.

Older tests are in unittests/core/test_leoNodes.py
"""
import sys
from leo.core.leoTest2 import LeoUnitTest
from leo.core import leoGlobals as g
assert g
assert sys

#@+others
#@+node:ekr.20221113062938.1: ** class TestOutlineCommands(LeoUnitTest)
class TestOutlineCommands(LeoUnitTest):
    """
    Unit tests for Leo's outline commands.
    """

    #@+others
    #@+node:ekr.20221113064908.1: *3* TestOutlineCommands.create_test_sort_outline
    def create_test_sort_outline(self) -> None:
        """Create a test outline suitable for sort commands."""
        p = self.c.p
        assert p == self.root_p
        assert p.h == 'root'
        table = (
            'child a',
            'child z',
            'child b',
            'child w',
        )
        for h in table:
            child = p.insertAsLastChild()
            child.h = h


    #@+node:ekr.20221112051634.1: *3* TestOutlineCommands.test_sort_children
    def test_sort_children(self):
        c, u = self.c, self.c.undoer
        assert self.root_p.h == 'root'
        self.create_test_sort_outline()
        original_children = [z.h for z in self.root_p.v.children]
        sorted_children = sorted(original_children)
        c.sortChildren()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, sorted_children)
        u.undo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, original_children)
        u.redo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, sorted_children)
        u.undo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, original_children)
    #@+node:ekr.20221112051650.1: *3* TestOutlineCommands.test_sort_siblings
    def test_sort_siblings(self):
        c, u = self.c, self.c.undoer
        assert self.root_p.h == 'root'
        self.create_test_sort_outline()
        original_children = [z.h for z in self.root_p.v.children]
        sorted_children = sorted(original_children)
        c.selectPosition(self.root_p.firstChild())
        c.sortSiblings()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, sorted_children)
        u.undo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, original_children)
        u.redo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, sorted_children)
        u.undo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, original_children)
    #@+node:ekr.20230720202352.1: *3* TestOutlineCommands.test_paste_retaining_clones
    def test_paste_retaining_clones(self):

        c = self.c
        p = c.p
        u = c.undoer
        
        # Clear everything but the root node.
        assert p == self.root_p
        assert p.h == 'root'
        p.deleteAllChildren()
        while p.hasNext():
            p.next().doDelete()
            
        #@+<< Create the test tree >>
        #@+node:ekr.20230723085648.1: *4* << Create the test tree >>
            
        # Create the following tree:
        # aa
        # bb
        # child1 (clone)
        # cc
        #   child1 (clone)
        #   child2
        aa = p.insertAfter()
        aa.h = 'aa'
        bb = aa.insertAfter()
        bb.h = 'bb'
        cc = bb.insertAfter()
        cc.h = 'cc'
        child1 = cc.insertAsLastChild()
        child1.h = 'child1'
        child1_gnx = child1.gnx
        child2 = child1.insertAfter()
        child2.h = 'child2'
        child2_gnx = child2.gnx
        clone = child1.clone()
        clone.moveAfter(bb)
        assert clone.v == child1.v
        # Careful: position cc has changed.
        cc = clone.next()
        clone_v = clone.v
        cc_gnx = cc.gnx
        assert cc.h == 'cc'
        #@-<< Create the test tree >>

        # Cut node cc
        c.selectPosition(cc)
        c.cutOutline()
        assert not clone.isCloned()
        assert c.p == clone
        assert c.p.h == 'child1'

        # Execute paste-retaining-clones
        c.pasteOutlineRetainingClones()
        
        # Quick tests.
        self.assertFalse(c.checkOutline())
        for p in c.all_positions():
            if p.h == 'child1':
                assert p.isCloned(), p.h
                # The vnode never changes *and* all positions share the same vnode.
                assert p.v == clone_v, p.h
            else:
                assert not p.isCloned(), p.h

        # Other tests.

        # Recreate the positions.
        clone = bb.next()
        cc = clone.next()
        child1 = cc.firstChild()
        assert clone.v == clone_v
        assert cc.gnx == cc_gnx
        assert child1.gnx == clone.gnx
        self.assertEqual(id(child1.v), id(clone.v))
        assert cc.firstChild().gnx == child1_gnx
        assert cc.firstChild().next().gnx == child2_gnx
        assert clone.isCloned()  # Fails.
        assert cc.firstChild().isCloned()
        
        # Test multiple undo/redo cycles.
        for i in range(3):

            # Undo paste-retaining-clones.
            u.undo()
            self.assertFalse(c.checkOutline())
            for p in c.all_positions():
                assert not p.isCloned(), p.h
                if p.h == 'child1':
                    # The vnode never changes!
                    assert p.v == clone_v, p.h

            # Redo paste-retaining-clones.
            u.redo()
            self.assertFalse(c.checkOutline())
            for p in c.all_positions():
                if p.h == 'child1':
                    assert p.isCloned(), p.h
                    # The vnode never changes *and* all positions share the same vnode.
                    assert p.v == clone_v, p.h
                else:
                    assert not p.isCloned(), p.h
    #@+node:ekr.20230722083123.1: *3* TestOutlineCommands.test_restoreFromCopiedTree (revise)
    def test_restoreFromCopiedTree(self):

        ###from leo.core import leoGlobals as g ###

        # Clean the tree.
        c = self.c
        fc = c.fileCommands
        p = c.p
        u = c.undoer
        assert p == self.root_p
        assert p.h == 'root'
        
        #@+<< create test tree >>
        #@+node:ekr.20230722084237.1: *4* << create test tree >>
        p.deleteAllChildren()
        while p.hasNext():
            p.next().doDelete()

        # aa
        # bb
        # child1 (clone)
        # cc
        #   child1 (clone)
        #   child2
        aa = p.insertAfter()
        aa.h = 'aa'
        bb = aa.insertAfter()
        bb.h = 'bb'
        cc = bb.insertAfter()
        cc.h = 'cc'
        child1 = cc.insertAsLastChild()
        child1.h = 'child1'
        child1_gnx = child1.gnx
        child2 = child1.insertAfter()
        child2.h = 'child2'
        child2_gnx = child2.gnx
        clone = child1.clone()
        clone.moveAfter(bb)
        assert clone.v == child1.v
        # Careful: position cc has changed.
        cc = clone.next()
        clone_v = clone.v
        cc_gnx = cc.gnx
        assert cc.h == 'cc'
        #@-<< create test tree >>
        
        assert fc  ###
        
        return ###

        # Cut node cc
        # self.dump_headlines(c)
        # self.dump_clone_info(c)
        c.selectPosition(cc)
        c.cutOutline()
        assert not clone.isCloned()
        assert c.p == clone
        assert c.p.h == 'child1'

        # Execute paste-retaining-clones
        c.pasteOutlineRetainingClones()
        # self.dump_clone_info(c)
        
        # Quick tests.
        self.assertFalse(c.checkOutline())
        for p in c.all_positions():
            if p.h == 'child1':
                assert p.isCloned(), p.h
                # The vnode never changes *and* all positions share the same vnode.
                assert p.v == clone_v, p.h
            else:
                assert not p.isCloned(), p.h

        # Other tests.

        # Recreate the positions.
        clone = bb.next()
        cc = clone.next()
        child1 = cc.firstChild()
        assert clone.v == clone_v
        assert cc.gnx == cc_gnx
        assert child1.gnx == clone.gnx
        self.assertEqual(id(child1.v), id(clone.v))
        assert cc.firstChild().gnx == child1_gnx
        assert cc.firstChild().next().gnx == child2_gnx
        assert clone.isCloned()  # Fails.
        assert cc.firstChild().isCloned()
        
        # Test multiple undo/redo cycles.
        for i in range(3):

            # Undo paste-retaining-clones.
            u.undo()
            self.assertFalse(c.checkOutline())
            for p in c.all_positions():
                assert not p.isCloned(), p.h
                if p.h == 'child1':
                    # The vnode never changes!
                    assert p.v == clone_v, p.h

            # Redo paste-retaining-clones.
            u.redo()
            # self.dump_clone_info(c)
            self.assertFalse(c.checkOutline())
            for p in c.all_positions():
                if p.h == 'child1':
                    assert p.isCloned(), p.h
                    # The vnode never changes *and* all positions share the same vnode.
                    assert p.v == clone_v, p.h
                else:
                    assert not p.isCloned(), p.h
    #@+node:ekr.20230722104508.1: *3* TestOutlineCommands.test_fc_getLeoOutlineFromClipBoardRetainingClones (new)
    def test_fc_getLeoOutlineFromClipBoardRetainingClones(self):

        c = self.c
        p = c.p
        u = c.undoer
        trace = False
        
        # define helper functions
        #@+others
        #@+node:ekr.20230723160526.1: *4* function: clean_tree
        def clean_tree() -> None:
            """Clear everything but the root node."""
            p = self.root_p
            assert p.h == 'root'
            p.deleteAllChildren()
            while p.hasNext():
                p.next().doDelete()
        #@+node:ekr.20230723161726.1: *4* function: copy_node
        def copy_node():
            """Copy c.p to the clipboard."""
            if 1:  # The content of c.copyOutline, w/o setting unused g.app.paste_c
                s = c.fileCommands.outline_to_clipboard_string()
                g.app.gui.replaceClipboardWith(s)
            else:
                c.copyOutline()
        #@+node:ekr.20230723161026.1: *4* function: create_gnx_dict
        def create_gnx_dict() -> dict[str, str]:
            """Return a *local* gnx dict"""
            vnodes = list(set(list(c.all_nodes())))
            return {z.h: z.gnx for z in vnodes}
        #@+node:ekr.20230723160812.1: *4* function: test_tree
        def test_tree(pasted_flag: bool, tag: str) -> None:
            """A quick test that clones are as expected."""
            if test_kind == 'cut':
                cloned_headlines = ('cc:child1',) if pasted_flag else ()
            else:
                cloned_headlines = ('cc:child1', 'cc') if pasted_flag else ('cc:child1',)
            try:
                clones_s = ', '.join([z for z in cloned_headlines]) if cloned_headlines else 'None'
                tag_s = f"{tag} kind: {test_kind} pasted? {int(pasted_flag)} expecting {clones_s}"
                for p in c.all_positions():
                    if p.h in cloned_headlines:
                        assert p.isCloned(), f"{tag_s}: not cloned: {p.h}"
                    else:
                        assert not p.isCloned(), f"{tag_s}: is cloned: {p.h}"
                    message = f"{tag}: p.gnx: {p.gnx} != expected {gnx_dict.get(p.h)}"
                    assert gnx_dict.get(p.h) == p.gnx, message
            except Exception:
                message = f"clone_test failed! {tag} {p!r}"
                print(f"\n{message}\n")
                self.dump_clone_info(c)
                g.printObj(gnx_dict, tag='gnx_dict')
                self.fail(message)
        #@-others
        
        for test_kind in ('cut', 'copy'):

            # Create the tree and gnx_dict.
            clean_tree()
            #@+<< create tree >>
            #@+node:ekr.20230723085723.1: *4* << create tree >>
            """
            Create the following tree:

                aa
                    aa:child1
                bb
                cc:child1 (clone)
                cc
                  cc:child1 (clone)
                  cc:child2
                dd
                  dd:child1
                    dd:child1:child1
                  dd:child2
                ee
                
            Define valid_postions as the tuple of those those positions after which cc may be pasted.
            """
            root = c.rootPosition()
            aa = root.insertAfter()
            aa.h = 'aa'
            aa_child1 = aa.insertAsLastChild()
            aa_child1.h = 'aa:child1'
            bb = aa.insertAfter()
            bb.h = 'bb'
            cc = bb.insertAfter()
            cc.h = 'cc'
            cc_child1 = cc.insertAsLastChild()
            cc_child1.h = 'cc:child1'
            cc_child2 = cc_child1.insertAfter()
            cc_child2.h = 'cc:child2'
            dd = cc.insertAfter()
            dd.h = 'dd'
            dd_child1 = dd.insertAsLastChild()
            dd_child1.h = 'dd:child1'
            dd_child2 = dd.insertAsLastChild()
            dd_child2.h = 'dd:child2'
            dd_child1_child1 = dd_child1.insertAsLastChild()
            dd_child1_child1.h = 'dd:child1:child1'
            ee = dd.insertAfter()
            ee.h = 'ee'
            clone = cc_child1.clone()
            clone.moveAfter(bb)
            assert clone.v == cc_child1.v
            # Careful: position cc has changed.
            cc = clone.next().copy()
            assert cc.h == 'cc'
            if 0:  # A short list for initial testing.
                valid_paste_positions = (aa,)
            else:  # The full list.
                valid_paste_positions = (root, aa, aa_child1, bb, dd, dd_child1, dd_child1_child1, dd_child2, ee)
            #@-<< create tree >>
            gnx_dict = create_gnx_dict()
            self.assertFalse(c.checkOutline())

            # Cut or copy cc.
            if test_kind == 'cut':
                c.selectPosition(cc)
                copy_node()
                back = cc.threadBack()
                assert back
                cc.doDelete()
                c.selectPosition(back)
            else:
                # *Copy*  node cc
                c.selectPosition(cc)
                copy_node()
            self.assertFalse(c.checkOutline())

            # Pretest: select all positions in the tree.
            for p in c.all_positions():
                c.selectPosition(p)

            # Execute paste-retaining-clones several position in reverse order.
            for target_p in valid_paste_positions:
                if trace:
                    print(f"Select: {target_p.h}")
                c.selectPosition(target_p)
                
                if trace:
                    print(f"Paste: {target_p.h}")
                c.pasteOutlineRetainingClones()
        
                self.assertFalse(c.checkOutline())
                test_tree(pasted_flag=True, tag='paste-retaining-clones')

                # Test multiple undo/redo cycles.
                for i in range(3):
                    u.undo()
                    self.assertFalse(c.checkOutline())
                    test_tree(pasted_flag=False, tag=f"undo {i}")
                   
                    u.redo()
                    self.assertFalse(c.checkOutline())
                    test_tree(pasted_flag=True, tag=f"redo {i}")
    #@-others
#@-others
#@-leo
