from uuid import UUID

from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse

from config import composicion
from config.database import db_dependency
from schemas.seguimiento import (
    BolsinSeguimientoOut,
    ConfirmacionCorreoRequest,
    ConfirmacionCorreoResponse,
    CoordenadaOut,
    MarcadorOut,
    MapaBolsinesOut,
    SeguimientoCreadoResponse,
    SeleccionBolsinRequest,
    SeleccionBolsinResponse,
    SinUbicacionOut,
)
from services import registro_casos_uso
from services.errores import SinBolsinesEnviadosError
from utils.auth import encargado_bolsines_dependency
from utils.errores import ErrorDeApi

router = APIRouter(prefix="/seguimiento-bolsines", tags=["seguimiento"])

CASO_NO_ENCONTRADO = "El caso de uso no existe o vencio."
CORREO_NO_ENVIADO = "No se pudo enviar el correo"


def _bolsin_out(bolsin) -> BolsinSeguimientoOut:
    destino = bolsin.obtenerCMDestino()
    return BolsinSeguimientoOut(
        numeroBolsin=bolsin.getNumeroBolsin(),
        numeroPrecinto=bolsin.numeroPrecinto,
        codigoCMDestino=destino.getCodigo() if destino is not None else "",
    )


def _marcador_out(ubicacion) -> MarcadorOut:
    return MarcadorOut(
        numeroBolsin=ubicacion.numeroBolsin,
        latitud=ubicacion.latitud,
        longitud=ubicacion.longitud,
        fechaHoraUltimaActualizacion=ubicacion.fechaHoraUltimaActualizacion,
    )


def _mapa_out(mapa) -> MapaBolsinesOut:
    return MapaBolsinesOut(
        centro=CoordenadaOut(
            latitud=mapa.centro.latitud, longitud=mapa.centro.longitud
        ),
        zoom=mapa.zoom,
        marcadores=[_marcador_out(u) for u in mapa.marcadores],
    )


def _mapa_vacio() -> MapaBolsinesOut:
    return MapaBolsinesOut(
        centro=CoordenadaOut(latitud=0.0, longitud=0.0),
        zoom=6,
        marcadores=[],
    )


def _enmascarar(mail) -> str | None:
    if not mail or "@" not in mail:
        return None
    local, dominio = mail.split("@", 1)
    return f"{local[0]}***@{dominio}"


@router.post("")
async def iniciar(
    usuario: encargado_bolsines_dependency, db: db_dependency
) -> JSONResponse:
    gestor = composicion.crear_gestor(db, usuario)
    try:
        await gestor.opcionSeguirBolsines()
    except SinBolsinesEnviadosError as exc:
        raise ErrorDeApi(
            status.HTTP_404_NOT_FOUND, "SIN_BOLSINES_ENVIADOS", str(exc)
        ) from exc

    idCU = registro_casos_uso.crear(gestor)
    mapa = gestor.mapa
    respuesta = SeguimientoCreadoResponse(
        idCU=idCU,
        codigoCM=gestor.codigoComisionMedica,
        bolsines=[_bolsin_out(b) for b in gestor.bolsinesEnviados],
        mapa=_mapa_out(mapa) if mapa is not None else _mapa_vacio(),
        sinUbicacion=[
            SinUbicacionOut(numeroBolsin=s.numeroBolsin, motivo=s.motivo)
            for s in gestor.sinUbicacion
        ],
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=respuesta.model_dump(mode="json"),
    )


@router.post("/{idCU}/seleccion", response_model=SeleccionBolsinResponse)
async def seleccionar(
    idCU: UUID,
    datos: SeleccionBolsinRequest,
    usuario: encargado_bolsines_dependency,
    db: db_dependency,
) -> SeleccionBolsinResponse:
    gestor = registro_casos_uso.obtener(str(idCU))
    if gestor is None:
        raise ErrorDeApi(
            status.HTTP_404_NOT_FOUND, "CASO_USO_NO_ENCONTRADO", CASO_NO_ENCONTRADO
        )
    try:
        resultado = gestor.tomarSeleccionBolsin(datos.numeroBolsin)
    except ValueError as exc:
        raise ErrorDeApi(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "BOLSIN_FUERA_DE_ENVIADOS",
            str(exc),
        ) from exc
    ubicacion = (
        _marcador_out(resultado.ubicacion) if resultado.ubicacion else None
    )
    return SeleccionBolsinResponse(
        idCU=idCU,
        bolsin=_bolsin_out(resultado.bolsin),
        ubicacion=ubicacion,
    )


@router.post(
    "/{idCU}/confirmacion-correo", response_model=ConfirmacionCorreoResponse
)
async def confirmar(
    idCU: UUID,
    datos: ConfirmacionCorreoRequest,
    usuario: encargado_bolsines_dependency,
    db: db_dependency,
) -> ConfirmacionCorreoResponse:
    gestor = registro_casos_uso.obtener(str(idCU))
    if gestor is None:
        raise ErrorDeApi(
            status.HTTP_404_NOT_FOUND, "CASO_USO_NO_ENCONTRADO", CASO_NO_ENCONTRADO
        )
    try:
        resultado = await gestor.tomarConfirmacionEnvioCorreo(datos.confirma)
    except Exception as exc:
        raise ErrorDeApi(
            status.HTTP_502_BAD_GATEWAY,
            "CORREO_NO_ENVIADO",
            CORREO_NO_ENVIADO,
        ) from exc
    if datos.confirma and not resultado.notificado:
        raise ErrorDeApi(
            status.HTTP_502_BAD_GATEWAY,
            "CORREO_NO_ENVIADO",
            CORREO_NO_ENVIADO,
        )
    registro_casos_uso.eliminar(str(idCU))
    return ConfirmacionCorreoResponse(
        notificado=resultado.notificado,
        destinatarioEnmascarado=_enmascarar(resultado.destinatario),
    )


@router.delete("/{idCU}", status_code=status.HTTP_204_NO_CONTENT)
async def cancelar(
    idCU: UUID, usuario: encargado_bolsines_dependency, db: db_dependency
) -> Response:
    if not registro_casos_uso.eliminar(str(idCU)):
        raise ErrorDeApi(
            status.HTTP_404_NOT_FOUND, "CASO_USO_NO_ENCONTRADO", CASO_NO_ENCONTRADO
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
