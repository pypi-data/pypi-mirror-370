from datetime import datetime, timezone
from typing import Dict, List

from .base import Serializable
from .component import Component
from .environment import Environment
from .vulnerability import Vulnerability


# This is our definitive approach to creating and managing SBOMS
class OSSBOM(Serializable):
    def __init__(self,
                 name: str = "",
                 env: Environment = None,
                 created: datetime = datetime.now(timezone.utc),
                 creators: List[str] | None = None,
                 version: str = "1.0"
                 ):

        self.name = name
        self.created = created
        self.creators = creators if creators else []
        self.version = version
        self.format = "OSSBOM"
        self.env = env

        # Create as a placeholder
        self.components: Dict[str, Component] = {}
        self.vulnerabilities = []
        return

    @classmethod
    def create(cls, name: str, env: Environment, created: datetime, creators: List[str], version: str) -> "OSSBOM":
        return cls(name, env, created, creators, version)

    def update_environment(self, env: Environment):
        self.env = env

    def add_component(self, name, version, source, env=None, type="library", location=[]):
        key = Component.get_hash(name, version, type)
        if key in self.components:
            self.components[key].add_source(source)
            self.components[key].add_env(env)
            self.components[key].add_location(location)
        else:
            self.components[key] = Component.create(name, version, source, env, type, location)

    def add_components(self, components: List[Component]):
        for component in components:
            if hash(component) in self.components:
                for source in component.source:
                    self.components[hash(component)].add_source(source)
                for env in component.env:
                    self.components[hash(component)].add_env(env)
                # Component stores locations in `location` (singular). Iterate over it
                for location in component.location:
                    self.components[hash(component)].add_location(location)
            else:
                self.components[hash(component)] = component

    def remove_component(self, name: str, version: str, type: str):
        key = Component.get_hash(name, version, type)
        self.components.pop(key, None)

    def get_components(self) -> List[Component]:
        """
        Returns components sorted by name and version.
        We sort to ensure that the same SBOM is always generated.
        """
        return sorted(self.components.values(), key=lambda cmp: (cmp.name, cmp.version))

    def add_vulnerability(self, vulnerability: Vulnerability):
        self.vulnerabilities.append(vulnerability)

    def add_vulnerabilities(self, vulnerabilities: List[Vulnerability]):
        self.vulnerabilities.extend(vulnerabilities)

    def get_vulnerabilities(self) -> List[Vulnerability]:
        return self.vulnerabilities

    def to_dict(self):
        return {
            "name": self.name,
            "created": self.created.isoformat(),
            "creators": self.creators,
            "version": self.version,
            "format": self.format,
            "env": self.env.to_dict() if self.env else Environment().to_dict(),
            "components": [component.to_dict() for component in self.get_components()],
            "vulnerabilities": [vulnerability.to_dict() for vulnerability in self.get_vulnerabilities()]
        }

    @classmethod
    def from_dict(cls, data: dict):
        sbom = cls()
        sbom.name = data.get("name", "")
        sbom.created = datetime.fromisoformat(data.get("created")) if "created" in data else datetime.now(timezone.utc)
        sbom.creators = data.get("creators", [])
        sbom.version = data.get("version", "1.0")
        sbom.format = data.get("format", "OSSBOM")
        sbom.env = Environment.from_dict(data.get("env", {}))
        for comp_data in data.get("components", []):
            component = Component.from_dict(comp_data)
            sbom.components[hash(component)] = component

        for vuln_data in data.get("vulnerabilities", []):
            sbom.vulnerabilities.append(Vulnerability.from_dict(vuln_data))

        return sbom

    def __eq__(self, value):
        return self.to_dict() == value.to_dict()
