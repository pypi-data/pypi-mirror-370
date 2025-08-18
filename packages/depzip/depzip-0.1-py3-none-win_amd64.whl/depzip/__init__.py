import os
import sys
from importlib import import_module


def bundle(applications=[], modules=[], includes=[], excludes=[], output="bundle.zip"):

    def contains(string, substrings):
        string = string.casefold()
        return any(s.casefold() in string for s in substrings)

    base = os.path.dirname(sys.executable)

    # Import modules to discover their dependencies

    for m in modules:
        import_module(m)

    dependencies = {
        n: m
        for n, m in sys.modules.items()
        if n not in ("__main__", __name__) and getattr(m, "__file__", None)
    }

    # Collect files to bundle

    bundle = {m.__file__ for m in dependencies.values()}

    # Find and collect license files for bundled modules

    from importlib.metadata import distribution, packages_distributions

    packages = {n.split(".", 1)[0] for n in dependencies.keys()}
    mapping = packages_distributions()
    licenses = {"Python": {os.path.join(base, "LICENSE.txt")}}

    for p in packages:
        for d in mapping.get(p, []):
            path = distribution(d)._path
            licenses.setdefault(d, set()).update(
                os.path.join(root, f)
                for root, _, files in os.walk(path)
                for f in files
                if contains(f, ("license", "copying"))
            )

    # Collect DLLs to bundle

    from dllist import dllist

    bundle.update(
        dll
        for dll in dllist()
        if os.path.commonpath([dll, base]) == base
        and not contains(os.path.basename(dll), ("vcruntime", "msvcp"))
    )

    # Include additional files and directories

    for path in includes:
        path = path if os.path.exists(path) else os.path.join(base, path)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                bundle.update(os.path.join(root, f) for f in files)
        elif os.path.isfile(path):
            bundle.add(path)

    # Exclude specified files

    bundle = {f for f in bundle if not contains(f, excludes)}

    # Create the output zip file

    from zipfile import ZipFile, ZIP_DEFLATED

    v = sys.version_info[:2]
    exe = os.path.join(__path__[0], f"import{v[0]}{v[1]}.exe")

    with ZipFile(output, "w", ZIP_DEFLATED) as zf:
        for a in applications:
            if os.path.isfile(exe):
                zf.write(exe, f"{a}.exe")

        for d, files in licenses.items():
            for f in sorted(files):
                name = os.path.join("Licenses", d, os.path.basename(f))
                zf.write(f, name)

        for f in sorted(bundle):
            if os.path.isfile(f):
                name = os.path.relpath(f, base) if os.path.isabs(f) else f
                zf.write(f, name)
