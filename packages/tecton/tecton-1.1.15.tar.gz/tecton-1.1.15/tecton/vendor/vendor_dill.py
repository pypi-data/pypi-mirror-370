"""
We vendor dill because it's a very important dependency to keep pinned (since
it handle serialization/deserialization) and it can conflict with other
dependencies users have (Beam is a known conflict).

Dill is a python-only package so it is easy to vendor fully.
"""

import os
import tempfile
import shutil
from pathlib import Path
import subprocess
import zipfile

DILL_VERSION = "0.3.0"

parent_dir = Path(__file__).parent
vendor_dir = parent_dir / "dill"
shutil.rmtree(vendor_dir, ignore_errors=True)
vendor_dir.mkdir()

with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    os.chdir(d)
    subprocess.check_call(["pip", "wheel", f"dill=={DILL_VERSION}"])


    def extract_whl(package_name):
        whl_glob = list(d.glob(f"{package_name}-*.whl"))
        assert len(whl_glob) == 1
        whl = whl_glob[0]
        with zipfile.ZipFile(whl) as z:
            for name in z.namelist():
                if all((name.startswith(f"{package_name}/"),
                        name.endswith(".py"),
                        not "/tests/" in name,
                        not "/examples/" in name)):
                    print(name)
                    z.extract(name, path=vendor_dir)

    extract_whl("dill")


subprocess.check_call(["patch", str(vendor_dir / "dill/objtypes.py"), str(parent_dir / "dill_objtypes.patch")])
