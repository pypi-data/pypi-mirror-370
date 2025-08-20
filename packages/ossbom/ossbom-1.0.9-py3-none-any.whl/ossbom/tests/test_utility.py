import random

from packageurl import PackageURL
from typing import Dict, Any

from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.vulnerability import Vulnerability
from cyclonedx.model.bom_ref import BomRef
from cyclonedx.model.vulnerability import VulnerabilityRating, VulnerabilitySource, VulnerabilityReference

from ..model.ossbom import OSSBOM
from ..model.component import Component as OSSBOM_Component
from ..model.vulnerability import Vulnerability as OSSBOM_Vulnerability


def create_example_component(
    name="example-pkg",
    version="1.0.0",
    source="pypi",
    env="dev",
    type="library",
    location=["/tmp"]
):
    """Creates a test Package instance, optionally with vulnerabilities."""
    package = OSSBOM_Component(name, version, source, env, type, location)
    return package


def create_example_vulnerability(
    id="CVE-2023-1234",
    purl=PackageURL("pypi", "example-pkg", "1.0.0"),
    description="Example vulnerability.",
    reference="https://example.com/vuln",
    type="Malware"
):
    return OSSBOM_Vulnerability(id, purl, description, reference, type)


def create_example_sbom():
    """Creates an SBOM instance with multiple example packages and vulnerabilities."""
    sbom = OSSBOM()
    sbom.name = "Cyclone Conversion"

    # Add multiple example packages
    sbom.add_component("example-pkg", "1.0.0", "pypi", "dev")
    sbom.add_component("dependency-pkg", "2.3.4", "npm", "prod")

    # Add a package with vulnerabilities
    package = create_example_component(
        name="vulnerable-pkg",
        version="0.9.0",
        source="pypi",
        env="dev",
        location=["/tmp"]
    )
    sbom.add_component(package.name, package.version, package.source, package.env)

    sbom.add_vulnerability(create_example_vulnerability())

    return sbom


def create_massive_sbom():
    ossbom = OSSBOM()

    for i in range(5000):
        ossbom.add_component(
            name=f"package-{i}",
            version=f"{random.randint(1, 10)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            source=random.choice(["pypi", "npm", "maven", "rubygems"]),
            env=random.choice(["dev", "prod"]),
        )

    return ossbom


def create_example_cyclonedx_dict() -> Dict[str, Any]:
    """Returns a sample CycloneDX JSON dictionary, including vulnerabilities."""
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {},
        "components": [
            {"name": "example-pkg", "version": "1.0.0", "type": "library", "purl": "pkg:pypi/example-pkg@1.0.0"},
            {"name": "dependency-pkg", "version": "2.3.4", "type": "library", "purl": "pkg:pypi/dependency-pkg@2.3.4"},
            {"name": "vulnerable-pkg", "version": "0.9.0", "type": "library", "purl": "pkg:pypi/vulnerable-pkg@0.9.0"},
        ],
        "vulnerabilities": [
            {
                "id": "CVE-2023-1234",
                "description": "Example vulnerability.",
                "affects": [{"ref": "vulnerable-pkg"}],
            },
            {
                "id": "CVE-2023-5678",
                "description": "Critical security risk.",
                "affects": [{"ref": "vulnerable-pkg"}],
            },
        ],
    }


def create_example_cyclonedx_object() -> Bom:
    """Returns a sample CycloneDX Bom object, including vulnerabilities."""
    bom = Bom()

    # Create components
    example_component = Component(name="example-pkg", version="1.0.0", type=ComponentType.LIBRARY, purl=PackageURL("pypi", "example-pkg", "1.0.0"))
    dependency_component = Component(name="dependency-pkg", version="2.3.4", type=ComponentType.LIBRARY)
    vulnerable_component = Component(name="vulnerable-pkg", version="0.9.0", type=ComponentType.LIBRARY)

    # Add components to BOM
    bom.components.update({example_component, dependency_component, vulnerable_component})

    # Create vulnerabilities
    vuln_1 = Vulnerability(
        bom_ref=BomRef("vulnerable-pkg"),
        id="CVE-2023-1234",
        description="Example vulnerability.",
        ratings=[VulnerabilityRating(source=VulnerabilitySource(name="NVD"))],
        references=[VulnerabilityReference(source=VulnerabilitySource(name="random", url="https://example.com/vuln"))],
    )

    vuln_2 = Vulnerability(
        bom_ref=BomRef("vulnerable-pkg"),
        id="CVE-2023-5678",
        description="Critical security risk.",
        ratings=[VulnerabilityRating(source=VulnerabilitySource(name="NVD"))],
    )

    # Add vulnerabilities to BOM
    bom.vulnerabilities.update({vuln_1, vuln_2})

    return bom

