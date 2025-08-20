# OSSBOM

This library manages the creations of SBOMs in our custom format, as well as conversion methods to create json dicts and CycloneDX SBOMs.

## Requirements


## Schema OSSBOM

```mermaid
classDiagram
    class OSSBOM {
        +string name
        +datetime created
        +string creator // optional
        +string version
        +string bomFormat // == OSSBOM
        +Environment env
        +List~Component~ components
        +List~Vulnerability~ vulnerabilities
    }

    class Environment {
        +string github_repo // optional
        +string github_org // optional
        +string branch // optional
        +string machine_name // optional
        +string product_env // optional
    }

    class Component {
        +string name
        +string version
        +string source // optional
        +string env // optional
        +string type // == library
    }

    class Vulnerability {
        +string purl
        +string description
        +string reference // optional
        +string type
    }

    OSSBOM --> Environment : has
    OSSBOM --> "many" Component : contains
    OSSBOM --> "many" Vulnerability : contains