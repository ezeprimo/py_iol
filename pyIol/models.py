"""
Modelos de datos para las respuestas de la API de Invertir Online
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional

# ---------------------------------------------------------------------------
# Helpers — conversión segura de valores numéricos desde la API
# ---------------------------------------------------------------------------


def _parse_number_string(value: str) -> str:
    """Convierte un string numérico regional a formato float estándar.

    Soporta:
    - ``"138.02"`` — estándar JSON (punto decimal)
    - ``"1,234.56"`` — coma como separador de miles, punto decimal
    - ``"1.250,50"`` — formato argentino/europeo (punto miles, coma decimal)
    - ``"1,000"`` — coma como separador de miles (3 dígitos a la derecha)
    - ``"1250,50"`` — coma decimal
    """
    if "," in value and "." in value:
        # Ambos presentes: el que está más a la derecha es el decimal
        if value.rfind(",") > value.rfind("."):
            # Formato europeo/argentino: "1.250,50" → 1250.50
            value = value.replace(".", "").replace(",", ".")
        else:
            # Formato inglés: "1,234.56" → 1234.56
            value = value.replace(",", "")
    elif "," in value:
        # Solo coma. Distinguir entre separador de miles y decimal.
        # Heurística: si la coma aparece una sola vez y tiene exactamente
        # 3 dígitos a la derecha → separador de miles; sino → decimal.
        parts = value.rsplit(",", 1)
        if len(parts[1]) == 3 and parts[1].isdigit():
            # Probablemente separador de miles: "1,000" → "1000"
            value = value.replace(",", "")
        else:
            # Decimal: "1250,50" → "1250.50"
            value = value.replace(",", ".")
    # Si solo hay punto, está en formato estándar — no hacer nada
    return value


def _to_float(value: Any, default: float = 0.0) -> float:
    """Convierte un valor de API a float de forma segura.

    La API de IOL a veces retorna números como strings (ej. ``"138.02"``).
    Este helper normaliza: ``None`` → *default*,
    ``str`` → ``float`` (con soporte regional),
    ``int``/``float`` → ``float(value)``.
    """
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        return float(_parse_number_string(value))
    # dicts, lists, etc. → no son convertibles a float
    return default


def _to_int(value: Any, default: int = 0) -> int:
    """Convierte un valor de API a int de forma segura.

    Idem ``_to_float`` pero retorna ``int``.
    """
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        return int(float(_parse_number_string(value)))
    return default


def _to_optional_float(value: Any) -> Optional[float]:
    """Convierte un valor de API a ``Optional[float]``.

    ``None`` → ``None``, resto igual que ``_to_float``.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        return float(_parse_number_string(value))
    # dicts (ej. parking vacío {}), lists, etc. → None
    return None


