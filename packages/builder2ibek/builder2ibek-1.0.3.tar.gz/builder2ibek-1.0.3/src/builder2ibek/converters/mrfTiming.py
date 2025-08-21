from builder2ibek.converters.globalHandler import globalHandler
from builder2ibek.types import Entity, Generic_IOC

xml_component = "mrfTiming"


@globalHandler
def handler(entity: Entity, entity_type: str, ioc: Generic_IOC):
    """
    XML to YAML specialist convertor function for the pvlogging support module
    """

    if entity_type == "EventReceiverPMC":
        if entity.get("name") is None or entity.get("name") == "":
            entity.name = f"EVR{entity.cardid}"
