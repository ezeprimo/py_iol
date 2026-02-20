# Constantes para la API de Invertir Online

# URLs base de la API
TOKEN_URL = "https://api.invertironline.com/token"
API_BASE_URL = "https://api.invertironline.com/api/v2"

# Headers por defecto
USER_AGENT = "pyIol/1.0"


# Constantes para mercados disponibles
class Markets:
    """Mercados disponibles en la API de IOL"""

    BCBA = "bCBA"  # Bolsa de Comercio de Buenos Aires
    NYSE = "nYSE"  # New York Stock Exchange
    NASDAQ = "nASDAQ"  # NASDAQ
    AMEX = "aMEX"  # American Stock Exchange
    BCS = "bCS"  # Bolsa de Comercio de Santiago
    ROFX = "rOFX"  # Rosario Futures Exchange


# Constantes para plazos de liquidación
class SettlementTerms:
    """Plazos de liquidación disponibles"""

    T0 = "t0"  # Liquidación inmediata
    T1 = "t1"  # Liquidación a 1 día
    T2 = "t2"  # Liquidación a 2 días
    T3 = "t3"  # Liquidación a 3 días


# Constantes para estados de operación
class OperationStates:
    """Estados de operación para filtros"""

    ALL = "todas"
    PENDING = "pendientes"
    FINISHED = "terminadas"
    CANCELLED = "canceladas"


# Constantes para países
class Countries:
    """Países disponibles en la API"""

    ARGENTINA = "argentina"
    USA = "estados_Unidos"


# Constantes para estados de CPD (Cheques de Pago Diferido)
class CPDStates:
    """Estados de cheques para filtros de CPD"""

    VIGENTES = "vigentes"  # Cheques vigentes para operar
    VENCIDOS = "vencidos"  # Cheques vencidos
    TODOS = "todos"  # Todos los cheques


# Constantes para segmentos de CPD
class CPDSegments:
    """Segmentos de cheques de pago diferido"""

    AVALADOS = "avalados"  # Cheques avalados por SGR
    PATROCINADOS = "patrocinados"  # Cheques patrocinados
    GARANTIZADOS = "garantizados"  # Cheques garantizados
    TODOS = "todos"  # Todos los segmentos


# Valores por defecto
DEFAULT_MARKET = Markets.BCBA
DEFAULT_SETTLEMENT_TERM = SettlementTerms.T1
DEFAULT_COUNTRY = Countries.ARGENTINA
DEFAULT_ORDER_VALIDITY_HOURS = 3
