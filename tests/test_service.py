from datetime import datetime, timedelta
import json
import random
from collections import OrderedDict
from pydantic import ValidationError

import pytest
from faker import Faker
from lxml.etree import Element, _Element
from zeep.exceptions import Fault
from lib.utils import create_client, get_detail_recursively
from service import handler, history
from tests.utils import get_list_proyectos_by_constructora

fake = Faker()

CONSTRUCTORA = "Constructora Bolivar S.A"

RADICACION = {
    "service": "post_cliente_radicacion",
    "data": {
        "idTransaccion": "32258d905f9aba15f1e6427249cd18c9",
        "lugarNacimiento": "76001",
        "lugarExpedicionCedula": "76001",
        "fechaExpedicionCedula": "2015-09-20T00:00:00",
        "nacionalidad": "Colombia",
        "nivelEducacion": "Pregrado (Graduado)",
        "activos": "2700000",
        "pasivos": "1000000",
        "direccionResidencia": "Calle 74 # 02 - 10",
        "ciudadResidencia": "76001",
        "estrato": 3,
        "tipoViviendaResidencia": "Familiar",
        "nitEmpresa": "764363838",
        "nombreEmpresa": "LQN",
        "direccionEmpresa": "Calle 74 # 02 - 10",
        "ciudadEmpresa": "76001",
        "telefonoEmpresa": "80000000",
        "trabajaSedeDiferente": False,
        "cargo": "Desarrollador jefe",
        "experienciaLaboral": 2,
        "egresos": "500000",
        "manejaRecursosPublicos": False,
        "tieneVinculoPEP": False,
        "referenciaPersonal": {
            "nombres": "Mauricio Gonzales",
            "parentesco": "Amigo(a)",
            "ciudad": "76001",
            "celular": "3876780000",
        },
        "referenciaFamiliar": {
            "nombres": "Mauricio Gonzales",
            "parentesco": "Hijo(a)",
            "ciudad": "76001",
            "celular": "3876780001",
        },
        "ip": "192.168.0.1",
        "canal": "Web",
        "vivienda": {
            "tipoVivienda": "Usada",
            "tipoInmueble": "Casa",
            "destinoInmueble": "Renta",
            "constructora": "Constructora Bolivar S.A",
            "tieneParqueadero": True,
            "tipoParqueadero": "Cubierto",
            "modalidadCredito": "Uvr",
            "plazoCredito": "20",
            "valorInmueble": "240000000",
            "creditoSolicitadoValorAFinanciar": "120000000",
            "recursosPropios": "24000000",
            "subsidioVivienda": "240000000",
        },
    },
}

RANDOM_EMPTY_FIELDS = [
    "ip",
    "canal",
    "idTransaccion",
    "lugarNacimiento",
    "lugarExpedicionCedula",
    "fechaExpedicionCedula",
    "nacionalidad",
    "nivelEducacion",
    "direccionResidencia",
    "ciudadResidencia",
    "estrato",
    "tipoViviendaResidencia",
    "vivienda",
    "referenciaPersonal",
    "referenciaFamiliar",
]

RANDOM_TYPE_FIELDS = {
    "plazoCredito": "plazoCredito",
    "valorInmueble": "valorInmueble",
    "creditoSolicitadoValorAFinanciar": "creditoSolicitado",
    "recursosPropios": "recursosPropios",
    "subsidioVivienda": "subsidioVivienda",
}

