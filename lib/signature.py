from zeep import Client
from zeep.wsse.signature import BinarySignature
from zeep.wsse import utils
from datetime import datetime, timedelta
from lxml import etree


class BinarySignatureTimestamp(BinarySignature):
    def find_by_str(self, elements: list, text: str):
        for e in elements:
            name = str(e)
            if text in name:
                return e
            childs = e.getchildren()
            if childs:
                result = self.find_by_str(childs, text)
                if result:
                    return result
        return None

    def apply(self, envelope, headers):
        super().apply(envelope, headers)

        security = utils.get_security_header(envelope)
        children = security.getchildren()
        ref = self.find_by_str(children, "SecurityTokenReference")
        old_key = ref.find("wsse:Reference", namespaces=utils.NSMAP)
        ref.remove(old_key)
        binary = security.find("wsse:BinarySecurityToken", namespaces=utils.NSMAP)
        identifier = utils.WSSE("KeyIdentifier")
        identifier.text = binary.text.replace("\n", "")
        identifier.set(
            "EncodingType",
            "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary",
        )
        identifier.set(
            "ValueType", "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3"
        )
        ref.append(identifier)
        se = security.find("wsse:BinarySecurityToken", namespaces=utils.NSMAP)
        parent = se.getparent()
        parent.remove(se)
        return envelope, headers

    def verify(self, envelope):
        return envelope
