import shutil
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from logging import Logger
import logging

logger = logging.getLogger(__name__)
from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Optional

from mitoolspro.exceptions import (
    ProjectError,
    ProjectFolderError,
    ProjectVersionError,
)
from mitoolspro.files import (
    build_dir_tree,
    file_in_folder,
    folder_in_subtree,
    folder_is_subfolder,
    read_json,
    write_json,
)
from mitoolspro.project.project_notebook import ProjectNotebook

PROJECT_FILENAME = Path("project.json")
PROJECT_FOLDER = Path(".project")
PROJECT_NOTEBOOK = "Project.ipynb"
PROJECT_ARCHIVE = ".archive"
PROJECT_BACKUP = ".backup"


class VersionState(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass
class VersionInfo:
    version: str
    creation: float
    state: VersionState = VersionState.ACTIVE
    description: str = ""


class Project:
    def __init__(
        self,
        project_name: str,
        root: PathLike = ".",
        version: str = "v0",
        logger: Logger = None,
    ):
        if not isinstance(project_name, str) or not project_name:
            raise ProjectError(f"Project 'root'={root} must be a non-empty string.")
        self.root = Path(root).absolute()
        if self.root.exists() and not self.root.is_dir():
            raise ProjectFolderError(f"{self.root} is not a directory")
        elif not self.root.exists():
            raise ProjectFolderError(f"{self.root} does not exist")
        self.logger = logger
        self.name = project_name
        self.folder = self.root / self.name
        self.project_folder = self.folder / PROJECT_FOLDER
        self.project_file = self.folder / PROJECT_FILENAME
        self.project_notebook = self.folder / PROJECT_NOTEBOOK
        self.backup_folder = self.folder / PROJECT_BACKUP
        self.create_main_folder()
        self.version = version
        self.version_folder = self.folder / self.version
        self.create_version_folder()
        self.versions = self.get_all_versions()
        self.versions_metadata: Dict[str, VersionInfo] = {}
        self.vars: Dict[str, Any] = {}
        self.paths: Dict[str, Path] = {}
        self.version_paths: Dict[str, Dict[str, str]] = {}
        self.tree = build_dir_tree(self.folder)
        self.update_info()

        if not self.project_file.exists():
            self.store_project()

    def create_main_folder(self) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        self.project_folder.mkdir(parents=True, exist_ok=True)
        self.create_project_notebook()  # TODO

    def create_version_folder(self) -> None:
        self.version_folder.mkdir(parents=True, exist_ok=True)

    def get_all_versions(self) -> List[str]:
        return [
            d.name
            for d in self.folder.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

    def folder_path_dict(self) -> List[str]:
        return {
            subfolder: self.version_folder / subfolder for subfolder in self.subfolders
        }

    def update_info(self) -> None:
        self.versions = self.get_all_versions()
        self.version_folders = [
            Path(self.folder) / version for version in self.versions
        ]
        self.version_folder = self.folder / self.version
        self.subfolders = self.list_version_subfolders()
        self.paths.update(self.folder_path_dict())

    def create_version(self, version: str, description: str = "") -> None:
        version_path = self.folder / version
        if not version_path.exists():
            version_path.mkdir(parents=True, exist_ok=True)
            self.update_info()
            self.add_version_metadata(version, description)
        else:
            raise ProjectVersionError(
                f"Version {version} already exists in Project {self.name}. Existing versions: [{self.versions}]"
            )

    def update_version(self, version: str) -> None:
        self.version = version
        self.version_folder = self.folder / self.version
        self.create_version_folder()
        self.update_info()

    def add_version_metadata(self, version: str, description: str = "") -> None:
        if version not in self.versions:
            raise ProjectError(
                f"Version {version} does not exist in Project {self.name} with version {self.versions}"
            )
        self.versions_metadata[version] = VersionInfo(
            version=version,
            creation=datetime.now(),
            description=description,
        )
        self.store_project()

    def create_version_subfolder(self, subfolder_name: str) -> None:
        subfolder_path = self.version_folder / subfolder_name
        subfolder_path.mkdir(parents=True, exist_ok=True)
        self.update_info()

    def list_version_subfolders(self) -> List[str]:
        return [d.name for d in self.version_folder.iterdir() if d.is_dir()]

    @contextmanager
    def version_context(self, version: str):
        original_version = self.version
        try:
            self.update_version(version)
            yield
        finally:
            self.update_version(original_version)

    def delete_subfolder(self, subfolder_name: str) -> None:
        subfolder_path = self.version_folder / subfolder_name
        if not subfolder_path.exists():
            raise ProjectFolderError(
                f"Subfolder {subfolder_name} does not exist in Project {self.name} version {self.version}"
            )
        for child in subfolder_path.iterdir():
            if child.is_file():
                child.unlink()
        subfolder_path.rmdir()
        self.update_info()

    def delete_version(self, version: str) -> None:
        if version in self.versions and len(self.versions) == 1:
            raise ProjectError(
                f"Cannot delete, {version} is the only version of Project {self.name}"
            )
        elif version not in self.versions:
            raise ProjectVersionError(
                f"Version {version} does not exist in Project {self.name}, with versions: {self.versions}"
            )
        version_path: Path = self.folder / version
        logger.info("About to remove version %s of Project %s...", version, self.name)
        if version_path.exists() and version_path.is_dir():
            for item in version_path.glob("**/*"):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
            version_path.rmdir()
        logger.info("Removed version %s of Project %s", version, self.name)
        if self.version == version:
            logger.info(
                "Changing current version of Project %s to %s",
                self.name,
                self.versions[0],
            )
            self.update_version(self.versions[0])

    def archive_version(self, version: str) -> None:
        if version not in self.versions_metadata:
            raise ProjectError(
                f"Version {version} not found int Project {self.name} with versions {self.versions}"
            )
        self.versions_metadata[version].state = VersionState.ARCHIVED
        archive_path = self.folder / PROJECT_ARCHIVE / version
        version_path = self.folder / version
        archive_path.parent.mkdir(exist_ok=True)
        shutil.move(str(version_path), str(archive_path))
        self.store_project()

    def restore_version(self, version: str) -> None:
        archive_path = self.folder / PROJECT_ARCHIVE / version
        if not archive_path.exists():
            raise ProjectError(
                f"Archived version {version} not found in Archive: {self.folder / PROJECT_ARCHIVE}"
            )
        version_path = self.folder / version
        shutil.move(str(archive_path), str(version_path))
        self.versions_metadata[version].state = VersionState.ACTIVE
        self.store_project()

    def reset_version(self, version: str) -> None:
        self.delete_version(version)
        self.update_version(version)

    def get_version_data(self, version: str) -> Dict[str, Any]:
        if version not in self.versions_metadata:
            raise ProjectVersionError(
                f"Version {version} not found in Porject {self.name} with versions {self.versions}"
            )
        metadata = self.versions_metadata[version]
        return {
            "name": version,
            "creation": metadata.creation,
            "state": metadata.state.value,
            "description": metadata.description,
            "subfolders": self.list_version_subfolders(),
        }

    def clear_version(self) -> None:
        for path in self.version_folder.rglob("*"):
            if path.is_file():
                path.unlink()

    def clear_project(self) -> None:
        for path in self.folder.rglob("*"):
            if (
                path.is_file()
                and path.name != PROJECT_FILENAME
                and path.name != PROJECT_NOTEBOOK
                and path.parent != PROJECT_FOLDER
                and path.parent != PROJECT_ARCHIVE
                and path.parent != PROJECT_BACKUP
            ):
                path.unlink()

    def delete_file(self, file_name: str, subfolder: str = None) -> None:
        subfolder_path = self.version_folder / subfolder
        if not subfolder_path.exists():
            raise ProjectFolderError(
                f"Subfolder {subfolder} does not exist in Project {self.name} version {self.version}"
            )
        file_path = subfolder_path / file_name
        if not file_path.exists():
            raise ProjectError(
                f"File {file_name} does not exist in subfolder {subfolder} of Project {self.name}"
            )
        file_path.unlink()

    def store_project(self) -> None:
        self.update_info()
        project_data = self.as_dict()
        write_json(
            project_data, self.project_file, ensure_ascii=False, encoding="utf-8"
        )

    @classmethod
    def find_project(
        cls,
        project_folder: Optional[PathLike] = None,
        max_depth: int = 3,
        auto_load: bool = False,
    ):
        if project_folder is None and auto_load:
            current_path = Path.cwd().resolve()
            for _ in range(max_depth):
                project_path = current_path / PROJECT_FILENAME
                if project_path.exists():
                    break
                if current_path.parent == current_path:  # reached the root directory
                    break
                current_path = current_path.parent
            else:
                raise ProjectError(
                    f"No {PROJECT_FILENAME} found in the current or {max_depth} parent directories."
                )
        else:
            project_path = Path(project_folder) / PROJECT_FILENAME
            if not project_path.exists():
                raise ProjectError(
                    f"{PROJECT_FILENAME} does not exist in the specified directory {project_folder}"
                )
        return project_path

    @classmethod
    def load(
        cls,
        project_folder: Optional[Path] = None,
        auto_load: bool = False,
        max_depth: int = 3,
    ) -> "Project":
        project_path = cls.find_project(
            project_folder=project_folder, max_depth=max_depth, auto_load=auto_load
        )
        project_json = read_json(project_path)
        obj = cls.from_dict(project_json)
        obj.update_info()
        current_path = Path.cwd().resolve()
        if folder_is_subfolder(obj.root, current_path):
            version_folder = folder_in_subtree(
                obj.root, current_path, obj.version_folders
            )
            if version_folder:
                obj.update_version(version_folder.stem)
                logger.info("Updated Project version to current %s version.", obj.version)
        return obj

    def __repr__(self) -> str:
        return f"Project({self.root}, {self.name}, {self.version})"

    def __str__(self) -> str:
        return (
            f"Project {self.name}\n\nCurrent Version: {self.version},\nRoot: {self.root},\n"
            + f"Folder: {self.folder},\nVersions: {self.versions}\n"
        )

    def get_info(self) -> Dict:
        self.update_info()
        return {
            "name": self.name,
            "root": str(self.root),
            "folder": str(self.folder),
            "version": self.version,
            "versions": self.versions,
            "subfolders": self.subfolders,
        }

    def version_tree(self) -> None:
        self.directory_tree(self.version_folder)

    def project_tree(self) -> None:
        self.directory_tree(self.folder)

    def directory_tree(self, directory: PathLike) -> None:
        self.tree = build_dir_tree(directory)
        self.tree.show()

    def clone_version(self, source_version: str, new_version: str) -> None:
        source_version_folder = self.folder / source_version
        new_version_folder = self.folder / new_version

        if not source_version_folder.exists():
            raise ProjectVersionError(
                f"Version {source_version} does not exists in Project {self.name}. Existing versions: [{self.versions}]"
            )

        if new_version_folder.exists():
            raise ProjectVersionError(
                f"Version {new_version} already exists in Project {self.name}. Existing versions: [{self.versions}]"
            )

        shutil.copytree(source_version_folder, new_version_folder)
        self.update_version(new_version)
        self.update_info()
        self.store_project()

    def add_var(
        self, key: str, value: Any, update: bool = False, exist_ok: bool = False
    ) -> None:
        if key in self.vars and not update:
            if not exist_ok:
                raise ProjectError(
                    f"Key '{key}' already exists in self.vars. Use update_var() to modify existing variables."
                )
            else:
                return
        self.vars[key] = value
        self.store_project()
        logger.info("Added '%s' to project variables and stored the project.", key)

    def remove_var(self, key: str) -> None:
        if key not in self.vars:
            raise ProjectError(f"Key '{key}' does not exist in self.vars")
        del self.vars[key]
        self.store_project()
        logger.info("Removed '%s' from project variables and stored the project.", key)

    def update_var(self, key: str, value: Any, create: bool = False) -> None:
        if key not in self.vars and not create:
            raise ProjectError(
                f"Key {key} does not exist in self.vars. Cannot update non-existing variable."
            )
        self.vars[key] = value
        self.store_project()
        logger.info("Updated '%s' of project variables and stored the project.", key)

    def add_path(
        self, key: str, path: PathLike, update: bool = False, exist_ok: bool = False
    ) -> None:
        current_version_folder = (self.folder / self.version).resolve()
        path_resolved = Path(path).resolve()
        is_version_child = file_in_folder(current_version_folder, path_resolved)
        if is_version_child:
            if self.version not in self.version_paths:
                self.version_paths[self.version] = {}
            if key in self.version_paths[self.version] and not update:
                if not exist_ok:
                    raise ProjectError(
                        f"Key '{key}' already exists in version '{self.version}' version_paths. "
                        f"Use overwrite=True to replace it."
                    )
                else:
                    return
            relative_path = path_resolved.relative_to(current_version_folder)
            self.version_paths[self.version][key] = str(relative_path)
        else:
            if key in self.paths and not update:
                if not exist_ok:
                    raise ProjectError(
                        f"Key '{key}' already exists in global 'paths'. Use overwrite=True to replace it."
                    )
                else:
                    return
            self.paths[key] = path_resolved
        self.store_project()
        logger.info("Added '%s' to project paths and stored the project.", key)

    def update_path(self, key: str, new_path: PathLike) -> None:
        if (
            self.version in self.version_paths
            and key in self.version_paths[self.version]
        ) or key in self.paths:
            self.add_path(key, new_path, update=True)
        else:
            raise ProjectError(
                f"Cannot update '{key}' because it does not exist in version '{self.version}' or global paths."
            )
        logger.info("Updated '%s' of project paths and stored the project.", key)

    def get_path(self, key: str) -> Path:
        if (
            self.version in self.version_paths
            and key in self.version_paths[self.version]
        ):
            relative_path = self.version_paths[self.version][key]
            return (self.version_folder / relative_path).resolve()
        if key in self.paths:
            return self.paths[key]
        raise ProjectError(
            f"Path key='{key}' not found in version '{self.version}' or global paths."
        )

    def remove_path(self, key: str) -> None:
        if (
            self.version in self.version_paths
            and key in self.version_paths[self.version]
        ):
            del self.version_paths[self.version][key]
            if not self.version_paths[self.version]:
                del self.version_paths[self.version]  # Clean up empty dict
            self.store_project()
            logger.info(
                "Removed path '%s' from version '%s' version_paths.", key, self.version
            )
            return
        if key in self.paths:
            del self.paths[key]
            self.store_project()
            logger.info("Removed path '%s' from global paths.", key)
        raise ProjectError(
            f"Cannot remove '{key}' because it does not exist in current version '{self.version}' or global paths."
        )

    def create_project_notebook(self) -> None:
        notebook = ProjectNotebook(self.name)
        if not self.project_notebook.exists():
            notebook.write(self.project_notebook)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "root": str(self.root),
            "name": self.name,
            "version": self.version,
            "versions": self.versions,
            "versions_metadata": {
                ver: {
                    "version": info.version,
                    "creation": info.creation.timestamp()
                    if isinstance(info.creation, datetime)
                    else info.creation,
                    "state": info.state.value if info.state else None,
                    "description": info.description,
                }
                for ver, info in self.versions_metadata.items()
            },
            "vars": self.vars,
            "paths": {k: str(p) for k, p in self.paths.items()},
            "version_paths": {
                version: {key: str(path) for key, path in paths.items()}
                for version, paths in self.version_paths.items()
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], logger: Logger = None) -> "Project":
        root = data["root"]
        project_name = data["name"]
        version = data["version"]
        project = cls(
            project_name=project_name,
            root=root,
            version=version,
            logger=logger,
        )
        project.versions = data.get("versions", [])
        raw_versions_metadata = data.get("versions_metadata", {})
        project.versions_metadata = {}
        for ver, meta in raw_versions_metadata.items():
            creation_ts = meta.get("creation")
            if isinstance(creation_ts, (float, int)):
                creation_dt = datetime.fromtimestamp(creation_ts)
            else:
                creation_dt = creation_ts
            project.versions_metadata[ver] = VersionInfo(
                version=meta["version"],
                creation=creation_dt,
                state=VersionState(meta["state"]) if meta["state"] else None,
                description=meta["description"],
            )
        project.vars = data.get("vars", {})
        project.paths = {k: Path(p) for k, p in data.get("paths", {}).items()}
        project.version_paths = {
            version: {k: Path(p) for k, p in paths.items()}
            for version, paths in data.get("version_paths", {}).items()
        }
        project.update_info()
        return project
