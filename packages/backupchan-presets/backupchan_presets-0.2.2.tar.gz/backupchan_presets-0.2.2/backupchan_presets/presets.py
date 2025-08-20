from backupchan import API, BackupchanAPIError, SequentialFile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Generator
import os
import json
import platformdirs

CONFIG_FILE_DIR = platformdirs.user_config_dir("backupchan")
CONFIG_FILE_PATH = f"{CONFIG_FILE_DIR}/presets.json"

class PresetError(Exception):
    pass

@dataclass
class Preset:
    location: str
    target_id: str

    def upload(self, api: API, manual: bool) -> str:
        self.check_existence()

        if os.path.isdir(self.location):
            return api.upload_backup_folder(self.target_id, self.location, manual)
        else:
            with open(self.location, "rb") as file:
                return api.upload_backup(self.target_id, file, os.path.basename(self.location), manual)

    def seq_upload(self, api: API, manual: bool) -> Generator[tuple[int, int, str], None, None]:
        """
        Generates (current index), (total files), (current filename)
        """

        self.check_existence()

        if not os.path.isdir(self.location):
            raise PresetError("Cannot upload single file sequentially")

        # Build a file list
        # TODO copied from cli; put into function probably in client lib
        file_list = []
        for dirpath, _, filenames in os.walk(self.location):
            rel_dir = os.path.relpath(dirpath, self.location)
            rel_dir = "/" if rel_dir == "." else "/" + rel_dir
            for filename in filenames:
                file_list.append(SequentialFile(rel_dir, filename, False))
        total_files = len(file_list)

        try:
            api.seq_begin(self.target_id, file_list, manual)
        except BackupchanAPIError as exc:
            if not (exc.status_code == 400 and "Target busy" in str(exc)):
                raise

            # exclude already uploaded files
            server_file_list = api.seq_check(self.target_id)
            already_uploaded = [file for file in server_file_list if file.uploaded]
            file_list = [file for file in file_list if SequentialFile(file.path, file.name, True) not in already_uploaded]
            total_files = len(file_list)
        
        for index, file in enumerate(file_list):
            full_path = os.path.join(file.path, file.name)
            yield index, total_files, full_path
            with open(os.path.join(self.location, full_path.lstrip("/")), "rb") as file_io:
                api.seq_upload(self.target_id, file_io, file)
        api.seq_finish(self.target_id)

    def check_existence(self):
        if not os.path.exists(self.location):
            raise PresetError(f"No such file or directory: {self.location}")

    @staticmethod
    def from_dict(d: dict) -> "Preset":
        return Preset(d["location"], d["target_id"])

class Presets:
    def __init__(self, config_path: str | None = None):
        self.presets: dict[str, Preset] = {}
        self.config_path = CONFIG_FILE_PATH if config_path is None else config_path

    def load(self):
        if not os.path.exists(self.config_path):
            return

        self.presets = {}
        with open(self.config_path, "r") as config_file:
            config = json.load(config_file)
            for json_preset in config["presets"]:
                self.presets[json_preset["name"]] = Preset.from_dict(json_preset)

    def save(self):
        Path(os.path.dirname(self.config_path)).mkdir(exist_ok=True, parents=True)

        presets_list = []

        for name, preset in self.presets.items():
            presets_list.append({
                "name": name,
                "location": preset.location,
                "target_id": preset.target_id
            })

        presets_dict = {
            "presets": presets_list
        }

        with open(self.config_path, "w") as config_file:
            json.dump(presets_dict, config_file)

    def add(self, name: str, location: str, target_id: str):
        if name in self.presets:
            raise PresetError(f"Preset '{name}' already exists")

        self.presets[name] = Preset(location, target_id)

    def remove(self, name: str):
        del self.presets[name]

    def __getitem__(self, name: str) -> Preset:
        return self.presets[name]

    def __iter__(self):
        return iter(self.presets.keys())

    def __len__(self):
        return len(self.presets)

    def __contains__(self, name: str) -> bool:
        return name in self.presets
