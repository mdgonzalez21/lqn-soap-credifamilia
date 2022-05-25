import json
import os
from collections import deque
from typing import Any
from urllib import parse
from urllib.request import pathname2url

from lxml.etree import _Element
from requests import Session
from zeep import Client, Settings, helpers
from zeep.exceptions import Fault
from zeep.transports import Transport

from lib.settings import WSDL, BASE_DIR
from lib.signature import BinarySignatureTimestamp


class CustomEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, _Element):
            return str(o)

        return json.JSONEncoder.default(self, o)


def capture_soap_error(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Fault as error:
            raise
            return render_soap_error(error, from_function=function.__name__)
        # except Exception as error:
        #     # raise
        #     print(traceback.format_exc())
        #     return build_reply_message(True, f"{type(error)}: {str(error)}", None, from_function=function.__name__)

    return wrapper


def build_reply_message(is_error: bool, message: str, payload: Any, from_function: str) -> dict:
    """
    allows to generate a standard response for the lambda
    :param is_error: identifies if the response is error
    :param message: text that summarizes the response
    :param payload: additional information answered by the credifamilia api
    :return: a reply message in json format
    """
    print("BUILD reply", is_error, payload)
    return {"error": is_error, "message": message, "payload": payload, "function": from_function}


def get_detail_recursively(element: _Element):
    """
    go through a tree of elements recursively and return the information
    :param element: main element to inspect
    :return: item inspected and organized
    """
    if isinstance(element, bytes):
        return element.decode("utf-8")

    if element.text is None and len(element.attrib) > 0:
        return element.tag, element.attrib
    return element.tag, dict(map(get_detail_recursively, element)) or element.text


def render_soap_error(error: Fault, from_function: str):
    """
    render an error provided by the api in the format set for responses
    :param error: instance of the generated error
    :return: a reply message in json format
    """
    detail = get_detail_recursively(error.detail)
    return build_reply_message(True, str(error), detail, from_function=from_function)


def serialize_soap_response(soap_object):
    """
    convert an api response to a dictionary
    :param soap_object: object returned by the library that consumes the api
    :return: dictionary with response elements
    """
    input_dict = helpers.serialize_object(soap_object)
    format_keys = []
    for x in input_dict:
        if isinstance(input_dict[x], deque):
            format_keys.append(x)

    for x in format_keys:
        input_dict[x] = list(input_dict[x])
    return json.loads(json.dumps(input_dict, cls=CustomEncoder, default=str))


def clean_dict(d):
    response = {}
    for k, v in d.items():
        if ("ax28:" or "ax22:") in k:
            k = k[5:]
        response[k] = v
    return response


def create_client(history):
    key_file = os.path.join(BASE_DIR, "lib/certs_lqn/key.pem")
    cert_file = os.path.join(BASE_DIR, "lib/certs_lqn/certificate.pem")

    session = Session()
    session.verify = False
    # session.cert = (cert_file, key_file)

    transport = Transport(session=session)
    settings = Settings(strict=False, xml_huge_tree=True)
    wsdl_url = parse.urljoin("file:", pathname2url(os.path.abspath(WSDL)))

    return Client(
        wsdl_url,
        transport=transport,
        settings=settings,
        wsse=BinarySignatureTimestamp(key_file=key_file, certfile=cert_file),
        plugins=[history],
    )
