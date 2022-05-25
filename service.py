import json
import os
import warnings
from typing import Any
from urllib import parse
from urllib.request import pathname2url

import xmltodict
from lxml import etree
from factories import FilingFactory
from zeep import helpers
from zeep.plugins import HistoryPlugin
from lib.settings import UNDEFINED_ERROR
from lib.utils import (
    CustomEncoder,
    build_reply_message,
    capture_soap_error,
    serialize_soap_response,
    create_client,
    clean_dict,
)


warnings.simplefilter("ignore")

history = HistoryPlugin()


@capture_soap_error
def get_list_selection(client):
    """
    Este servicio retorna un listado de objetos cuyo nombre indica el tipo de información que contiene
    (ej.: listTipoContrato, listTipoDocumento), estos a su vez contienen un conjunto de opciones (field) con su
    respectiva etiqueta (label) y valor (value). Se recomienda consumir este servicio a diario para estar
    sincronizados con los posibles cambios que se puedan presentar en nuestro CRM y evitar errores en el
    registro del cliente.
    """
    get_list_selection_response = helpers.serialize_object(client.service.getListSelection(_soapheaders=None))
    return get_list_selection_response


@capture_soap_error
def post_existe_cliente(client, request_data):
    """
    Este método debe ser invocado al inicio del proceso ya que retorna si el cliente se encuentra registrado en
    nuestro CRM, si ya existe NO se permitirá su registro.
    """
    post_existe_cliente_response = client.service.postExisteCliente(**{"request": request_data}, _soapheaders=None)
    return serialize_soap_response(post_existe_cliente_response)


@capture_soap_error
def get_list_proyectos_by_constructora(client, request_data):
    """
    Llamado al servicio para conocer los proyectos existentes que se encuentran activos y con aprobación de riesgos,
    relacionados a la constructora indicada.
    """
    resp = client.service.getListProyectosByConstructora(request=request_data, _soapheaders=None)
    return serialize_soap_response(resp)



@capture_soap_error
def post_cliente_radicacion(client, request_data):
    """
    Después de registrar al cliente, se debe invocar este servicio para registrar la radicación de crédito.
    """
    filing = FilingFactory.get_filing(request_data)
    filing_data = filing.dict(exclude_unset=True)

    resp = client.service.postClienteRadicacion(request=filing_data, _soapheaders=None)
    return serialize_soap_response(resp)


@capture_soap_error
def get_address_pregunta(client):
    """
    Nota: Al consumir este servicio se debe tener en cuenta que la url de la imagen viene codificada con entidades
    html (específicamente en el carácter & el cual viene codificado como &amp;)
    Ej:
    http://aplicaciones.adres.gov.co/COM_4023//Telerik.Web.UI.WebResource.axd?type=rca&amp;isc=true&amp;guid=54889294-a809-4632-9d1d-cce8da7a8a59

    En este caso la url debe ser decodificada para poder acceder correctamente a la imagen del captcha. Posterior a
    la decodificación la url debe tener la siguiente forma

    http://aplicaciones.adres.gov.co/COM_4023//Telerik.Web.UI.WebResource.axd?type=rca&isc=true&guid=54889294-a809-4632-9d1d-cce8da7a8a59
    """

    get_address_pregunta_response = client.service.getAdresPreguntaRequest()
    return serialize_soap_response(get_address_pregunta_response)


@capture_soap_error
def post_cliente(client, request_data):
    """
    Después de validar que el cliente no exista en nuestro CRM se puede proceder a consumir este servicio el cual
    permite el registro del cliente y su respectiva pre-validación, todos los campos descritos a continuación
    son requeridos
    """
    post_cliente_response = client.service.postCliente(**{"request": request_data}, _soapheaders=None)
    return serialize_soap_response(post_cliente_response)


