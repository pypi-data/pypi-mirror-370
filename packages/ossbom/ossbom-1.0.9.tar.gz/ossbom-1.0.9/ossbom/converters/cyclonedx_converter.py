import json
import logging

from typing import Dict, Any

from ..model.ossbom import OSSBOM
from ..model.vulnerability import Vulnerability as OSSBOM_Vulnerability
from ..model.component import Component as OSSBOM_Component
from ..model.component import DependencyEnv

from cyclonedx.model.bom import Bom, BomMetaData
from cyclonedx.model import Property
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.vulnerability import Vulnerability, VulnerabilityReference, VulnerabilitySource
from cyclonedx.validation.json import JsonStrictValidator
from cyclonedx.schema import SchemaVersion
from cyclonedx.output.json import JsonV1Dot5
from cyclonedx.model.contact import OrganizationalContact

logger = logging.getLogger(__name__)


class CycloneDXConverter:
    """
    Handles conversion between CycloneDX SBOMs and OSSBOM.
    """

    @staticmethod
    def from_cyclonedx_dict(cdx_json: Dict[str, Any]) -> OSSBOM:
        """
        Converts a CycloneDX JSON (dict) to an OSSBOM SBOM object.
        """

        # Validate the JSON format
        my_json_validator = JsonStrictValidator(SchemaVersion.V1_5)
        sbom_json_str = json.dumps(cdx_json)
        validation_errors = my_json_validator.validate_str(sbom_json_str)

        if validation_errors:
            logger.error(f"JSON invalid - ValidationError: {repr(validation_errors)}")
            raise Exception("Invalid CycloneDX JSON")

        # Convert to CycloneDX Bom object
        cdx_obj = Bom.from_json(cdx_json)

        # Call from_cyclonedx_object
        return CycloneDXConverter.from_cyclonedx_object(cdx_obj)

    @staticmethod
    def from_cyclonedx_object(cdx_obj: Bom) -> OSSBOM:
        """
        Converts a CycloneDX Bom object to an OSSBOM SBOM object.
        """

        sbom = OSSBOM(
            name="Cyclone Conversion",
            creators=[author.name for author in cdx_obj.metadata.authors],
            created=cdx_obj.metadata.timestamp,
        )

        # Extract components
        components = []
        for component in cdx_obj.components:
            source = set(next((prop.value for prop in component.properties if prop.name == "source"), "CycloneDx").split(','))
            env_values = next((prop.value for prop in component.properties if prop.name == "env"), None)
            env = set(DependencyEnv(e) for e in env_values.split(',')) if env_values else set()
            type = component.purl.type if component.purl else component.type.value

            components.append(
                OSSBOM_Component(
                    name=component.name,
                    version=component.version,
                    source=source,
                    env=env,
                    type=type
                )
            )

        sbom.add_components(components)

        def get_reference_from_vuln(vuln: Vulnerability) -> str:
            if len(vuln.references) == 0 or vuln.references[0].source is None:
                return None

            return str(vuln.references[0].source.url)

        vulnerabilities = [
            OSSBOM_Vulnerability(
                id=vulnerability.id,
                description=vulnerability.description,
                reference=get_reference_from_vuln(vulnerability),
                type=next((prop.value for prop in vulnerability.properties if prop.name == "type"), "Unknown"),
                purl=next((prop.value for prop in vulnerability.properties if prop.name == "purl"), "Unknown"),
            )
            for vulnerability in cdx_obj.vulnerabilities
        ]

        sbom.add_vulnerabilities(vulnerabilities)

        return sbom

    @staticmethod
    def to_cyclonedx_object(sbom: OSSBOM) -> Bom:
        """
        Converts an OSSBOM SBOM object to CycloneDX JSON format.
        """
        # Create a CycloneDX Bom object
        cdx_obj = Bom()

        # Set metadata
        cdx_obj.metadata = BomMetaData(
            authors=[OrganizationalContact(name=creator) for creator in sbom.creators],
            timestamp=sbom.created,
        )

        # Add components
        for component in sbom.get_components():
            source = ','.join(component.source)
            env = ','.join([e.value for e in component.env])

            properties = [
                Property(name="source", value=source),
                Property(name="env", value=env),
            ]
            for key, value in component.metadata.items():
                properties.append(Property(name=key, value=value))

            cdx_obj.components.add(
                Component(
                    name=component.name,
                    version=component.version,
                    type=ComponentType.LIBRARY,
                    purl=component.get_purl(),
                    properties=properties
                )
            )
        
        # TODO need to add bom references in somehow
        # Add vulnerabilities
        for vulnerability in sbom.vulnerabilities:

            if vulnerability.reference is not None:
                references = [VulnerabilityReference(id="OSSBOM", source=VulnerabilitySource(url=vulnerability.reference))]
            else:
                references = []

            cdx_obj.vulnerabilities.add(
                Vulnerability(
                    id=vulnerability.id,
                    description=vulnerability.description,
                    references=references,
                    properties=[
                        Property(name="purl", value=str(vulnerability.purl)),
                        Property(name="type", value=vulnerability.type),
                    ]
                )
            )
        
        return cdx_obj

    def to_cyclonedx_dict(sbom: OSSBOM) -> Dict[str, Any]:
        """
        Converts an OSSBOM SBOM object to CycloneDX JSON format.
        """

        cdx: Bom = CycloneDXConverter.to_cyclonedx_object(sbom)

        my_json_outputter: 'JsonOutputter' = JsonV1Dot5(cdx)
        cdx_json = my_json_outputter.output_as_string()
        return json.loads(cdx_json)

