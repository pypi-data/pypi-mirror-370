# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
from enum import StrEnum, Enum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError, conlist, constr
import re

from semantic_version import Version

UNDEFINED_CONST = "______UNDEFINED______"

VALID_POSIX_DIR_NAME_REGEX = re.compile(r"[\w\-.]+$")
VALID_POSIX_PATH_REGEX = re.compile(r"^(~|.)?/?([\w\-.]+/)*[\w\-.]+/?$")
VALID_NAME_REGEX = re.compile(r"^\w+$")
VALID_IP_OWNER_NAME_REGEX = re.compile(r"^(?:(\w+)/)?(\w+)$")
VALID_FSOC_NAME_REGEX = re.compile(r"^[\w\-]+$")
VALID_FSOC_NAMESPACE_REGEX = re.compile(r"^([\w\-]+\.[\w\-]+):(?:([\w\-]+):)?([\w\-]+)$")
VALID_LOGIC_SIMULATION_TIMESCALE_REGEX= re.compile(r'^\d+(ms|us|ns|ps|fs)/\d+(ms|us|ns|ps|fs)$')


PosixPath = constr(pattern=VALID_POSIX_PATH_REGEX)
PosixDirName = constr(pattern=VALID_POSIX_DIR_NAME_REGEX)
OptionalPosixPath = PosixPath | None
PosixPathList = conlist(item_type=constr(pattern=VALID_POSIX_PATH_REGEX), min_length=0)
HdlNameList = conlist(item_type=constr(pattern=VALID_NAME_REGEX), min_length=0)
HdlName = constr(pattern=VALID_NAME_REGEX)
OrgName = constr(pattern=VALID_IP_OWNER_NAME_REGEX)

class Model(BaseModel):
    class Config:
        #use_enum_values = True  # Ensures enums are serialized using their values
        arbitrary_types_allowed = True

# Define custom representer for semantic_version.Version
def version_representer(dumper, data):
    return dumper.represent_str(str(data))

# Register the custom representer
yaml.SafeDumper.add_representer(Version, version_representer)