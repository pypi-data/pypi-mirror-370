# Copyright 2020-2024 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import pytest


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "single_process" in item.keywords:
            item.add_marker(pytest.mark.run())  # Ensure it runs first/serially
