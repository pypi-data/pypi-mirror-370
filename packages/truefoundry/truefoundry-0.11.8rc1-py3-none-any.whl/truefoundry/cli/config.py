from dataclasses import dataclass


@dataclass
class _CliConfig:
    json: bool = False
    debug: bool = False


CliConfig = _CliConfig()
