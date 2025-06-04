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
