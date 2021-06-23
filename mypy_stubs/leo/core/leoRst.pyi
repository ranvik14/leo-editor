import io
import unittest
from typing import Any

StringIO = io.StringIO

def cmd(name): ...

class RstCommands:
    c: Any
    n_intermediate: int
    n_docutils: int
    anchor_map: Any
    http_map: Any
    nodeNumber: int
    at_auto_underlines: str
    at_auto_write: bool
    encoding: str
    path: str
    result_list: Any
    root: Any
    default_underline_characters: str
    user_filter_b: Any
    user_filter_h: Any
    def __init__(self, c) -> None: ...
    silent: Any
    http_server_support: Any
    node_begin_marker: Any
    default_path: Any
    generate_rst_header_comment: Any
    underline_characters: Any
    write_intermediate_file: Any
    write_intermediate_extension: Any
    call_docutils: Any
    publish_argv_for_missing_stylesheets: Any
    stylesheet_embed: Any
    stylesheet_name: Any
    stylesheet_path: Any
    def reloadSettings(self) -> None: ...
    def convert_legacy_outline(self, event: Any | None = ...) -> None: ...
    options_pat: Any
    default_pat: Any
    def convert_rst_options(self, p) -> None: ...
    def preformat(self, p) -> None: ...
    def rst3(self, event: Any | None = ...) -> None: ...
    def processTopTree(self, p): ...
    def processTree(self, root) -> None: ...
    def write_rst_tree(self, p, fn): ...
    def write_slides(self, p) -> None: ...
    def writeSlideTitle(self, title, n, n_tot) -> None: ...
    def writeNode(self, p) -> None: ...
    def http_addNodeMarker(self, p) -> None: ...
    def write_docutils_files(self, fn, p, source) -> None: ...
    def addTitleToHtml(self, s): ...
    def computeOutputFileName(self, fn): ...
    def createDirectoryForFile(self, fn): ...
    def writeIntermediateFile(self, fn, p, s) -> None: ...
    def writeToDocutils(self, p, s, ext): ...
    def handleMissingStyleSheetArgs(self, p, s: Any | None = ...): ...
    def writeAtAutoFile(self, p, fileName, outputFile): ...
    underlines1: Any
    underlines2: Any
    def initAtAutoWrite(self, p) -> None: ...
    def isSafeWrite(self, p): ...
    def writeNodeToString(self, p): ...
    def filter_b(self, c, p): ...
    def filter_h(self, c, p): ...
    def register_body_filter(self, f) -> None: ...
    def register_headline_filter(self, f) -> None: ...
    def in_ignore_tree(self, p): ...
    def in_rst_tree(self, p): ...
    def in_slides_tree(self, p): ...
    def is_ignore_node(self, p): ...
    def is_rst_node(self, p): ...
    def rst_parents(self, p) -> None: ...
    def compute_result(self): ...
    def dumpDict(self, d, tag) -> None: ...
    def encode(self, s): ...
    def report(self, name, p) -> None: ...
    def rstComment(self, s): ...
    def underline(self, p, s): ...

class TestRst3(unittest.TestCase):
    c: Any
    maxDiff: Any
    def setUp(self) -> None: ...
    def tearDown(self) -> None: ...
    def runLegacyTest(self, c, p) -> None: ...
    def test_1(self) -> None: ...
