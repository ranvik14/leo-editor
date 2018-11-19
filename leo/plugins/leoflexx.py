# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181103094900.1: * @file leoflexx.py
#@@first
#@@language python
#@@tabwidth -4
'''
A stand-alone prototype for Leo using flexx.
'''
# pylint: disable=logging-not-lazy
#@+<< leoflexx imports >>
#@+node:ekr.20181113041314.1: ** << leoflexx imports >>
import leo.core.leoGlobals as g
    # **Note**: JS code can not use g.trace, g.callers, g.pdb.
import leo.core.leoBridge as leoBridge
import leo.core.leoFrame as leoFrame
import leo.core.leoGui as leoGui
import leo.core.leoMenu as leoMenu
import leo.core.leoNodes as leoNodes
from flexx import flx
import re
import time
assert re and time
    # Suppress pyflakes complaints
#@-<< leoflexx imports >>
#@+<< ace assets >>
#@+node:ekr.20181111074958.1: ** << ace assets >>
# Assets for ace, embedded in the LeoFlexxBody and LeoFlexxLog classes.
base_url = 'https://cdnjs.cloudflare.com/ajax/libs/ace/1.2.6/'
flx.assets.associate_asset(__name__, base_url + 'ace.js')
flx.assets.associate_asset(__name__, base_url + 'mode-python.js')
flx.assets.associate_asset(__name__, base_url + 'theme-solarized_dark.js')
#@-<< ace assets >>
debug = True
debug_keys = True
debug_tree = False
print('\n===== debug: %s =====\n' % debug)
#@+others
#@+node:ekr.20181103151350.1: **  init
def init():
    # At present, leoflexx is not a true plugin.
    # I am executing leoflexx.py from an external script.
    return False
#@+node:ekr.20181113041410.1: **  suppress_unwanted_log_messages
def suppress_unwanted_log_messages():
    '''
    Suppress the "Automatically scrolling cursor into view" messages by
    *allowing* only important messages.
    '''
    allowed = r'(Traceback|Critical|Error|Leo|Session|Starting|Stopping|Warning)'
    pattern = re.compile(allowed, re.IGNORECASE)
    flx.set_log_level('INFO', pattern)
#@+node:ekr.20181107052522.1: ** class LeoBrowserApp(PyComponent)
# pscript never converts flx.PyComponents to JS.

