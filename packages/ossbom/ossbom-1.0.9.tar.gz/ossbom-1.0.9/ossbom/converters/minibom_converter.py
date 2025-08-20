from packageurl import PackageURL

from ..model.ossbom import OSSBOM
from ..model.minicomponent import MiniComponent


class MiniBOMConverter:

    """ Mini Bom is a compressed version of the OSSBOM """

    @staticmethod
    def from_minibom(minibom: dict) -> OSSBOM:

        # Convert the components back to OSSBOM style components
        minibom['components'] = [MiniComponent.from_dict(c).to_component().to_dict() for c in minibom['components']]

        # Convert from dict
        return OSSBOM.from_dict(minibom)
    
    @staticmethod
    def to_minibom(sbom: OSSBOM) -> dict:

        # Take the SBOM and convert it to a dict
        minibom = sbom.to_dict()

        # Replace all Components with a simplified component entry
        minibom['components'] = [MiniComponent.from_component(c).to_dict() for c in sbom.get_components()]

        return minibom
