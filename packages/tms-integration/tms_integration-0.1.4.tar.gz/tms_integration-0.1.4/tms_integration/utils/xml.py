from datetime import datetime
from typing import Any, Optional, Union
import xml.etree.ElementTree as ET
from pydantic import BaseModel
import pytz


class XmlAttribute:
    """A marker type for XML attributes."""

    def __init__(self, value: Any):
        self.value = value


def to_xml_element(
    tag: str, value: Union[str, int, float, bool, datetime, list, BaseModel, None]
) -> Optional[ET.Element]:
    """Convert a Pydantic model or a primitive type to an XML element."""
    if isinstance(value, BaseModel):
        element = ET.Element(tag)
        for field_name, field_value in value:
            if isinstance(field_value, XmlAttribute):
                element.set(field_name, str(field_value.value))
            else:
                child_element = to_xml_element(field_name, field_value)
                if child_element is not None:
                    element.append(child_element)
    elif isinstance(value, list):
        element = ET.Element(tag)
        for item in value:
            item_tag = item.__class__.__name__
            child_element = to_xml_element(item_tag, item)
            if child_element is not None:
                element.append(child_element)
    elif isinstance(value, datetime):
        if value.tzinfo is None:
            # Assume CET/CEST
            cet = pytz.timezone("Europe/Berlin")
            value = cet.localize(value)

        # Format the datetime explicitly
        iso_format = value.strftime("%Y-%m-%dT%H:%M:%S%z")
        iso_format = (
            iso_format[:-2] + ":" + iso_format[-2:]
        )  # Add colon in the timezone part

        element = ET.Element(tag)
        element.text = iso_format
    elif value is None:
        return None
    else:
        element = ET.Element(tag)
        element.text = str(value)

    return element