class LeoBrowserApp(flx.PyComponent):
    '''
    The browser component of Leo in the browser.
    This is self.root for all flx.Widget objects!
    This is *not* g.app. Leo's core defines g.app.
    '''
    # This may be optional, but it doesn't hurt.
    main_window = flx.ComponentProp(settable=True)

    def init(self):
        c, g = self.open_bridge()
        ###
            # g.trace('(LeoBrowserApp) id(g)', repr(id(g)))
            # g.trace('(LeoBrowserApp) c.frame', repr(c.frame))
            # g.trace('(LeoBrowserApp) g.app', repr(g.app))
            # g.trace('(LeoBrowserApp) g.app.gui', repr(g.app.gui))
        self.c = c
        self.gui = gui = LeoBrowserGui()
        # Inject the newly-created gui into g.app.
        g.app.gui = gui
        title = c.computeWindowTitle(c.mFileName)
        c.frame = gui.lastFrame = LeoBrowserFrame(c, title, gui)
            # Instantiate all wrappers first.
        # Force minibuffer find mode.
        c.findCommands.minibuffer_mode = True
        # Create all data-related ivars.
        self.create_all_data()
        # Create the main window and all its components.
        ### p = c.rootPosition()
        c.selectPosition(c.rootPosition()) ### A temp hack.
        p = c.p
        g.trace('app.init: c.p.h:', c.p.h)
        signon = '%s\n%s' % (g.app.signon, g.app.signon2)
        status_lt, status_rt = c.frame.statusLine.update(p.b, 0)
        redraw_dict = self.make_redraw_dict()
        main_window = LeoFlexxMainWindow(p.b, redraw_dict, signon, status_lt, status_rt)
        self._mutate('main_window', main_window)

    #@+others
    #@+node:ekr.20181111152542.1: *3* app.actions
    #@+node:ekr.20181111142921.1: *4* app.action: do_command
    @flx.action
    def do_command(self, command):
        w = self.main_window
        c = self.c
        
        #@+others # define test_log & test_select.
        #@+node:ekr.20181119103144.1: *5* tests
        def test_echo():
            print('testing echo...')
            self.gui.echo()
            self.gui.tree_echo()

        def test_log():
            print('testing log...')
            w.log.put('Test message to LeoFlexxLog.put')
                # Test LeoFlexxLog.put.
            c.frame.log.put('Test message to LeoBrowserLog.put')
                # Test LeoBrowserLog.put.
                
        def test_positions():
            print('testing positions...')
            self.test_round_trip_positions()
                
        def test_redraw():
            print('testing redraw...')
            self.redraw()
                
        def test_select():
            print('testing select...')
            h = 'Active Unit Tests'
            p = g.findTopLevelNode(c, h, exact=True)
            if p:
                c.frame.tree.select(p)
                # LeoBrowserTree.select.
            else:
                g.trace('not found: %s' % h)
        #@-others

        if command.startswith('echo'):
            test_echo()
        elif command == 'log':
            test_log()
        elif command == 'redraw':
            test_redraw()
        elif command.startswith('sel'):
            test_select()
        elif command == 'status':
            self.update_status_line()
        elif command == 'test': # All except unit tests.
            test_echo()
            test_log()
            test_positions()
            test_redraw()
            test_select()
        elif command == 'unit':
            self.run_all_unit_tests()
        else:
            g.trace('unknown command: %r' % command)
            ### To do: pass the command on to Leo's core.
    #@+node:ekr.20181117163223.1: *4* app.action: do_key
    @flx.action
    def do_key (self, ev, kind):
        '''
        https://flexx.readthedocs.io/en/stable/ui/widget.html#flexx.ui.Widget.key_down
        See Widget._create_key_event in flexx/ui/_widget.py:
            
        Modifiers: 'Alt', 'Shift', 'Ctrl', 'Meta'
            
        Keys: 'Enter', 'Tab', 'Escape', 'Delete'
              'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowUp',
        '''
        # ev is a dict, keys are type, source, key, modifiers
        trace = debug_keys and not g.unitTesting
        c = self.c
        key, mods = ev ['key'], ev ['modifiers']
        d = {
            'ArrowDown':'Down',
            'ArrowLeft':'Left',
            'ArrowRight': 'Right',
            'ArrowUp': 'Up',
            'PageDown': 'Next',
            'PageUp': 'Prior',
        }
        char = d.get(key, key)
        if 'Ctrl' in mods:
            mods.remove('Ctrl')
            mods.append('Control')
        ###
            # # Required by Leo's core.  Big sigh.
            # if mods and key.isalpha() and len(key) == 1:
                # binding_char = key.upper()
            # else:
                # binding_char = key
        binding = '%s%s' % (''.join(['%s+' % (z) for z in mods]), char)
        widget = getattr(c.frame, kind)
        w = widget.wrapper
        key_event = leoGui.LeoKeyEvent(c,
            char = char, event = { 'c': c }, binding = binding, w = w)
        if trace:
            g.app.debug = ['keys',]
        try:
            c.k.masterKeyHandler(key_event)
        finally:
            g.app.debug = []
        if trace:
            g.trace('mods: %r key: %r ==> %r %r IN %6r %s' % (
                mods, key, char, binding, widget.wrapper.getName(), c.p.h))
    #@+node:ekr.20181113053154.1: *4* app.action: dump_redraw_dict
    @flx.action
    def dump_redraw_dict(self, d):
        '''Pretty print the redraw dict.'''
        print('app.dump_redraw dict...')
        padding, tag = None, 'c.p'
        self.dump_ap(d ['c.p'], padding, tag)
        level = 0
        for i, item in enumerate(d ['items']):
            self.dump_redraw_item(i, item, level)
            print('')
    #@+node:ekr.20181113085722.1: *4* app.action: dump_ap
    @flx.action
    def dump_ap (self, ap, padding=None, tag=None):
        '''Print an archived position fully.'''
        stack = ap ['stack']
        if not padding:
            padding = ''
        padding = padding + ' '*4 
        if stack:
            print('%s%s:...' % (padding, tag or 'ap'))
            padding = padding + ' '*4
            print('%schildIndex: %s v: %s %s stack...' % (
                padding,
                str(ap ['childIndex']),
                ap['gnx'],
                ap['headline'],
            ))
            padding = padding + ' '*4
            for d in ap ['stack']:
                print('%s%s %s %s' % (
                    padding,
                    str(d ['childIndex']).ljust(3),
                    d ['gnx'],
                    d ['headline'],
                ))
        else:
            print('%s%s: childIndex: %s v: %s stack: [] %s' % (
                padding, tag or 'ap',
                str(ap ['childIndex']).ljust(3),
                ap['gnx'],
                ap['headline'],
            ))
    #@+node:ekr.20181116053210.1: *4* app.action: echo
    @flx.action
    def echo (self, message=None):
        print('===== echo =====', message or '<Empty Message>')
    #@+node:ekr.20181113091522.1: *4* app.action: redraw_item
    @flx.action
    def dump_redraw_item(self, i, item, level):
        '''Pretty print one item in the redraw dict.'''
        padding = ' '*4*level
        # Print most of the item.
        print('%s%s gnx: %s body: %s %s' % (
            padding,
            str(i).ljust(3),
            item ['gnx'].ljust(25),
            str(len(item ['body'])).ljust(4),
            item ['headline'],
        ))
        tag = None
        self.dump_ap(item ['ap'], padding, tag)
        # Print children...
        children = item ['children']
        if children:
            print('%sChildren...' % padding)
            print('%s[' % padding)
            padding = padding + ' '*4
            for j, child in enumerate(children):
                index = '%s.%s' % (i, j)
                self.dump_redraw_item(index, child, level+1)
            padding = padding[:-4]
            print('%s]' % padding)
    #@+node:ekr.20181112165240.1: *4* app.action: info (deprecated)
    @flx.action
    def info (self, s):
        '''Send the string s to the flex logger, at level info.'''
        if not isinstance(s, str):
            s = repr(s)
        flx.logger.info('Leo: ' + s)
            # A hack: automatically add the "Leo" prefix so
            # the top-level suppression logic will not delete this message.
    #@+node:ekr.20181113042549.1: *4* app.action: redraw
    def redraw (self):
        '''
        Send a **redraw list** to the tree.
        
        This is a recusive list lists of items (ap, gnx, headline) describing
        all and *only* the presently visible nodes in the tree.
        
        As a side effect, app.make_redraw_dict updates all internal dicts.
        '''
        # print('app.redraw', g.callers())
        w = self.main_window
        # Be careful during startup.
        if w and w.tree:
            d = self.make_redraw_dict()
            w.tree.redraw(d)
    #@+node:ekr.20181111202747.1: *4* app.action: select_ap & helpers
    @flx.action
    def select_ap(self, ap):
        '''Select the position in Leo's core corresponding to the archived position.'''
        trace = debug_tree and not g.unitTesting
        c, w = self.c, self.main_window
        p = self.ap_to_p(ap)
        c.frame.tree.super_select(p)
            # call LeoTree.select, but not self.select_p.
            # This hack prevents an unbounded recursion.
        w.body.set_body(p.v.b)
        self.update_status_line()
        self.send_children_to_tree(ap, p)
        if trace:
            print('app.select_ap: after: c.p.h: ', c.p.h)
    #@+node:ekr.20181111095640.1: *5* app.action: send_children_to_tree
    def send_children_to_tree(self, parent_ap, p):
        '''
        Call w.tree.receive_children(d), where d has the form:
            {
                'parent': parent_ap,
                'children': [ap1, ap2, ...],
            }
        '''
        w = self.main_window
        if p.hasChildren():
            w.tree.receive_children({
                'parent': parent_ap,
                'children': [self.p_to_ap(z) for z in p.children()],
            })
        elif debug:
            # Not an error.
            print('app.send_children_to_tree: no children', p.h)
    #@+node:ekr.20181118061020.1: *4* app.action: select_p
    @flx.action
    def select_p(self, p):
        '''
        Select the position in the tree.
        
        Called from LeoBrowserTree.select, so do *not* call c.frame.tree.select.
        '''
        # print'app.select_p', p.h)
        w = self.main_window
        # Be careful during startup.
        if w and w.tree:
            ap = self.p_to_ap(p)
            w.tree.select_ap(ap)
    #@+node:ekr.20181118064309.1: *4* app.action: set_body
    @flx.action
    def set_body(self, s):
        w = self.main_window
        w.body.set_body(s)
    #@+node:ekr.20181119044723.1: *4* app.action: update_status_line
    @flx.action
    def update_status_line(self, body_text=None, insert_point=0):
        '''Update both fields of the status area.'''
        w = self.main_window
        c = self.c
        # Be careful during startup.
        if w and getattr(w, 'status_line', None):
            c.frame.statusLine.update(insert_point=insert_point)
        ###
            # else:
                # g.trace('===== status line not instantiated', g.callers())
    #@+node:ekr.20181114015356.1: *3* app.create_all_data
    def create_all_data(self):
        '''Compute the initial values all data structures.'''
        t1 = time.clock()
        # This is likely the only data that ever will be needed.
        self.gnx_to_vnode = { v.gnx: v for v in self.c.all_unique_nodes() }
        t2 = time.clock()
        if debug:
            print('app.create_all_data: %5.2f sec. %s entries' % (
                (t2-t1), len(list(self.gnx_to_vnode.keys()))))
        if debug:
            self.test_round_trip_positions()
    #@+node:ekr.20181111155525.1: *3* app.archived positions
    #@+node:ekr.20181111204659.1: *4* app.p_to_ap (updates app.gnx_to_vnode)
    def p_to_ap(self, p):
        '''
        Convert a true Leo position to a serializable archived position.
        '''
        gnx = p.v.gnx
        if gnx not in self.gnx_to_vnode:
            print('=== update gnx_to_vnode', gnx.ljust(15), p.h,
                len(list(self.gnx_to_vnode.keys())))
            self.gnx_to_vnode [gnx] = p.v
        return {
            'childIndex': p._childIndex,
            'gnx': gnx,
            'headline': p.h, # For dumps.
            'stack': [{
                'gnx': v.gnx,
                'childIndex': childIndex,
                'headline': v.h, # For dumps & debugging.
            } for (v, childIndex) in p.stack ],
        }
    #@+node:ekr.20181111203114.1: *4* app.ap_to_p (uses gnx_to_vnode)
    def ap_to_p (self, ap):
        '''Convert an archived position to a true Leo position.'''
        childIndex = ap ['childIndex']
        v = self.gnx_to_vnode [ap ['gnx']]
        stack = [
            (self.gnx_to_vnode [d ['gnx']], d ['childIndex'])
                for d in ap ['stack']
        ]
        return leoNodes.position(v, childIndex, stack)
    #@+node:ekr.20181113043539.1: *4* app.make_redraw_dict & helpers
    def make_redraw_dict(self):
        '''
        Return a recursive, archivable, list of lists describing all and only
        the visible nodes of the tree.
        
        As a side effect, all LeoApp data are recomputed.
        '''
        c = self.c
        t1 = time.clock()
        aList = []
        p = c.rootPosition()
        ### Don't do this: it messes up tree redraw.
            # Testing: forcibly expand the first node.
            # p.expand()
        while p:
            if p.level() == 0 or p.isVisible():
                aList.append(self.make_dict_for_position(p))
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        d = {
            'c.p': self.p_to_ap(c.p),
            'items': aList,
        }
        if 0:
            t2 = time.clock()
            print('app.make_redraw_dict: %5.4f sec' % (t2-t1))
        return d
    #@+node:ekr.20181113044701.1: *5* app.make_dict_for_position
    def make_dict_for_position(self, p):
        '''
        Recursively add a sublist for p and all its visible nodes.
        
        Update all data structures for p.
        '''
        c = self.c
        self.gnx_to_vnode[p.v.gnx] = p.v
        children = [
            self.make_dict_for_position(child)
                for child in p.children()
                    if child.isVisible(c)
        ]
        return {
            'ap': self.p_to_ap(p),
            'body': p.b,
            'children': children,
            'gnx': p.v.gnx,
            'headline': p.h,
        }
    #@+node:ekr.20181113180246.1: *4* app.test_round_trip_positions
    def test_round_trip_positions(self):
        '''Test the round tripping of p_to_ap and ap_to_p.'''
        c = self.c
        t1 = time.clock()
        for p in c.all_positions():
            ap = self.p_to_ap(p)
            p2 = self.ap_to_p(ap)
            assert p == p2, (repr(p), repr(p2), repr(ap))
        t2 = time.clock()
        if 1:
            print('app.test_new_tree: %5.3f sec' % (t2-t1))
    #@+node:ekr.20181105091545.1: *3* app.open_bridge
    def open_bridge(self):
        '''Can't be in JS.'''
        bridge = leoBridge.controller(gui = None,
            loadPlugins = False,
            readSettings = True, # Required to get bindings!
            silent = False,
            tracePlugins = False,
            verbose = False, # True: prints log messages.
        )
        if not bridge.isOpen():
            flx.logger.error('Error opening leoBridge')
            return
        g = bridge.globals()
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'test', 'unitTest.leo')
        if not g.os_path_exists(path):
            flx.logger.error('open_bridge: does not exist: %r' % path)
            return
        c = bridge.openLeoFile(path)
        return c, g
    #@+node:ekr.20181115171220.1: *3* app.message
    def message(self, s):
        '''For testing.'''
        print('app.message: %s' % s)
    #@+node:ekr.20181112182636.1: *3* app.run_all_unit_tests
    def run_all_unit_tests (self):
        '''Run all unit tests from the bridge.'''
        print('===== app.run_all_unit_tests: Start')
        c = self.c
        h = 'Active Unit Tests'
        p = g.findTopLevelNode(c, h, exact=True)
        if p:
            ### self.gui.frame.tree.select(p)
            c.frame.tree.select(p)
            c.debugCommands.runSelectedUnitTestsLocally()
            print('===== app.run_all_unit_tests: Done')
        else:
            print('do_command: select: not found: %s' % h)
    #@-others
