"""
Librería Python para interactuar con la API de Invertir Online (IOL)
"""

from .client import IOLClient, IOLAPIError
from .constants import (
    TOKEN_URL, API_BASE_URL, USER_AGENT, 
    Markets, SettlementTerms, OperationStates, Countries,
    DEFAULT_MARKET, DEFAULT_SETTLEMENT_TERM, DEFAULT_COUNTRY,
    CPDStates, CPDSegments
)
from .models import (
    # Modelos de cotizaciones
    CotizacionTitulo, Punta, DatosTitulo, OpcionTitulo, 
    InstrumentoPais, CotizacionesMasivas, TituloCotizacion, 
    PuntasCotizacion, CotizacionDetallada,
    # Modelos de estado de cuenta y portafolio
    EstadoCuenta, Cuenta, Saldo,
    Portafolio, Activo, TituloPortafolio, TituloInfo,
    Operacion, OperacionDetalle,
    # Modelos de trading
    OrdenOperacion, ResultadoOrden, OrdenEspecieD,
    # Modelos de FCI
    FondoComunInversion, FCIDetalle, TipoFondo, AdministradoraFCI,
    OrdenFCI, ResultadoFCI,
    # Modelos de MEP Simplificado
    EstimacionMEP, ParametrosMEP, ValidacionMEP, ResultadoMEP,
    # Modelos de CPD
    PuedeOperarCPD, ChequeCPD, ComisionesCPD, OrdenCPD, ResultadoCPD,
    # Modelos de Asesores
    MovimientoCliente, MovimientosAsesor, OpcionRespuesta, 
    PreguntaTestInversor, TestInversor, RespuestaTest,
    PerfilInversor, ResultadoOperacionAsesor
)

__version__ = "0.1.0"
__all__ = [
    # Cliente y errores
    "IOLClient", 
    "IOLAPIError", 
    # URLs y configuración
    "TOKEN_URL", 
    "API_BASE_URL", 
    "USER_AGENT",
    # Constantes de enumeración
    "Markets",
    "SettlementTerms",
    "OperationStates",
    "Countries",
    "CPDStates",
    "CPDSegments",
    # Valores por defecto
    "DEFAULT_MARKET",
    "DEFAULT_SETTLEMENT_TERM",
    "DEFAULT_COUNTRY",
    # Modelos de cotizaciones
    "CotizacionTitulo",
    "Punta",
    "DatosTitulo",
    "OpcionTitulo",
    "InstrumentoPais",
    "CotizacionesMasivas",
    "TituloCotizacion",
    "PuntasCotizacion",
    "CotizacionDetallada",
    # Modelos de estado de cuenta y portafolio
    "EstadoCuenta",
    "Cuenta",
    "Saldo",
    "Portafolio",
    "Activo",
    "TituloPortafolio",
    "TituloInfo",
    "Operacion",
    "OperacionDetalle",
    # Modelos de trading
    "OrdenOperacion",
    "ResultadoOrden",
    "OrdenEspecieD",
    # Modelos de FCI
    "FondoComunInversion",
    "FCIDetalle",
    "TipoFondo",
    "AdministradoraFCI",
    "OrdenFCI",
    "ResultadoFCI",
    # Modelos de MEP Simplificado
    "EstimacionMEP",
    "ParametrosMEP",
    "ValidacionMEP",
    "ResultadoMEP",
    # Modelos de CPD
    "PuedeOperarCPD",
    "ChequeCPD",
    "ComisionesCPD",
    "OrdenCPD",
    "ResultadoCPD",
    # Modelos de Asesores
    "MovimientoCliente",
    "MovimientosAsesor",
    "OpcionRespuesta",
    "PreguntaTestInversor",
    "TestInversor",
    "RespuestaTest",
    "PerfilInversor",
    "ResultadoOperacionAsesor"
]