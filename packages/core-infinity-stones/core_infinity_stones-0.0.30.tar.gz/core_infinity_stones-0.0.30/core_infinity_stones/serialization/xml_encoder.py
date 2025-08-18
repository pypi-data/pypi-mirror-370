from typing import Any, Callable, Sequence
import xml.etree.ElementTree as ET

from core_infinity_stones.serialization.schemas import XmlEncodableModel


class XmlEncoder:
    def __init__(
        self,
        key_encoder: Callable[[str], str] = lambda key: key,
        param_value_encoder: Callable[[Any], str] = str,
    ):
        self.key_encoder = key_encoder
        self.param_value_encoder = param_value_encoder

    def encode_as_xml_element(self, model: XmlEncodableModel) -> ET.Element:
        properties_dict = model.__dict__
        xml_element_params = self._encode_params(properties_dict)

        element = ET.Element(model.xml_tag_name, xml_element_params)
        sub_elements = self._encode_sub_elements(properties_dict)

        element.extend(sub_elements)

        return element

    def encode_as_xml_string(
        self, model: XmlEncodableModel, encoding: str = "unicode"
    ) -> str:
        xml = self.encode_as_xml_element(model)
        return ET.tostring(xml, encoding=encoding)

    def _is_sequence_of_xml_encodable_models(self, value: Any) -> bool:
        return isinstance(value, list) and all(
            isinstance(item, XmlEncodableModel) for item in value
        )

    def _is_sub_element(self, value: Any) -> bool:
        return isinstance(
            value, XmlEncodableModel
        ) or self._is_sequence_of_xml_encodable_models(value)

    def _encode_params(self, properties_dict: dict[str, Any]) -> dict[str, str]:
        xml_element_params: dict[str, str] = {}

        for key, value in properties_dict.items():
            if value is None:
                continue

            if self._is_sub_element(value):
                continue

            encoded_key = self.key_encoder(key)
            encoded_value = self.param_value_encoder(value)

            xml_element_params[encoded_key] = encoded_value

        return xml_element_params

    def _encode_sub_elements(self, properties_dict: dict[str, Any]) -> list[ET.Element]:
        sub_elements = []

        for _, value in properties_dict.items():
            if value is None:
                continue

            if not self._is_sub_element(value):
                continue

            if isinstance(value, Sequence):
                for item in value:
                    if not isinstance(item, XmlEncodableModel):
                        continue
                    xml = self.encode_as_xml_element(item)
                    sub_elements.append(xml)

            elif isinstance(value, XmlEncodableModel):
                xml = self.encode_as_xml_element(value)
                sub_elements.append(xml)

        return sub_elements