data = {
    "origen": "LQN",
    "tipoDocumento": "Cédula ciudadanía",
    "numeroDocumento": random.randint(10000000, 9999999999),
    "fechaNacimiento": "1997-09-20T00:00:00",
    "nombres": fake.name(),
    "apellidos": fake.name(),
    "correoElectronico": fake.email(),
    "celular": random.randint(3000000000, 3999999999),
    "ocupacion": "Empleado",
    "tipoActividad": "Empleado",
    "tipoContrato": "Término indefinido",
    "fechaIngresoEmpleo": "2021-07-19T00:00:00",
    "ciudadResidencia": "Cali",
    "viviendaPropia": False,
    "tipoProducto": "Crédito de vivienda nueva",
    "valorInmueble": 120000000,
    "valorCredito": 70000000,
    "estadoCivil": "Soltero",
    "sexo": "Masculino",
    "numeroPersonasaCargo": 0,
    "ingresosMensuales": 2700000,
    "recursosPropios": 0,
    "encontroVivienda": True,
    "codigoCapcha": "",
    "idTransaccion": "",
    "ip": "192.168.0.1",
    "canal": "Web",
    "autorizacionConsultaCentrales": True,
    "codeudor": {
        "nombres": fake.name(),
        "apellidos": fake.name(),
        "tipoDocumento": "Cédula ciudadanía",
        "numeroDocumento": random.randint(10000000, 9999999999),
        "ciudadResidencia": "Cali",
        "ocupacion": "Independiente",
        "fechaNacimiento": "1968-01-26T00:00:00",
        "correoElectronico": fake.email(),
        "celular": random.randint(3000000000, 3999999999),
        "aportaIngresos": True,
        "ingresoMensual": 2000000,
        "autorizacionConsultaCentrales": True,
        "ip": "192.168.0.2",
        "canal": "Web",
    },
}

data_sin_codeudor = {
    "origen": "LQN",
    "tipoDocumento": "Cédula ciudadanía",
    "numeroDocumento": random.randint(10000000, 9999999999),
    # "fechaNacimiento": "1997-09-20",
    "fechaNacimiento": "1997-09-20T00:00:00",
    "nombres": fake.name(),
    "apellidos": fake.name(),
    "correoElectronico": fake.email(),
    "celular": random.randint(3000000000, 3999999999),
    "ocupacion": "Empleado",
    "tipoActividad": "Empleado",
    "tipoContrato": "Término indefinido",
    # "fechaIngresoEmpleo": "2021-07-19",
    "fechaIngresoEmpleo": "2021-07-19T00:00:00",
    "ciudadResidencia": "Cali",
    "viviendaPropia": False,
    "tipoProducto": "Crédito de vivienda nueva",
    "valorInmueble": 120000000,
    "valorCredito": 70000000,
    "estadoCivil": "Soltero",
    "sexo": "Masculino",
    "numeroPersonasaCargo": 0,
    "ingresosMensuales": 2700000,
    "recursosPropios": 0,
    "encontroVivienda": True,
    "codigoCapcha": "",
    "idTransaccion": "",
    "ip": "192.168.0.1",
    "canal": "Web",
    "autorizacionConsultaCentrales": True,
}

# ------------------------ service_create_client ------------------------


def test_service_create_client_not_error():
    """para crear cliente se debe ir a la url del captcha y obtener el codigo por el momento
    no se tiene el codigo para automatizar dicha prueba y se debe realizar manualmente
    """
    service = "create_client"
    # expected_result = {'error': False, 'message': 'Cliente creado correctamente'}
    expected_result = {
        "error": True,
        "message": "Error al crear cliente: codigoCapcha: El campo CodigoCapcha no puede estar vacío.",
    }
    result = handler({"data": data, "service": service}, None)
    assert expected_result["error"] == result["error"]
    assert expected_result["message"] == result["message"]


def test_service_create_client_error():
    client_exist_data = {
        "tipoDocumento": "Cédula ciudadanía",
        "numeroDocumento": 103175892,
        "origen": "LQN",
    }
    service = "create_client"
    expected_result = {"error": False, "message": "Lead en gestión por otro canal"}
    result = handler({"data": client_exist_data, "service": service}, None)
    assert expected_result["error"] == result["error"]
    assert expected_result["message"] == result["message"]


def test_service_create_client_without_codeudor_not_error():
    """para crear cliente se debe ir a la url del captcha y obtener el codigo por el momento
    no se tiene el codigo para automatizar dicha prueba y se debe realizar manualmente
    """
    service = "create_client"
    # expected_result = {'error': False, 'message': 'Cliente creado correctamente'}
    expected_result = {
        "error": True,
        "message": "Error al crear cliente: codigoCapcha: El campo CodigoCapcha no puede estar vacío.",
    }
    result = handler({"data": data_sin_codeudor, "service": service}, None)
    assert expected_result["error"] == result["error"]
    assert expected_result["message"] == result["message"]


