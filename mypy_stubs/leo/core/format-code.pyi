import io
from typing import Any

StringIO = io.StringIO
h: str
p: Any
fn: Any
defaultOptionsDict: Any

class formatController:
    c: Any
    p: Any
    defaultOptionsDict: Any
    optionsDict: Any
    vnodeOptionDict: Any
    code_block_string: str
    node_counter: int
    topLevel: int
    topNode: Any
    atAutoWrite: bool
    atAutoWriteUnderlines: str
    leoDirectivesList: Any
    encoding: str
    ext: Any
    outputFileName: Any
    outputFile: Any
    path: str
    source: Any
    trialWrite: bool
    def __init__(self, c, p, defaultOptionsDict) -> None: ...
    singleNodeOptions: Any
    def initSingleNodeOptions(self) -> None: ...
    def getOption(self, name): ...
    def setOption(self, name, val, tag) -> None: ...
    def munge(self, name): ...
    def scanAllOptions(self, p) -> None: ...
    def initOptionsFromSettings(self) -> None: ...
    def handleSingleNodeOptions(self, p) -> None: ...
    def preprocessNode(self, p) -> None: ...
    def scanNodeForOptions(self, p): ...
    def parseOptionLine(self, s): ...
    def scanForOptionDocParts(self, p, s): ...
    def scanHeadlineForOptions(self, p): ...
    def scanOption(self, p, s): ...
    def scanOptions(self, p, s): ...
    def encode(self, s): ...
    def run(self, event: Any | None = ...) -> None: ...
    def underline(self, s, p): ...
    def write(self, s) -> None: ...
    def writeBody(self, p) -> None: ...
    def split_parts(self, lines, showDocsAsParagraphs): ...
    def write_code_block(self, lines): ...
    def writeHeadline(self, p) -> None: ...
    def writeHeadlineHelper(self, p) -> None: ...
    def writeNode(self, p) -> None: ...
    def writeTree(self, p) -> None: ...

fc: Any
