# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, ValidationError, constr
from .model import Model, VALID_NAME_REGEX


class User(Model):
    def __init__(self, **data):
        super().__init__(**data)
        self._use_pre_set_username = False
        self._pre_set_username = ""
        self._use_pre_set_password = False
        self._pre_set_password = ""
    authenticated: bool = False
    username: Optional[constr(pattern=VALID_NAME_REGEX)] = "__ANONYMOUS__"
    session_cookies: Optional[dict] = {}
    session_headers: Optional[dict] = {}

    def reset(self):
        self.authenticated = False
        self.username = "__ANONYMOUS__"
        self.session_cookies = {}
        self.session_headers = {}

    @classmethod
    def new(cls):
        data= {}
        return cls(**data)

    @classmethod
    def load(cls, file_path):
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            if data is None:
                data = {}
            return cls(**data)

    def save(self, file_path: Path):
        """Save the current User instance to a YAML file."""
        with open(file_path, 'w') as f:
            model_data: dict = self.model_dump()
            yaml.safe_dump(model_data, f)

    @property
    def use_pre_set_username(self) -> bool:
        return self._use_pre_set_username
    @property
    def pre_set_username(self) -> str:
        return self._pre_set_username
    @pre_set_username.setter
    def pre_set_username(self, value: str):
        self._use_pre_set_username = True
        self._pre_set_username = value

    @property
    def use_pre_set_password(self) -> bool:
        return self._use_pre_set_password
    @property
    def pre_set_password(self) -> str:
        return self._pre_set_password
    @pre_set_password.setter
    def pre_set_password(self, value: str):
        self._use_pre_set_password = True
        self._pre_set_password = value