def test_service_create_client_error_base():
    service = "create_client"
    data_base_error = {
        "tipoDocumento": data["tipoDocumento"],
        "numeroDocumento": random.randint(10000000, 9999999999),
        "origen": data["origen"],
    }
    expected_result = {
        "payload": {
            "error": True,
            "message": "Ha sucedido un problema al registrar el cliente",
        }
    }
    result = handler({"data": data_base_error, "service": service}, None)
    assert expected_result["payload"]["error"] == result["payload"]["error"]
    assert expected_result["payload"]["message"] == result["payload"]["message"]


def test_service_create_client_error_empty_field():
    service = "create_client"
    data["nombres"] = ""
    expected_result = {
        "error": True,
        "message": "Error al crear cliente: nombres: El campo Nombres no puede estar vacío.",
    }
    result = handler({"data": data, "service": service}, None)
    assert expected_result["error"] == result["error"]
    assert expected_result["message"] == result["message"]


# ------------------------ get_list_selection ------------------------


def test_get_list_selection_json():
    service = "get_list_selection"
    format = "json"
    result = handler({"data": data, "service": service, "format": format}, None)
    result_json = json.loads(result)
    expected_result = {
        "listCiudadResidencia": {
            "field": [
                {"label": "Bogotá", "value": "Bogotá"},
                {"label": "Medellín", "value": "Medellín"},
                {"label": "Cali", "value": "Cali"},
                {"label": "Barranquilla", "value": "Barranquilla"},
                {"label": "Bucaramanga", "value": "Bucaramanga"},
                {"label": "Pereira", "value": "Pereira"},
                {"label": "Manizales", "value": "Manizales"},
                {"label": "Armenia", "value": "Armenia"},
            ]
        },
        "listEstadoCivil": {
            "field": [
                {"label": "Soltero", "value": "Soltero"},
                {"label": "Unión libre", "value": "Unión libre"},
                {"label": "Divorciado", "value": "Divorciado"},
                {"label": "Separado", "value": "Separado"},
                {"label": "Casado ", "value": "Casado"},
            ]
        },
        "listOcupacionCodeudor": {
            "field": [
                {"label": "Empleado", "value": "Empleado"},
                {"label": "Independiente", "value": "Independiente"},
                {"label": "Pensionado", "value": "Pensionado"},
                {"label": "Empleado con negocio", "value": "Empleado con negocio"},
                {"label": "Ama de casa", "value": "Ama de casa"},
                {"label": "Rentista de capital", "value": "Rentista de capital"},
                {"label": "Prestador de servicios", "value": "Prestador de servicios"},
                {"label": "Estudiante", "value": "Estudiante"},
            ]
        },
        "listOcupacionPrincipal": {
            "field": [
                {"label": "Empleado", "value": "Empleado"},
                {"label": "Independiente", "value": "Independiente"},
                {"label": "Pensionado", "value": "Pensionado"},
            ]
        },
        "listProfesionActividadEmpleado": {
            "field": [
                {"label": "Magisterio", "value": "Magisterio"},
                {"label": "Fuerzas Militares", "value": "Fuerzas Militares"},
                {"label": "Ninguno", "value": "Empleado"},
            ]
        },
        "listProfesionActividadIndependiente": {
            "field": [
                {"label": "Dueño de negocio", "value": "Dueño de negocio"},
                {"label": "Conductor", "value": "Conductor"},
                {"label": "Transportador", "value": "Transportador"},
                {"label": "Rentista de capital", "value": "Rentista de capital"},
                {"label": "Prestador de servicios", "value": "Prestador de servicios"},
            ]
        },
        "listSexo": {
            "field": [
                {"label": "Masculino", "value": "Masculino"},
                {"label": "Femenino", "value": "Femenino"},
            ]
        },
        "listTipoContrato": {
            "field": [
                {"label": "Término fijo/Obra labor", "value": "Término fijo"},
                {"label": "Término indefinido", "value": "Término indefinido"},
            ]
        },
        "listTipoDocumento": {
            "field": [
                {"label": "Cédula de ciudadanía", "value": "Cédula ciudadanía"},
                {"label": "Cédula de extranjería", "value": "Cédula de extranjería"},
            ]
        },
        "listTipoProducto": {
            "field": [
                {
                    "label": "Crédito de vivienda nueva",
                    "value": "Crédito de vivienda nueva",
                },
                {
                    "label": "Crédito de vivienda usada",
                    "value": "Crédito de vivienda usada",
                },
            ]
        },
    }
    assert expected_result == result_json


