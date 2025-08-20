from pathlib import Path


def resolve_path(path: str, separator: str = "/") -> str:
    path_parts = path.split(separator)
    if len(path_parts) == 1:
        return path

    resolved_path_parts = []
    for i, p in enumerate(path_parts):
        if p == "" or p == ".":
            continue

        if p == "..":
            if len(resolved_path_parts) == 0:
                raise ValueError("Invalid path.")
            resolved_path_parts = resolved_path_parts[:-1]
        else:
            resolved_path_parts.append(p)

    if path.startswith(separator):
        # prepend separator to absolute paths
        resolved_path_parts = [""] + resolved_path_parts
    return separator.join(resolved_path_parts)
