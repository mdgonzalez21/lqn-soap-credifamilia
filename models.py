import json
from typing import Optional

from pydantic import BaseModel


class House(BaseModel):
    tipoVivienda: str
    tipoInmueble: str
    destinoInmueble: str
    constructora: str
    proyecto: str
    tipoParqueadero: str
    fechaEstimadaEntrega: str
    modalidadCredito: str
    plazoCredito: int
    valorInmueble: int
    creditoSolicitadoValorAFinanciar: int
    recursosPropios: int
    subsidioVivienda: int


class FinancialInformation(BaseModel):
    activos: int
    pasivos: int
    egresos: int
    manejaRecursosPublicos: bool
    tieneVinculoPEP: bool
    tipoVinculoPEP: Optional[str]
    nombrePEP: Optional[str]
    cedulaPEP: Optional[str]


class Reference(BaseModel):
    nombres: str
    parentesco: str
    ciudad: str
    celular: str


class UserBasicInfo(FinancialInformation):
    ip: str
    canal: str
    idTransaccion: str
    lugarNacimiento: str
    lugarExpedicionCedula: str
    fechaExpedicionCedula: str
    nacionalidad: str
    nivelEducacion: str
    direccionResidencia: str
    ciudadResidencia: str
    estrato: int
    tipoViviendaResidencia: str
    fechaVigenciaCedulaExtranjeria: Optional[str]
    vivienda: House
    referenciaPersonal: Reference
    referenciaFamiliar: Reference

    def pretty_dict(self, **kwargs):
        return json.dumps(self.dict(**kwargs), indent=4)


class Employe(UserBasicInfo):
    nitEmpresa: str
    nombreEmpresa: str
    direccionEmpresa: str
    ciudadEmpresa: str
    telefonoEmpresa: int
    trabajaSedeDiferente: str
    cargo: str
    experienciaLaboral: int

    direccionOficina: Optional[str]
    ciudadOficina: Optional[str]
    telefonoOficina: Optional[str]


class Pensioner(UserBasicInfo):
    nombreEmpresa: str
    nitEmpresa: str
    direccionEmpresa: str
    ciudadEmpresa: str
    telefonoEmpresa: int


class IndependentServiceProvider(UserBasicInfo):
    nitEmpresa: str
    nombreEmpresa: str
    direccionEmpresa: str
    ciudadEmpresa: str
    telefonoEmpresa: int
    extensionTelefonoEmpresa: Optional[int]
    trabajaSedeDiferente: str
    cargo: str
    experienciaLaboral: str


class IndependentCapitalAnnuitant(UserBasicInfo):
    direccionEmpresa: str
    ciudadEmpresa: str
    experienciaLaboral: str


class IndependentBusinessOwner(UserBasicInfo):
    nitEmpresa: str
    nombreEmpresa: str
    direccionEmpresa: str
    ciudadEmpresa: str
    telefonoEmpresa: int
    experienciaLaboral: int

    extensionTelefonoEmpresa: Optional[int]


class IndependentDriver(UserBasicInfo):
    nombreEmpresa: str
    telefonoEmpresa: int
    experienciaLaboral: int
