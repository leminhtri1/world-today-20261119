"""Copy the pre-rendered front page to /output/entry.png (standard library only)."""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "/output"

os.makedirs(OUT_DIR, exist_ok=True)
shutil.copyfile(os.path.join(HERE, "entry.png"), os.path.join(OUT_DIR, "entry.png"))
