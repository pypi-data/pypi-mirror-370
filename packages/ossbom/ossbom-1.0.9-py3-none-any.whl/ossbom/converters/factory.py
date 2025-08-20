from cyclonedx.model.bom import Bom

from .cyclonedx_converter import CycloneDXConverter
from .minibom_converter import MiniBOMConverter
from ..model.ossbom import OSSBOM


class SBOMConverterFactory:
    """
    Factory class to handle SBOM conversions between different formats.
    """

    @staticmethod
    def from_cyclonedx_dict(cdx_dict: dict) -> OSSBOM:
        """
        Converts a CycloneDX JSON dictionary to an OSSBOM SBOM object.

        :param cdx_dict: CycloneDX SBOM as a JSON dictionary
        :return: OSSBOM SBOM object
        """
        return CycloneDXConverter.from_cyclonedx_dict(cdx_dict)

    @staticmethod
    def from_cyclonedx(cdx_json: Bom) -> OSSBOM:
        """
        Converts a CycloneDX Bom Object to an OSSBOM SBOM object.

        :param cdx_json: CycloneDX SBOM as an object
        :return: OSSBOM SBOM object
        """
        return CycloneDXConverter.from_cyclonedx_object(cdx_json)

    @staticmethod
    def to_cyclonedx_dict(ossbom: OSSBOM) -> dict:
        """
        Converts an OSSBOM SBOM object to CycloneDX Json Dictionary.

        :param ossbom: OSSBOM SBOM object
        :return: CycloneDX SBOM as a JSON dictionary
        """
        return CycloneDXConverter.to_cyclonedx_dict(ossbom)

    @staticmethod
    def to_cyclonedx(ossbom: OSSBOM) -> Bom:
        """
        Converts an OSSBOM SBOM object to CycloneDX SBom Object.

        :param ossbom: OSSBOM SBOM object
        :return: CycloneDX SBOM as a SBOM Object
        """
        return CycloneDXConverter.to_cyclonedx_object(ossbom)

    @staticmethod
    def to_minibom(ossbom: OSSBOM) -> dict:
        """
        Converts an OSSBOM SBOM object to MiniBOM.

        :param ossbom: OSSBOM SBOM object
        :return: MiniBOM
        """
        return MiniBOMConverter.to_minibom(ossbom)

    @staticmethod
    def from_minibom(minibom: dict) -> OSSBOM:
        """
        Converts a MiniBOM to OSSBOM SBOM object.

        :param minibom: MiniBOM
        :return: OSSBOM SBOM object
        """
        return MiniBOMConverter.from_minibom(minibom)
