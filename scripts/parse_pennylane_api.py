import importlib
import importlib.util
import inspect
import json
import pkgutil
import sys

import pennylane as qml


def walk_qml_modules(package):
    prefix = package.__name__ + "."
    for _, mod_name, _ in pkgutil.walk_packages(package.__path__, prefix):
        yield mod_name


def parse_api():
    print(f"Pennylane version: {qml.__version__}")
    result = {}
    for mod_name in walk_qml_modules(qml):
        try:
            module = importlib.import_module(mod_name)
        except Exception:
            continue
        for attr_name, obj in inspect.getmembers(
            module, predicate=lambda o: inspect.isclass(o) or inspect.isfunction(o)
        ):
            if not hasattr(qml, attr_name):
                continue
            fq = f"qml.{attr_name}"
            try:
                source = inspect.getsource(obj)
            except (OSError, TypeError):
                source = None
            try:
                sig = str(inspect.signature(obj))
            except (ValueError, TypeError):
                sig = None
            doc = inspect.getdoc(obj) or ""
            result[fq] = {"signature": sig, "docstring": doc, "source": source}
    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_pennylane_api.py <output_json_path>")
        sys.exit(1)

    out_path = sys.argv[1]
    data = parse_api()
    with open(out_path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)
    print(f"Written {len(data)} entries to {out_path}")
