from packageurl import PackageURL
from typing import Set

from .base import Serializable
from .dependency_env import DependencyEnv


class Component(Serializable):
    def __init__(self,
                 name: str,
                 version: str,
                 source: Set[str] | None = None,
                 env: Set[DependencyEnv] | None = None,
                 type: str = "library",
                 location: list | None = None,
                 metadata: dict | None = None) -> None:

        self.name = name
        self.version = version
        self.source = source if source else set()
        self.env = env if env else set()
        self.type = type
        self.location = location if location else []
        self.metadata = metadata if metadata else {}

    @classmethod
    def create(cls,
               name: str,
               version: str,
               source: str | None = None,
               env: str | None = None,
               type: str = "library",
               location: list | None = None,
               metadata: dict | None = None
               ):

        source = {source} if source else set()
        env = {DependencyEnv(env)} if env else set()
        location = location if location else []
        metadata = metadata if metadata else {}

        return cls(name, version, source, env, type, location, metadata)

    def __hash__(self):
        # Hash based on the name and version concatenated
        return hash(self.get_purl().to_string())

    def __eq__(self, other):
        # Equality based on name and version
        if not isinstance(other, Component):
            return NotImplemented
        return self.name == other.name and self.version == other.version

    def add_source(self, source):
        self.source.add(source)

    def add_env(self, env):
        self.env.add(env)

    def get_type(self):
        return self.type

    def add_location(self, location):
        self.location.append(location)

    def get_purl(self):
        return PackageURL(name=self.name, version=self.version, type=self.type)

    def __repr__(self):
        return f"pkg:{self.type}/{self.name}@{self.version} Source:({', '.join([s for s in self.source])}) Env:({', '.join([t.value for t in self.env])})"

    def to_dict(self):
        return {
            "name": self.name,
            "version": self.version,
            "source": list(self.source) if self.source else [],
            "env": [t.value for t in self.env] if self.env else [],
            "type": self.type,
            "location": self.location,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data):
        name = data['name']  # Not optional
        version = data['version']  # Not optional
        type = data.get("type", "library")
        env = set(DependencyEnv(e) for e in data.get('env', []))
        source = set(data.get('source', []))
        location = data.get('location', [])
        metadata = data.get('metadata', {})

        return Component(name, version, source, env, type, location, metadata)

    @staticmethod
    def get_hash(name, version, type):
        return hash(PackageURL(name=name, version=version, type=type).to_string())
