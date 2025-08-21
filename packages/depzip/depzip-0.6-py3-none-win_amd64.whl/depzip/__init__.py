import sys
from importlib import import_module


def bundle(applications=[], modules=[], includes=[], excludes=[], output="bundle.zip"):

    # Import modules to discover their dependencies

    for m in modules:
        import_module(m)

    dependencies = {
        n: m
        for n, m in sys.modules.copy().items()
        if n not in ("__main__", __name__) and getattr(m, "__file__", None)
    }

    # Helper functions

    from pathlib import Path

    def contains(string, substrings):
        string = string.casefold()
        return any(s.casefold() in string for s in substrings)

    def abspath(path, bases):
        if path.is_absolute():
            return path
        for b in bases:
            result = b / path
            if result.exists():
                return result
        return None

    def relpath(path, bases):
        if not path.is_absolute():
            return path
        for b in bases:
            if path.is_relative_to(b):
                return path.relative_to(b)
        return None

    bases = []
    for p in sorted(Path(p).resolve() for p in sys.path):
        if not any(p.is_relative_to(b) for b in bases):
            bases.append(p)

    # Collect files to bundle

    bundle = {Path(m.__file__) for m in dependencies.values()}

    # Find and collect license files for bundled modules

    from importlib.metadata import distribution, packages_distributions

    packages = {n.split(".", 1)[0] for n in dependencies.keys()}
    mapping = packages_distributions()
    version = ".".join(str(v) for v in sys.version_info[:3])
    licenses = {f"Python-{version}": {Path(sys.base_prefix) / "LICENSE.txt"}}

    for p in packages:
        for n in mapping.get(p, []):
            d = distribution(n)
            licenses.setdefault(f"{n}-{d.version}", set()).update(
                root / f
                for root, _, files in Path(d._path).walk()
                for f in files
                if contains(f, ("license", "copying"))
            )

    # Collect DLLs to bundle

    from dllist import dllist

    bundle.update(
        dll
        for dll in (Path(dll) for dll in dllist())
        if relpath(dll, bases) and not contains(dll.name, ("vcruntime", "msvcp"))
    )

    # Include additional files and directories

    for i in includes:
        path = abspath(Path(i), bases)
        if path is None:
            continue
        if path.is_dir():
            for root, dirs, files in path.walk():
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                bundle.update(root / f for f in files)
        elif path.is_file():
            bundle.add(path)

    # Exclude specified files

    bundle = {f for f in bundle if not contains(f.name, excludes)}

    # Create the output zip file

    from zipfile import ZipFile, ZIP_DEFLATED

    version = "".join(str(v) for v in sys.version_info[:2])
    run = Path(__file__).parent / f"run{version}.exe"

    with ZipFile(output, "w", ZIP_DEFLATED) as zf:
        for a in sorted(applications):
            if run.is_file():
                zf.write(run, f"{a}.exe")

        for d, files in licenses.items():
            for f in sorted(files):
                name = Path("Licenses") / d / f.name
                zf.write(f, name)

        for f in sorted(bundle):
            if f.is_file():
                zf.write(f, relpath(f, bases))
