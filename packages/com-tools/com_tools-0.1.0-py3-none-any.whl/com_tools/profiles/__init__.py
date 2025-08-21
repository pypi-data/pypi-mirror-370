from __future__ import annotations

import json
import click
from typing import Dict, Iterator, List, Optional
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field

from com_tools._protocols import SupportedProtocols
from com_tools.utils import storage
from com_tools.loggers import logger


class ProfileRepo(object):

    def __init__(self, directory: str=None):
        if directory is None:
            self._repository = storage.DEFAULT_STORAGE_FOLDER
        else:
            self._repository = directory
        self._profiles = {}
        self._load_saved_profiles()

    def __contains__(self, profile: ComProfile | str) -> bool:
        if isinstance(profile, str):
            return profile in self._profiles

        return profile.name in self._profiles
    
    def __iter__(self) -> Iterator[ComProfile]:
        return iter(self._profiles.values())
 
    def _load_saved_profiles(self) -> None:
        all_files =  storage.scan_storage_directory(self._repository)
        for name, file in all_files.items():
            self._profiles[name] = ComProfile.from_path(file)


    def list_profiles(self) -> Dict[str, ComProfile]:
        return self._profiles.items()
    
    def add_profile(self, profile: ComProfile, save: bool=True) -> None:
        self._profiles[profile.name] = profile
        if save:
            storage.save_file(profile, self._repository, filename=f"{profile.name}.json")

    def get_profile(self, profile_name: str) -> ComProfile | None:
        if profile_name in self:
            return self._profiles[profile_name]

    def delete_profile(self, profile_name: str) -> None:
        logger.info(f"Deleting {profile_name=} (in {self._profiles})")
        if profile_name in self._profiles:
            storage.remove_file(self._repository, profile_name)
            self._profiles.pop(profile_name, None)

pass_repo_context =  click.make_pass_decorator(ProfileRepo)


class ComProfile(BaseModel):
    """
    A generic profile of a client's protocol.
    JSON configuration stores as dict in the config attribute (inheriting from base model)
    """
    model_config = ConfigDict(
        extra="allow"
    )

    name: str
    protocol: SupportedProtocols
    config: Optional[Dict] = Field(default_factory=dict) # Contain all config specific to your profile.

    def __eq__(self, value: ComProfile):
        return (value.name == self.name) and (value.protocol == self.protocol)
        
    @classmethod
    def from_path(cls, file: Path) -> ComProfile | None:
        with open(file, "r") as f:
            return cls.model_validate(json.load(f))