def _to_optional_int(value: Any) -> Optional[int]:
    """Convierte un valor de API a ``Optional[int]``.

    ``None`` → ``None``, resto igual que ``_to_int``.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        return int(float(_parse_number_string(value)))
    return None


def _first_present(data: dict, *keys: str) -> Any:
    """Devuelve el valor de la primera clave presente en el dict.

    A diferencia de ``data.get(a) or data.get(b)`` no se rompe con
    valores falsy legítimos (``0``, ``0.0``, ``""``).
    """
    for key in keys:
        if key in data:
            return data[key]
    return None


@dataclass
class Punta:
    """Modelo para las puntas de compra y venta"""

    cantidad_compra: int
    precio_compra: float
    precio_venta: float
    cantidad_venta: int

    @classmethod
    def from_dict(cls, data: dict) -> "Punta":
        """Crea una instancia de Punta desde un diccionario"""
        return cls(
            cantidad_compra=_to_int(data.get("cantidadCompra")),
            precio_compra=_to_float(data.get("precioCompra")),
            precio_venta=_to_float(data.get("precioVenta")),
            cantidad_venta=_to_int(data.get("cantidadVenta")),
        )


@dataclass
class CotizacionTitulo:
    """Modelo para la cotización de un título"""

    ultimo_precio: float
    variacion: float
    apertura: float
    maximo: float
    minimo: float
    fecha_hora: datetime
    tendencia: str
    cierre_anterior: float
    monto_operado: int
    volumen_nominal: int
    precio_promedio: float
    moneda: str
    precio_ajuste: float
    intereses_abiertos: int
    puntas: List[Punta]
    cantidad_operaciones: int
    descripcion_titulo: str
    plazo: str
    lamina_minima: int
    lote: int

    @classmethod
    def from_dict(cls, data: dict) -> "CotizacionTitulo":
        """Crea una instancia de CotizacionTitulo desde un diccionario"""
        # Parsear la fecha
        fecha_hora_str = data.get("fechaHora", "")
        try:
            # Intentar parsear la fecha ISO con timezone
            fecha_hora = datetime.fromisoformat(fecha_hora_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            # Si no se puede parsear, usar datetime actual
            fecha_hora = datetime.now()

        # Parsear las puntas
        puntas_data = data.get("puntas", [])
        puntas = [Punta.from_dict(punta) for punta in puntas_data]

        return cls(
            ultimo_precio=_to_float(data.get("ultimoPrecio")),
            variacion=_to_float(data.get("variacion")),
            apertura=_to_float(data.get("apertura")),
            maximo=_to_float(data.get("maximo")),
            minimo=_to_float(data.get("minimo")),
            fecha_hora=fecha_hora,
            tendencia=data.get("tendencia", ""),
            cierre_anterior=_to_float(data.get("cierreAnterior")),
            monto_operado=_to_int(data.get("montoOperado")),
            volumen_nominal=_to_int(data.get("volumenNominal")),
            precio_promedio=_to_float(data.get("precioPromedio")),
            moneda=data.get("moneda", ""),
            precio_ajuste=_to_float(data.get("precioAjuste")),
            intereses_abiertos=_to_int(data.get("interesesAbiertos")),
            puntas=puntas,
            cantidad_operaciones=_to_int(data.get("cantidadOperaciones")),
            descripcion_titulo=data.get("descripcionTitulo", ""),
            plazo=data.get("plazo", ""),
            lamina_minima=_to_int(data.get("laminaMinima")),
            lote=_to_int(data.get("lote")),
        )

    def __str__(self) -> str:
        """Representación string del objeto"""
        return (
            f"{self.descripcion_titulo} ({self.moneda})\n"
            f"Último precio: {self.ultimo_precio}\n"
            f"Variación: {self.variacion}%\n"
            f"Apertura: {self.apertura} | Máximo: {self.maximo} | Mínimo: {self.minimo}\n"
            f"Tendencia: {self.tendencia}\n"
            f"Fecha/Hora: {self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    @property
    def mejor_compra(self) -> Optional[Punta]:
        """Retorna la mejor punta de compra (precio más alto)"""
        if not self.puntas:
            return None
        return max(self.puntas, key=lambda p: p.precio_compra)

    @property
    def mejor_venta(self) -> Optional[Punta]:
        """Retorna la mejor punta de venta (precio más bajo)"""
        if not self.puntas:
            return None
        return min(self.puntas, key=lambda p: p.precio_venta)

    @property
    def spread(self) -> Optional[float]:
        """Calcula el spread entre la mejor compra y venta"""
        mejor_compra = self.mejor_compra
        mejor_venta = self.mejor_venta

        if mejor_compra and mejor_venta:
            return mejor_venta.precio_venta - mejor_compra.precio_compra
        return None

    @property
    def variacion_porcentual(self) -> float:
        """Retorna la variación como porcentaje"""
        return self.variacion

    @property
    def rendimiento_diario(self) -> float:
        """Calcula el rendimiento del día en porcentaje"""
        if self.cierre_anterior > 0:
            return ((self.ultimo_precio - self.cierre_anterior) / self.cierre_anterior) * 100
        return 0.0


@dataclass
class CotizacionOpcion:
    """Modelo para la cotización de una opción"""

    ultimo_precio: float
    variacion: float
    apertura: float
    maximo: float
    minimo: float
    fecha_hora: datetime
    tendencia: str
    cierre_anterior: float
    monto_operado: int
    volumen_nominal: int
    precio_promedio: float
    moneda: int  # En opciones viene como int, no string
    precio_ajuste: float
    intereses_abiertos: int
    puntas: Optional[List[Punta]]  # Puede ser null
    cantidad_operaciones: int
    descripcion_titulo: Optional[str]  # Puede ser null
    plazo: Optional[str]  # Puede ser null
    lamina_minima: int
    lote: int

    @classmethod
    def from_dict(cls, data: dict) -> "CotizacionOpcion":
        """Crea una instancia de CotizacionOpcion desde un diccionario"""
        # Parsear la fecha
        fecha_hora_str = data.get("fechaHora", "")
        try:
            # Intentar parsear la fecha ISO con timezone
            if fecha_hora_str and fecha_hora_str != "0001-01-01T00:00:00":
                fecha_hora = datetime.fromisoformat(fecha_hora_str.replace("Z", "+00:00"))
            else:
                # Si es la fecha por defecto o vacía, usar datetime actual
                fecha_hora = datetime.now()
        except (ValueError, AttributeError):
            # Si no se puede parsear, usar datetime actual
            fecha_hora = datetime.now()

        # Parsear las puntas (puede ser null)
        puntas_data = data.get("puntas", [])
        puntas = None
        if puntas_data:
            puntas = [Punta.from_dict(punta) for punta in puntas_data]

        return cls(
            ultimo_precio=_to_float(data.get("ultimoPrecio")),
            variacion=_to_float(data.get("variacion")),
            apertura=_to_float(data.get("apertura")),
            maximo=_to_float(data.get("maximo")),
            minimo=_to_float(data.get("minimo")),
            fecha_hora=fecha_hora,
            tendencia=data.get("tendencia", ""),
            cierre_anterior=_to_float(data.get("cierreAnterior")),
            monto_operado=_to_int(data.get("montoOperado")),
            volumen_nominal=_to_int(data.get("volumenNominal")),
            precio_promedio=_to_float(data.get("precioPromedio")),
            moneda=_to_int(data.get("moneda")),  # En opciones es int
            precio_ajuste=_to_float(data.get("precioAjuste")),
            intereses_abiertos=_to_int(data.get("interesesAbiertos")),
            puntas=puntas,
            cantidad_operaciones=_to_int(data.get("cantidadOperaciones")),
            descripcion_titulo=data.get("descripcionTitulo"),  # Puede ser null
            plazo=data.get("plazo"),  # Puede ser null
            lamina_minima=_to_int(data.get("laminaMinima")),
            lote=_to_int(data.get("lote")),
        )

    def __str__(self) -> str:
        """Representación string del objeto"""
        titulo = self.descripcion_titulo or "Opción"
        return (
            f"{titulo}\n"
            f"Último precio: {self.ultimo_precio}\n"
            f"Variación: {self.variacion}%\n"
            f"Apertura: {self.apertura} | Máximo: {self.maximo} | Mínimo: {self.minimo}\n"
            f"Tendencia: {self.tendencia}\n"
            f"Fecha/Hora: {self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    @property
    def mejor_compra(self) -> Optional[Punta]:
        """Retorna la mejor punta de compra (precio más alto)"""
        if not self.puntas:
            return None
        return max(self.puntas, key=lambda p: p.precio_compra)

    @property
    def mejor_venta(self) -> Optional[Punta]:
        """Retorna la mejor punta de venta (precio más bajo)"""
        if not self.puntas:
            return None
        return min(self.puntas, key=lambda p: p.precio_venta)

    @property
    def spread(self) -> Optional[float]:
        """Calcula el spread entre la mejor compra y venta"""
        mejor_compra = self.mejor_compra
        mejor_venta = self.mejor_venta

        if mejor_compra and mejor_venta:
            return mejor_venta.precio_venta - mejor_compra.precio_compra
        return None


@dataclass
class DatosTitulo:
    """Modelo para los datos básicos de un título"""

    simbolo: str
    descripcion: str
    pais: str
    mercado: str
    tipo: str
    plazo: str
    moneda: str

    @classmethod
    def from_dict(cls, data: dict) -> "DatosTitulo":
        """Crea una instancia de DatosTitulo desde un diccionario"""
        return cls(
            simbolo=data.get("simbolo", ""),
            descripcion=data.get("descripcion", ""),
            pais=data.get("pais", ""),
            mercado=data.get("mercado", ""),
            tipo=data.get("tipo", ""),
            plazo=data.get("plazo", ""),
            moneda=data.get("moneda", ""),
        )

    def __str__(self) -> str:
        """Representación string del objeto"""
        return (
            f"{self.descripcion} ({self.simbolo})\n"
            f"Mercado: {self.mercado} | País: {self.pais}\n"
            f"Tipo: {self.tipo} | Plazo: {self.plazo}\n"
            f"Moneda: {self.moneda}"
        )


@dataclass
class OpcionTitulo:
    """Modelo para una opción de un título"""

    cotizacion: Optional[CotizacionOpcion]
    simbolo_subyacente: str
    fecha_vencimiento: datetime
    tipo_opcion: str  # "Call" o "Put"
    simbolo: str
    descripcion: str
    pais: str
    mercado: str
    tipo: str
    plazo: str
    moneda: str

    @classmethod
    def from_dict(cls, data: dict) -> "OpcionTitulo":
        """Crea una instancia de OpcionTitulo desde un diccionario"""
        # Parsear la fecha de vencimiento
        fecha_vencimiento_str = data.get("fechaVencimiento", "")
        try:
            # Intentar parsear la fecha ISO
            fecha_vencimiento = datetime.fromisoformat(fecha_vencimiento_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            # Si no se puede parsear, usar datetime actual
            fecha_vencimiento = datetime.now()

        # Parsear la cotización anidada
        cotizacion_data = data.get("cotizacion", {})
        cotizacion = CotizacionOpcion.from_dict(cotizacion_data) if cotizacion_data else None

        return cls(
            cotizacion=cotizacion,
            simbolo_subyacente=data.get("simboloSubyacente", ""),
            fecha_vencimiento=fecha_vencimiento,
            tipo_opcion=data.get("tipoOpcion", ""),
            simbolo=data.get("simbolo", ""),
            descripcion=data.get("descripcion", ""),
            pais=data.get("pais", ""),
            mercado=data.get("mercado", ""),
            tipo=data.get("tipo", ""),
            plazo=data.get("plazo", ""),
            moneda=data.get("moneda", ""),
        )

    def __str__(self) -> str:
        """Representación string del objeto"""
        precio = self.cotizacion.ultimo_precio if self.cotizacion else 0
        variacion = self.cotizacion.variacion if self.cotizacion else 0
        return (
            f"{self.descripcion}\n"
            f"Símbolo: {self.simbolo} | Subyacente: {self.simbolo_subyacente}\n"
            f"Tipo: {self.tipo_opcion} | Vencimiento: {self.fecha_vencimiento.strftime('%d/%m/%Y')}\n"
            f"Precio: ${precio} | Variación: {variacion}%\n"
            f"Mercado: {self.mercado} | Moneda: {self.moneda}"
        )

    @property
    def dias_hasta_vencimiento(self) -> int:
        """Calcula los días hasta el vencimiento"""
        if self.fecha_vencimiento:
            delta = self.fecha_vencimiento - datetime.now()
            return max(0, delta.days)
        return 0

    @property
    def es_call(self) -> bool:
        """Retorna True si es una opción Call"""
        return self.tipo_opcion.lower() == "call"

    @property
    def es_put(self) -> bool:
        """Retorna True si es una opción Put"""
        return self.tipo_opcion.lower() == "put"

    @property
    def precio_strike(self) -> Optional[float]:
        """Extrae el precio strike de la descripción si es posible"""
        try:
            # Buscar el patrón de precio en la descripción (ej: "400.00")
            import re

            match = re.search(r"(\d+\.?\d*)", self.descripcion.replace(",", ""))
            if match:
                return float(match.group(1))
        except (ValueError, AttributeError):
            pass
        return None


@dataclass
class InstrumentoPais:
    """Modelo para los instrumentos de cotización disponibles por país"""

    instrumento: str
    pais: str

    @classmethod
    def from_dict(cls, data: dict) -> "InstrumentoPais":
        """Crea una instancia de InstrumentoPais desde un diccionario"""
        return cls(instrumento=data.get("instrumento", ""), pais=data.get("pais", ""))

    def __str__(self) -> str:
        """Representación string del objeto"""
        return f"Instrumento: {self.instrumento} | País: {self.pais}\n"


@dataclass
class PuntasCotizacion:
    """Modelo para las puntas de compra y venta de una cotización"""

    cantidad_compra: int
    precio_compra: float
    precio_venta: float
    cantidad_venta: int

    @classmethod
    def from_dict(cls, data) -> "PuntasCotizacion":
        """Crea una instancia de PuntasCotizacion desde un diccionario

        Maneja el caso cuando data es None o no es un diccionario.
        """
        if data is None or not isinstance(data, dict):
            return cls(cantidad_compra=0, precio_compra=0.0, precio_venta=0.0, cantidad_venta=0)
        return cls(
            cantidad_compra=_to_int(data.get("cantidadCompra")),
            precio_compra=_to_float(data.get("precioCompra")),
            precio_venta=_to_float(data.get("precioVenta")),
            cantidad_venta=_to_int(data.get("cantidadVenta")),
        )


@dataclass
class TituloCotizacion:
    """Modelo para un título en las cotizaciones masivas"""

    simbolo: str
    puntas: PuntasCotizacion
    ultimo_precio: float
    variacion_porcentual: float
    apertura: float
    maximo: float
    minimo: float
    ultimo_cierre: float
    volumen: int
    cantidad_operaciones: int
    fecha: datetime
    tipo_opcion: Optional[str]
    precio_ejercicio: Optional[float]
    fecha_vencimiento: Optional[datetime]
    mercado: str
    moneda: str
    descripcion: str
    plazo: str
    lamina_minima: int
    lote: int

    @classmethod
    def from_dict(cls, data: dict) -> "TituloCotizacion":
        """Crea una instancia de TituloCotizacion desde un diccionario"""
        # Parsear la fecha
        fecha_str = data.get("fecha", "")
        try:
            # Intentar parsear la fecha ISO
            fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            # Si no se puede parsear, usar datetime actual
            fecha = datetime.now()

        # Parsear fecha de vencimiento si existe
        fecha_vencimiento = None
        fecha_venc_str = data.get("fechaVencimiento")
        if fecha_venc_str:
            try:
                fecha_vencimiento = datetime.fromisoformat(fecha_venc_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        # Parsear las puntas
        puntas_data = data.get("puntas", {})
        puntas = PuntasCotizacion.from_dict(puntas_data)

        return cls(
            simbolo=data.get("simbolo", ""),
            puntas=puntas,
            ultimo_precio=_to_float(data.get("ultimoPrecio")),
            variacion_porcentual=_to_float(data.get("variacionPorcentual")),
            apertura=_to_float(data.get("apertura")),
            maximo=_to_float(data.get("maximo")),
            minimo=_to_float(data.get("minimo")),
            ultimo_cierre=_to_float(data.get("ultimoCierre")),
            volumen=_to_int(data.get("volumen")),
            cantidad_operaciones=_to_int(data.get("cantidadOperaciones")),
            fecha=fecha,
            tipo_opcion=data.get("tipoOpcion"),
            precio_ejercicio=_to_optional_float(data.get("precioEjercicio")),
            fecha_vencimiento=fecha_vencimiento,
            mercado=data.get("mercado", ""),
            moneda=data.get("moneda", ""),
            descripcion=data.get("descripcion", ""),
            plazo=data.get("plazo", ""),
            lamina_minima=_to_int(data.get("laminaMinima")),
            lote=_to_int(data.get("lote")),
        )

    def __str__(self) -> str:
        """Representación string del objeto"""
        return (
            f"{self.simbolo} - {self.descripcion}\n"
            f"Último precio: ${self.ultimo_precio} | Variación: {self.variacion_porcentual}%\n"
            f"Apertura: ${self.apertura} | Máximo: ${self.maximo} | Mínimo: ${self.minimo}\n"
            f"Compra: ${self.puntas.precio_compra} ({self.puntas.cantidad_compra}) | "
            f"Venta: ${self.puntas.precio_venta} ({self.puntas.cantidad_venta})\n"
            f"Volumen: {self.volumen:,} | Operaciones: {self.cantidad_operaciones}\n"
            f"Mercado: {self.mercado} | Moneda: {self.moneda} | Plazo: {self.plazo}"
        )


@dataclass
class CotizacionesMasivas:
    """Modelo para la respuesta de cotizaciones masivas"""

    titulos: List[TituloCotizacion]

    @classmethod
    def from_dict(cls, data) -> "CotizacionesMasivas":
        """Crea una instancia de CotizacionesMasivas desde un diccionario o lista

        La API puede devolver:
        - Un diccionario con clave 'titulos' que contiene la lista
        - Directamente una lista de títulos
        """
        # Si es None, devolver vacío
        if data is None:
            return cls(titulos=[])

        # Si es una lista, usarla directamente
        if isinstance(data, list):
            titulos_data = data
        # Si es un diccionario, buscar la clave 'titulos'
        elif isinstance(data, dict):
            titulos_data = data.get("titulos", [])
        else:
            titulos_data = []

        titulos = [TituloCotizacion.from_dict(titulo_data) for titulo_data in titulos_data]

        return cls(titulos=titulos)

    def __str__(self) -> str:
        """Representación string del objeto"""
        return f"Cotizaciones masivas: {len(self.titulos)} títulos"

    def get_by_symbol(self, simbolo: str) -> Optional[TituloCotizacion]:
        """Busca un título por su símbolo"""
        for titulo in self.titulos:
            if titulo.simbolo == simbolo:
                return titulo
        return None

    def filter_by_market(self, mercado: str) -> List[TituloCotizacion]:
        """Filtra títulos por mercado"""
        return [titulo for titulo in self.titulos if titulo.mercado == mercado]

    def sort_by_variation(self, ascending: bool = False):
        """Ordena títulos por variación porcentual"""
        return sorted(self.titulos, key=lambda t: t.variacion_porcentual, reverse=not ascending)

    def sort_by_volume(self, ascending: bool = False):
        """Ordena títulos por volumen"""
        return sorted(self.titulos, key=lambda t: t.volumen, reverse=not ascending)


@dataclass
class CotizacionDetallada:
    """Modelo para la cotización detallada de un título (endpoint CotizacionDetalle)"""

    ultimo_precio: float
    variacion: float
    apertura: float
    maximo: float
    minimo: float
    fecha_hora: datetime
    tendencia: str
    cierre_anterior: float
    monto_operado: int
    volumen_nominal: int
    precio_promedio: float
    moneda: str
    precio_ajuste: float
    intereses_abiertos: int
    puntas: List[Punta]
    cantidad_operaciones: int
    simbolo: str
    pais: str
    mercado: str
    tipo: str
    descripcion_titulo: str
    plazo: str
    lamina_minima: int
    lote: int
    cantidad_minima: int
    puntos_variacion: float

    @classmethod
    def from_dict(cls, data: dict) -> "CotizacionDetallada":
        """Crea una instancia de CotizacionDetallada desde un diccionario"""
        # Parsear la fecha
        fecha_hora_str = data.get("fechaHora", "")
        try:
            # Intentar parsear la fecha ISO con timezone
            fecha_hora = datetime.fromisoformat(fecha_hora_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            # Si no se puede parsear, usar datetime actual
            fecha_hora = datetime.now()

        # Parsear las puntas
        puntas_data = data.get("puntas", [])
        puntas = [Punta.from_dict(punta) for punta in puntas_data]

        return cls(
            ultimo_precio=_to_float(data.get("ultimoPrecio")),
            variacion=_to_float(data.get("variacion")),
            apertura=_to_float(data.get("apertura")),
            maximo=_to_float(data.get("maximo")),
            minimo=_to_float(data.get("minimo")),
            fecha_hora=fecha_hora,
            tendencia=data.get("tendencia", ""),
            cierre_anterior=_to_float(data.get("cierreAnterior")),
            monto_operado=_to_int(data.get("montoOperado")),
            volumen_nominal=_to_int(data.get("volumenNominal")),
            precio_promedio=_to_float(data.get("precioPromedio")),
            moneda=data.get("moneda", ""),
            precio_ajuste=_to_float(data.get("precioAjuste")),
            intereses_abiertos=_to_int(data.get("interesesAbiertos")),
            puntas=puntas,
            cantidad_operaciones=_to_int(data.get("cantidadOperaciones")),
            simbolo=data.get("simbolo", ""),
            pais=data.get("pais", ""),
            mercado=data.get("mercado", ""),
            tipo=data.get("tipo", ""),
            descripcion_titulo=data.get("descripcionTitulo", ""),
            plazo=data.get("plazo", ""),
            lamina_minima=_to_int(data.get("laminaMinima")),
            lote=_to_int(data.get("lote")),
            cantidad_minima=_to_int(data.get("cantidadMinima")),
            puntos_variacion=_to_float(data.get("puntosVariacion")),
        )

    def __str__(self) -> str:
        """Representación string del objeto"""
        return (
            f"{self.simbolo} - {self.descripcion_titulo}\n"
            f"Último precio: ${self.ultimo_precio} | Variación: {self.variacion}% ({self.puntos_variacion:+} pts)\n"
            f"Apertura: ${self.apertura} | Máximo: ${self.maximo} | Mínimo: ${self.minimo}\n"
            f"Tendencia: {self.tendencia} | Cierre anterior: ${self.cierre_anterior}\n"
            f"Monto operado: ${self.monto_operado:,} | Operaciones: {self.cantidad_operaciones}\n"
            f"Mercado: {self.mercado} | País: {self.pais} | Tipo: {self.tipo}\n"
            f"Moneda: {self.moneda} | Plazo: {self.plazo}\n"
            f"Fecha/Hora: {self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    @property
    def mejor_compra(self) -> Optional[Punta]:
        """Retorna la mejor punta de compra (precio más alto)"""
        if not self.puntas:
            return None
        return max(self.puntas, key=lambda p: p.precio_compra)

    @property
    def mejor_venta(self) -> Optional[Punta]:
        """Retorna la mejor punta de venta (precio más bajo)"""
        if not self.puntas:
            return None
        # Filtrar puntas con precio_venta > 0 para evitar precios inválidos
        puntas_validas = [p for p in self.puntas if p.precio_venta > 0]
        if not puntas_validas:
            return None
        return min(puntas_validas, key=lambda p: p.precio_venta)

    @property
    def spread(self) -> Optional[float]:
        """Calcula el spread entre la mejor compra y venta"""
        mejor_compra = self.mejor_compra
        mejor_venta = self.mejor_venta

        if mejor_compra and mejor_venta:
            return mejor_venta.precio_venta - mejor_compra.precio_compra
        return None

    @property
    def spread_porcentual(self) -> Optional[float]:
        """Calcula el spread porcentual respecto al precio actual"""
        spread = self.spread
        if spread and self.ultimo_precio > 0:
            return (spread / self.ultimo_precio) * 100
        return None

    @property
    def variacion_porcentual(self) -> float:
        """Retorna la variación como porcentaje"""
        return self.variacion

    @property
    def rendimiento_diario(self) -> float:
        """Calcula el rendimiento del día en porcentaje"""
        if self.cierre_anterior > 0:
            return ((self.ultimo_precio - self.cierre_anterior) / self.cierre_anterior) * 100
        return 0.0

    @property
    def total_puntas_compra(self) -> int:
        """Calcula la cantidad total en todas las puntas de compra"""
        return sum(punta.cantidad_compra for punta in self.puntas)

    @property
    def total_puntas_venta(self) -> int:
        """Calcula la cantidad total en todas las puntas de venta"""
        return sum(punta.cantidad_venta for punta in self.puntas)

    @property
    def profundidad_libro(self) -> int:
        """Retorna el número de niveles de puntas disponibles"""
        return len(self.puntas)


# =============================================================================
# MODELOS DE PERFIL DE USUARIO
# =============================================================================


@dataclass
class DatosPerfil:
    """
    Modelo para los datos del perfil del usuario.
    Representa la información personal y de cuenta del usuario en IOL.
    """

    nombre: str
    apellido: str
    numero_cuenta: str
    dni: str
    cuit_cuil: str
    sexo: str
    perfil_inversor: str  # "Conservador", "Moderado", "Agresivo"
    email: str
    cuenta_abierta: bool
    actualizar_ddjj: bool  # Debe actualizar declaración jurada
    actualizar_test_inversor: bool  # Debe actualizar test de inversor
    es_baja_arrepentimiento: bool
    actualizar_tyc: bool  # Debe actualizar términos y condiciones
    actualizar_tyc_app: bool  # Debe actualizar T&C de la app

    @classmethod
    def from_dict(cls, data: dict) -> "DatosPerfil":
        """Crea una instancia de DatosPerfil desde un diccionario"""
        return cls(
            nombre=data.get("nombre", ""),
            apellido=data.get("apellido", ""),
            numero_cuenta=data.get("numeroCuenta", ""),
            dni=data.get("dni", ""),
            cuit_cuil=data.get("cuitCuil", ""),
            sexo=data.get("sexo", ""),
            perfil_inversor=data.get("perfilInversor", ""),
            email=data.get("email", ""),
            cuenta_abierta=data.get("cuentaAbierta", False),
            actualizar_ddjj=data.get("actualizarDDJJ", False),
            actualizar_test_inversor=data.get("actualizarTestInversor", False),
            es_baja_arrepentimiento=data.get("esBajaArrepentimiento", False),
            actualizar_tyc=data.get("actualizarTyC", False),
            actualizar_tyc_app=data.get("actualizarTyCApp", False),
        )

    def __str__(self) -> str:
        return (
            f"{self.nombre} {self.apellido}\n"
            f"Cuenta: {self.numero_cuenta} | DNI: {self.dni}\n"
            f"CUIT/CUIL: {self.cuit_cuil} | Email: {self.email}\n"
            f"Perfil inversor: {self.perfil_inversor}"
        )

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del usuario"""
        return f"{self.nombre} {self.apellido}"

    @property
    def requiere_actualizacion(self) -> bool:
        """Retorna True si el usuario debe actualizar algún dato"""
        return (
            self.actualizar_ddjj
            or self.actualizar_test_inversor
            or self.actualizar_tyc
            or self.actualizar_tyc_app
        )