#@+node:ekr.20181115071559.1: ** Python wrappers
#@+node:ekr.20181115092337.3: *3* class LeoBrowserBody
class LeoBrowserBody(leoFrame.NullBody):
   
    def __init__(self, frame):
        super().__init__(frame, parentFrame=None)
        assert self.wrapper.getName().startswith('body')
        self.c = frame.c
        assert self.c
        self.root = Root()
        self.widget = None
        
    ### This destroys the body text!
    # def onBodyChanged(self, *args, **keys):
        # c = self.c
        # g.trace('body-wrapper', c.p.h)
        # super().onBodyChanged(*args, **keys)
        # ### self.root.set_body(c.p.b)
#@+node:ekr.20181115092337.6: *3* class LeoBrowserFrame
class LeoBrowserFrame(leoFrame.NullFrame):
    
    def __init__(self, c, title, gui):
        '''Ctor for the LeoBrowserFrame class.'''
        super().__init__(c, title, gui)
        assert self.c == c
        frame = self
        self.root = Root()
        self.body = LeoBrowserBody(frame)
        self.tree = LeoBrowserTree(frame)
        self.log = LeoBrowserLog(frame)
        self.menu = LeoBrowserMenu(frame)
        self.iconBar = LeoBrowserIconBar(c, frame)
        self.statusLine = LeoBrowserStatusLine(c, frame)
            # NullFrame does this in createStatusLine.
        self.top = TracingNullObject() if debug else g.NullObject()
            # Use the TracingNullObject class for better tracing.
        
    def finishCreate(self):
        '''Override NullFrame.finishCreate.'''
        pass # Do not call self.createFirstTreeNode.

    #@+others
    #@-others
