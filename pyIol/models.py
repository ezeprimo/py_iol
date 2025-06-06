"""
Modelos de datos para las respuestas de la API de Invertir Online
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Punta:
    """Modelo para las puntas de compra y venta"""
    cantidad_compra: int
    precio_compra: float
    precio_venta: float
    cantidad_venta: int

    @classmethod
    def from_dict(cls, data: dict) -> 'Punta':
        """Crea una instancia de Punta desde un diccionario"""
        return cls(
            cantidad_compra=data.get('cantidadCompra', 0),
            precio_compra=data.get('precioCompra', 0.0),
            precio_venta=data.get('precioVenta', 0.0),
            cantidad_venta=data.get('cantidadVenta', 0)
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
    def from_dict(cls, data: dict) -> 'CotizacionTitulo':
        """Crea una instancia de CotizacionTitulo desde un diccionario"""
        # Parsear la fecha
        fecha_hora_str = data.get('fechaHora', '')
        try:
            # Intentar parsear la fecha ISO con timezone
            fecha_hora = datetime.fromisoformat(fecha_hora_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            # Si no se puede parsear, usar datetime actual
            fecha_hora = datetime.now()
        
        # Parsear las puntas
        puntas_data = data.get('puntas', [])
        puntas = [Punta.from_dict(punta) for punta in puntas_data]
        
        return cls(
            ultimo_precio=data.get('ultimoPrecio', 0.0),
            variacion=data.get('variacion', 0.0),
            apertura=data.get('apertura', 0.0),
            maximo=data.get('maximo', 0.0),
            minimo=data.get('minimo', 0.0),
            fecha_hora=fecha_hora,
            tendencia=data.get('tendencia', ''),
            cierre_anterior=data.get('cierreAnterior', 0.0),
            monto_operado=data.get('montoOperado', 0),
            volumen_nominal=data.get('volumenNominal', 0),
            precio_promedio=data.get('precioPromedio', 0.0),
            moneda=data.get('moneda', ''),
            precio_ajuste=data.get('precioAjuste', 0.0),
            intereses_abiertos=data.get('interesesAbiertos', 0),
            puntas=puntas,
            cantidad_operaciones=data.get('cantidadOperaciones', 0),
            descripcion_titulo=data.get('descripcionTitulo', ''),
            plazo=data.get('plazo', ''),
            lamina_minima=data.get('laminaMinima', 1),
            lote=data.get('lote', 1)
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
    def from_dict(cls, data: dict) -> 'CotizacionOpcion':
        """Crea una instancia de CotizacionOpcion desde un diccionario"""
        # Parsear la fecha
        fecha_hora_str = data.get('fechaHora', '')
        try:
            # Intentar parsear la fecha ISO con timezone
            if fecha_hora_str and fecha_hora_str != '0001-01-01T00:00:00':
                fecha_hora = datetime.fromisoformat(fecha_hora_str.replace('Z', '+00:00'))
            else:
                # Si es la fecha por defecto o vacía, usar datetime actual
                fecha_hora = datetime.now()
        except (ValueError, AttributeError):
            # Si no se puede parsear, usar datetime actual
            fecha_hora = datetime.now()
        
        # Parsear las puntas (puede ser null)
        puntas_data = data.get('puntas', [])
        puntas = None
        if puntas_data:
            puntas = [Punta.from_dict(punta) for punta in puntas_data]
        
        return cls(
            ultimo_precio=data.get('ultimoPrecio', 0.0),
            variacion=data.get('variacion', 0.0),
            apertura=data.get('apertura', 0.0),
            maximo=data.get('maximo', 0.0),
            minimo=data.get('minimo', 0.0),
            fecha_hora=fecha_hora,
            tendencia=data.get('tendencia', ''),
            cierre_anterior=data.get('cierreAnterior', 0.0),
            monto_operado=data.get('montoOperado', 0),
            volumen_nominal=data.get('volumenNominal', 0),
            precio_promedio=data.get('precioPromedio', 0.0),
            moneda=data.get('moneda', 0),  # En opciones es int
            precio_ajuste=data.get('precioAjuste', 0.0),
            intereses_abiertos=data.get('interesesAbiertos', 0),
            puntas=puntas,
            cantidad_operaciones=data.get('cantidadOperaciones', 0),
            descripcion_titulo=data.get('descripcionTitulo'),  # Puede ser null
            plazo=data.get('plazo'),  # Puede ser null
            lamina_minima=data.get('laminaMinima', 0),
            lote=data.get('lote', 0)
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
    def from_dict(cls, data: dict) -> 'DatosTitulo':
        """Crea una instancia de DatosTitulo desde un diccionario"""
        return cls(
            simbolo=data.get('simbolo', ''),
            descripcion=data.get('descripcion', ''),
            pais=data.get('pais', ''),
            mercado=data.get('mercado', ''),
            tipo=data.get('tipo', ''),
            plazo=data.get('plazo', ''),
            moneda=data.get('moneda', '')
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
    def from_dict(cls, data: dict) -> 'OpcionTitulo':
        """Crea una instancia de OpcionTitulo desde un diccionario"""
        # Parsear la fecha de vencimiento
        fecha_vencimiento_str = data.get('fechaVencimiento', '')
        try:
            # Intentar parsear la fecha ISO
            fecha_vencimiento = datetime.fromisoformat(fecha_vencimiento_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            # Si no se puede parsear, usar datetime actual
            fecha_vencimiento = datetime.now()
        
        # Parsear la cotización anidada
        cotizacion_data = data.get('cotizacion', {})
        cotizacion = CotizacionOpcion.from_dict(cotizacion_data) if cotizacion_data else None
        
        return cls(
            cotizacion=cotizacion,
            simbolo_subyacente=data.get('simboloSubyacente', ''),
            fecha_vencimiento=fecha_vencimiento,
            tipo_opcion=data.get('tipoOpcion', ''),
            simbolo=data.get('simbolo', ''),
            descripcion=data.get('descripcion', ''),
            pais=data.get('pais', ''),
            mercado=data.get('mercado', ''),
            tipo=data.get('tipo', ''),
            plazo=data.get('plazo', ''),
            moneda=data.get('moneda', '')
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
        return self.tipo_opcion.lower() == 'call'

    @property
    def es_put(self) -> bool:
        """Retorna True si es una opción Put"""
        return self.tipo_opcion.lower() == 'put'

    @property
    def precio_strike(self) -> Optional[float]:
        """Extrae el precio strike de la descripción si es posible"""
        try:
            # Buscar el patrón de precio en la descripción (ej: "400.00")
            import re
            match = re.search(r'(\d+\.?\d*)', self.descripcion.replace(',', ''))
            if match:
                return float(match.group(1))
        except:
            pass
        return None

@dataclass
class InstrumentoPais:
    """Modelo para los instrumentos de cotización disponibles por país"""
    instrumento: str
    pais: str
    

    @classmethod
    def from_dict(cls, data: dict) -> 'InstrumentoPais':
        """Crea una instancia de InstrumentoPais desde un diccionario"""
        return cls(
            instrumento=data.get('instrumento', ''),
            pais=data.get('pais', '')
        )

    def __str__(self) -> str:
        """Representación string del objeto"""
        return (
            f"Instrumento: {self.instrumento} | País: {self.pais}\n"
        )


@dataclass
class PuntasCotizacion:
    """Modelo para las puntas de compra y venta de una cotización"""
    cantidad_compra: int
    precio_compra: float
    precio_venta: float
    cantidad_venta: int

    @classmethod
    def from_dict(cls, data: dict) -> 'PuntasCotizacion':
        """Crea una instancia de PuntasCotizacion desde un diccionario"""
        return cls(
            cantidad_compra=data.get('cantidadCompra', 0),
            precio_compra=data.get('precioCompra', 0.0),
            precio_venta=data.get('precioVenta', 0.0),
            cantidad_venta=data.get('cantidadVenta', 0)
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
    def from_dict(cls, data: dict) -> 'TituloCotizacion':
        """Crea una instancia de TituloCotizacion desde un diccionario"""
        # Parsear la fecha
        fecha_str = data.get('fecha', '')
        try:
            # Intentar parsear la fecha ISO
            fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            # Si no se puede parsear, usar datetime actual
            fecha = datetime.now()
        
        # Parsear fecha de vencimiento si existe
        fecha_vencimiento = None
        fecha_venc_str = data.get('fechaVencimiento')
        if fecha_venc_str:
            try:
                fecha_vencimiento = datetime.fromisoformat(fecha_venc_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        # Parsear las puntas
        puntas_data = data.get('puntas', {})
        puntas = PuntasCotizacion.from_dict(puntas_data)
        
        return cls(
            simbolo=data.get('simbolo', ''),
            puntas=puntas,
            ultimo_precio=data.get('ultimoPrecio', 0.0),
            variacion_porcentual=data.get('variacionPorcentual', 0.0),
            apertura=data.get('apertura', 0.0),
            maximo=data.get('maximo', 0.0),
            minimo=data.get('minimo', 0.0),
            ultimo_cierre=data.get('ultimoCierre', 0.0),
            volumen=data.get('volumen', 0),
            cantidad_operaciones=data.get('cantidadOperaciones', 0),
            fecha=fecha,
            tipo_opcion=data.get('tipoOpcion'),
            precio_ejercicio=data.get('precioEjercicio'),
            fecha_vencimiento=fecha_vencimiento,
            mercado=data.get('mercado', ''),
            moneda=data.get('moneda', ''),
            descripcion=data.get('descripcion', ''),
            plazo=data.get('plazo', ''),
            lamina_minima=data.get('laminaMinima', 1),
            lote=data.get('lote', 1)
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
    def from_dict(cls, data: dict) -> 'CotizacionesMasivas':
        """Crea una instancia de CotizacionesMasivas desde un diccionario"""
        titulos_data = data.get('titulos', [])
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
