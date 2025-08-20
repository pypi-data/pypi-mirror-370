from .base import Serializable


class Environment(Serializable):

    def __init__(self,
                 github_repo: str = None,
                 github_org: str = None,
                 project: str = None,
                 branch: str = None,
                 machine_name: str = None,
                 product_env: str = None,
                 ):
        self.github_repo = github_repo
        self.github_org = github_org
        self.branch = branch
        self.machine_name = machine_name
        self.product_env = product_env
        self.project = project

    def to_dict(self) -> dict:
        """Convert Environment instance to a dictionary."""
        return {
            "github_repo": self.github_repo,
            "github_org": self.github_org,
            "branch": self.branch,
            "machine_name": self.machine_name,
            "product_env": self.product_env,
            "project": self.project
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Environment":
        """Create an Environment instance from a dictionary."""
        return Environment(
            github_repo=data.get("github_repo", None),
            github_org=data.get("github_org", None),
            branch=data.get("branch", None),
            machine_name=data.get("machine_name", None),
            product_env=data.get("product_env", None),
            project=data.get("project", None)
        )

    @classmethod
    def create(cls,
               github_repo: str = None,
               github_org: str = None,
               branch: str = None,
               project: str = None,
               machine_name: str = None,
               product_env: str = None
               ) -> "Environment":
        """Create an Environment instance."""

        return cls(github_repo, github_org, project, branch, machine_name, product_env)
