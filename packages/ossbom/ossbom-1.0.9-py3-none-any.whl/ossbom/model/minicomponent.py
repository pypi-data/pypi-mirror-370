from packageurl import PackageURL
from typing import List, Set

from .base import Serializable
from .component import Component
from .dependency_env import DependencyEnv


class MiniComponent(Serializable):
    def __init__(self,
                 purl: PackageURL,
                 source: Set[str] | None = None,
                 env: Set[DependencyEnv] | None = None,
                 location: List[str] | None = None
                 ) -> None:

        self.name = purl.name
        self.version = purl.version
        self.source = source if source else set()
        self.env = env if env else set()
        self.type = purl.type
        self.location = location if location else []

    @classmethod
    def create(cls,
               purl: PackageURL,
               source: str | None = None,
               env: str | None = None,
               location: List[str] | None = None
               ) -> 'MiniComponent':

        source = {source} if source else set()
        env = {DependencyEnv(env)} if env else set()
        location = location if location else []
        
        return cls(purl, source, env, location)

    def __hash__(self):
        # Hash based on the name and version concatenated
        return hash(self.get_purl().to_string())

    def __eq__(self, other):
        # Equality based on name and version
        if not isinstance(other, MiniComponent):
            return NotImplemented
        return self.name == other.name and self.version == other.version

    def add_source(self, source):
        self.source.add(source)

    def add_env(self, env):
        self.env.add(env)

    def get_type(self):
        return self.type

    def get_purl(self):
        return PackageURL(name=self.name, version=self.version, type=self.type)

    def __repr__(self):
        return f"pkg:{self.type}/{self.name}@{self.version} Source:({', '.join([s for s in self.source])}) Env:({', '.join([t.value for t in self.env])})"

    def to_dict(self):
        data = {
            "purl": str(self.get_purl()),
            "source": list(self.source) if self.source else [],
            "env": [t.value for t in self.env] if self.env else [],
        }
        # Only include location if it has data to avoid bloating minibom size
        if self.location:
            data["location"] = self.location
        return data

    @classmethod
    def from_dict(cls, data):

        purl = PackageURL.from_string(data['purl'])

        env = set(DependencyEnv(e) for e in data.get('env', []))
        source = set(data.get('source', []))
        location = data.get('location', [])

        return cls(purl, source, env, location)

    @staticmethod
    def get_hash(name, version, type):
        return hash(PackageURL(name=name, version=version, type=type).to_string())

    @classmethod
    def from_component(cls, component):
        return cls(PackageURL(name=component.name, version=component.version, type=component.type), component.source, component.env, component.location)

    def to_component(self):
        return Component(name=self.name, version=self.version, type=self.type, source=self.source, env=self.env, location=self.location)
