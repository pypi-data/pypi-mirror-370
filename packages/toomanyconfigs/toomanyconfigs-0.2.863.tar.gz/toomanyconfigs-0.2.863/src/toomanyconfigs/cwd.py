from loguru import logger as log
from pathlib import Path
from typing import Union

class CWDNamespace:
    def __init__(self, path: Path):
        self._path = path

    def __repr__(self):
        return f"[CWDNamespace: {self._path}]"

class CWD:
    def __init__(self, *args: Union[str, dict], ensure: bool = True, path: Path = Path.cwd()):
        self.cwd = path
        self.file_structure = []
        self.folder_structure = []
        self.file_content = {}

        for arg in args:
            self._process_arg(arg, self.cwd)

        self._create_namespaces()
        if ensure:
            self.ensure_files()

    def _process_arg(self, arg, base_path: Path):
        if isinstance(arg, str):
            path = base_path / (arg.rstrip('/') if arg.endswith('/') else arg)
            (self.folder_structure if arg.endswith('/') else self.file_structure).append(path)

        elif isinstance(arg, list):
            raise NotImplemented

        elif isinstance(arg, dict):
            for key, value in arg.items():
                path = base_path / key
                if isinstance(value, str):
                    self.file_structure.append(path)
                    self.file_content[path] = value
                elif value is None:
                    self.file_structure.append(path)
                elif isinstance(value, dict) and len(value) == 0:
                    # Empty dict = empty folder
                    self.folder_structure.append(path)
                elif isinstance(value, (list, dict)):
                    self._process_arg(value, path)

        elif isinstance(arg, Path):
            raise NotImplemented

    def _create_namespaces(self):
        all_paths = self.file_structure + self.folder_structure

        for path in all_paths:
            parts = path.relative_to(self.cwd).parts
            current = self

            for i, part in enumerate(parts):
                attr_name = self._clean_name(part)

                if i == len(parts) - 1:
                    # Final part - set actual path or namespace
                    if path in self.folder_structure or any(p.parent == path for p in all_paths):
                        setattr(current, attr_name, CWDNamespace(path))
                    else:
                        setattr(current, attr_name, path)
                else:
                    # Intermediate - ensure namespace exists
                    if not hasattr(current, attr_name):
                        setattr(current, attr_name, CWDNamespace(self.cwd / Path(*parts[:i+1])))
                    current = getattr(current, attr_name)

    def _clean_name(self, name):
        if '.' in name:
            name = name.rsplit('.', 1)[0]
        name = name.replace('-', '_').replace(' ', '_')
        if name and not (name[0].isalpha() or name[0] == '_'):
            name = f"_{name}"
        return name

    def ensure_files(self):
        for folder_path in self.folder_structure:
            folder_path.mkdir(parents=True, exist_ok=True)

        for file_path in self.file_structure:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if not file_path.exists():
                if file_path in self.file_content:
                    file_path.write_text(self.file_content[file_path])
                else:
                    file_path.touch()

        log.info(f"{self}: Created file structure:\n{self.tree_structure}")

    @property
    def tree_structure(self):
        if not self.file_structure and not self.folder_structure:
            return "Empty file structure"

        dirs = {}
        for path in self.file_structure + self.folder_structure:
            rel_path = path.relative_to(self.cwd)
            parent = rel_path.parent
            if parent not in dirs:
                dirs[parent] = {'files': [], 'folders': []}

            if path in self.folder_structure:
                dirs[parent]['folders'].append(rel_path.name)
            else:
                dirs[parent]['files'].append(rel_path.name)

        lines = [str(self.cwd)]
        for i, dir_path in enumerate(sorted(dirs.keys())):
            is_last_dir = i == len(dirs) - 1

            if str(dir_path) == '.':
                items = [(n, 'folder') for n in sorted(dirs[dir_path]['folders'])] + \
                       [(n, 'file') for n in sorted(dirs[dir_path]['files'])]
                for j, (name, type_) in enumerate(items):
                    prefix = "└── " if j == len(items) - 1 and is_last_dir else "├── "
                    suffix = "/" if type_ == 'folder' else ""
                    lines.append(f"{prefix}{name}{suffix}")
            else:
                lines.append(f"{'└── ' if is_last_dir else '├── '}{dir_path}/")
                items = [(n, 'folder') for n in sorted(dirs[dir_path]['folders'])] + \
                       [(n, 'file') for n in sorted(dirs[dir_path]['files'])]
                for j, (name, type_) in enumerate(items):
                    indent = "    " if is_last_dir else "│   "
                    prefix = "└── " if j == len(items) - 1 else "├── "
                    suffix = "/" if type_ == 'folder' else ""
                    lines.append(f"{indent}{prefix}{name}{suffix}")

        return "\n".join(lines)

    def list_structure(self):
        for path in self.folder_structure:
            log.debug(f"Folder: {path}")
        for path in self.file_structure:
            content_info = " (with content)" if path in self.file_content else ""
            log.debug(f"File: {path}{content_info}")

    def __repr__(self):
        return f"[CWD: {self.cwd}]"