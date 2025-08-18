from typing import Any, List, Optional
from datetime import date, datetime

from pydantic import BaseModel, field_validator
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

from tms_integration.utils.xml import XmlAttribute, to_xml_element


class BaseCarloClass(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    @field_validator("Action", mode="before")
    @classmethod
    def set_action(cls, v: Any) -> Any:
        return XmlAttribute(v)


class Address(BaseCarloClass):
    Street: str
    HouseNumber: str
    Location1: str
    ZipCode: str
    IsoTwoCharacterCountryCode: str


class OriginalBusinessPartner(BaseCarloClass):
    Action: XmlAttribute
    GlobalLocationNumber: str
    Name1: str
    Addresses: Address


class Receiver(BaseCarloClass):
    OriginalBusinessPartner: OriginalBusinessPartner


class Sender(BaseCarloClass):
    OriginalBusinessPartner: OriginalBusinessPartner


class Package(BaseCarloClass):
    Matchcode: Optional[str] = None


class SsccCurrent(BaseCarloClass):
    Code: str


class ConsignmentItem(BaseCarloClass):
    PositionNumber: int
    Quantity: int
    Package: Package
    EffectiveWeightInKilogram: float
    StoragePlaces: Optional[float] = None
    Meter: Optional[float] = None
    SsccCurrents: Optional[List[SsccCurrent]] = None


class Times(BaseCarloClass):
    LieferdatumStart: Optional[datetime] = None
    LieferdatumEnd: Optional[datetime] = None
    LadedatumStart: Optional[datetime] = None
    LadedatumEnd: Optional[datetime] = None


class InformationClass(BaseCarloClass):
    Info10: str


class EditStatusClass(BaseCarloClass):
    Matchcode: str = ""


class ConsignmentCustomFields(BaseCarloClass):
    Action: XmlAttribute = "updateorcreate"
    CustomTypeValue1: str = ""
    ConsignmentReference1: str = ""


class Consignment(BaseCarloClass):
    Number: int
    ConsignmentReference2: str
    Times: Times
    Incoterms: int
    Receiver: Receiver
    Sender: Sender
    ConsignmentItems: Optional[List[ConsignmentItem]] = None
    ConsignmentReference1: Optional[str] = None
    ExternalNumber: Optional[str] = None
    ContainsDangerousGoods: Optional[bool] = None
    Information: Optional[InformationClass] = None
    EditStatus: Optional[EditStatusClass] = None
    AdditionalFields: Optional[ConsignmentCustomFields] = None
    Matchcode: Optional[str] = None


class Customer(BaseCarloClass):
    GlobalLocationNumber: str


class NormalOrder(BaseCarloClass):
    Action: XmlAttribute = "updateorcreate"
    ExternalNumber: str
    Date: date
    Info1: str = ""
    Customer: Customer
    Consignments: List[Consignment]


def remove_interim_tag(element: ET.Element, tag: str) -> None:
    """Recursively remove an interim tag from the element and replace it with its children, which get the interim element's name."""
    for child in list(
        element
    ):  # Convert to list to safely modify the tree during iteration
        if child.tag == tag:
            element.remove(child)  # Remove the interim element
            for grandchild in list(child):  # Again, convert to list to safely iterate
                grandchild.tag = (
                    tag  # Rename the grandchild tag to the interim element's tag name
                )
                element.append(
                    grandchild
                )  # Append the grandchild to the parent element
        else:
            remove_interim_tag(child, tag)  # Recurse into child elements


class NormalOrderData(BaseCarloClass):
    NormalOrder: NormalOrder

    def generate_xml(self) -> str:
        # Create the root element
        root = to_xml_element("NormalOrderData", self)

        # Remove and replace tags according to Carlo schema
        remove_interim_tag(root, "ConsignmentItems")
        remove_interim_tag(root, "Consignments")

        # Generate the XML string
        xml_str = ET.tostring(root, encoding="utf-8").decode("utf-8")

        # Add XML declaration and namespaces manually
        xml_declaration = '<?xml version="1.0" encoding="utf-8"?>'

        final_xml = f"{xml_declaration}{xml_str}"

        # Pretty-print the XML and return it
        dom = parseString(final_xml)
        return dom.toprettyxml(indent="  ")
