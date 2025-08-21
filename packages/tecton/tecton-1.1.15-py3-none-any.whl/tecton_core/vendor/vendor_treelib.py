import os
import tempfile
import shutil
from pathlib import Path
import subprocess
import zipfile

TREELIB_VERSION = "1.6.1"

vendor_dir = Path(__file__).parent

with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    os.chdir(d)
    subprocess.check_call(["pip", "wheel", f"treelib=={TREELIB_VERSION}"])


    def extract_whl(package_name):
        """Extracts source files from the wheel. In order for the module to be used, it must be added to the
        appropriate BUILD.bazel configuration file.
        """
        whl_glob = list(d.glob(f"{package_name}-*.whl"))
        assert len(whl_glob) == 1
        whl = whl_glob[0]
        with zipfile.ZipFile(whl) as z:
            for name in z.namelist():
                if all((name.startswith(f"{package_name}/"),
                        name.endswith(".py"))):
                    print(name)
                    z.extract(name, path=vendor_dir)


    extract_whl("treelib")

subprocess.check_call(["patch", str(vendor_dir / "treelib/node.py"), str(vendor_dir / "treelib_node.patch")])
subprocess.check_call(["patch", str(vendor_dir / "treelib/tree.py"), str(vendor_dir / "treelib_tree.patch")])
subprocess.check_call(["patch", str(vendor_dir / "treelib/plugins.py"), str(vendor_dir / "treelib_plugins.patch")])