#@+node:ekr.20181113041113.1: *3* class LeoBrowserGui
class LeoBrowserGui(leoGui.NullGui):

    def __init__ (self, guiName='nullGui'):
        super().__init__(guiName='BrowserGui')
        self.root = Root()
        
    def isTextWrapper(self, w):
        '''Return True if w is supposedly a text widget.'''
        g.trace('==========', repr(w))
        return True ####
        
    def insertKeyEvent(self, event, i):
        '''Insert the key given by event in location i of widget event.w.'''
        # Mysterious...
        assert False, g.callers()
        
    # Testing only...
    def echo(self):
        self.root.echo('From LeoBrowser Gui')
        
    def tree_echo(self):
        self.root.main_window.tree.echo('From LeoBrowser Gui')

    #@+others
    #@-others
#@+node:ekr.20181115092337.21: *3* class LeoBrowserIconBar
class LeoBrowserIconBar(leoFrame.NullIconBarClass):

    def __init__(self, c, parentFrame):
        super().__init__(c, parentFrame)
        assert self.c == c
        self.root = Root()
            
    #@+others
    #@-others
#@+node:ekr.20181115092337.22: *3* class LeoBrowserLog
class LeoBrowserLog(leoFrame.NullLog):
    
    def __init__(self, frame, parentFrame=None):
        super().__init__(frame, parentFrame)
        self.root = Root()
        self.logCtrl = self
            # Required
        self.wrapper = self
            
    # Overrides...
    def getName(self):
        return 'log' # Required for proper pane bindings.
        
    def hasSelection(self):
        # A bug: this should be in the NullGui class.
        return self.widget.hasSelection()

    def put(self, s, color=None, tabName='Log', from_redirect=False, nodeLink=None):
        self.root.main_window.log.put(s)
    
    def putnl(self, tabName='Log'):
        self.root.main_window.log.put('')
