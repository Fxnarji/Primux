from pathlib import Path
import json

class ProjectContext:
    def __init__(self):
        self.project_root = Path(r"D:\BLENDER_RELOADED\Seafile\Seafile\Highlanders\PRODUCTION")
        self.show_path = self.project_root / "Show"
        self.assets_path = self.project_root / "Assets"

        # Optional: define other directories
        self.thumbnails_path = self.project_root / "_thumbnails"
        self.metadata_path = self.project_root / "_metadata"

    def set_project(self, root: Path):
        root = root.resolve()
        self.project_root = root
        self.show_path = self.project_root / "Show"
        self.assets_path = self.project_root / "Assets"
        self.thumbnails_path = self.project_root / "_thumbnails"
        self.metadata_path = self.project_root / "_metadata"

    @property
    def root(self) -> Path:
        if not self.project_root:
            raise RuntimeError("Project root not set.")
        return self.project_root

    def ensure_directories_exist(self):
        """Make sure expected folders exist."""
        self.show_path.mkdir(parents=True, exist_ok=True)
        self.assets_path.mkdir(parents=True, exist_ok=True)
        self.thumbnails_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
