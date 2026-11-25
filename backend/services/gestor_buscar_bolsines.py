from typing import Optional

from sqlmodel import select

from integrations.correo.interfaz_correo import InterfazCorreo
from integrations.google_maps.interfaz_google_maps import InterfazGoogleMaps
from integrations.gps_tracker.errores import UbicacionNoDisponibleError
from integrations.gps_tracker.interfaz_gps_tracker import InterfazGPSTracker
from models.bolsin import Bolsin
from models.comision_medica import ComisionMedica
from models.empleado import Empleado
from models.iterator.i_agregado import IAgregado
from models.iterator.i_iterador import IIterador
from models.iterator.iterador_bolsin import IteradorBolsin
from models.mapa_bolsines import MapaBolsines
from models.resultados import (
    ResultadoConfirmacion,
    ResultadoSeleccion,
    SinUbicacion,
)
from models.ubicacion_bolsin import UbicacionBolsin
from services.errores import SinBolsinesEnviadosError


class GestorBuscarBolsines(IAgregado):
    def __init__(self, db, usuario, gps, maps, correo) -> None:
        self._db = db
        self._usuario = usuario
        self._gps = gps
        self._maps = maps
        self._correo = correo

        self.nombreComisionMedica = ""
        self.codigoComisionMedica = ""
        self.bolsines: list[Bolsin] = []
        self.bolsinesEnviados: list[Bolsin] = []
        self.ubicacionesBolsines: list[UbicacionBolsin] = []
        self.seleccionBolsin: Optional[Bolsin] = None
        self.mapa: Optional[MapaBolsines] = None
        self.codigoBolsin: list[int] = []
        self.sinUbicacion: list[SinUbicacion] = []
        self.advertencias: list[str] = []

        self._codigoCM = ""
        self._destinatario: Optional[str] = None

    def buscarUsuarioLogueado(self) -> Empleado:
        empleado = self._usuario.getEmpleado()
        if empleado is None:
            raise ValueError("El usuario logueado no tiene empleado asociado")
        return empleado

    def getCMUsuarioLogueado(self) -> ComisionMedica:
        cm = self.buscarUsuarioLogueado().getCM()
        if cm is None:
            raise ValueError("El empleado logueado no tiene CM asignada")
        self.nombreComisionMedica = cm.nombre
        self.codigoComisionMedica = cm.getCodigo()
        self._codigoCM = cm.getCodigo()
        return cm

    async def opcionSeguirBolsines(self) -> None:
        self.getCMUsuarioLogueado()
        self.bolsines = await self._cargarBolsines()
        enviados = self.obtenerBolsinesEnviados()
        if not enviados:
            raise SinBolsinesEnviadosError(self._codigoCM)
        await self.obtenerUbicacionBolsin()
        self.obtenerMapa()

    def crearIterador(self, elementos: list[Bolsin]) -> IIterador:
        return IteradorBolsin(elementos, ["origen", self._codigoCM])

    def obtenerBolsinesEnviados(self) -> list[Bolsin]:
        iterador = self.crearIterador(self.bolsines)
        enviados: list[Bolsin] = []
        codigos: list[int] = []
        iterador.primero()
        while not iterador.haFinalizado():
            bolsin = iterador.elementoActual()
            enviados.append(bolsin)
            codigos.append(bolsin.getNumeroBolsin())
            iterador.siguiente()
        self.bolsinesEnviados = enviados
        self.codigoBolsin = codigos
        return enviados

    async def obtenerUbicacionBolsin(self) -> None:
        self.ubicacionesBolsines = []
        self.sinUbicacion = []
        for bolsin in self.bolsinesEnviados:
            numeroBolsin = bolsin.getNumeroBolsin()
            try:
                ubicacion = await self._gps.getBolsinLocation(
                    numeroBolsin, self._codigoCM
                )
            except UbicacionNoDisponibleError as exc:
                self.sinUbicacion.append(
                    SinUbicacion(exc.numeroBolsin, exc.motivo)
                )
                self.advertencias.append(
                    f"Bolsin {exc.numeroBolsin} sin ubicacion: {exc.motivo}"
                )
            else:
                self.ubicacionesBolsines.append(ubicacion)

    def obtenerMapa(self) -> MapaBolsines:
        self.mapa = self._maps.obtenerMapa(self.ubicacionesBolsines)
        return self.mapa

    def filtrarPorPrecinto(self, precinto: str) -> list[Bolsin]:
        texto = precinto.strip().lower()
        if not texto:
            return list(self.bolsinesEnviados)
        coincidencias = [
            bolsin
            for bolsin in self.bolsinesEnviados
            if texto in (bolsin.numeroPrecinto or "").lower()
        ]
        if not coincidencias:
            self.advertencias.append(
                f"No se encontro bolsin con precinto {precinto}"
            )
        return coincidencias

    def tomarSeleccionBolsin(self, numeroBolsin: int) -> ResultadoSeleccion:
        for bolsin in self.bolsinesEnviados:
            if bolsin.getNumeroBolsin() == numeroBolsin:
                self.seleccionBolsin = bolsin
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

    async def enviarMailGCM(self) -> bool:
        if self.seleccionBolsin is None:
            return False
        cmDestino = self.seleccionBolsin.obtenerCMDestino()
        if cmDestino is None:
            return False
        codigoDestino = cmDestino.getCodigo()

        gcm: Optional[Empleado] = None
        for empleado in await self._cargarEmpleados():
            if empleado.esTuCM(codigoDestino) and empleado.sosGCM():
                gcm = empleado
                break
        if gcm is None:
            return False
        usuario = gcm.getUsuario()
        if usuario is None:
            return False
        destinatario = usuario.getMail()

        ubicacion = self._ubicacionDe(self.seleccionBolsin.getNumeroBolsin())
        cuerpo = f"Bolsin {self.seleccionBolsin.getNumeroBolsin()}"
        if ubicacion is not None:
            cuerpo += (
                "\nFecha y hora de ultima actualizacion: "
                f"{ubicacion.fechaHoraUltimaActualizacion.isoformat()}"
                f"\nCoordenadas: {ubicacion.latitud}, {ubicacion.longitud}"
            )
        await self._correo.enviarMail(destinatario, "Ubicacion de bolsin", cuerpo)
        self._destinatario = destinatario
        return True

    def finCU(self) -> None:
        self.seleccionBolsin = None
        self._destinatario = None

    def cancelar(self) -> None:
        self.finCU()

    def _ubicacionDe(self, numeroBolsin: int) -> Optional[UbicacionBolsin]:
        for ubicacion in self.ubicacionesBolsines:
            if ubicacion.numeroBolsin == numeroBolsin:
                return ubicacion
        return None

    async def _cargarBolsines(self) -> list[Bolsin]:
        resultado = await self._db.exec(select(Bolsin))
        return list(resultado.all())

    async def _cargarEmpleados(self) -> list[Empleado]:
        resultado = await self._db.exec(select(Empleado))
        return list(resultado.all())