#@+node:ekr.20181115092337.31: *3* class LeoBrowserMenu
class LeoBrowserMenu(leoMenu.NullMenu):
    '''Browser wrapper for menus.'''

    # def __init__(self, frame):
        # super().__init__(frame)
        # self.root = Root()

    # @others
#@+node:ekr.20181115120317.1: *3* class LeoBrowserMinibuffer (not used)
class LeoBrowserMinibuffer (object):
    '''Browser wrapper for minibuffer.'''
    
    # def __init__(self, c, frame):
        # self.c = c
        # self.frame = frame
        # self.root = Root()
        
    # @others
#@+node:ekr.20181115092337.32: *3* class LeoBrowserStatusLine
class LeoBrowserStatusLine(leoFrame.NullStatusLineClass):
    
    def __init__(self, c, parentFrame):
        super().__init__(c, parentFrame)
        self.root = Root()
        self.w = self # Required.
        
    #@+others
    #@+node:ekr.20181119045430.1: *4* status_line.clear & get
    def clear(self):
        pass
        
    def get(self):
        g.trace('(LeoBrowserStatusLine): NOT READY')
        return ''
    #@+node:ekr.20181119045343.1: *4* status_line.put and put1
    def put(self, s, bg=None, fg=None):
        w = self.root.main_window
        # Be careful during startup.
        if w and w.status_line:
            w.status_line.put(s, bg, fg)

    def put1(self, s, bg=None, fg=None):
        w = self.root.main_window
        # Be careful during startup.
        if w and w.status_line:
            w.status_line.put2(s, bg, fg)
    #@+node:ekr.20181119042937.1: *4* status_line.update & helpers
    def update(self, body_text='', insert_point=0):
        '''
        Update the status line, based on the contents of the body.
        
        Called from LeoTree.select, and should also be called from the JS side.
        
        Returns (lt_part, rt_part) for LeoBrowserApp.init.
        '''
        # pylint: disable=arguments-differ
        if g.app.killed:
            return
        c, p = self.c, self.c.p
        if not p:
            return
        # Calculate lt_part
        row, col = g.convertPythonIndexToRowCol(body_text, insert_point)
        fcol = c.gotoCommands.find_node_start(p)
        lt_part = "line: %2d col: %2d fcol: %s" % (row, col, fcol or '')
        # Calculate rt_part.
        headlines = [v.h for (v, childIndex) in p.stack] + [p.h]
        rt_part = '%s#%s' % (g.shortFileName(c.fileName()), '->'.join(headlines))
        # Update the status area.
        self.put(lt_part)
        self.put1(rt_part)
        return lt_part, rt_part
    #@-others
#@+node:ekr.20181115092337.57: *3* class LeoBrowserTree
class LeoBrowserTree(leoFrame.NullTree):
    
    def __init__(self, frame):
        super().__init__(frame)
        self.root = Root()
        self.wrapper = self
        
    def getName(self):
        return 'canvas(tree)' # Required for proper pane bindings.

    #@+others
    #@+node:ekr.20181116081421.1: *4* LeoBrowserTree.select & super_select
    def select(self, p):
        '''Override NullTree.select, which is actually LeoTree.select.'''
        super().select(p)
            # Call LeoTree.select.'''
        self.root.select_p(p)
            # Call app.select_position.

    def super_select(self, p):
        '''Call only LeoTree.select.'''
        super().select(p)
    #@+node:ekr.20181118052203.1: *4* LeoBrowserTree.redraw
    def redraw(self, p=None):
        ### print('===== browser-tree.redraw', g.callers())
        self.root.redraw()
    #@-others