def test_get_list_selection_default():
    service = "get_list_selection"
    format = None
    result = handler({"data": data, "service": service, "format": format}, None)
    expected_result = [
        OrderedDict([("label", "Bogotá"), ("value", "Bogotá")]),
        OrderedDict([("label", "Medellín"), ("value", "Medellín")]),
        OrderedDict([("label", "Cali"), ("value", "Cali")]),
        OrderedDict([("label", "Barranquilla"), ("value", "Barranquilla")]),
        OrderedDict([("label", "Bucaramanga"), ("value", "Bucaramanga")]),
        OrderedDict([("label", "Pereira"), ("value", "Pereira")]),
        OrderedDict([("label", "Manizales"), ("value", "Manizales")]),
        OrderedDict([("label", "Armenia"), ("value", "Armenia")]),
    ]
    assert expected_result == result["listCiudadResidencia"]["field"]


def test_get_list_selection_raw_elements():
    service = "get_list_selection"
    format = None
    result = handler({"data": data, "service": service, "format": format}, None)
    expected_result = [
        OrderedDict([("label", "Bogotá"), ("value", "Bogotá")]),
        OrderedDict([("label", "Medellín"), ("value", "Medellín")]),
        OrderedDict([("label", "Cali"), ("value", "Cali")]),
        OrderedDict([("label", "Barranquilla"), ("value", "Barranquilla")]),
        OrderedDict([("label", "Bucaramanga"), ("value", "Bucaramanga")]),
        OrderedDict([("label", "Pereira"), ("value", "Pereira")]),
        OrderedDict([("label", "Manizales"), ("value", "Manizales")]),
        OrderedDict([("label", "Armenia"), ("value", "Armenia")]),
    ]
    assert expected_result == result["listCiudadResidencia"]["field"]


# ------------------------ get_address_pregunta ------------------------


def test_get_address_pregunta():
    service = "get_address_pregunta"
    result = handler({"data": data, "service": service}, None)
    expected_result = "http://aplicaciones.adres.gov.co/"

    assert type(result["idTransaccion"]) is str
    url = result["urlCaptcha"]
    assert expected_result == url[:33]
    # assert expected_result == result


# ------------------------ post_existe_cliente ------------------------


def test_post_existe_cliente_no_existe():
    cliente = {
        "tipoDocumento": data["tipoDocumento"],
        "numeroDocumento": random.randint(10000000, 9999999999),
        "origen": data["origen"],
    }
    expected_result = {"existe": False, "mensaje": None}
    service = "post_existe_cliente"
    result = handler({"data": cliente, "service": service}, None)
    assert expected_result == result


# ------------------------ get_preaprobado ------------------------


def test_get_preaprobado_not_found():
    service = "get_preaprobado"
    expected_result = {"error": True, "message": "Transaccion no encontrada"}
    result = handler({"data": data, "service": service}, None)
    assert expected_result["error"] == result["error"]
    assert expected_result["message"] == result["message"]


def test_get_preaprobado_id():
    service = "get_preaprobado"
    expected_result = {
        "result_client": {
            "@xsi:type": "ax28:ResultadoCliente",
            "estadoConsulta": "Disponible para consulta",
            "fechaRetomaSolicitud": {"@xsi:nil": "true"},
            "observacionesPrevalidador": "Consulta exitosa",
            "resultadPrevalidador": "VIABLE",
        },
        "result_client_detail": {
            "@xsi:type": "ax28:Detalle",
            "LTVPrevalidado": "70.0",
            "endeudamientoFinancieroPrevalidado": "14.917695473251028",
            "montoSugeridoPreaprobado": "102260992",
            "relacionCuotaIngresoPrevalidado": "33.0",
        },
    }
    data = {"idTransaccion": "1128bd688fb4eeaf8ae2b4965cf2ab4b"}
    result = handler({"data": data, "service": service}, None)
    assert (
        expected_result["result_client"]["resultadPrevalidador"]
        == result["resultadPrevalidador"]
    )
    assert (
        expected_result["result_client_detail"]["montoSugeridoPreaprobado"]
        == result["montoSugeridoPreaprobado"]
    )


# ------------------------ utils ------------------------


