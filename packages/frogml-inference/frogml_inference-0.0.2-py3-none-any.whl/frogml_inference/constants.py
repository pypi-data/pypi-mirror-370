from os import getenv
from pathlib import Path


class FrogMLConstants:
    """
    FrogML Configuration settings
    """

    FROGML_HOME = (
        getenv("FROGML_HOME")
        if getenv("FROGML_HOME") is not None
        else f"{str(Path.home())}"
    )

    FROGML_CONFIG_FOLDER: str = f"{FROGML_HOME}/.frogml"

    FROGML_CONFIG_FILE: str = f"{FROGML_CONFIG_FOLDER}/config.json"

    QWAK_DEFAULT_SECTION: str = "default"  # remove

    QWAK_AUTHENTICATED_USER_ENDPOINT: str = (
        "https://grpc.qwak.ai/api/v0/runtime/get-authenticated-user-context"
    )