#@+node:ekr.20181119094122.1: *3* class TracingNullObject
#@@nobeautify

class TracingNullObject(object):
    '''A tracing version of g.NullObject.'''
    def __init__(self, *args, **keys):
        pass

    def __call__(self, *args, **keys):
        return self

    def __repr__(self):
        return "NullObject"

    def __str__(self):
        return "NullObject"

    def __bool__(self):
        return False

    def __delattr__(self, attr):
        print('')
        print('NullObject.__delattr__', attr, g.callers())
        print('')
        return self

    def __getattr__(self, attr):
        print('')
        print('NullObject.__getattr__', attr, g.callers())
        print('')
        return self

    def __setattr__(self, attr, val):
        print('')
        print('NullObject.__setattr__', attr, g.callers())
        print('')
        return self

#@+node:ekr.20181107052700.1: ** Js side: flx.Widgets
#@+node:ekr.20181104082144.1: *3* class LeoFlexxBody

class LeoFlexxBody(flx.Widget):
    
    """ A CodeEditor widget based on Ace.
    """

    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """

    def init(self, body):
        # pylint: disable=arguments-differ
        # pylint: disable=undefined-variable
            # window
        global window
        self.ace = window.ace.edit(self.node, "editor")
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        self.ace.setTheme("ace/theme/solarized_dark")
        self.ace.getSession().setMode("ace/mode/python")
        self.set_body(body)
        
    @flx.emitter
    def key_press(self, e):
        ev = self._create_key_event(e)
        print('===== body.key_down.emitter', repr(ev))
        if ev ['modifiers']:
            e.preventDefault()
        return ev
        
    @flx.reaction('key_press')
    def on_key_press(self, *events):
        for ev in events:
            self.root.do_key(ev, 'body')

    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()
        
    @flx.action
    def set_body(self, body):
        self.ace.setValue(body)
        self.root.update_status_line(body_text=body, insert_point=0)

#@+node:ekr.20181104082149.1: *3* class LeoFlexxLog
class LeoFlexxLog(flx.Widget):

    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """

    def init(self, signon):
        # pylint: disable=arguments-differ
        # pylint: disable=undefined-variable
            # window
        global window
        self.ace = window.ace.edit(self.node, "editor")
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        self.ace.setTheme("ace/theme/solarized_dark")
        self.ace.setValue(signon)
        
    @flx.emitter
    def key_press(self, e):
        """Overload key_press emitter to override browser commands."""
        ev = self._create_key_event(e)
        mods = ev ['modifiers']
        print('===== log.key_down.emitter', repr(ev))
        if mods:
            e.preventDefault()
        return ev

    @flx.action
    def put(self, s):
        self.ace.setValue(self.ace.getValue() + '\n' + s)

    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()
        
    @flx.reaction('key_press')
    def on_key_press(self, *events):
        for ev in events:
            self.root.do_key(ev, 'log')

#@+node:ekr.20181104082130.1: *3* class LeoFlexxMainWindow
class LeoFlexxMainWindow(flx.Widget):
    
    '''
    Leo's main window, that is, root.main_window.
    
    Each property x below is accessible as root.main_window.x.
    '''
    # All these properties *are* needed.
    body = flx.ComponentProp(settable=True)
    log = flx.ComponentProp(settable=True)
    minibuffer = flx.ComponentProp(settable=True)
    status_line = flx.ComponentProp(settable=True)
    tree = flx.ComponentProp(settable=True)

    def init(self, body_s, data, signon, status_lt, status_rt):
        # pylint: disable=arguments-differ
        ###with flx.TabLayout():
        if 1:
            with flx.VSplit():
                with flx.HSplit(flex=1):
                    tree = LeoFlexxTree(data, flex=1)
                    log = LeoFlexxLog(signon, flex=1)
                body = LeoFlexxBody(body_s, flex=1)
                minibuffer = LeoFlexxMiniBuffer()
                status_line = LeoFlexxStatusLine(status_lt, status_rt)
        for name, prop in (
            ('body', body),
            ('log', log),
            ('minibuffer', minibuffer),
            ('status_line', status_line),
            ('tree', tree),
        ):
            self._mutate(name, prop)
            
    @flx.emitter
    def key_press(self, e):
        ev = self._create_key_event(e)
        print('===== main.key_down.emitter', repr(ev))
        if ev ['modifiers']:
            e.preventDefault()
        return ev

    #@+others
    #@-others
#@+node:ekr.20181104082154.1: *3* class LeoFlexxMiniBuffer
class LeoFlexxMiniBuffer(flx.Widget):

    def init(self): 
        with flx.HBox():
            flx.Label(text='Minibuffer')
            self.widget = flx.LineEdit(flex=1, placeholder_text='Enter command')
        self.widget.apply_style('background: yellow')
        
    @flx.emitter
    def key_press(self, e):
        ev = self._create_key_event(e)
        print('===== minibuffer.key_down.emitter', repr(ev))
        if ev ['modifiers']:
            e.preventDefault()
        return ev
    
    @flx.action
    def set_text(self, s):
        self.widget.set_text(s)
        
    @flx.reaction('widget.user_done')
    def on_event(self, *events):
        for ev in events:
            command = self.widget.text
            if command.strip():
                self.widget.set_text('')
                self.root.do_command(command)
