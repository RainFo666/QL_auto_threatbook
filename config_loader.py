import json


class Config:
    def __init__(self, config_dict):
        for key, value in config_dict.items():
            if isinstance(value, dict):
                value = Config(value)
            setattr(self, key, value)

    @classmethod
    def from_json(cls, config_file):
        with open(config_file, 'r') as file:
            config_dict = json.load(file)
        return cls(config_dict)
