from pathlib import Path
import json

class ProjectContext:
    def __init__(self):
        self._project_root = Path(r"D:\BLENDER_RELOADED\Seafile\Seafile\Highlanders\PRODUCTION\Show")

    def set_project(self, root: Path):
        root = root.resolve()
        if not (root / "PRODUCTION").is_dir():
            raise ValueError(f"'{root}' does not appear to be a valid project (missing _assets).")
        self._project_root = root

    @property
    def root(self) -> Path:
        if not self._project_root:
            raise RuntimeError("Project root not set.")
        return self._project_root

    @property
    def assets_path(self) -> Path:
        return self.root / ""


    def ensure_directories_exist(self):
        """Make sure expected folders exist."""
        self.assets_path.mkdir(parents=True, exist_ok=True)
        self.thumbnails_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
    