@capture_soap_error
def get_preaprobado(client, idTransaccion):
    """
    Después de recibir la notificación del resultado del prevalidador a través del webhook proporcionado por la
    proptech se debe invocar este servicio para obtener el detalle del resultado del prevalidador.
    """
    request_data = {"idTransaccion": idTransaccion or "1"}
    post_existe_cliente_response = client.service.getPreaprobado(**{"request": request_data}, _soapheaders=None)
    your_pretty_xml = etree.tostring(history.last_received["envelope"], encoding="unicode", pretty_print=True)
    xml = xmltodict.parse(your_pretty_xml)
    result_str = json.dumps(xml, cls=CustomEncoder, default=str)
    result = json.loads(result_str)
    result_return = (
        result.get("soapenv:Envelope").get("soapenv:Body").get("ns:getPreaprobadoResponse").get("ns:return")
    )
    result_client = result_return.get("ax22:resultadoCliente")
    result_client_detail = result_return.get("ax22:resultadoCliente").get("ax28:detalle")
    preaproved_letter = result_return.get("ax22:cartaPreaprobado")
    result_client.pop("ax28:detalle")
    response = {}
    response["result_client"] = clean_dict(result_client)
    response["result_client_detail"] = clean_dict(result_client_detail)
    response["preaproved_letter"] = preaproved_letter
    response = clean_dict(response)
    return serialize_soap_response(response)


@capture_soap_error
def service_create_client(client, data):
    client_exist_data = {
        "tipoDocumento": data.get("tipoDocumento"),
        "numeroDocumento": data.get("numeroDocumento"),
        "origen": "LQN",
    }
    client_exist_result = post_existe_cliente(client, client_exist_data)
    exists = client_exist_result.get("existe")
    if exists is False:
        client_result = post_cliente(client, data)
        your_pretty_xml = etree.tostring(history.last_received["envelope"], encoding="unicode", pretty_print=True)
        xml = xmltodict.parse(your_pretty_xml)
        result_str = json.dumps(xml, cls=CustomEncoder, default=str)
        result = json.loads(result_str)
        fault = result.get("soapenv:Envelope").get("soapenv:Body").get("soapenv:Fault")
        if fault:
            description = None
            fault_string = fault.get("faultstring", UNDEFINED_ERROR)
            if fault_string == UNDEFINED_ERROR:
                # TODO: Reportar error a Sentry
                pass

            fault_detail = fault.get("detail", UNDEFINED_ERROR)
            if fault_detail is not None:
                description = (
                    fault_detail.get("ns:proptechEndPointServiceFaultException")
                    .get("ServiceFaultException")
                    .get("ax21:serviceStatus")
                    .get("ax22:description")
                )

            if description is not None:
                fault_string += f". {str(description)}"

            return build_reply_message(
                True,
                f"Error al crear cliente: (fault = {fault_string})",
                client_result,
                from_function="service_create_client",
            )
        else:
            approved_result = get_preaprobado(client, client_result.get("idTransaccion"))
            approved_result.update({"idTransaccion": client_result.get("idTransaccion")})
            return build_reply_message(
                False, "Cliente creado correctamente", approved_result, from_function="service_create_client"
            )
    else:
        return build_reply_message(
            False, client_exist_result.get("mensaje"), client_exist_result, from_function="service_create_client"
        )


def handler(event, context):
    client = create_client(history)
    service = event.get("service")
    format = event.get("format", "json")
    data = event.get("data", None)
    result = {"error": True, "message": "Ningun servicio utilizado"}

    if service == "create_client":  # post_cliente
        result = service_create_client(client, data)
    elif service == "get_list_selection":
        result = get_list_selection(client)
    elif service == "get_address_pregunta":
        result = get_address_pregunta(client)
    elif service == "post_existe_cliente":
        result = post_existe_cliente(client, data)
    elif service == "get_preaprobado":
        id_transaccion = data["idTransaccion"]
        result = get_preaprobado(client, id_transaccion)
    elif service == "post_cliente_radicacion":
        result = post_cliente_radicacion(client, data)
    elif service == "get_list_proyectos_by_constructora":
        result = get_list_proyectos_by_constructora(client, data)

    if format == "json" and not isinstance(result, str):
        result = json.dumps(result, cls=CustomEncoder, default=str)

    return result