#@+node:ekr.20181104082201.1: *3* class LeoFlexxStatusLine
class LeoFlexxStatusLine(flx.Widget):
    
    def init(self, status_lt, status_rt):
        # pylint: disable=arguments-differ
        with flx.HBox():
            flx.Label(text='Status Line')
            self.widget = flx.LineEdit(flex=1)
            self.widget2 = flx.LineEdit(flex=1)
        self.widget.set_text(status_lt)
        self.widget2.set_text(status_rt)
        self.widget.apply_style('background: green')
        self.widget2.apply_style('background: green')
        
    @flx.emitter
    def key_press(self, e):
        ev = self._create_key_event(e)
        print('===== status line.key_down.emitter', repr(ev))
        if ev ['modifiers']:
            e.preventDefault()
        return ev

    @flx.action
    def put(self, s, bg, fg):
        self.widget.set_text(s)
        
    @flx.action
    def put2(self, s, bg, fg):
        self.widget2.set_text(s)
#@+node:ekr.20181104082138.1: *3* class LeoFlexxTree
class LeoFlexxTree(flx.Widget):

    CSS = '''
    .flx-TreeWidget {
        background: #000;
        color: white;
        /* background: #ffffec; */
        /* Leo Yellow */
        /* color: #afa; */
    }
    '''
    
    def init(self, redraw_dict):
        # pylint: disable=arguments-differ
        self.leo_items = {}
            # Keys are ap keys, created by tree.ap_to_key.
            # values are LeoTreeItems.
        self.leo_populated_dict = {}
            # Keys are ap keys, created by tree.ap_to_key.
            # values are ap's.
        self.clear_tree()
        self.tree = flx.TreeWidget(flex=1, max_selected=1)
            # The gnx of the selected tree item.
        self.redraw_with_dict(redraw_dict)
        
    @flx.emitter
    def key_press(self, e):
        ev = self._create_key_event(e)
        print('===== tree.key_down.emitter', repr(ev))
        if ev ['modifiers']:
            e.preventDefault()
        return ev
        
    #@+others
    #@+node:ekr.20181112163222.1: *4* tree.actions
    #@+node:ekr.20181112163252.1: *5* tree.action: clear_tree
    @flx.action
    def clear_tree(self):
        '''
        Completely clear the tree, preparing to recreate it.
        
        Important: we do *not* clear self.tree itself!
        '''
        # pylint: disable=access-member-before-definition
        #
        if debug_tree:
            print('===== tree.clear_tree')
        #
        # Clear all tree items.
        for item in self.leo_items.values():
            if debug_tree:
                print('tree.clear_tree: dispose: %r' % item)
            item.dispose()
        #
        # Clear the internal data structures.
        self.leo_items = {}
        self.leo_populated_dict = {}
    #@+node:ekr.20181116054402.1: *5* tree.action: echo
    @flx.action
    def echo (self, message=None):
        print('===== tree echo =====', message or '<Empty Message>')
    #@+node:ekr.20181110175222.1: *5* tree.action: receive_children
    @flx.action
    def receive_children(self, d):
        '''
        Using d, populate the children of ap. d has the form:
            {
                'parent': ap,
                'children': [ap1, ap2, ...],
            }
        '''
        parent_ap = d ['parent']
        children = d ['children']
        self.populate_children(children, parent_ap)
    #@+node:ekr.20181113043004.1: *5* tree.action: redraw
    @flx.action
    def redraw(self, redraw_dict):
        '''
        Clear the present tree and redraw using the redraw_list.
        '''
        if debug_tree:
            print('===== tree.redraw')
        self.clear_tree()
        self.redraw_with_dict(redraw_dict)
    #@+node:ekr.20181116083916.1: *5* tree.action: select_ap
    @flx.action
    def select_ap(self, ap):
        #
        # Unselect.
        if self.leo_selected_ap:
            old_key = self.ap_to_key(self.leo_selected_ap)
            old_item = self.leo_items.get(old_key)
            if old_item:
                # print('tree.select_ap: un-select:')
                old_item.set_selected(False)
            else:
                print('===== tree.select_ap: error: no item to unselect')
        else:
            print('tree.select_ap: no previously selected item.')
        #
        # Select.
        new_key = self.ap_to_key(ap)
        new_item = self.leo_items.get(new_key)
        if new_item:
            if debug_tree:
                print('tree.select_ap: select:')
            new_item.set_selected(True)
            self.leo_selected_ap = ap
        else:
            print('===== tree.select_ap: error: no item for ap:')
            self.leo_selected_ap = None
    #@+node:ekr.20181114072307.1: *4* tree.ap_to_key
    def ap_to_key(self, ap):
        '''Produce a key for the given ap.'''
        childIndex = ap ['childIndex']
        gnx = ap ['gnx']
        headline = ap ['headline'] # Important for debugging.
        stack = ap ['stack']
        stack_s = '::'.join([
            'childIndex: %s, gnx: %s' % (z ['childIndex'], z ['gnx'])
                for z in stack
        ])
        key = 'Tree key<childIndex: %s, gnx: %s, %s <stack: %s>>' % (
            childIndex, gnx, headline, stack_s or '[]')
        if False and key not in self.leo_populated_dict:
            print('')
            print('tree.ap_to_key: new key', ap ['headline'])
            print('key', key)
        return key
    #@+node:ekr.20181112172518.1: *4* tree.reactions
    #@+node:ekr.20181109083659.1: *5* tree.reaction: on_selected_event
    @flx.reaction('tree.children**.selected')
    def on_selected_event(self, *events):
        '''
        Update the tree and body text when the user selects a new tree node.
        '''
        for ev in events:
            if ev.new_value:
                # We are selecting a node, not de-selecting it.
                ap = ev.source.leo_ap
                    # Get the ap from the LeoTreeItem.
                self.root.select_ap(ap)
    #@+node:ekr.20181104080854.3: *5* tree.reaction: on_tree_event
    # actions: set_checked, set_collapsed, set_parent, set_selected, set_text, set_visible
    @flx.reaction(
        'tree.children**.checked',
        'tree.children**.collapsed',
        'tree.children**.visible', # Never seems to fire.
    )
    def on_tree_event(self, *events):
        for ev in events:
            if 0:
                self.show_event(ev)
    #@+node:ekr.20181116172300.1: *5* tree.reaction: key_down
    @flx.reaction('tree.key_press')
    def on_key_press(self, *events):
        for ev in events:
            self.root.do_key(ev, 'tree')
    #@+node:ekr.20181111011928.1: *4* tree.populate_children
    def populate_children(self, children, parent_ap):
        '''Populate parent with the children if necessary.'''
        trace = debug_tree and not g.unitTesting
        parent_key = self.ap_to_key(parent_ap)
        if parent_key in self.leo_populated_dict:
            # print('tree.populate_children: already populated', parent_ap ['headline'])
            return
        #
        # Set the key once, here.
        self.leo_populated_dict [parent_key] = parent_ap
        #
        # Populate the items.
        if parent_key not in self.leo_items:
            print('tree.populate_children: can not happen')
            self.root.dump_ap(parent_ap, None, 'parent_ap')
            for item in self.leo_items:
                print(item)
            return
        if trace:
            print('tree.populate_children:', len(children))
            if 0:
                print('parent_ap', repr(parent_ap))
                parent_key = self.ap_to_key(parent_ap)
                print('parent item:', repr(self.leo_items[parent_key]))
        with self.leo_items[parent_key]:
            for child_ap in children:
                headline = child_ap ['headline']
                child_item = LeoFlexxTreeItem(child_ap, text=headline, checked=None, collapsed=True)
                child_key = self.ap_to_key(child_ap)
                self.leo_items [child_key] = child_item
    #@+node:ekr.20181113043131.1: *4* tree.redraw_with_dict & helper
    def redraw_with_dict(self, d):
        '''
        Create LeoTreeItems from all items in the redraw_dict.
        The tree has already been cleared.
        '''
        # if debug: print('===== tree.redraw_from_dict')
        self.leo_selected_ap = d ['c.p']
            # Usually set in on_selected_event.
        for item in d ['items']:
            self.create_item_with_parent(item, self.tree)
           
    def create_item_with_parent(self, item, parent):
        '''Create a tree item for item and all its visible children.'''
        with parent:
            ap = item ['ap']
            headline = ap ['headline']
            # Create the tree item.
            tree_item = LeoFlexxTreeItem(ap, text=headline, checked=None, collapsed=True)
            key = self.ap_to_key(ap)
            self.leo_items [key] = tree_item
            # Create the item's children...
            for child in item ['children']:
                self.create_item_with_parent(child, tree_item)
    #@+node:ekr.20181108232118.1: *4* tree.show_event
    def show_event(self, ev):
        '''Put a description of the event to the log.'''
        w = self.root.main_window
        id_ = ev.source.title or ev.source.text
        kind = '' if ev.new_value else 'un-'
        s = kind + ev.type
        message = '%s: %s' % (s.rjust(15), id_)
        w.log.put(message)
        if 0: ###
            print('tree.show_event: ' + message)
    #@-others
#@+node:ekr.20181108233657.1: *3* class LeoFlexxTreeItem
class LeoFlexxTreeItem(flx.TreeItem):
    
    def init(self, leo_ap):
        # pylint: disable=arguments-differ
        self.leo_ap = leo_ap
        
    def getName(self):
        return 'head' # Required, for proper pane bindings.
        
    @flx.emitter
    def key_press(self, e):
        ev = self._create_key_event(e)
        print('===== tree-item.key_down.emitter', repr(ev))
        if ev ['modifiers']:
            e.preventDefault()
        return ev
#@+node:ekr.20181115191638.1: ** class Root
class Root(flx.PyComponent):
    
    '''
    This class allows *plain* python classes to access *component* classes.
    '''
    def __getattr__ (self, attr):
        return getattr(self.root, attr)
#@-others
if __name__ == '__main__':
    flx.launch(LeoBrowserApp)
    flx.logger.info('LeoApp: after flx.launch')
    if not debug:
        suppress_unwanted_log_messages()
    flx.run()
#@-leo
