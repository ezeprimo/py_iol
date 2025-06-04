# Constantes para la API de Invertir Online

# URLs base de la API
TOKEN_URL = "https://api.invertironline.com/token"
API_BASE_URL = "https://api.invertironline.com/api/v2"

# Headers por defecto
USER_AGENT = "pyIol/1.0"

# Constantes para mercados disponibles
class Markets:
    """Mercados disponibles en la API de IOL"""
    BCBA = "bCBA"        # Bolsa de Comercio de Buenos Aires
    NYSE = "nYSE"        # New York Stock Exchange
    NASDAQ = "nASDAQ"    # NASDAQ
    AMEX = "aMEX"        # American Stock Exchange
    BCS = "bCS"          # Bolsa de Comercio de Santiago
    ROFX = "rOFX"        # Rosario Futures Exchange

# Constantes para plazos de liquidación
class SettlementTerms:
    """Plazos de liquidación disponibles"""
    T0 = "t0"    # Liquidación inmediata
    T1 = "t1"    # Liquidación a 1 día
    T2 = "t2"    # Liquidación a 2 días
    T3 = "t3"    # Liquidación a 3 días

# Valores por defecto
DEFAULT_MARKET = Markets.BCBA
DEFAULT_SETTLEMENT_TERM = SettlementTerms.T1