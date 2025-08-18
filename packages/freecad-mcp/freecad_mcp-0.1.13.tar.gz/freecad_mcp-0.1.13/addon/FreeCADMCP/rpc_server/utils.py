import os


HEADLESS = os.environ.get("FREECAD_HEADLESS", "0") == "1"
GUI_AVAILABLE = not HEADLESS


if GUI_AVAILABLE:
    import FreeCADGui          # noqa: E402
    from PySide import QtCore  # noqa: E402
else:
    class _Dummy:
        def __getattr__(self, name):
            raise RuntimeError(f"FreeCADGui::{name} is not available in headless mode")
    FreeCADGui = _Dummy()      # type: ignore
    QtCore = None              # type: ignore
