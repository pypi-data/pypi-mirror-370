import shutil
import warnings
import zipfile
from pathlib import Path

import yaml
from pathspec import GitIgnoreSpec


class BackupSystem:
    def __init__(self, cfg):
        self.cfg = cfg
        log_path = cfg.path.log if cfg.path and cfg.path.log else f"log"
        self.backup_dir = Path(log_path) / cfg.name

    def run(self):
        if self.backup_dir.exists() and self.cfg.resume:
            return

        shutil.rmtree(self.backup_dir, ignore_errors=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._create_backup_zip()

    def _load_gitignore(self):
        gitignore_path = Path(".gitignore")
        if not gitignore_path.exists():
            return GitIgnoreSpec([])
        with gitignore_path.open("r") as f:
            return GitIgnoreSpec.from_lines(f)

    def _should_ignore(self, path, spec):
        git_style_path = path.relative_to(Path.cwd()).as_posix()
        if path.is_dir():
            git_style_path += "/"
        return spec.match_file(git_style_path)

    def _write_config_to_zip(self, zip_file: zipfile.ZipFile) -> None:
        config_content = yaml.dump(self.cfg.to_dict())
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            zip_file.writestr(str(self.cfg.config), config_content)

    def _create_backup_zip(self):
        ignore_spec = self._load_gitignore()
        backup_abs = self.backup_dir.resolve()
        zip_path = self.backup_dir / "backup.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in Path.cwd().rglob("*"):
                file_abs = file_path.resolve()

                if file_abs == backup_abs or backup_abs in file_abs.parents:
                    continue
                if self._should_ignore(file_path, ignore_spec):
                    continue
                if not file_path.is_file():
                    continue

                arcname = file_path.relative_to(Path.cwd())
                zipf.write(file_path, arcname)

            self._write_config_to_zip(zipf)