# =============================================================================
# MODELOS DE ESTADO DE CUENTA Y PORTAFOLIO
# =============================================================================


@dataclass
class Saldo:
    """Modelo para los saldos por plazo de liquidación"""

    liquidacion: str  # "inmediato", "hrs24", "hrs48", "hrs72", etc.
    saldo: float
    comprometido: float
    disponible: float
    disponible_operar: float

    @classmethod
    def from_dict(cls, data: dict) -> "Saldo":
        """Crea una instancia de Saldo desde un diccionario"""
        return cls(
            liquidacion=data.get("liquidacion", ""),
            saldo=_to_float(data.get("saldo")),
            comprometido=_to_float(data.get("comprometido")),
            disponible=_to_float(data.get("disponible")),
            disponible_operar=_to_float(data.get("disponibleOperar")),
        )

    def __str__(self) -> str:
        return f"{self.liquidacion}: ${self.disponible:,.2f} disponible"


@dataclass
class Cuenta:
    """Modelo para una cuenta del estado de cuenta"""

    numero: str
    tipo: str
    moneda: str
    disponible: float
    comprometido: float
    saldo: float
    titulos_valorizados: float  # Cambiado de titulo_valorizado a titulos_valorizados
    total: float
    margen_descubierto: float
    saldos: List["Saldo"]
    estado: str  # Estado de la cuenta (ej: "operable")

    @classmethod
    def from_dict(cls, data: dict) -> "Cuenta":
        """Crea una instancia de Cuenta desde un diccionario"""
        saldos_data = data.get("saldos", [])
        saldos = [Saldo.from_dict(s) for s in saldos_data] if saldos_data else []

        return cls(
            numero=data.get("numero", ""),
            tipo=data.get("tipo", ""),
            moneda=data.get("moneda", ""),
            disponible=_to_float(data.get("disponible")),
            comprometido=_to_float(data.get("comprometido")),
            saldo=_to_float(data.get("saldo")),
            titulos_valorizados=_to_float(
                data.get("titulosValorizados")
            ),  # Corregido nombre del campo
            total=_to_float(data.get("total")),
            margen_descubierto=_to_float(data.get("margenDescubierto")),
            saldos=saldos,
            estado=data.get("estado", ""),  # Nuevo campo
        )

    def __str__(self) -> str:
        return (
            f"Cuenta {self.numero} ({self.tipo}) - {self.moneda}\n"
            f"Saldo: ${self.saldo:,.2f} | Disponible: ${self.disponible:,.2f}\n"
            f"Títulos: ${self.titulos_valorizados:,.2f} | Total: ${self.total:,.2f}"
        )


@dataclass
class Estadistica:
    """Modelo para las estadísticas de operaciones del estado de cuenta"""

    descripcion: str  # "Anterior" o "Actual"
    cantidad: int  # Cantidad de operaciones
    volumen: float  # Volumen operado

    @classmethod
    def from_dict(cls, data: dict) -> "Estadistica":
        """Crea una instancia de Estadistica desde un diccionario"""
        return cls(
            descripcion=data.get("descripcion", ""),
            cantidad=_to_int(data.get("cantidad")),
            volumen=_to_float(data.get("volumen")),
        )

    def __str__(self) -> str:
        return f"{self.descripcion}: {self.cantidad} ops, ${self.volumen:,.2f}"


@dataclass
class EstadoCuenta:
    """Modelo para el estado de cuenta completo"""

    cuentas: List[Cuenta]
    total_en_pesos: float
    estadisticas: List[Estadistica]  # Estadísticas de operaciones

    @classmethod
    def from_dict(cls, data: dict) -> "EstadoCuenta":
        """Crea una instancia de EstadoCuenta desde un diccionario"""
        cuentas_data = data.get("cuentas", [])
        cuentas = [Cuenta.from_dict(c) for c in cuentas_data] if cuentas_data else []

        estadisticas_data = data.get("estadisticas", [])
        estadisticas = (
            [Estadistica.from_dict(e) for e in estadisticas_data] if estadisticas_data else []
        )

        return cls(
            cuentas=cuentas,
            total_en_pesos=_to_float(data.get("totalEnPesos")),
            estadisticas=estadisticas,
        )

    def __str__(self) -> str:
        return (
            f"Estado de Cuenta: {len(self.cuentas)} cuenta(s) | Total: ${self.total_en_pesos:,.2f}"
        )

    def get_cuenta_por_moneda(self, moneda: str) -> Optional[Cuenta]:
        """Busca una cuenta por moneda (pesos, dolares, etc.)"""
        for cuenta in self.cuentas:
            if cuenta.moneda.lower() == moneda.lower():
                return cuenta
        return None

    @property
    def cuenta_pesos(self) -> Optional[Cuenta]:
        """Retorna la cuenta en pesos si existe"""
        return self.get_cuenta_por_moneda("peso_Argentino")

    @property
    def cuenta_dolares(self) -> Optional[Cuenta]:
        """Retorna la cuenta en dólares si existe"""
        return self.get_cuenta_por_moneda("dolar_Estadounidense")


@dataclass
class TituloInfo:
    """Modelo para la información básica de un título (dentro de un activo del portafolio)"""

    simbolo: str
    descripcion: str
    pais: str
    mercado: str
    tipo: str
    plazo: str
    moneda: str

    @classmethod
    def from_dict(cls, data: dict) -> "TituloInfo":
        """Crea una instancia de TituloInfo desde un diccionario"""
        if data is None:
            data = {}
        return cls(
            simbolo=data.get("simbolo", ""),
            descripcion=data.get("descripcion", ""),
            pais=data.get("pais", ""),
            mercado=data.get("mercado", ""),
            tipo=data.get("tipo", ""),
            plazo=data.get("plazo", ""),
            moneda=data.get("moneda", ""),
        )


