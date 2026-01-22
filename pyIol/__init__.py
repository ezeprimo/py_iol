"""
Librería Python para interactuar con la API de Invertir Online (IOL)
"""

from .client import IOLAPIError, IOLClient
from .constants import (
    API_BASE_URL,
    DEFAULT_COUNTRY,
    DEFAULT_MARKET,
    DEFAULT_SETTLEMENT_TERM,
    TOKEN_URL,
    USER_AGENT,
    Countries,
    CPDSegments,
    CPDStates,
    Markets,
    OperationStates,
    SettlementTerms,
)
from .models import (
    Activo,
    AdministradoraFCI,
    ChequeCPD,
    ComisionesCPD,
    CotizacionDetallada,
    CotizacionesMasivas,
    # Modelos de cotizaciones
    CotizacionTitulo,
    Cuenta,
    # Modelos de perfil de usuario
    DatosPerfil,
    DatosTitulo,
    # Modelos de estado de cuenta y portafolio
    Estadistica,
    EstadoCuenta,
    # Modelos de MEP Simplificado
    EstimacionMEP,
    FCIDetalle,
    # Modelos de FCI
    FondoComunInversion,
    InstrumentoPais,
    # Modelos de Asesores
    MovimientoCliente,
    MovimientosAsesor,
    OpcionRespuesta,
    OpcionTitulo,
    Operacion,
    OperacionDetalle,
    OrdenCPD,
    OrdenEspecieD,
    OrdenFCI,
    # Modelos de trading
    OrdenOperacion,
    ParametrosMEP,
    PerfilInversor,
    Portafolio,
    PreguntaTestInversor,
    # Modelos de CPD
    PuedeOperarCPD,
    Punta,
    PuntasCotizacion,
    RespuestaTest,
    ResultadoCPD,
    ResultadoFCI,
    ResultadoMEP,
    ResultadoOperacionAsesor,
    ResultadoOrden,
    Saldo,
    TestInversor,
    TipoFondo,
    TituloCotizacion,
    TituloInfo,
    TituloPortafolio,
    ValidacionMEP,
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
    "Estadistica",
    "Cuenta",
    "Saldo",
    "Portafolio",
    "Activo",
    "TituloPortafolio",
    "TituloInfo",
    "Operacion",
    "OperacionDetalle",
    # Modelos de perfil de usuario
    "DatosPerfil",
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
    "ResultadoOperacionAsesor",
]
