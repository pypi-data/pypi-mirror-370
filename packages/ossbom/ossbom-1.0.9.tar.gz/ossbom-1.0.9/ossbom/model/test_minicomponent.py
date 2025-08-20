from ossbom.model.component import Component
import pytest

from packageurl import PackageURL

from .minicomponent import MiniComponent
from .dependency_env import DependencyEnv


def test_init_MiniComponent():
    """Test creating a MiniComponent instance."""
    comp = MiniComponent(purl=PackageURL(name="example-pkg", version="1.0.0", type="pypi"), source={"pyreqs"}, env={DependencyEnv.DEV})

    assert comp.name == "example-pkg"
    assert comp.version == "1.0.0"
    assert comp.source == {"pyreqs"}  # Stored as a set
    assert comp.env == {DependencyEnv.DEV}
    assert comp.type == "pypi"


def test_create_MiniComponent():
    """Test creating a MiniComponent instance."""
    comp = MiniComponent.create(purl=PackageURL(name="example-pkg", version="1.0.0", type="pypi"), source="pyreqs", env=DependencyEnv.DEV)

    assert comp.name == "example-pkg"
    assert comp.version == "1.0.0"
    assert comp.source == {"pyreqs"}  # Stored as a set
    assert comp.env == {DependencyEnv.DEV}
    assert comp.type == "pypi"


def test_MiniComponent_hash():
    """Test that MiniComponents with the same name and version have the same hash."""
    comp1 = MiniComponent.create(purl=PackageURL(name="example-pkg", version="1.0.0", type="pypi"), env=DependencyEnv.DEV)
    comp2 = MiniComponent.create(purl=PackageURL(name="example-pkg", version="1.0.0", type="pypi"), env=DependencyEnv.PROD)
    comp3 = MiniComponent.create(purl=PackageURL(name="example-pkg", version="1.0.0", type="npm"), env=DependencyEnv.PROD)

    assert hash(comp1) == hash(comp2)  # Hash is based on name + version
    assert comp1 == comp2  # MiniComponents should be equal
    assert hash(comp1) != hash(comp3)
    assert not str(comp1) == str(comp3)


def test_MiniComponent_get_purl():
    """Test getting the Package URL of a MiniComponent."""
    comp = MiniComponent.create(purl=PackageURL(name="example-pkg", version="1.0.0", type="pypi"), env=DependencyEnv.DEV)

    assert str(comp.get_purl()) == "pkg:pypi/example-pkg@1.0.0"


def test_MiniComponent_add_source():
    """Test adding a source to a MiniComponent."""
    comp = MiniComponent.create(purl=PackageURL(name="example-pkg", version="1.0.0", type="pypi"), source="pyreqs", env=DependencyEnv.DEV)

    comp.add_source("npm")
    comp.add_source("yarn")

    assert comp.source == {"pyreqs", "npm", "yarn"}


def test_MiniComponent_add_env():
    """Test adding an environment to a MiniComponent."""
    comp = MiniComponent.create(purl=PackageURL(name="example-pkg", version="1.0.0", type="pypi"), source="pyreqs", env=DependencyEnv.DEV)

    comp.add_env(DependencyEnv.PROD)

    assert comp.env == {DependencyEnv.DEV, DependencyEnv.PROD}


def test_MiniComponent_repr():
    """Test the string representation of a MiniComponent."""
    comp = MiniComponent.create(purl=PackageURL(name="example-pkg", version="1.0.0", type="pypi"), source="pyreqs", env=DependencyEnv.DEV)

    expected_repr = "pkg:pypi/example-pkg@1.0.0 Source:(pyreqs) Env:(dev)"
    assert repr(comp) == expected_repr


def test_MiniComponent_to_dict():
    """Test converting a MiniComponent to a dictionary."""
    comp = MiniComponent.create(purl=PackageURL(name="example-pkg", version="1.0.0", type="pypi"), source="pyreqs", env=DependencyEnv.DEV)

    expected_dict = {
        "purl": "pkg:pypi/example-pkg@1.0.0",
        "source": ["pyreqs"],
        "env": ["dev"]
    }

    assert comp.to_dict() == expected_dict


def test_MiniComponent_from_dict():
    """Test creating a MiniComponent from a dictionary."""
    data = {
        "purl": "pkg:pypi/example-pkg@1.0.0",
        "source": ["pyreqs"],
        "env": ["dev"]
    }

    comp = MiniComponent.from_dict(data)

    assert comp.name == "example-pkg"
    assert comp.version == "1.0.0"
    assert comp.source == {"pyreqs"}
    assert comp.env == {DependencyEnv.DEV}
    assert comp.type == "pypi"


@pytest.mark.parametrize("data", [
    {"version": "1.0.0", "source": ["pypi"], "env": ["dev"], "type": "library"},
    {"name": "example-pkg", "source": ["pypi"], "env": ["dev"], "type": "library"}
])
def test_MiniComponent_from_dict_missing_params_fails(data):
    """Test creating a MiniComponent from a dictionary without a name or version."""

    try:
        MiniComponent.from_dict(data)
        assert False
    except KeyError:
        assert True


def test_get_hash():
    """Test getting the hash of a MiniComponent."""
    comp = MiniComponent.create(purl=PackageURL(name="example-pkg", version="1.0.0", type="pypi"), source="pypi", env=DependencyEnv.DEV)

    assert MiniComponent.get_hash("example-pkg", "1.0.0", "pypi") == hash(comp)


def test_minicomponent_from_component():
    """Test creating a MiniComponent from a Component."""
    component = Component(name="example-pkg", version="1.0.0", type="pypi", source={"pypi"}, env={DependencyEnv.DEV}, location=["/tmp"])
    mini_component = MiniComponent.from_component(component)

    assert mini_component.name == component.name
    assert mini_component.version == component.version
    assert mini_component.type == component.type
    assert mini_component.source == component.source
    assert mini_component.env == component.env
    assert mini_component.location == component.location
