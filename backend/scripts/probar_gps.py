import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.composicion import crear_gps
from integrations.gps_tracker.errores import (
    ErrorIntegracionGPS,
    UbicacionNoDisponibleError,
)


async def _probar(numeroBolsin: int, codigoCM: str) -> int:
    try:
        gps = crear_gps()
        ubicacion = await gps.getBolsinLocation(numeroBolsin, codigoCM)
    except UbicacionNoDisponibleError as exc:
        print(f"Sin ubicacion: {exc}")
        return 1
    except ErrorIntegracionGPS as exc:
        print(f"Error de integracion: {exc}")
        return 1
    except Exception as exc:
        print(f"Error al consultar el GPS: {exc}")
        return 1

    print(
        f"Bolsin {ubicacion.numeroBolsin}: "
        f"lat={ubicacion.latitud}, lon={ubicacion.longitud}, "
        f"actualizado={ubicacion.fechaHoraUltimaActualizacion.isoformat()}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Prueba la API real del GPS")
    parser.add_argument("numeroBolsin", nargs="?", type=int, default=101)
    parser.add_argument("codigoCM", nargs="?", default="CM-CBA-01")
    args = parser.parse_args()
    return asyncio.run(_probar(args.numeroBolsin, args.codigoCM))


if __name__ == "__main__":
    raise SystemExit(main())
