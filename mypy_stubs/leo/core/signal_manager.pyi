from typing import Any

class SignalData:
    listeners: Any
    emitters: Any
    locked: bool
    def __init__(self) -> None: ...

class MsgSignalHandled: ...

def emit(source, signal_name, *args, **kwargs) -> None: ...
def connect(source, signal_name, listener) -> None: ...
def disconnect_all(listener) -> None: ...
def is_locked(obj): ...
def lock(obj) -> None: ...
def unlock(obj) -> None: ...

class SignalManager:
    def emit(self, signal_name, *args, **kwargs) -> None: ...
    def connect(self, signal_name, listener) -> None: ...

def main() -> None: ...
