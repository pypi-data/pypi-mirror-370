try:
    from .wizard import Wizard
except Exception:
    class Wizard:  # minimal shim
        def __init__(self, *args, **kwargs):
            pass
        def run(self):
            raise NotImplementedError("Wizard not implemented")

__all__ = ["Wizard"]