@dataclass
class TituloPortafolio:
    """Modelo para un activo en el portafolio (representa una posición)"""

    # Datos de la posición
    cantidad: int
    comprometido: int
    puntos_variacion: float
    variacion_diaria: float
    ultimo_precio: float
    ppc: float  # Precio Promedio de Compra
    ganancia_porcentaje: float
    ganancia_dinero: float
    valorizado: float
    parking: Optional[float]
    # Datos del título
    titulo: TituloInfo

    @classmethod
    def from_dict(cls, data: dict) -> "TituloPortafolio":
        """Crea una instancia de TituloPortafolio desde un diccionario"""
        titulo_data = data.get("titulo", {})
        titulo = TituloInfo.from_dict(titulo_data)

        return cls(
            cantidad=_to_int(data.get("cantidad")),
            comprometido=_to_int(data.get("comprometido")),
            puntos_variacion=_to_float(data.get("puntosVariacion")),
            variacion_diaria=_to_float(data.get("variacionDiaria")),
            ultimo_precio=_to_float(data.get("ultimoPrecio")),
            ppc=_to_float(data.get("ppc")),
            ganancia_porcentaje=_to_float(data.get("gananciaPorcentaje")),
            ganancia_dinero=_to_float(data.get("gananciaDinero")),
            valorizado=_to_float(data.get("valorizado")),
            parking=_to_optional_float(data.get("parking")),
            titulo=titulo,
        )

    def __str__(self) -> str:
        signo = "+" if self.ganancia_porcentaje >= 0 else ""
        return (
            f"{self.simbolo} - {self.titulo.descripcion}\n"
            f"Cantidad: {self.cantidad} | Precio: ${self.ultimo_precio:,.2f}\n"
            f"Valorizado: ${self.valorizado:,.2f} | "
            f"Ganancia: {signo}{self.ganancia_porcentaje:.2f}%"
        )

    @property
    def simbolo(self) -> str:
        """Atajo para obtener el símbolo del título"""
        return self.titulo.simbolo

    @property
    def descripcion(self) -> str:
        """Atajo para obtener la descripción del título"""
        return self.titulo.descripcion

    @property
    def tipo(self) -> str:
        """Atajo para obtener el tipo del título"""
        return self.titulo.tipo

    @property
    def mercado(self) -> str:
        """Atajo para obtener el mercado del título"""
        return self.titulo.mercado

    @property
    def moneda(self) -> str:
        """Atajo para obtener la moneda del título"""
        return self.titulo.moneda

    @property
    def cantidad_disponible(self) -> int:
        """Retorna la cantidad disponible (no comprometida)"""
        return self.cantidad - self.comprometido


# Mantener Activo como alias por compatibilidad hacia atrás
Activo = TituloPortafolio


@dataclass
class Portafolio:
    """Modelo para el portafolio completo"""

    pais: str
    activos: List[TituloPortafolio]  # Lista de posiciones (antes llamadas "activos" en la API)
    total_en_pesos: float

    @classmethod
    def from_dict(cls, data: dict, pais: str = "argentina") -> "Portafolio":
        """Crea una instancia de Portafolio desde un diccionario"""
        activos_data = data.get("activos", [])
        activos = [TituloPortafolio.from_dict(a) for a in activos_data] if activos_data else []

        # El país puede venir en el JSON o pasarse como parámetro
        pais_data = data.get("pais", pais)

        return cls(
            pais=pais_data, activos=activos, total_en_pesos=_to_float(data.get("totalEnPesos"))
        )

    def __str__(self) -> str:
        return f"Portafolio {self.pais}: {len(self.activos)} título(s) | Total: ${self.total_en_pesos:,.2f}"

    def get_titulo(self, simbolo: str) -> Optional[TituloPortafolio]:
        """Busca un título por símbolo en el portafolio"""
        for activo in self.activos:
            if activo.simbolo.upper() == simbolo.upper():
                return activo
        return None

    @property
    def todos_los_titulos(self) -> List[TituloPortafolio]:
        """Retorna todos los títulos del portafolio (alias de activos para compatibilidad)"""
        return self.activos

    def filtrar_por_tipo(self, tipo: str) -> List[TituloPortafolio]:
        """Filtra los títulos por tipo (ACCIONES, CEDEARS, etc.)"""
        return [a for a in self.activos if a.tipo.upper() == tipo.upper()]

    @property
    def total_valorizado(self) -> float:
        """Retorna el total valorizado del portafolio"""
        return sum(a.valorizado for a in self.activos)

    @property
    def total_ganancia(self) -> float:
        """Retorna la ganancia total en dinero del portafolio"""
        return sum(a.ganancia_dinero for a in self.activos)


