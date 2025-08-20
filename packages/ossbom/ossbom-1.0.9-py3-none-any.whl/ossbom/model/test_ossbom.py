import json

from datetime import datetime
from .ossbom import OSSBOM
from .dependency_env import DependencyEnv
from .vulnerability import Vulnerability
from .environment import Environment
from ..tests.test_utility import create_example_sbom


def test_create_ossbom():
    """Test creating an OSSBOM instance."""
    env = Environment(github_repo="example/repo", branch="main")
    sbom = OSSBOM(name="Test SBOM", env=env, creators=["TestUser"])

    assert sbom.name == "Test SBOM"
    assert isinstance(sbom.created, datetime)
    assert sbom.creators == ["TestUser"]
    assert sbom.version == "1.0"
    assert sbom.format == "OSSBOM"
    assert sbom.env.github_repo == "example/repo"
    assert sbom.env.branch == "main"
    assert sbom.get_components() == []
    assert sbom.get_vulnerabilities() == []


def test_add_component():
    """Test adding components to an OSSBOM."""
    sbom = OSSBOM()
    sbom.add_component(name="example-pkg", version="1.0.0", source="pypi", env="dev")

    components = sbom.get_components()
    assert len(components) == 1
    assert components[0].name == "example-pkg"
    assert components[0].version == "1.0.0"
    assert components[0].source == {"pypi"}
    assert components[0].env == {DependencyEnv.DEV}


def test_remove_component():
    """Test removing a component from an OSSBOM."""
    sbom = OSSBOM()
    sbom.add_component(name="example-pkg", version="1.0.0", type="pypi", source="pyreqs", env="dev")

    sbom.remove_component(name="example-pkg", version="1.0.0", type="pypi")

    assert sbom.get_components() == []


def test_add_vulnerability():
    """Test adding a vulnerability to an OSSBOM."""
    sbom = OSSBOM()
    vuln = Vulnerability(
        id="123",
        purl="pkg:pypi/example-pkg@1.0.0",
        description="Example security issue",
        reference="https://security-db.com/vuln-1234",
        type="Security"
    )

    sbom.add_vulnerability(vuln)

    vulnerabilities = sbom.get_vulnerabilities()
    assert len(vulnerabilities) == 1
    assert vulnerabilities[0].purl == "pkg:pypi/example-pkg@1.0.0"
    assert vulnerabilities[0].description == "Example security issue"
    assert vulnerabilities[0].reference == "https://security-db.com/vuln-1234"
    assert vulnerabilities[0].type == "Security"


def test_add_multiple_vulnerabilities():
    """Test adding multiple vulnerabilities to an OSSBOM."""
    sbom = OSSBOM()
    vuln1 = Vulnerability(
        id="123",
        purl="pkg:pypi/example-pkg@1.0.0",
        description="Example security issue 1",
        reference="https://security-db.com/vuln-1234",
    )
    vuln2 = Vulnerability(
        id="5678",
        purl="pkg:pypi/example-pkg@2.0.0",
        description="Example security issue 2",
        reference="https://security-db.com/vuln-5678",
    )

    sbom.add_vulnerabilities([vuln1, vuln2])

    vulnerabilities = sbom.get_vulnerabilities()
    assert len(vulnerabilities) == 2
    assert vulnerabilities[0].description == "Example security issue 1"
    assert vulnerabilities[1].description == "Example security issue 2"


def test_ossbom_to_dict():
    """Test serializing an OSSBOM instance to a dictionary."""
    sbom = OSSBOM(name="Test SBOM", creators=["TestUser"])
    sbom.add_component(name="example-pkg", version="1.0.0", source="pypi", env="dev")

    vuln = Vulnerability(
        id="123",
        purl="pkg:pypi/example-pkg@1.0.0",
        description="Security flaw",
        reference="https://security-db.com/vuln-9999"
    )
    sbom.add_vulnerability(vuln)

    sbom_dict = sbom.to_dict()

    assert sbom_dict["name"] == "Test SBOM"
    assert sbom_dict["creators"] == ["TestUser"]
    assert sbom_dict["format"] == "OSSBOM"
    assert isinstance(sbom_dict["components"], list)
    assert isinstance(sbom_dict["vulnerabilities"], list)
    assert sbom_dict["components"][0]["name"] == "example-pkg"
    assert sbom_dict["vulnerabilities"][0]["description"] == "Security flaw"


def test_ossbom_from_dict():
    """Test deserializing an OSSBOM instance from a dictionary."""
    data = {
        "name": "Test SBOM",
        "creators": ["TestUser"],
        "version": "1.0",
        "format": "OSSBOM",
        "env": {"github_repo": "example/repo", "branch": "main"},
        "components": [
            {"name": "example-pkg", "version": "1.0.0", "source": ["pypi"], "env": ["dev"], "type": "library"}
        ],
        "vulnerabilities": [
            {"id": "123", "purl": "pkg:pypi/example-pkg@1.0.0", "description": "Security flaw", "reference": "https://security-db.com/vuln-9999"}
        ]
    }

    sbom = OSSBOM.from_dict(data)

    assert sbom.name == "Test SBOM"
    assert sbom.creators == ["TestUser"]
    assert sbom.format == "OSSBOM"
    assert sbom.env.github_repo == "example/repo"
    assert sbom.env.branch == "main"

    components = sbom.get_components()
    assert len(components) == 1
    assert components[0].name == "example-pkg"
    assert components[0].source == {"pypi"}

    vulnerabilities = sbom.get_vulnerabilities()
    assert len(vulnerabilities) == 1
    assert vulnerabilities[0].description == "Security flaw"


def test_can_be_converted_to_json():

    sbom = create_example_sbom()

    str = json.dumps(sbom.to_dict())

    new_str = json.loads(str)

    new_sbom = OSSBOM.from_dict(new_str)

    assert sbom == new_sbom


def test_add_components_adds_and_merges():
    """Test add_components merges sources/envs/locations for existing components and adds new ones."""
    sbom = OSSBOM()

    # Create a base component and add it via add_component
    sbom.add_component(name="example-pkg", version="1.0.0", source="pypi", env="dev", location=["/src"])

    # Create another Component instance with same name/version but different source/env/location
    from .component import Component
    from .dependency_env import DependencyEnv

    comp_same = Component.create(name="example-pkg", version="1.0.0", source="npm", env=DependencyEnv.PROD, type="library", location=["/lib"])

    # Create a completely new component
    comp_new = Component.create(name="other-pkg", version="2.0.0", source="maven", env=DependencyEnv.DEV, type="library", location=["/opt"])

    sbom.add_components([comp_same, comp_new])

    components = sbom.get_components()
    # Expect two components
    assert len(components) == 2

    # Find example-pkg and verify merged sources/env/location
    example = next(c for c in components if c.name == "example-pkg")
    assert example.source >= {"pypi", "npm"}
    # env contains DependencyEnv members
    assert DependencyEnv.DEV in example.env and DependencyEnv.PROD in example.env
    # locations should include both entries
    assert any("/src" in loc for loc in example.location) or "/src" in example.location
    assert any("/lib" in loc for loc in example.location) or "/lib" in example.location

    # Verify new component present
    other = next(c for c in components if c.name == "other-pkg")
    assert other.source == {"maven"}
    assert DependencyEnv.DEV in other.env
