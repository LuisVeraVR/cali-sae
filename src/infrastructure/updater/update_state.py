import json
import os
from pathlib import Path
from typing import Optional


class UpdateState:
    def __init__(self, app_name: str = "CaliSAE"):
        self.app_name = app_name
        self._path = self._default_path(app_name)

    @staticmethod
    def _default_path(app_name: str) -> Path:
        base = os.environ.get("APPDATA") or str(Path.home())
        return Path(base) / app_name / "update_state.json"

    @property
    def path(self) -> Path:
        return self._path

    def get_installed_tag(self) -> Optional[str]:
        try:
            if not self._path.exists():
                return None
            data = json.loads(self._path.read_text(encoding="utf-8"))
            value = data.get("installed_tag")
            return value if isinstance(value, str) and value else None
        except Exception:
            return None

    def set_installed_tag(self, tag: str) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps({"installed_tag": tag}, ensure_ascii=False), encoding="utf-8")

