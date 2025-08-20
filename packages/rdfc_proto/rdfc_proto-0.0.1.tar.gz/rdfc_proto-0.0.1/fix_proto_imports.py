import re
import pathlib

# Where grpc_tools.protoc outputs generated files
OUTPUT_DIR = pathlib.Path("src/rdfc_proto/generated")

# Regex to match _pb2 and _pb2_grpc imports
pattern = re.compile(r"^import (\w+_pb2(?:_grpc)?) as (\w+)$")

def fix_imports():
    for file_path in OUTPUT_DIR.rglob("*.py"):  # recursive in case of subdirs
        lines = file_path.read_text().splitlines()
        fixed_lines = []
        changed = False

        for line in lines:
            match = pattern.match(line.strip())
            if match:
                module, alias = match.groups()
                fixed_lines.append(f"from . import {module} as {alias}")
                changed = True
            else:
                fixed_lines.append(line)

        if changed:
            file_path.write_text("\n".join(fixed_lines))
            print(f"Fixed imports in {file_path}")

if __name__ == "__main__":
    fix_imports()
    print("All imports fixed ✅")
