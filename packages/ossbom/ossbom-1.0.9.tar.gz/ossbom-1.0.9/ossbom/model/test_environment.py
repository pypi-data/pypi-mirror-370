from .environment import Environment


def test_create_environment():
    """Test creating an Environment instance using direct instantiation."""
    env = Environment(
        github_repo="example/repo",
        github_org="example-org",
        branch="main",
        machine_name="server-1",
        product_env="prod"
    )

    assert env.github_repo == "example/repo"
    assert env.github_org == "example-org"
    assert env.branch == "main"
    assert env.machine_name == "server-1"
    assert env.product_env == "prod"


def test_create_environment_classmethod():
    """Test creating an Environment instance using the create() method."""
    env = Environment.create(
        github_repo="example/repo",
        github_org="example-org",
        branch="develop",
        machine_name="server-2",
        product_env="dev"
    )

    assert env.github_repo == "example/repo"
    assert env.github_org == "example-org"
    assert env.branch == "develop"
    assert env.machine_name == "server-2"
    assert env.product_env == "dev"


def test_environment_to_dict():
    """Test serializing an Environment instance to a dictionary."""
    env = Environment(
        github_repo="example/repo",
        github_org="example-org",
        branch="feature",
        machine_name="server-3",
        product_env="staging"
    )

    env_dict = env.to_dict()

    assert isinstance(env_dict, dict)
    assert env_dict["github_repo"] == "example/repo"
    assert env_dict["github_org"] == "example-org"
    assert env_dict["branch"] == "feature"
    assert env_dict["machine_name"] == "server-3"
    assert env_dict["product_env"] == "staging"


def test_environment_from_dict():
    """Test deserializing an Environment instance from a dictionary."""
    data = {
        "github_repo": "example/repo",
        "github_org": "example-org",
        "branch": "hotfix",
        "machine_name": "server-4",
        "product_env": "prod"
    }

    env = Environment.from_dict(data)

    assert isinstance(env, Environment)
    assert env.github_repo == "example/repo"
    assert env.github_org == "example-org"
    assert env.branch == "hotfix"
    assert env.machine_name == "server-4"
    assert env.product_env == "prod"


def test_environment_from_empty_dict():

    data = {}
    env = Environment.from_dict(data)
    assert env.github_repo is None
    assert env.github_org is None
    assert env.branch is None
    assert env.machine_name is None
    assert env.product_env is None


def test_environment_empty_fields():
    """Test creating an Environment instance with no parameters."""
    env = Environment()
    
    assert env.github_repo is None
    assert env.github_org is None
    assert env.branch is None
    assert env.machine_name is None
    assert env.product_env is None
