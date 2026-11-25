from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from schemas.seguimiento import (
    ConfirmacionCorreoRequest,
    ConfirmacionCorreoResponse,
    MarcadorOut,
    SeleccionBolsinRequest,
)


def test_seleccion_requiere_numero_positivo() -> None:
    with pytest.raises(ValidationError):
        SeleccionBolsinRequest(numeroBolsin=0)
    with pytest.raises(ValidationError):
        SeleccionBolsinRequest(numeroBolsin=-1)
    assert SeleccionBolsinRequest(numeroBolsin=101).numeroBolsin == 101


def test_confirmacion_acepta_false() -> None:
    assert ConfirmacionCorreoRequest(confirma=False).confirma is False


def test_confirmacion_correo_response() -> None:
    respuesta = ConfirmacionCorreoResponse(notificado=False)
    assert respuesta.estado == "FINALIZADO"
    assert respuesta.destinatarioEnmascarado is None


def test_marcador_serializa_fecha() -> None:
    marcador = MarcadorOut(
        numeroBolsin=101,
        latitud=-31.4201,
        longitud=-64.1888,
        fechaHoraUltimaActualizacion=datetime(2026, 3, 7, 12, 30),
    )
    assert marcador.model_dump()["numeroBolsin"] == 101


def test_id_cu_es_uuid() -> None:
    ident = uuid4()
    assert str(ident)
