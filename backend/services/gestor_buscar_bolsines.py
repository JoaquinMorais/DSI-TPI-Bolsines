from typing import Optional

from sqlmodel import select

from integrations.correo.interfaz_correo import InterfazCorreo
from integrations.google_maps.interfaz_google_maps import InterfazGoogleMaps
from integrations.gps_tracker.errores import UbicacionNoDisponibleError
from integrations.gps_tracker.interfaz_gps_tracker import InterfazGPSTracker
from models.bolsin import Bolsin
from models.empleado import Empleado
from models.iterator.i_agregado import IAgregado
from models.iterator.i_iterador import IIterador
from models.iterator.iterador_bolsin import IteradorBolsin
from models.resultados import (
    ResultadoConfirmacion,
    ResultadoSeleccion,
    ResultadoSeguimiento,
    SinUbicacion,
)
from models.ubicacion_bolsin import UbicacionBolsin


class GestorBuscarBolsines(IAgregado):
    def __init__(
        self,
        db,
        gps: InterfazGPSTracker,
        maps: InterfazGoogleMaps,
        correo: InterfazCorreo,
    ) -> None:
        self._db = db
        self._gps = gps
        self._maps = maps
        self._correo = correo
        self._codigoCM = ""
        self._bolsines: list[Bolsin] = []
        self._bolsinesEnviados: list[Bolsin] = []
        self._ubicaciones: list[UbicacionBolsin] = []
        self._sinUbicacion: list[SinUbicacion] = []
        self._seleccionBolsin: Optional[Bolsin] = None
        self._destinatario: Optional[str] = None

    def crearIterador(self, elementos: list[Bolsin]) -> IIterador:
        return IteradorBolsin(elementos, ["origen", self._codigoCM])

    def obtenerCodigoBolsinesEnviados(self) -> list[int]:
        iterador = self.crearIterador(self._bolsines)
        codigos: list[int] = []
        enviados: list[Bolsin] = []
        iterador.primero()
        while not iterador.haFinalizado():
            bolsin = iterador.elementoActual()
            enviados.append(bolsin)
            codigos.append(bolsin.getNumeroBolsin())
            iterador.siguiente()
        self._bolsinesEnviados = enviados
        return codigos

    async def opcionSeguirBolsines(self, usuario) -> ResultadoSeguimiento:
        empleado = usuario.getEmpleado()
        self._codigoCM = empleado.getCM().getCodigo()
        self._bolsines = await self._cargarBolsines()
        codigos = self.obtenerCodigoBolsinesEnviados()
        self._ubicaciones = []
        self._sinUbicacion = []
        for numeroBolsin in codigos:
            try:
                ubicacion = await self._gps.getBolsinLocation(
                    numeroBolsin, self._codigoCM
                )
            except UbicacionNoDisponibleError as exc:
                self._sinUbicacion.append(
                    SinUbicacion(exc.numeroBolsin, exc.motivo)
                )
            else:
                self._ubicaciones.append(ubicacion)
        mapa = self._maps.obtenerMapa(self._ubicaciones)
        return ResultadoSeguimiento(
            codigoCM=self._codigoCM,
            bolsines=list(self._bolsinesEnviados),
            mapa=mapa,
            sinUbicacion=list(self._sinUbicacion),
        )

    def tomarSeleccionBolsin(self, numeroBolsin: int) -> ResultadoSeleccion:
        for bolsin in self._bolsinesEnviados:
            if bolsin.getNumeroBolsin() == numeroBolsin:
                self._seleccionBolsin = bolsin
                return ResultadoSeleccion(
                    bolsin=bolsin,
                    ubicacion=self._ubicacionDe(numeroBolsin),
                )
        raise ValueError(f"El bolsin {numeroBolsin} no esta entre los enviados")

    async def tomarConfirmacionEnvioCorreo(
        self, confirma: bool
    ) -> ResultadoConfirmacion:
        if not confirma:
            return ResultadoConfirmacion(notificado=False, destinatario=None)
        notificado = await self.enviarMailGCM()
        return ResultadoConfirmacion(
            notificado=notificado, destinatario=self._destinatario
        )

    def cancelar(self) -> None:
        self._seleccionBolsin = None
        self._destinatario = None

    def _ubicacionDe(self, numeroBolsin: int) -> Optional[UbicacionBolsin]:
        for ubicacion in self._ubicaciones:
            if ubicacion.numeroBolsin == numeroBolsin:
                return ubicacion
        return None

    async def _cargarBolsines(self) -> list[Bolsin]:
        resultado = await self._db.exec(select(Bolsin))
        return list(resultado.all())

    async def enviarMailGCM(self) -> bool:
        if self._seleccionBolsin is None:
            return False
        cmDestino = self._seleccionBolsin.obtenerCMDestino()
        if cmDestino is None:
            return False
        gcm = await Empleado.obtenerGCMDeCM(self._db, cmDestino.getCodigo())
        if gcm is None or not gcm.sosGCM():
            return False
        usuario = gcm.getUsuario()
        if usuario is None:
            return False
        destinatario = usuario.getMail()
        ubicacion = self._ubicacionDe(self._seleccionBolsin.getNumeroBolsin())
        cuerpo = (
            f"Bolsin {self._seleccionBolsin.getNumeroBolsin()} "
            f"hacia CM {cmDestino.getCodigo()}"
        )
        if ubicacion is not None:
            cuerpo += (
                f"\nUbicacion: {ubicacion.latitud}, {ubicacion.longitud}"
                f"\nActualizado: {ubicacion.fechaHoraUltimaActualizacion.isoformat()}"
            )
        await self._correo.enviarMail(destinatario, "Ubicacion de bolsin", cuerpo)
        self._destinatario = destinatario
        return True