@dataclass
class Operacion:
    """Modelo para una operación"""

    numero: int
    fecha_orden: datetime  # Corregido: fechaOrden en la API
    tipo: str  # "Compra", "Venta", "Pago de Dividendos"
    estado: str  # "pendiente", "terminada", "cancelada"
    mercado: str
    simbolo: str
    cantidad: Optional[int]
    cantidad_operada: Optional[int]
    precio: Optional[float]
    precio_operado: Optional[float]  # Nuevo: precio al que se ejecutó
    monto: Optional[float]
    monto_operado: Optional[float]  # Nuevo: monto total operado
    modalidad: str  # "precio_Limite", "precio_Mercado"
    plazo: str  # "a24horas", "inmediata", etc.
    validez: Optional[datetime]
    fecha_operada: Optional[datetime]  # Nuevo: fecha de ejecución

    @classmethod
    def from_dict(cls, data: dict) -> "Operacion":
        """Crea una instancia de Operacion desde un diccionario"""
        # Parsear fecha orden (API usa "fechaOrden", no "fechaOrdenado")
        fecha_orden_str = data.get("fechaOrden", data.get("fechaOrdenado", ""))
        try:
            fecha_orden = datetime.fromisoformat(fecha_orden_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            fecha_orden = datetime.now()

        # Parsear validez (puede ser null)
        validez = None
        validez_str = data.get("validez")
        if validez_str:
            try:
                validez = datetime.fromisoformat(validez_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        # Parsear fecha operada (puede ser null)
        fecha_operada = None
        fecha_operada_str = data.get("fechaOperada")
        if fecha_operada_str:
            try:
                fecha_operada = datetime.fromisoformat(fecha_operada_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return cls(
            numero=_to_int(data.get("numero")),
            fecha_orden=fecha_orden,
            tipo=data.get("tipo", ""),
            estado=data.get("estado", ""),
            mercado=data.get("mercado", ""),
            simbolo=data.get("simbolo", ""),
            cantidad=_to_optional_int(data.get("cantidad")),
            cantidad_operada=_to_optional_int(data.get("cantidadOperada")),
            precio=_to_optional_float(data.get("precio")),
            precio_operado=_to_optional_float(data.get("precioOperado")),
            monto=_to_optional_float(data.get("monto")),
            monto_operado=_to_optional_float(data.get("montoOperado")),
            modalidad=data.get("modalidad", ""),
            plazo=data.get("plazo", ""),
            validez=validez,
            fecha_operada=fecha_operada,
        )

    def __str__(self) -> str:
        precio_str = f"${self.precio:,.2f}" if self.precio is not None else "N/A"
        monto_str = f"${self.monto:,.2f}" if self.monto is not None else "N/A"
        cantidad_str = f"{self.cantidad_operada or 0}/{self.cantidad or 0}"
        return (
            f"Op #{self.numero} - {self.tipo} {self.simbolo}\n"
            f"Estado: {self.estado} | Cantidad: {cantidad_str}\n"
            f"Precio: {precio_str} | Monto: {monto_str}\n"
            f"Fecha: {self.fecha_orden.strftime('%Y-%m-%d %H:%M')}"
        )

    @property
    def esta_pendiente(self) -> bool:
        """Retorna True si la operación está pendiente"""
        return self.estado.lower() == "pendiente"

    @property
    def esta_terminada(self) -> bool:
        """Retorna True si la operación está terminada"""
        return self.estado.lower() == "terminada"

    @property
    def esta_cancelada(self) -> bool:
        """Retorna True si la operación está cancelada"""
        return self.estado.lower() == "cancelada"

    @property
    def porcentaje_ejecutado(self) -> float:
        """Retorna el porcentaje ejecutado de la operación"""
        if self.cantidad and self.cantidad > 0 and self.cantidad_operada is not None:
            return (self.cantidad_operada / self.cantidad) * 100
        return 0.0

    # Alias para compatibilidad hacia atrás
    @property
    def fecha_ordenado(self) -> datetime:
        """Alias para fecha_orden (compatibilidad hacia atrás)"""
        return self.fecha_orden


@dataclass
class OperacionDetalle(Operacion):
    """Modelo para el detalle completo de una operación (hereda de Operacion)"""

    precio_promedio: float = 0.0
    arancel: float = 0.0
    iva_arancel: float = 0.0
    derechos_mercado: float = 0.0
    iva_derechos_mercado: float = 0.0
    descripcion: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "OperacionDetalle":
        """Crea una instancia de OperacionDetalle desde un diccionario"""
        # Parsear fecha orden (API usa "fechaOrden")
        fecha_orden_str = data.get("fechaOrden", data.get("fechaOrdenado", ""))
        try:
            fecha_orden = datetime.fromisoformat(fecha_orden_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            fecha_orden = datetime.now()

        # Parsear validez (puede ser null)
        validez = None
        validez_str = data.get("validez")
        if validez_str:
            try:
                validez = datetime.fromisoformat(validez_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        # Parsear fecha operada (puede ser null)
        fecha_operada = None
        fecha_operada_str = data.get("fechaOperada")
        if fecha_operada_str:
            try:
                fecha_operada = datetime.fromisoformat(fecha_operada_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return cls(
            numero=_to_int(data.get("numero")),
            fecha_orden=fecha_orden,
            tipo=data.get("tipo", ""),
            estado=data.get("estado", ""),
            mercado=data.get("mercado", ""),
            simbolo=data.get("simbolo", ""),
            cantidad=_to_optional_int(data.get("cantidad")),
            cantidad_operada=_to_optional_int(data.get("cantidadOperada")),
            precio=_to_optional_float(data.get("precio")),
            precio_operado=_to_optional_float(data.get("precioOperado")),
            monto=_to_optional_float(data.get("monto")),
            monto_operado=_to_optional_float(data.get("montoOperado")),
            modalidad=data.get("modalidad", ""),
            plazo=data.get("plazo", ""),
            validez=validez,
            fecha_operada=fecha_operada,
            precio_promedio=_to_float(data.get("precioPromedio")),
            arancel=_to_float(data.get("arancel")),
            iva_arancel=_to_float(data.get("ivaArancel")),
            derechos_mercado=_to_float(data.get("derechosMercado")),
            iva_derechos_mercado=_to_float(data.get("ivaDerechosMercado")),
            descripcion=data.get("descripcion", ""),
        )

    def __str__(self) -> str:
        base = super().__str__()
        return (
            f"{base}\n"
            f"Precio promedio: ${self.precio_promedio:,.2f}\n"
            f"Arancel: ${self.arancel:,.2f} (IVA: ${self.iva_arancel:,.2f})\n"
            f"Derechos mercado: ${self.derechos_mercado:,.2f} (IVA: ${self.iva_derechos_mercado:,.2f})"
        )

    @property
    def costo_total(self) -> float:
        """Calcula el costo total de comisiones e impuestos"""
        return self.arancel + self.iva_arancel + self.derechos_mercado + self.iva_derechos_mercado


# =============================================================================
# MODELOS DE TRADING (COMPRA/VENTA)
# =============================================================================


@dataclass
class OrdenOperacion:
    """
    Modelo para una orden de compra o venta.
    Representa los datos necesarios para enviar una orden al mercado.
    """

    mercado: str  # Mercado (ej: "bCBA")
    simbolo: str  # Símbolo del título (ej: "GGAL")
    cantidad: int  # Cantidad de títulos a operar
    precio: float  # Precio límite de la operación
    plazo: str  # Plazo de liquidación (ej: "t2")
    validez: Optional[datetime] = None  # Fecha de validez de la orden

    def to_dict(self) -> dict:
        """Convierte la orden a un diccionario para enviar a la API"""
        data = {
            "mercado": self.mercado,
            "simbolo": self.simbolo,
            "cantidad": self.cantidad,
            "precio": self.precio,
            "plazo": self.plazo,
        }
        if self.validez:
            data["validez"] = self.validez.isoformat()
        return data

    def __str__(self) -> str:
        validez_str = f" (válida hasta {self.validez.strftime('%Y-%m-%d')})" if self.validez else ""
        return (
            f"Orden: {self.simbolo} x {self.cantidad} @ ${self.precio:,.2f}\n"
            f"Mercado: {self.mercado} | Plazo: {self.plazo}{validez_str}"
        )


@dataclass
class ResultadoOrden:
    """
    Modelo para el resultado de una orden de compra o venta.
    Contiene la información devuelta por la API tras enviar una orden.
    """

    numero_operacion: int  # Número de la operación asignado por IOL
    ok: bool  # Si la orden fue aceptada
    mensaje: Optional[str] = None  # Mensaje de la API (si hay)

    @classmethod
    def from_dict(cls, data: dict) -> "ResultadoOrden":
        """Crea una instancia de ResultadoOrden desde un diccionario"""
        # La API puede devolver diferentes formatos
        # Intentamos manejar los más comunes
        numero = _to_int(data.get("numeroOperacion") or data.get("numero"))
        ok = data.get("ok", True) if "ok" in data else (numero > 0)
        mensaje = data.get("mensaje", data.get("message", None))

        return cls(numero_operacion=numero, ok=ok, mensaje=mensaje)

    def __str__(self) -> str:
        estado = "ACEPTADA" if self.ok else "RECHAZADA"
        msg = f" - {self.mensaje}" if self.mensaje else ""
        return f"Orden {estado} - Número: {self.numero_operacion}{msg}"

    @property
    def exito(self) -> bool:
        """Alias para ok - indica si la operación fue exitosa"""
        return self.ok


# =============================================================================
# MODELOS DE CHEQUES DE PAGO DIFERIDO (CPD)
# =============================================================================


@dataclass
class PuedeOperarCPD:
    """
    Modelo para la respuesta de verificación de si el usuario puede operar CPD.
    Indica si el usuario tiene habilitada la operatoria de cheques de pago diferido.
    """

    puede_operar: bool  # Si puede operar CPD
    mensaje: Optional[str] = None  # Mensaje informativo
    motivo: Optional[str] = None  # Motivo si no puede operar
    requiere_habilitacion: bool = False  # Si necesita solicitar habilitación

    @classmethod
    def from_dict(cls, data: dict) -> "PuedeOperarCPD":
        """Crea una instancia de PuedeOperarCPD desde un diccionario"""
        puede = data.get("puedeOperar", data.get("habilitado", data.get("puede", False)))
        return cls(
            puede_operar=puede,
            mensaje=data.get("mensaje", data.get("message")),
            motivo=data.get("motivo", data.get("razon")),
            requiere_habilitacion=data.get("requiereHabilitacion", not puede),
        )

    def __str__(self) -> str:
        estado = "HABILITADO" if self.puede_operar else "NO HABILITADO"
        msg = f" - {self.mensaje}" if self.mensaje else ""
        return f"Operatoria CPD: {estado}{msg}"


@dataclass
class ChequeCPD:
    """
    Modelo para un Cheque de Pago Diferido disponible para operar.
    Representa la información de un cheque en el mercado.
    """

    numero_cheque: str  # Número único del cheque
    librador: str  # Nombre del librador
    cuit_librador: Optional[str] = None  # CUIT del librador
    fecha_pago: Optional[datetime] = None  # Fecha de pago del cheque
    fecha_vencimiento: Optional[datetime] = None  # Fecha de vencimiento
    importe: float = 0.0  # Importe nominal del cheque
    tasa: Optional[float] = None  # Tasa de descuento
    valor_presente: Optional[float] = None  # Valor presente del cheque
    plazo: int = 0  # Días hasta el vencimiento
    segmento: Optional[str] = None  # Segmento (avalado, patrocinado, etc.)
    estado: Optional[str] = None  # Estado del cheque
    entidad_avaladora: Optional[str] = None  # Entidad que avala (si aplica)
    calificacion: Optional[str] = None  # Calificación de riesgo
    moneda: str = "ARS"  # Moneda del cheque

    @classmethod
    def from_dict(cls, data: dict) -> "ChequeCPD":
        """Crea una instancia de ChequeCPD desde un diccionario"""
        # Parsear fecha de pago
        fecha_pago = None
        fecha_pago_str = data.get("fechaPago", data.get("fechaCobro"))
        if fecha_pago_str:
            try:
                fecha_pago = datetime.fromisoformat(fecha_pago_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        # Parsear fecha de vencimiento
        fecha_vencimiento = None
        fecha_venc_str = data.get("fechaVencimiento")
        if fecha_venc_str:
            try:
                fecha_vencimiento = datetime.fromisoformat(fecha_venc_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return cls(
            numero_cheque=data.get("numeroCheque", data.get("numero", "")),
            librador=data.get("librador", data.get("nombreLibrador", "")),
            cuit_librador=data.get("cuitLibrador", data.get("cuit")),
            fecha_pago=fecha_pago,
            fecha_vencimiento=fecha_vencimiento,
            importe=_to_float(data.get("importe") or data.get("monto")),
            tasa=_to_optional_float(data.get("tasa") or data.get("tasaDescuento")),
            valor_presente=_to_optional_float(
                data.get("valorPresente") or data.get("precioCompra")
            ),
            plazo=_to_int(data.get("plazo") or data.get("diasAlVencimiento")),
            segmento=data.get("segmento"),
            estado=data.get("estado"),
            entidad_avaladora=data.get("entidadAvaladora", data.get("avalista")),
            calificacion=data.get("calificacion"),
            moneda=data.get("moneda", "ARS"),
        )

    def __str__(self) -> str:
        fecha = self.fecha_pago.strftime("%d/%m/%Y") if self.fecha_pago else "N/A"
        tasa_str = f"{self.tasa:.2f}%" if self.tasa else "N/A"
        return (
            f"Cheque #{self.numero_cheque}\n"
            f"Librador: {self.librador}\n"
            f"Importe: ${self.importe:,.2f} | Valor presente: ${self.valor_presente or 0:,.2f}\n"
            f"Tasa: {tasa_str} | Plazo: {self.plazo} días\n"
            f"Fecha pago: {fecha} | Segmento: {self.segmento or 'N/A'}"
        )

    @property
    def descuento(self) -> Optional[float]:
        """Calcula el descuento aplicado al cheque"""
        if self.importe and self.valor_presente:
            return self.importe - self.valor_presente
        return None

    @property
    def descuento_porcentual(self) -> Optional[float]:
        """Calcula el descuento porcentual"""
        if self.importe and self.valor_presente and self.importe > 0:
            return ((self.importe - self.valor_presente) / self.importe) * 100
        return None

    @property
    def es_avalado(self) -> bool:
        """Retorna True si el cheque es avalado"""
        if self.segmento:
            return "avalado" in self.segmento.lower()
        return self.entidad_avaladora is not None


@dataclass
class ComisionesCPD:
    """
    Modelo para las comisiones de una operación con CPD.
    Detalla los costos de operar con un cheque de pago diferido.
    """

    comision: float  # Comisión del broker
    iva_comision: float  # IVA sobre la comisión
    derechos_mercado: float  # Derechos de mercado
    iva_derechos: float  # IVA sobre derechos
    arancel: Optional[float] = None  # Arancel adicional
    otros_gastos: Optional[float] = None  # Otros gastos
    total_gastos: float = 0.0  # Total de gastos
    monto_neto: Optional[float] = None  # Monto neto después de gastos
    importe: Optional[float] = None  # Importe original
    plazo: Optional[int] = None  # Plazo de la operación
    tasa: Optional[float] = None  # Tasa aplicada

    @classmethod
    def from_dict(cls, data: dict) -> "ComisionesCPD":
        """Crea una instancia de ComisionesCPD desde un diccionario"""
        comision = _to_float(_first_present(data, "comision", "comisiones"))
        iva_comision = _to_float(_first_present(data, "ivaComision", "iva"))
        derechos = _to_float(_first_present(data, "derechoMercado", "derechosMercado", "derechos"))
        iva_derechos = _to_float(
            _first_present(data, "ivaDerechoMercado", "ivaDerechosMercado", "ivaDerechos")
        )
        arancel = _to_optional_float(data.get("arancel"))
        otros = _to_optional_float(_first_present(data, "otrosGastos", "otros"))

        # Calcular total si no viene
        total = _to_optional_float(_first_present(data, "totalGastos", "total"))
        if total is None:
            total = comision + iva_comision + derechos + iva_derechos
            if arancel is not None:
                total += arancel
            if otros is not None:
                total += otros

        return cls(
            comision=comision,
            iva_comision=iva_comision,
            derechos_mercado=derechos,
            iva_derechos=iva_derechos,
            arancel=arancel,
            otros_gastos=otros,
            total_gastos=total,
            monto_neto=_to_optional_float(_first_present(data, "montoInversion", "montoNeto")),
            importe=_to_optional_float(data.get("importe")),
            plazo=_to_optional_int(data.get("plazo")),
            tasa=_to_optional_float(data.get("tasa")),
        )

    def __str__(self) -> str:
        return (
            f"Comisiones CPD\n"
            f"Comisión: ${self.comision:,.2f} (IVA: ${self.iva_comision:,.2f})\n"
            f"Derechos: ${self.derechos_mercado:,.2f} (IVA: ${self.iva_derechos:,.2f})\n"
            f"Total gastos: ${self.total_gastos:,.2f}"
        )

    @property
    def costo_total(self) -> float:
        """Alias para total_gastos"""
        return self.total_gastos


@dataclass
class OrdenCPD:
    """
    Modelo para una orden de compra de Cheque de Pago Diferido.
    Representa los datos necesarios para enviar una orden al mercado.
    """

    numero_cheque: str  # Número del cheque a comprar
    precio: float  # Precio de compra (valor presente)
    cantidad: int = 1  # Cantidad de cheques (normalmente 1)

    def to_dict(self) -> dict:
        """Convierte la orden a un diccionario para enviar a la API"""
        return {
            "numeroCheque": self.numero_cheque,
            "precio": self.precio,
            "cantidad": self.cantidad,
        }

    def __str__(self) -> str:
        return f"Orden CPD: Cheque #{self.numero_cheque} @ ${self.precio:,.2f}"


@dataclass
class ResultadoCPD:
    """
    Modelo para el resultado de una operación con CPD.
    Contiene la información devuelta tras comprar un cheque de pago diferido.
    """

    ok: bool  # Si la operación fue exitosa
    numero_operacion: Optional[int] = None  # Número de operación asignado
    mensaje: Optional[str] = None  # Mensaje de la API
    numero_cheque: Optional[str] = None  # Número del cheque operado
    importe: Optional[float] = None  # Importe del cheque
    precio: Optional[float] = None  # Precio de compra
    fecha_liquidacion: Optional[datetime] = None  # Fecha de liquidación

    @classmethod
    def from_dict(cls, data: dict) -> "ResultadoCPD":
        """Crea una instancia de ResultadoCPD desde un diccionario"""
        # Parsear fecha de liquidación
        fecha_liquidacion = None
        fecha_str = data.get("fechaLiquidacion")
        if fecha_str:
            try:
                fecha_liquidacion = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        numero = _to_int(data.get("numeroOperacion") or data.get("numero"))
        ok = data.get("ok", True) if "ok" in data else (numero > 0)

        return cls(
            ok=ok,
            numero_operacion=numero if numero > 0 else None,
            mensaje=data.get("mensaje", data.get("message")),
            numero_cheque=data.get("numeroCheque"),
            importe=_to_optional_float(data.get("importe")),
            precio=_to_optional_float(data.get("precio")),
            fecha_liquidacion=fecha_liquidacion,
        )

    def __str__(self) -> str:
        estado = "EXITOSA" if self.ok else "FALLIDA"
        num = f" (Op #{self.numero_operacion})" if self.numero_operacion else ""
        cheque = f" - Cheque #{self.numero_cheque}" if self.numero_cheque else ""
        msg = f" - {self.mensaje}" if self.mensaje else ""
        return f"Operación CPD {estado}{num}{cheque}{msg}"

    @property
    def exito(self) -> bool:
        """Alias para ok - indica si la operación fue exitosa"""
        return self.ok


@dataclass
class OrdenEspecieD:
    """
    Modelo para una orden de compra/venta de Especie D (bonos en dólares).
    Similar a OrdenOperacion pero específico para operaciones con bonos dolarizados.
    """

    mercado: str  # Mercado (ej: "bCBA")
    simbolo: str  # Símbolo del bono (ej: "AL30D", "GD30D")
    cantidad: int  # Cantidad de títulos a operar
    precio: float  # Precio límite de la operación
    plazo: str  # Plazo de liquidación (ej: "t2")
    validez: Optional[datetime] = None  # Fecha de validez de la orden

    def to_dict(self) -> dict:
        """Convierte la orden a un diccionario para enviar a la API"""
        data = {
            "mercado": self.mercado,
            "simbolo": self.simbolo,
            "cantidad": self.cantidad,
            "precio": self.precio,
            "plazo": self.plazo,
        }
        if self.validez:
            data["validez"] = self.validez.isoformat()
        return data

    def __str__(self) -> str:
        validez_str = f" (válida hasta {self.validez.strftime('%Y-%m-%d')})" if self.validez else ""
        return (
            f"Orden Especie D: {self.simbolo} x {self.cantidad} @ USD {self.precio:,.2f}\n"
            f"Mercado: {self.mercado} | Plazo: {self.plazo}{validez_str}"
        )


# =============================================================================
# MODELOS DE FONDOS COMUNES DE INVERSIÓN (FCI)
# =============================================================================


@dataclass
class TipoFondo:
    """Modelo para un tipo de fondo de inversión"""

    identificador: str  # Ej: "plazo_fijo_pesos", "renta_fija_pesos"
    nombre: str  # Ej: "Plazos Fijos Pesos", "Renta Fija Pesos"

    @classmethod
    def from_dict(cls, data: dict) -> "TipoFondo":
        """Crea una instancia de TipoFondo desde un diccionario"""
        return cls(
            identificador=data.get("identificador", ""),
            nombre=data.get("nombre", ""),
        )

    def __str__(self) -> str:
        return f"{self.nombre} ({self.identificador})"

    # Alias para compatibilidad hacia atrás
    @property
    def id(self) -> str:
        """Alias para identificador (compatibilidad hacia atrás)"""
        return self.identificador


@dataclass
class AdministradoraFCI:
    """Modelo para una administradora de Fondos Comunes de Inversión"""

    id: int
    nombre: str
    descripcion: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "AdministradoraFCI":
        """Crea una instancia de AdministradoraFCI desde un diccionario"""
        return cls(
            id=_to_int(data.get("id")),
            nombre=data.get("nombre", data.get("administradora", "")),
            descripcion=data.get("descripcion"),
        )

    def __str__(self) -> str:
        return f"{self.nombre} (ID: {self.id})"


@dataclass
class FondoComunInversion:
    """
    Modelo para un Fondo Común de Inversión (FCI).
    Representa la información completa de un FCI disponible para operar.
    """

    simbolo: str  # Símbolo del FCI (ej: "PRTAVAB")
    nombre: str  # Nombre completo del fondo (campo "descripcion" de la API)
    tipo_fondo: str  # Tipo de fondo (ej: "renta_variable_pesos", "renta_fija_dolares")
    moneda: str  # Moneda del fondo (ej: "peso_Argentino", "dolar_Estadounidense")
    # Campos opcionales
    horizonte: Optional[str] = (
        None  # Horizonte de inversión ("Corto Plazo", "Mediano Plazo", "Largo Plazo")
    )
    valor_cuotaparte: Optional[float] = None  # Último valor operado de la cuotaparte
    variacion_diaria: Optional[float] = None  # Variación diaria en %
    variacion_mensual: Optional[float] = None  # Variación mensual en %
    variacion_anual: Optional[float] = None  # Variación anual en %
    rescate: Optional[str] = None  # Plazo de rescate (ej: "t0", "t1", "t2")
    perfil_inversor: Optional[str] = (
        None  # Perfil de inversor ("Conservador", "Moderado", "Agresivo")
    )
    monto_minimo: Optional[float] = None  # Monto mínimo de suscripción
    invierte: Optional[str] = None  # Descripción de dónde invierte el fondo
    administradora: Optional[str] = None  # Tipo de administradora (ej: "supervielle", "convexity")
    aviso_horario_ejecucion: Optional[str] = None  # Aviso sobre horario de ejecución
    fecha_corte: Optional[str] = None  # Fecha de corte para operaciones
    codigo_bloomberg: Optional[str] = None  # Código Bloomberg del fondo
    informe_mensual: Optional[str] = None  # URL del informe mensual
    reglamento_gestion: Optional[str] = None  # URL del reglamento de gestión
    pais: Optional[str] = None  # País del fondo (ej: "argentina")
    mercado: Optional[str] = None  # Mercado (ej: "bcba")
    tipo: Optional[str] = None  # Tipo de instrumento (ej: "FondoComundeInversion")
    plazo: Optional[str] = None  # Plazo de liquidación (ej: "t0")
    # Campos legacy para compatibilidad
    patrimonio: Optional[float] = None  # Patrimonio total del fondo
    disponible_suscripcion: bool = True  # Si permite suscripción
    disponible_rescate: bool = True  # Si permite rescate

    @classmethod
    def from_dict(cls, data: dict) -> "FondoComunInversion":
        """Crea una instancia de FondoComunInversion desde un diccionario"""
        return cls(
            simbolo=data.get("simbolo", ""),
            nombre=data.get("descripcion", data.get("nombre", "")),
            tipo_fondo=data.get("tipoFondo", data.get("tipo", "")),
            moneda=data.get("moneda", ""),
            horizonte=data.get("horizonteInversion", data.get("horizonte")),
            valor_cuotaparte=_to_optional_float(
                data.get("ultimoOperado") or data.get("valorCuotaparte") or data.get("ultimoPrecio")
            ),
            variacion_diaria=_to_optional_float(
                data.get("variacion") or data.get("variacionDiaria")
            ),
            variacion_mensual=_to_optional_float(data.get("variacionMensual")),
            variacion_anual=_to_optional_float(data.get("variacionAnual")),
            rescate=data.get("rescate"),
            perfil_inversor=data.get("perfilInversor", data.get("perfilRiesgo")),
            monto_minimo=_to_optional_float(data.get("montoMinimo")),
            invierte=data.get("invierte"),
            administradora=data.get("tipoAdministradoraTituloFCI", data.get("administradora")),
            aviso_horario_ejecucion=data.get("avisoHorarioEjecucion"),
            fecha_corte=data.get("fechaCorte"),
            codigo_bloomberg=data.get("codigoBloomberg"),
            informe_mensual=data.get("informeMensual"),
            reglamento_gestion=data.get("reglamentoGestion"),
            pais=data.get("pais"),
            mercado=data.get("mercado"),
            tipo=data.get("tipo"),
            plazo=data.get("plazo"),
            patrimonio=_to_optional_float(data.get("patrimonio")),
            disponible_suscripcion=data.get("disponibleSuscripcion", True),
            disponible_rescate=data.get("disponibleRescate", True),
        )

    def __str__(self) -> str:
        valor = f"${self.valor_cuotaparte:,.4f}" if self.valor_cuotaparte else "N/A"
        variacion = f"{self.variacion_diaria:+.2f}%" if self.variacion_diaria is not None else "N/A"
        return (
            f"{self.simbolo} - {self.nombre}\n"
            f"Tipo: {self.tipo_fondo} | Administradora: {self.administradora or 'N/A'}\n"
            f"Valor cuotaparte: {valor} | Variación: {variacion}\n"
            f"Moneda: {self.moneda} | Rescate: {self.rescate or 'N/A'}"
        )

    @property
    def es_renta_fija(self) -> bool:
        """Retorna True si es un fondo de renta fija"""
        return "fija" in self.tipo_fondo.lower()

    @property
    def es_renta_variable(self) -> bool:
        """Retorna True si es un fondo de renta variable"""
        return "variable" in self.tipo_fondo.lower()

    @property
    def es_money_market(self) -> bool:
        """Retorna True si es un fondo money market o plazo fijo"""
        return "plazo_fijo" in self.tipo_fondo.lower() or "money" in self.tipo_fondo.lower()

    @property
    def es_en_dolares(self) -> bool:
        """Retorna True si el fondo es en dólares"""
        return "dolar" in self.moneda.lower() or "dolares" in self.tipo_fondo.lower()

    @property
    def rescate_en_t(self) -> Optional[int]:
        """Retorna los días de rescate como entero (para compatibilidad)"""
        if self.rescate:
            # Extraer número de "t0", "t1", "t2", etc.
            try:
                return int(self.rescate.replace("t", "").replace("T", ""))
            except ValueError:
                pass
        return None

    # Alias para compatibilidad hacia atrás
    @property
    def perfil_riesgo(self) -> Optional[str]:
        """Alias para perfil_inversor (compatibilidad hacia atrás)"""
        return self.perfil_inversor


@dataclass
class FCIDetalle(FondoComunInversion):
    """
    Modelo para el detalle completo de un FCI.
    Extiende FondoComunInversion con información adicional.
    """

    fecha_cotizacion: Optional[datetime] = None  # Fecha de la última cotización
    rendimiento_mes: Optional[float] = None  # Rendimiento del mes en %
    rendimiento_anio: Optional[float] = None  # Rendimiento del año en %
    rendimiento_12m: Optional[float] = None  # Rendimiento últimos 12 meses en %
    duracion: Optional[float] = None  # Duración (para renta fija)
    tir: Optional[float] = None  # TIR estimada
    gastos_administracion: Optional[float] = None  # Gastos de administración en %
    reglamento_url: Optional[str] = None  # URL del reglamento

    @classmethod
    def from_dict(cls, data: dict) -> "FCIDetalle":
        """Crea una instancia de FCIDetalle desde un diccionario"""
        # Parsear fecha de cotización
        fecha_cotizacion = None
        fecha_str = data.get("fechaCotizacion", data.get("fecha"))
        if fecha_str:
            try:
                fecha_cotizacion = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return cls(
            simbolo=data.get("simbolo", ""),
            nombre=data.get("descripcion", data.get("nombre", "")),
            tipo_fondo=data.get("tipoFondo", data.get("tipo", "")),
            moneda=data.get("moneda", ""),
            horizonte=data.get("horizonteInversion", data.get("horizonte")),
            valor_cuotaparte=_to_optional_float(
                data.get("ultimoOperado") or data.get("valorCuotaparte") or data.get("ultimoPrecio")
            ),
            variacion_diaria=_to_optional_float(
                data.get("variacion") or data.get("variacionDiaria")
            ),
            variacion_mensual=_to_optional_float(data.get("variacionMensual")),
            variacion_anual=_to_optional_float(data.get("variacionAnual")),
            rescate=data.get("rescate"),
            perfil_inversor=data.get("perfilInversor", data.get("perfilRiesgo")),
            monto_minimo=_to_optional_float(data.get("montoMinimo")),
            invierte=data.get("invierte"),
            administradora=data.get("tipoAdministradoraTituloFCI", data.get("administradora")),
            aviso_horario_ejecucion=data.get("avisoHorarioEjecucion"),
            fecha_corte=data.get("fechaCorte"),
            codigo_bloomberg=data.get("codigoBloomberg"),
            informe_mensual=data.get("informeMensual"),
            reglamento_gestion=data.get("reglamentoGestion"),
            pais=data.get("pais"),
            mercado=data.get("mercado"),
            tipo=data.get("tipo"),
            plazo=data.get("plazo"),
            patrimonio=_to_optional_float(data.get("patrimonio")),
            disponible_suscripcion=data.get("disponibleSuscripcion", True),
            disponible_rescate=data.get("disponibleRescate", True),
            fecha_cotizacion=fecha_cotizacion,
            rendimiento_mes=_to_optional_float(data.get("rendimientoMes")),
            rendimiento_anio=_to_optional_float(
                data.get("rendimientoAnio") or data.get("rendimientoAño")
            ),
            rendimiento_12m=_to_optional_float(
                data.get("rendimiento12m") or data.get("rendimiento12Meses")
            ),
            duracion=_to_optional_float(data.get("duracion")),
            tir=_to_optional_float(data.get("tir")),
            gastos_administracion=_to_optional_float(data.get("gastosAdministracion")),
            reglamento_url=data.get("reglamentoUrl"),
        )

    def __str__(self) -> str:
        base = super().__str__()
        rend_mes = f"{self.rendimiento_mes:+.2f}%" if self.rendimiento_mes else "N/A"
        rend_anio = f"{self.rendimiento_anio:+.2f}%" if self.rendimiento_anio else "N/A"
        return f"{base}\nRendimiento: Mes {rend_mes} | Año {rend_anio}"


@dataclass
class OrdenFCI:
    """
    Modelo para una orden de suscripción o rescate de FCI.
    Representa los datos necesarios para operar con un fondo.
    """

    simbolo: str  # Símbolo del FCI
    monto: Optional[float] = None  # Monto a suscribir (para suscripción)
    cantidad: Optional[float] = None  # Cantidad de cuotapartes (para rescate)
    solo_validar: bool = False  # Si es True, solo valida sin ejecutar

    def to_dict(self) -> dict:
        """Convierte la orden a un diccionario para enviar a la API"""
        data = {"simbolo": self.simbolo}

        if self.monto is not None:
            data["monto"] = self.monto
        if self.cantidad is not None:
            data["cantidad"] = self.cantidad
        if self.solo_validar:
            data["soloValidar"] = self.solo_validar

        return data

    def __str__(self) -> str:
        if self.monto:
            return f"Orden FCI: Suscribir ${self.monto:,.2f} en {self.simbolo}"
        elif self.cantidad:
            return f"Orden FCI: Rescatar {self.cantidad:,.4f} cuotapartes de {self.simbolo}"
        return f"Orden FCI: {self.simbolo}"


@dataclass
class ResultadoFCI:
    """
    Modelo para el resultado de una operación con FCI.
    Contiene la información devuelta por la API tras suscribir o rescatar.
    """

    ok: bool  # Si la operación fue exitosa
    numero_operacion: Optional[int] = None  # Número de operación asignado
    mensaje: Optional[str] = None  # Mensaje de la API
    cuotapartes_estimadas: Optional[float] = None  # Cuotapartes estimadas (suscripción)
    monto_estimado: Optional[float] = None  # Monto estimado (rescate)
    fecha_liquidacion: Optional[datetime] = None  # Fecha estimada de liquidación

    @classmethod
    def from_dict(cls, data: dict) -> "ResultadoFCI":
        """Crea una instancia de ResultadoFCI desde un diccionario"""
        # Parsear fecha de liquidación
        fecha_liquidacion = None
        fecha_str = data.get("fechaLiquidacion")
        if fecha_str:
            try:
                fecha_liquidacion = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        numero = _to_int(data.get("numeroOperacion") or data.get("numero"))
        ok = data.get("ok", True) if "ok" in data else (numero > 0)

        return cls(
            ok=ok,
            numero_operacion=numero if numero > 0 else None,
            mensaje=data.get("mensaje", data.get("message")),
            cuotapartes_estimadas=_to_optional_float(data.get("cuotapartesEstimadas")),
            monto_estimado=_to_optional_float(data.get("montoEstimado")),
            fecha_liquidacion=fecha_liquidacion,
        )

    def __str__(self) -> str:
        estado = "EXITOSA" if self.ok else "FALLIDA"
        num = f" (Op #{self.numero_operacion})" if self.numero_operacion else ""
        msg = f" - {self.mensaje}" if self.mensaje else ""
        return f"Operación FCI {estado}{num}{msg}"

    @property
    def exito(self) -> bool:
        """Alias para ok - indica si la operación fue exitosa"""
        return self.ok


# =============================================================================
# MODELOS DE DÓLAR MEP SIMPLIFICADO
# =============================================================================


@dataclass
class EstimacionMEP:
    """
    Modelo para la estimación de una operación de dólar MEP.
    Contiene los montos estimados para compra o venta de dólar MEP.
    """

    monto_pesos: float  # Monto en pesos a debitar/acreditar
    monto_dolares: float  # Monto en dólares a acreditar/debitar
    tipo_cambio: float  # Tipo de cambio MEP estimado
    comision: Optional[float] = None  # Comisión estimada
    impuestos: Optional[float] = None  # Impuestos estimados
    costo_total: Optional[float] = None  # Costo total de la operación
    titulo_utilizado: Optional[str] = None  # Bono usado para la operación (ej: AL30)
    cantidad_titulos: Optional[int] = None  # Cantidad de títulos a operar
    precio_compra: Optional[float] = None  # Precio de compra del bono
    precio_venta: Optional[float] = None  # Precio de venta del bono

    @classmethod
    def from_dict(cls, data: dict) -> "EstimacionMEP":
        """Crea una instancia de EstimacionMEP desde un diccionario"""
        # Payloads reales (v0.1.x):
        #  - compra:  montoDolar, montoBrutoPesos, montoNetoPesos,
        #             comisionCompra, comisionCompraIVA, derechoMercadoCompra
        #  - venta:   montoPesos, montoBrutoDolar, montoNetoDolar,
        #             comisionVenta, comisionVentaIVA, derechoMercadoVenta
        es_compra = "montoPesos" not in data
        monto_pesos = _to_float(
            _first_present(data, "montoPesos", "montoBrutoPesos", "montoEnPesos")
        )
        monto_dolares = _to_float(
            _first_present(data, "montoDolar", "montoBrutoDolar", "montoDolares", "montoEnDolares")
        )
        # La API no devuelve el tipo de cambio en este endpoint: se deriva de
        # pesos/dólares (mismo criterio que tipo_cambio_efectivo).
        tipo_cambio = _to_optional_float(_first_present(data, "tipoCambio", "cotizacionMep"))
        if tipo_cambio is None and monto_dolares > 0:
            tipo_cambio = monto_pesos / monto_dolares
        if es_compra:
            comision = _to_optional_float(
                _first_present(data, "comisionCompra", "comision", "comisiones")
            )
            iva = _to_optional_float(_first_present(data, "comisionCompraIVA", "ivaComision"))
            derechos = _to_optional_float(
                _first_present(data, "derechoMercadoCompra", "derechoMercado")
            )
            costo_total = _to_optional_float(
                _first_present(data, "montoNetoPesos", "costoTotal", "total")
            )
        else:
            comision = _to_optional_float(
                _first_present(data, "comisionVenta", "comision", "comisiones")
            )
            iva = _to_optional_float(_first_present(data, "comisionVentaIVA", "ivaComision"))
            derechos = _to_optional_float(
                _first_present(data, "derechoMercadoVenta", "derechoMercado")
            )
            costo_total = _to_optional_float(
                _first_present(data, "montoPesos", "costoTotal", "total")
            )
        impuestos = None
        if iva is not None or derechos is not None:
            impuestos = (iva or 0.0) + (derechos or 0.0)
        return cls(
            monto_pesos=monto_pesos,
            monto_dolares=monto_dolares,
            tipo_cambio=tipo_cambio or 0.0,
            comision=comision,
            impuestos=impuestos,
            costo_total=costo_total,
            titulo_utilizado=data.get("tituloUtilizado", data.get("simbolo")),
            cantidad_titulos=_to_optional_int(data.get("cantidadTitulos") or data.get("cantidad")),
            precio_compra=_to_optional_float(data.get("precioCompra")),
            precio_venta=_to_optional_float(data.get("precioVenta")),
        )

    def __str__(self) -> str:
        return (
            f"Estimación MEP\n"
            f"Pesos: ${self.monto_pesos:,.2f} | Dólares: USD {self.monto_dolares:,.2f}\n"
            f"Tipo de cambio: ${self.tipo_cambio:,.2f}\n"
            f"Título: {self.titulo_utilizado or 'N/A'}"
        )

    @property
    def tipo_cambio_efectivo(self) -> float:
        """Calcula el tipo de cambio efectivo incluyendo costos"""
        if self.monto_dolares and self.monto_dolares > 0:
            return self.monto_pesos / self.monto_dolares
        return self.tipo_cambio


@dataclass
class ParametrosMEP:
    """
    Modelo para los parámetros de operatoria MEP simplificada.
    Contiene la configuración y límites para operar dólar MEP.
    """

    id_tipo_operatoria: str  # ID del tipo de operatoria (ej: "mep")
    nombre: str  # Nombre de la operatoria
    descripcion: Optional[str] = None  # Descripción
    monto_minimo: Optional[float] = None  # Monto mínimo en pesos
    monto_maximo: Optional[float] = None  # Monto máximo en pesos
    horario_inicio: Optional[str] = None  # Hora de inicio de operaciones
    horario_fin: Optional[str] = None  # Hora de fin de operaciones
    disponible: bool = True  # Si está disponible para operar
    titulo_default: Optional[str] = None  # Título por defecto (ej: AL30)
    plazo: Optional[int] = None  # Plazo de liquidación

    @classmethod
    def from_dict(cls, data: dict) -> "ParametrosMEP":
        """Crea una instancia de ParametrosMEP desde un diccionario"""
        # Payload real (v0.1.x): idTipoOperacion, montoLimiteMinimo/Maximo,
        # esHorarioValido, horarioApertura/Cierre, simboloTituloCompra/Venta,
        # idPlazoOperatoriaCompra/Venta
        id_tipo = _first_present(data, "idTipoOperacion", "idTipoOperatoria", "id")
        return cls(
            id_tipo_operatoria=str(id_tipo) if id_tipo is not None else "",
            nombre=data.get("nombre", ""),
            descripcion=data.get("descripcion"),
            monto_minimo=_to_optional_float(
                _first_present(data, "montoLimiteMinimo", "montoMinimo")
            ),
            monto_maximo=_to_optional_float(
                _first_present(data, "montoLimiteMaximo", "montoMaximo")
            ),
            horario_inicio=_first_present(data, "horarioApertura", "horarioInicio", "horaInicio"),
            horario_fin=_first_present(data, "horarioCierre", "horarioFin", "horaFin"),
            disponible=data.get(
                "esHorarioValido", data.get("disponible", data.get("habilitado", True))
            ),
            titulo_default=_first_present(data, "simboloTituloCompra", "tituloDefault", "simbolo"),
            plazo=_to_optional_int(
                _first_present(data, "idPlazoOperatoriaCompra", "idPlazoOperatoriaVenta", "plazo")
            ),
        )

    def __str__(self) -> str:
        estado = "Disponible" if self.disponible else "No disponible"
        horario = ""
        if self.horario_inicio and self.horario_fin:
            horario = f" ({self.horario_inicio} - {self.horario_fin})"
        return (
            f"{self.nombre} (ID: {self.id_tipo_operatoria})\n"
            f"Estado: {estado}{horario}\n"
            f"Monto: ${self.monto_minimo or 0:,.0f} - ${self.monto_maximo or 0:,.0f}"
        )


@dataclass
class ValidacionMEP:
    """
    Modelo para el resultado de validación de una operación MEP.
    Indica si la operación puede ejecutarse y cualquier mensaje de error.
    """

    valido: bool  # Si la operación es válida
    mensaje: Optional[str] = None  # Mensaje de validación
    monto_ajustado: Optional[float] = None  # Monto ajustado si hubo corrección
    error_codigo: Optional[str] = None  # Código de error si no es válida

    @classmethod
    def from_dict(cls, data: dict) -> "ValidacionMEP":
        """Crea una instancia de ValidacionMEP desde un diccionario"""
        valido = data.get("valido", data.get("ok", data.get("esValido", True)))
        mensaje = data.get("mensaje", data.get("message"))
        if not mensaje:
            # Payload real (v0.1.x): {"ok": false, "messages": [{"title", "description"}]}
            textos = [
                (m.get("description") or m.get("title") or "").strip()
                for m in (data.get("messages") or [])
                if isinstance(m, dict)
            ]
            mensaje = "; ".join(t for t in textos if t) or None
        return cls(
            valido=valido,
            mensaje=mensaje,
            monto_ajustado=_to_optional_float(data.get("montoAjustado")),
            error_codigo=data.get("errorCodigo", data.get("codigoError")),
        )

    def __str__(self) -> str:
        estado = "VÁLIDA" if self.valido else "INVÁLIDA"
        msg = f" - {self.mensaje}" if self.mensaje else ""
        return f"Validación MEP: {estado}{msg}"

    @property
    def es_valida(self) -> bool:
        """Alias para valido"""
        return self.valido


@dataclass
class ResultadoMEP:
    """
    Modelo para el resultado de una operación de dólar MEP simplificado.
    Contiene la información devuelta tras ejecutar la compra/venta de MEP.
    """

    ok: bool  # Si la operación fue exitosa
    numero_operacion: Optional[int] = None  # Número de operación principal
    numero_operacion_compra: Optional[int] = None  # Número de operación de compra
    numero_operacion_venta: Optional[int] = None  # Número de operación de venta
    mensaje: Optional[str] = None  # Mensaje de la API
    monto_pesos: Optional[float] = None  # Monto en pesos operado
    monto_dolares: Optional[float] = None  # Monto en dólares operado
    tipo_cambio: Optional[float] = None  # Tipo de cambio obtenido
    fecha_liquidacion: Optional[datetime] = None  # Fecha estimada de liquidación

    @classmethod
    def from_dict(cls, data: dict) -> "ResultadoMEP":
        """Crea una instancia de ResultadoMEP desde un diccionario"""
        # Parsear fecha de liquidación
        fecha_liquidacion = None
        fecha_str = data.get("fechaLiquidacion")
        if fecha_str:
            try:
                fecha_liquidacion = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        numero = _to_int(data.get("numeroOperacion") or data.get("numero"))
        ok = data.get("ok", True) if "ok" in data else (numero > 0)

        return cls(
            ok=ok,
            numero_operacion=numero if numero > 0 else None,
            numero_operacion_compra=_to_optional_int(data.get("numeroOperacionCompra")),
            numero_operacion_venta=_to_optional_int(data.get("numeroOperacionVenta")),
            mensaje=data.get("mensaje", data.get("message")),
            monto_pesos=_to_optional_float(data.get("montoPesos") or data.get("montoEnPesos")),
            monto_dolares=_to_optional_float(
                data.get("montoDolares") or data.get("montoEnDolares")
            ),
            tipo_cambio=_to_optional_float(data.get("tipoCambio") or data.get("cotizacionMep")),
            fecha_liquidacion=fecha_liquidacion,
        )

    def __str__(self) -> str:
        estado = "EXITOSA" if self.ok else "FALLIDA"
        ops = []
        if self.numero_operacion:
            ops.append(f"Op #{self.numero_operacion}")
        if self.numero_operacion_compra:
            ops.append(f"Compra #{self.numero_operacion_compra}")
        if self.numero_operacion_venta:
            ops.append(f"Venta #{self.numero_operacion_venta}")
        ops_str = f" ({', '.join(ops)})" if ops else ""
        msg = f" - {self.mensaje}" if self.mensaje else ""
        return f"Operación MEP {estado}{ops_str}{msg}"

    @property
    def exito(self) -> bool:
        """Alias para ok - indica si la operación fue exitosa"""
        return self.ok


# =============================================================================
# MODELOS DE ASESORES
# =============================================================================


@dataclass
class MovimientoCliente:
    """
    Modelo para un movimiento de cliente en la cuenta de un asesorado.
    Representa operaciones históricas de un cliente del asesor.
    """

    fecha: Optional[datetime] = None  # Fecha del movimiento
    tipo_movimiento: str = ""  # Tipo de movimiento
    descripcion: str = ""  # Descripción del movimiento
    simbolo: Optional[str] = None  # Símbolo del título (si aplica)
    cantidad: Optional[int] = None  # Cantidad de títulos
    precio: Optional[float] = None  # Precio unitario
    monto: float = 0.0  # Monto total del movimiento
    moneda: str = "ARS"  # Moneda del movimiento
    saldo: Optional[float] = None  # Saldo después del movimiento
    numero_operacion: Optional[int] = None  # Número de operación (si aplica)
    id_cliente: Optional[str] = None  # ID del cliente asesorado
    nombre_cliente: Optional[str] = None  # Nombre del cliente

    @classmethod
    def from_dict(cls, data: dict) -> "MovimientoCliente":
        """Crea una instancia de MovimientoCliente desde un diccionario"""
        # Parsear fecha
        fecha = None
        fecha_str = data.get("fecha", data.get("fechaMovimiento"))
        if fecha_str:
            try:
                fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return cls(
            fecha=fecha,
            tipo_movimiento=data.get("tipoMovimiento", data.get("tipo", "")),
            descripcion=data.get("descripcion", ""),
            simbolo=data.get("simbolo"),
            cantidad=_to_optional_int(data.get("cantidad")),
            precio=_to_optional_float(data.get("precio")),
            monto=_to_float(data.get("monto") or data.get("importe")),
            moneda=data.get("moneda", "ARS"),
            saldo=_to_optional_float(data.get("saldo") or data.get("saldoFinal")),
            numero_operacion=_to_optional_int(data.get("numeroOperacion") or data.get("numero")),
            id_cliente=data.get("idCliente", data.get("idClienteAsesorado")),
            nombre_cliente=data.get("nombreCliente", data.get("cliente")),
        )

    def __str__(self) -> str:
        fecha_str = self.fecha.strftime("%d/%m/%Y") if self.fecha else "N/A"
        simbolo = f" - {self.simbolo}" if self.simbolo else ""
        return (
            f"{fecha_str}: {self.tipo_movimiento}{simbolo}\n"
            f"Monto: ${self.monto:,.2f} {self.moneda}\n"
            f"{self.descripcion}"
        )


@dataclass
class MovimientosAsesor:
    """
    Modelo para la respuesta de movimientos históricos de clientes del asesor.
    Contiene una lista de movimientos con información de paginación.
    """

    movimientos: List[MovimientoCliente]
    total_registros: int = 0
    pagina_actual: int = 1
    registros_por_pagina: int = 50

    @classmethod
    def from_dict(cls, data: dict) -> "MovimientosAsesor":
        """Crea una instancia de MovimientosAsesor desde un diccionario"""
        movimientos_data = data.get("movimientos", data.get("items", []))
        if isinstance(data, list):
            movimientos_data = data

        movimientos = [MovimientoCliente.from_dict(m) for m in movimientos_data]

        return cls(
            movimientos=movimientos,
            total_registros=_to_int(
                data.get("totalRegistros") or data.get("total") or len(movimientos)
            ),
            pagina_actual=_to_int(data.get("paginaActual") or data.get("pagina")),
            registros_por_pagina=_to_int(data.get("registrosPorPagina") or data.get("porPagina")),
        )

    def __str__(self) -> str:
        return f"Movimientos Asesor: {len(self.movimientos)} de {self.total_registros} registros"


@dataclass
class OpcionRespuesta:
    """Modelo para una opción de respuesta en una pregunta del test de inversor"""

    id: int
    texto: str
    valor: Optional[int] = None  # Valor/puntaje de la opción

    @classmethod
    def from_dict(cls, data: dict) -> "OpcionRespuesta":
        """Crea una instancia de OpcionRespuesta desde un diccionario"""
        return cls(
            id=_to_int(data.get("id")),
            texto=data.get("texto", data.get("descripcion", "")),
            valor=_to_optional_int(data.get("valor") or data.get("puntaje")),
        )

    def __str__(self) -> str:
        return f"  [{self.id}] {self.texto}"


@dataclass
class PreguntaTestInversor:
    """
    Modelo para una pregunta del test de perfil de inversor.
    Contiene la pregunta y sus opciones de respuesta.
    """

    id: int
    numero: int
    texto: str
    categoria: Optional[str] = None
    opciones: Optional[List[OpcionRespuesta]] = None

    @classmethod
    def from_dict(cls, data: dict) -> "PreguntaTestInversor":
        """Crea una instancia de PreguntaTestInversor desde un diccionario"""
        opciones_data = data.get("opciones", data.get("respuestas", []))
        opciones = [OpcionRespuesta.from_dict(o) for o in opciones_data] if opciones_data else None

        return cls(
            id=_to_int(data.get("id")),
            numero=_to_int(data.get("numero") or data.get("orden")),
            texto=data.get("texto", data.get("pregunta", "")),
            categoria=data.get("categoria", data.get("seccion")),
            opciones=opciones,
        )

    def __str__(self) -> str:
        opciones_str = ""
        if self.opciones:
            opciones_str = "\n" + "\n".join(str(o) for o in self.opciones)
        return f"Pregunta {self.numero}: {self.texto}{opciones_str}"


@dataclass
class TestInversor:
    """
    Modelo para el test completo de perfil de inversor.
    Contiene todas las preguntas necesarias para calcular el perfil.
    """

    preguntas: List[PreguntaTestInversor]
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    cantidad_preguntas: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "TestInversor":
        """Crea una instancia de TestInversor desde un diccionario"""
        preguntas_data = data.get("preguntas", data.get("items", []))
        if isinstance(data, list):
            preguntas_data = data

        preguntas = [PreguntaTestInversor.from_dict(p) for p in preguntas_data]

        return cls(
            preguntas=preguntas,
            titulo=data.get("titulo"),
            descripcion=data.get("descripcion"),
            cantidad_preguntas=_to_int(data.get("cantidadPreguntas") or len(preguntas)),
        )

    def __str__(self) -> str:
        titulo = self.titulo or "Test de Perfil de Inversor"
        return f"{titulo}: {len(self.preguntas)} preguntas"

    def get_pregunta(self, numero: int) -> Optional[PreguntaTestInversor]:
        """Busca una pregunta por su número"""
        for pregunta in self.preguntas:
            if pregunta.numero == numero:
                return pregunta
        return None


@dataclass
class RespuestaTest:
    """
    Modelo para una respuesta al test de inversor.
    Representa la respuesta seleccionada para una pregunta.
    """

    id_pregunta: int
    id_respuesta: int

    def to_dict(self) -> dict:
        """Convierte la respuesta a un diccionario para enviar a la API"""
        return {"idPregunta": self.id_pregunta, "idRespuesta": self.id_respuesta}


@dataclass
class PerfilInversor:
    """
    Modelo para el resultado del cálculo del perfil de inversor.
    Contiene el perfil calculado basado en las respuestas al test.
    """

    perfil: str  # Perfil calculado (ej: "Conservador", "Moderado", "Agresivo")
    descripcion: Optional[str] = None  # Descripción del perfil
    puntaje: Optional[int] = None  # Puntaje obtenido
    puntaje_maximo: Optional[int] = None  # Puntaje máximo posible
    recomendaciones: Optional[List[str]] = None  # Lista de recomendaciones
    guardado: bool = False  # Si el perfil fue guardado
    id_cliente: Optional[str] = None  # ID del cliente (si se guardó)
    fecha_calculo: Optional[datetime] = None  # Fecha del cálculo

    @classmethod
    def from_dict(cls, data: dict) -> "PerfilInversor":
        """Crea una instancia de PerfilInversor desde un diccionario"""
        # Parsear fecha
        fecha_calculo = None
        fecha_str = data.get("fechaCalculo", data.get("fecha"))
        if fecha_str:
            try:
                fecha_calculo = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        recomendaciones = data.get("recomendaciones", [])
        if isinstance(recomendaciones, str):
            recomendaciones = [recomendaciones]

        return cls(
            perfil=data.get("perfil", data.get("perfilInversor", "")),
            descripcion=data.get("descripcion", data.get("descripcionPerfil")),
            puntaje=_to_optional_int(data.get("puntaje") or data.get("puntos")),
            puntaje_maximo=_to_optional_int(data.get("puntajeMaximo") or data.get("puntosMaximos")),
            recomendaciones=recomendaciones if recomendaciones else None,
            guardado=data.get("guardado", False),
            id_cliente=data.get("idCliente", data.get("idClienteAsesorado")),
            fecha_calculo=fecha_calculo,
        )

    def __str__(self) -> str:
        puntaje_str = f" ({self.puntaje}/{self.puntaje_maximo})" if self.puntaje else ""
        guardado_str = " [GUARDADO]" if self.guardado else ""
        return f"Perfil: {self.perfil}{puntaje_str}{guardado_str}"

    @property
    def es_conservador(self) -> bool:
        """Retorna True si el perfil es conservador"""
        return "conservador" in self.perfil.lower()

    @property
    def es_moderado(self) -> bool:
        """Retorna True si el perfil es moderado"""
        return "moderado" in self.perfil.lower()

    @property
    def es_agresivo(self) -> bool:
        """Retorna True si el perfil es agresivo"""
        return "agresivo" in self.perfil.lower() or "arriesgado" in self.perfil.lower()


@dataclass
class ResultadoOperacionAsesor:
    """
    Modelo para el resultado de una operación ejecutada como asesor.
    Similar a ResultadoOrden pero específico para operaciones de asesores.
    """

    ok: bool  # Si la operación fue exitosa
    numero_operacion: Optional[int] = None  # Número de operación asignado
    mensaje: Optional[str] = None  # Mensaje de la API
    id_cliente: Optional[str] = None  # ID del cliente asesorado
    simbolo: Optional[str] = None  # Símbolo operado
    cantidad: Optional[int] = None  # Cantidad operada
    precio: Optional[float] = None  # Precio de la operación

    @classmethod
    def from_dict(cls, data: dict) -> "ResultadoOperacionAsesor":
        """Crea una instancia de ResultadoOperacionAsesor desde un diccionario"""
        numero = _to_int(data.get("numeroOperacion") or data.get("numero"))
        ok = data.get("ok", True) if "ok" in data else (numero > 0)

        return cls(
            ok=ok,
            numero_operacion=numero if numero > 0 else None,
            mensaje=data.get("mensaje", data.get("message")),
            id_cliente=data.get("idCliente", data.get("idClienteAsesorado")),
            simbolo=data.get("simbolo"),
            cantidad=_to_optional_int(data.get("cantidad")),
            precio=_to_optional_float(data.get("precio")),
        )

    def __str__(self) -> str:
        estado = "EXITOSA" if self.ok else "FALLIDA"
        num = f" (Op #{self.numero_operacion})" if self.numero_operacion else ""
        cliente = f" - Cliente {self.id_cliente}" if self.id_cliente else ""
        msg = f" - {self.mensaje}" if self.mensaje else ""
        return f"Operación Asesor {estado}{num}{cliente}{msg}"

    @property
    def exito(self) -> bool:
        """Alias para ok - indica si la operación fue exitosa"""
        return self.ok
