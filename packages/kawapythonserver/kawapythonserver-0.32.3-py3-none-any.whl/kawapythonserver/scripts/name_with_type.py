from dataclasses import dataclass


@dataclass
class NameWithType:
    name: str
    type: str

    @classmethod
    def from_dict(cls, d: dict) -> 'NameWithType':
        return cls(d['name'], d['type'])
