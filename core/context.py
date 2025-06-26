from pathlib import Path
import shutil

class ProjectContext:
    def __init__(self):
        self._project_root = Path(r"C:\Users\Fxnarji\Documents\GitHub\Primux\SampleStructure\NewProject")

    def set_project(self, root: Path):
        root = root.resolve()
        if not (root / "_assets").is_dir():
            raise ValueError(f"'{root}' does not appear to be a valid project (missing _assets).")
        self._project_root = root

    @property
    def root(self) -> Path:
        if not self._project_root:
            raise RuntimeError("Project root not set.")
        return self._project_root

    @property
    def assets_path(self) -> Path:
        return self.root / "_assets"


    def ensure_directories_exist(self):
        """Make sure expected folders exist."""
        self.assets_path.mkdir(parents=True, exist_ok=True)
        self.thumbnails_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
    
    
    def create_folder(self, path):
        new_folder_path = self.assets_path / path
        print(f"created folder at: {new_folder_path}")
        new_folder_path.mkdir()
    
    def delete_directory(self,path):
        folder_path = self.assets_path / path
        print(f"deleted folder @: {folder_path}")
        shutil.rmtree(folder_path)

