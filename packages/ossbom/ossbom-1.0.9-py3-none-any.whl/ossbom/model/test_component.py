import pytest

from .component import Component
from .dependency_env import DependencyEnv


def test_init_component():
    """Test creating a Component instance."""
    comp = Component(
        name="example-pkg",
        version="1.0.0",
        source={"pypi"},
        env={DependencyEnv.DEV},
        metadata={"license": "MIT", "homepage": "https://example.com"}
    )

    assert comp.name == "example-pkg"
    assert comp.version == "1.0.0"
    assert comp.source == {"pypi"}  # Stored as a set
    assert comp.env == {DependencyEnv.DEV}
    assert comp.type == "library"
    assert comp.metadata == {"license": "MIT", "homepage": "https://example.com"}


def test_create_component():
    """Test creating a Component instance."""
    comp = Component.create(
        name="example-pkg",
        version="1.0.0",
        source="pypi",
        env=DependencyEnv.DEV,
        metadata={"license": "MIT"}
    )

    assert comp.name == "example-pkg"
    assert comp.version == "1.0.0"
    assert comp.source == {"pypi"}  # Stored as a set
    assert comp.env == {DependencyEnv.DEV}
    assert comp.type == "library"
    assert comp.metadata == {"license": "MIT"}


def test_component_hash():
    """Test that Components with the same name and version have the same hash."""
    comp1 = Component.create(name="example-pkg", version="1.0.0", type="pypi", env=DependencyEnv.DEV)
    comp2 = Component.create(name="example-pkg", version="1.0.0", type="pypi", env=DependencyEnv.PROD)
    comp3 = Component.create(name="example-pkg", version="1.0.0", type="npm", env=DependencyEnv.PROD)

    assert hash(comp1) == hash(comp2)
    assert comp1 == comp2 
    assert hash(comp1) != hash(comp3)
    assert str(comp1) != str(comp3)


def test_component_get_purl():
    """Test getting the Package URL of a Component."""
    comp = Component.create(name="example-pkg", version="1.0.0", type="pypi", env=DependencyEnv.DEV)

    assert str(comp.get_purl()) == "pkg:pypi/example-pkg@1.0.0"


def test_component_add_source():
    """Test adding a source to a Component."""
    comp = Component.create(name="example-pkg", version="1.0.0", source="pypi", env=DependencyEnv.DEV)

    comp.add_source("npm")
    comp.add_source("maven")

    assert comp.source == {"pypi", "npm", "maven"}


def test_component_add_env():
    """Test adding an environment to a Component."""
    comp = Component.create(name="example-pkg", version="1.0.0", source="pypi", env=DependencyEnv.DEV)

    comp.add_env(DependencyEnv.PROD)

    assert comp.env == {DependencyEnv.DEV, DependencyEnv.PROD}


def test_component_repr():
    """Test the string representation of a Component."""
    comp = Component.create(name="example-pkg", version="1.0.0", source="pypi", env=DependencyEnv.DEV)

    expected_repr = "pkg:library/example-pkg@1.0.0 Source:(pypi) Env:(dev)"
    assert repr(comp) == expected_repr


def test_component_to_dict():
    """Test converting a Component to a dictionary."""
    comp = Component.create(name="example-pkg", version="1.0.0", source="pypi", env=DependencyEnv.DEV)

    expected_dict = {
        "name": "example-pkg",
        "version": "1.0.0",
        "source": ["pypi"],
        "env": ["dev"],
        "type": "library",
        "location": [],
        "metadata": {}
    }

    assert comp.to_dict() == expected_dict


def test_component_to_dict_with_metadata():
    """Test converting a Component with metadata to a dictionary."""
    comp = Component.create(
        name="example-pkg",
        version="1.0.0",
        source="pypi",
        env=DependencyEnv.DEV,
        metadata={"license": "MIT", "homepage": "https://example.com"}
    )

    d = comp.to_dict()
    assert d["metadata"] == {"license": "MIT", "homepage": "https://example.com"}


def test_component_from_dict():
    """Test creating a Component from a dictionary."""
    data = {
        "name": "example-pkg",
        "version": "1.0.0",
        "source": ["pypi"],
        "env": ["dev"],
        "type": "library"
    }

    comp = Component.from_dict(data)

    assert comp.name == "example-pkg"
    assert comp.version == "1.0.0"
    assert comp.source == {"pypi"}
    assert comp.env == {DependencyEnv.DEV}
    assert comp.type == "library"
    assert comp.metadata == {}


def test_component_from_dict_with_metadata():
    """Test creating a Component from a dictionary including metadata."""
    data = {
        "name": "example-pkg",
        "version": "1.0.0",
        "source": ["pypi"],
        "env": ["dev"],
        "type": "library",
        "metadata": {"license": "MIT"}
    }

    comp = Component.from_dict(data)

    assert comp.metadata == {"license": "MIT"}


@pytest.mark.parametrize("data", [
    {"version": "1.0.0", "source": ["pypi"], "env": ["dev"], "type": "library"},
    {"name": "example-pkg", "source": ["pypi"], "env": ["dev"], "type": "library"}
])
def test_component_from_dict_missing_params_fails(data):
    """Test creating a Component from a dictionary without a name or version."""

    try:
        Component.from_dict(data)
        assert False
    except KeyError:
        assert True


def test_get_hash():
    """Test getting the hash of a Component."""
    comp = Component.create(name="example-pkg", version="1.0.0", type="pypi", source="pyreqs", env=DependencyEnv.DEV)

    assert Component.get_hash("example-pkg", "1.0.0", "pypi") == hash(comp)
