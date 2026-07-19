"""Make available ECSS TEEY, as exported by SPARK3D."""

from importlib import resources

files = resources.files(__name__)
al = files / "aluminium_ecss.txt"
ag = files / "silver_ecss.txt"
cu = files / "copper_ecss.txt"