def test_get_detail_recursively_text():
    element = Element("root", interesting="totally")
    expected_result = ("root", {"interesting": "totally"})
    result = get_detail_recursively(element)
    assert expected_result == result


def test_get_detail_recursively_bytes():
    element = Element("root", interesting="totally")
    element = bytes(element)
    expected_result = ""
    result = get_detail_recursively(element)
    assert expected_result == result


def test_get_list_proyectos_by_constructora_success():
    json_proyectos = get_list_proyectos_by_constructora(handler, CONSTRUCTORA)

    assert json_proyectos.get("listProyectos") is not None
    proyectos = json_proyectos.get("listProyectos")

    assert proyectos.get("field") is not None
    assert proyectos.get("message") is None
    proyectos = proyectos.get("field")
    
    assert isinstance(proyectos, (list,))


def test_post_cliente_radicacion_already_exists():
    fecha_estimada_entrega = datetime.now() + timedelta(days=60)
    fecha_estimada_entrega = fecha_estimada_entrega.strftime("%Y-%m-%dT00:00:00")

    json_proyectos = get_list_proyectos_by_constructora(handler, CONSTRUCTORA)
    proyecto = json_proyectos["listProyectos"]["field"][0]

    RADICACION["data"]["vivienda"]["fechaEstimadaEntrega"] = fecha_estimada_entrega
    RADICACION["data"]["vivienda"]["proyecto"] = proyecto["value"]
    RADICACION["data"]["type"] = "employe"

    try:
        handler(
            RADICACION,
            None,
        )
    except Fault as e:
        err_msg = "No se ha podido generar la radicación debido al estado actual de la transacción"
        client = create_client(history)

        parsed_fault_detail = client.wsdl.types.deserialize(e.detail[0])

        service_fault_exception = parsed_fault_detail["ServiceFaultException"]
        service_status = service_fault_exception["serviceStatus"]

        assert err_msg in service_status["description"]
        assert service_status["code"] == "RAD_CTE_ERR"


def test_post_cliente_radicacion_fail_empty_random_fields():
    fecha_estimada_entrega = datetime.now() + timedelta(days=60)
    fecha_estimada_entrega = fecha_estimada_entrega.strftime("%Y-%m-%dT00:00:00")

    json_proyectos = get_list_proyectos_by_constructora(handler, CONSTRUCTORA)
    proyecto = json_proyectos["listProyectos"]["field"][0]

    radicacion = RADICACION.copy()

    radicacion["data"]["vivienda"]["fechaEstimadaEntrega"] = fecha_estimada_entrega
    radicacion["data"]["vivienda"]["proyecto"] = proyecto["value"]
    radicacion["data"]["type"] = "employe"

    delete_field = random.choice(RANDOM_TYPE_FIELDS)
    radicacion["data"].pop(delete_field)

    try:
        handler(
            radicacion,
            None,
        )
    except ValidationError as e:
        json_err = json.loads(e.json())[0]

        assert json_err["msg"] == "field required"
        assert json_err["loc"][0] == delete_field


def test_post_cliente_radicacion_fail_type_random_fields():
    fecha_estimada_entrega = datetime.now() + timedelta(days=60)
    fecha_estimada_entrega = fecha_estimada_entrega.strftime("%Y-%m-%dT00:00:00")

    json_proyectos = get_list_proyectos_by_constructora(handler, CONSTRUCTORA)
    proyecto = json_proyectos["listProyectos"]["field"][0]

    radicacion = RADICACION.copy()

    radicacion["data"]["vivienda"]["fechaEstimadaEntrega"] = fecha_estimada_entrega
    radicacion["data"]["vivienda"]["proyecto"] = proyecto["value"]
    radicacion["data"]["type"] = "employe"

    random_field = random.choice(list(RANDOM_TYPE_FIELDS.keys()))
    change_field = RANDOM_TYPE_FIELDS.get(random_field)

    # radicacion["data"]["valorInmueble"] = "change_field"
    radicacion["data"][random_field] = change_field

    breakpoint()
    # delete_field = random.choice(RANDOM_TYPE_FIELDS.keys())

    # radicacion["data"].pop(delete_field)

    try:
        handler(
            radicacion,
            None,
        )
    except ValidationError as e:
        json_err = json.loads(e.json())[0]

        assert json_err["msg"] == "field required"
        assert json_err["loc"][0] == delete_field
