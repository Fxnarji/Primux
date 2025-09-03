from pathlib import Path

class ProjectContext:
    def __init__(self):
        self.project_root: Path | None = None
        self.show_path: Path | None = None
        self.assets_path: Path | None = None
        self.thumbnails_path: Path | None = None
        self.metadata_path: Path | None = None

    def set_project(self, root: Path):
        root = root.resolve()
        self.project_root = root
        self.show_path = root / "Show"
        self.assets_path = root / "Assets"
        self.thumbnails_path = root / "_thumbnails"
        self.metadata_path = root / "_metadata"

    @property
    def root(self) -> Path:
        if self.project_root is None:
            raise RuntimeError("Project root not set.")
        return self.project_root

    def ensure_directories_exist(self):
        """Make sure expected folders exist if root is set."""
        if self.project_root is None:
            raise RuntimeError("Cannot ensure directories: project root not set.")

        self.show_path.mkdir(parents=True, exist_ok=True)
        self.assets_path.mkdir(parents=True, exist_ok=True)
        self.thumbnails_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
