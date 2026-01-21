"""
Configuracion y fixtures compartidas para tests
"""

import pytest


@pytest.fixture
def sample_cotizacion_data():
    """Datos de ejemplo para CotizacionTitulo"""
    return {
        "ultimoPrecio": 1250.50,
        "variacion": 2.35,
        "apertura": 1220.00,
        "maximo": 1260.00,
        "minimo": 1215.00,
        "fechaHora": "2024-01-15T14:30:00-03:00",
        "tendencia": "sube",
        "cierreAnterior": 1221.80,
        "montoOperado": 150000000,
        "volumenNominal": 120000,
        "precioPromedio": 1235.25,
        "moneda": "peso_Argentino",
        "precioAjuste": 0.0,
        "interesesAbiertos": 0,
        "puntas": [
            {
                "cantidadCompra": 100,
                "precioCompra": 1249.50,
                "precioVenta": 1251.00,
                "cantidadVenta": 150,
            },
            {
                "cantidadCompra": 200,
                "precioCompra": 1248.00,
                "precioVenta": 1252.50,
                "cantidadVenta": 300,
            },
        ],
        "cantidadOperaciones": 450,
        "descripcionTitulo": "Grupo Financiero Galicia S.A.",
        "plazo": "t1",
        "laminaMinima": 1,
        "lote": 1,
    }


@pytest.fixture
def sample_punta_data():
    """Datos de ejemplo para Punta"""
    return {
        "cantidadCompra": 100,
        "precioCompra": 1249.50,
        "precioVenta": 1251.00,
        "cantidadVenta": 150,
    }


@pytest.fixture
def sample_datos_titulo_data():
    """Datos de ejemplo para DatosTitulo"""
    return {
        "simbolo": "GGAL",
        "descripcion": "Grupo Financiero Galicia S.A.",
        "tipo": "ACCIONES",
        "pais": "argentina",
        "mercado": "bCBA",
        "moneda": "peso_Argentino",
        "plazo": "t1",
        "laminaMinima": 1,
        "lote": 1,
        "cantidadMinima": 1,
    }


@pytest.fixture
def sample_instrumento_pais_data():
    """Datos de ejemplo para InstrumentoPais"""
    return {
        "instrumento": "acciones",
        "pais": "argentina",
        "paneles": ["merval", "panel_general", "cedears"],
    }


@pytest.fixture
def sample_auth_response():
    """Respuesta de autenticacion de ejemplo"""
    return {
        "access_token": "test_token_123456789",
        "token_type": "bearer",
        "expires_in": 900,
        "refresh_token": "refresh_token_123456789",
    }


@pytest.fixture
def sample_estado_cuenta_data():
    """Datos de ejemplo para EstadoCuenta"""
    return {
        "cuentas": [
            {
                "numero": "12345",
                "tipo": "inversion_Argentina",
                "moneda": "peso_Argentino",
                "disponible": 50000.00,
                "comprometido": 10000.00,
                "saldo": 60000.00,
                "titulosValorizados": 150000.00,
                "total": 210000.00,
                "margenDescubierto": 0.0,
                "saldos": [
                    {
                        "liquidacion": "inmediato",
                        "saldo": 50000.00,
                        "comprometido": 10000.00,
                        "disponible": 40000.00,
                    }
                ],
            }
        ],
        "estadisticas": {
            "variacionDiaria": 1250.50,
            "variacionDiariaPorcentaje": 0.85,
        },
        "totalEnPesos": 210000.00,
    }


@pytest.fixture
def sample_portafolio_data():
    """Datos de ejemplo para Portafolio"""
    return {
        "pais": "argentina",
        "activos": [
            {
                "titulo": {
                    "simbolo": "GGAL",
                    "descripcion": "Grupo Financiero Galicia S.A.",
                    "tipo": "acciones",
                    "plazo": "t1",
                    "moneda": "peso_Argentino",
                },
                "cantidad": 100,
                "comprometido": 0,
                "puntosVariacion": 25.50,
                "variacionDiaria": 2.1,
                "ultimoPrecio": 1250.50,
                "ppc": 1100.00,
                "gananciaPorcentaje": 13.68,
                "gananciaDinero": 15050.00,
                "valorizado": 125050.00,
                "parking": {},
            }
        ],
        "totalEnPesos": 125050.00,
    }
