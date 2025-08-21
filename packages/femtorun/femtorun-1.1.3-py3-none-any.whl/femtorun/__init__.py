from .runner import FemtoRunner, ComposedRunner
from .io_spec import IOSpec
from .dummy_runner import DummyRunner


def _get_dir():
    import pathlib

    return pathlib.Path(__file__).parent.resolve()


__version__ = (_get_dir() / "VERSION").read_text(encoding="utf-8").strip()
