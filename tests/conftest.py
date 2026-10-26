import importlib.util
import pathlib
import sys

# Sisyphus is installed as the "sisyphus" package, but in the source tree it
# lives in src/backend. Load it under that name so the tests can import
# sisyphus.<module> the same way the program does.
BACKEND = pathlib.Path(__file__).resolve().parent.parent / "src" / "backend"

spec = importlib.util.spec_from_file_location(
    "sisyphus", BACKEND / "__init__.py", submodule_search_locations=[str(BACKEND)])
sisyphus = importlib.util.module_from_spec(spec)
sys.modules["sisyphus"] = sisyphus
spec.loader.exec_module(sisyphus)
