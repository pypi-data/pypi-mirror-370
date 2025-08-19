# coding: utf-8

import importlib.resources
from pathlib import Path
from ksupk import singleton_decorator


@singleton_decorator
class ResourceManager:
    def __init__(self):
        self.package_name = "krypto_gui_smalk"
        self.package_assets_folder = "assets"

    def file_path(self, file_path) -> Path | None:
        res = None
        with importlib.resources.path(f"{self.package_name}.{self.package_assets_folder}", file_path) as tmp_file_path:
            res = Path(str(tmp_file_path))
        return res

    def ico_path(self) -> Path:
        return self.file_path("ico.png")
