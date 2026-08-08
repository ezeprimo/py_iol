"""
Tests para pyIol.models
"""

from datetime import datetime

import pytest

from pyIol.models import (
    ComisionesCPD,
    CotizacionesMasivas,
    CotizacionTitulo,
    DatosTitulo,
    EstadoCuenta,
    EstimacionMEP,
    InstrumentoPais,
    Portafolio,
    Punta,
    ResultadoOrden,
    TituloCotizacion,
    _to_float,
    _to_int,
    _to_optional_float,
    _to_optional_int,
)


class TestPunta:
    """Tests para el modelo Punta"""

    def test_from_dict(self, sample_punta_data):
        """Verifica la creacion de Punta desde diccionario"""
        punta = Punta.from_dict(sample_punta_data)

        assert punta.cantidad_compra == 100
        assert punta.precio_compra == 1249.50
        assert punta.precio_venta == 1251.00
        assert punta.cantidad_venta == 150

    def test_from_dict_empty(self):
        """Verifica la creacion de Punta con diccionario vacio"""
        punta = Punta.from_dict({})

        assert punta.cantidad_compra == 0
        assert punta.precio_compra == 0.0
        assert punta.precio_venta == 0.0
        assert punta.cantidad_venta == 0

    def test_from_dict_partial(self):
        """Verifica la creacion de Punta con datos parciales"""
        data = {"cantidadCompra": 50, "precioCompra": 100.0}
        punta = Punta.from_dict(data)

        assert punta.cantidad_compra == 50
        assert punta.precio_compra == 100.0
        assert punta.precio_venta == 0.0
        assert punta.cantidad_venta == 0


class TestCotizacionTitulo:
    """Tests para el modelo CotizacionTitulo"""

    def test_from_dict(self, sample_cotizacion_data):
        """Verifica la creacion de CotizacionTitulo desde diccionario"""
        cotizacion = CotizacionTitulo.from_dict(sample_cotizacion_data)

        assert cotizacion.ultimo_precio == 1250.50
        assert cotizacion.variacion == 2.35
        assert cotizacion.apertura == 1220.00
        assert cotizacion.maximo == 1260.00
        assert cotizacion.minimo == 1215.00
        assert cotizacion.tendencia == "sube"
        assert cotizacion.cierre_anterior == 1221.80
        assert cotizacion.moneda == "peso_Argentino"
        assert cotizacion.descripcion_titulo == "Grupo Financiero Galicia S.A."
        assert cotizacion.plazo == "t1"
        assert len(cotizacion.puntas) == 2

    def test_from_dict_empty(self):
        """Verifica la creacion con diccionario vacio"""
        cotizacion = CotizacionTitulo.from_dict({})

        assert cotizacion.ultimo_precio == 0.0
        assert cotizacion.variacion == 0.0
        assert cotizacion.puntas == []
        assert cotizacion.moneda == ""

    def test_fecha_hora_parsing(self, sample_cotizacion_data):
        """Verifica el parseo correcto de fecha/hora"""
        cotizacion = CotizacionTitulo.from_dict(sample_cotizacion_data)

        assert isinstance(cotizacion.fecha_hora, datetime)
        assert cotizacion.fecha_hora.year == 2024
        assert cotizacion.fecha_hora.month == 1
        assert cotizacion.fecha_hora.day == 15

    def test_fecha_hora_invalid(self):
        """Verifica el manejo de fecha invalida"""
        data = {"fechaHora": "invalid-date"}
        cotizacion = CotizacionTitulo.from_dict(data)

        # Deberia usar datetime.now() como fallback
        assert isinstance(cotizacion.fecha_hora, datetime)

    def test_mejor_compra(self, sample_cotizacion_data):
        """Verifica el calculo de mejor punta de compra"""
        cotizacion = CotizacionTitulo.from_dict(sample_cotizacion_data)

        mejor = cotizacion.mejor_compra
        assert mejor is not None
        assert mejor.precio_compra == 1249.50  # La mas alta

    def test_mejor_venta(self, sample_cotizacion_data):
        """Verifica el calculo de mejor punta de venta"""
        cotizacion = CotizacionTitulo.from_dict(sample_cotizacion_data)

        mejor = cotizacion.mejor_venta
        assert mejor is not None
        assert mejor.precio_venta == 1251.00  # La mas baja

    def test_mejor_compra_sin_puntas(self):
        """Verifica mejor_compra cuando no hay puntas"""
        cotizacion = CotizacionTitulo.from_dict({})

        assert cotizacion.mejor_compra is None

    def test_mejor_venta_sin_puntas(self):
        """Verifica mejor_venta cuando no hay puntas"""
        cotizacion = CotizacionTitulo.from_dict({})

        assert cotizacion.mejor_venta is None

    def test_spread(self, sample_cotizacion_data):
        """Verifica el calculo del spread"""
        cotizacion = CotizacionTitulo.from_dict(sample_cotizacion_data)

        spread = cotizacion.spread
        assert spread is not None
        assert spread == 1251.00 - 1249.50  # 1.50

    def test_spread_sin_puntas(self):
        """Verifica spread cuando no hay puntas"""
        cotizacion = CotizacionTitulo.from_dict({})

        assert cotizacion.spread is None

    def test_variacion_porcentual(self, sample_cotizacion_data):
        """Verifica la propiedad variacion_porcentual"""
        cotizacion = CotizacionTitulo.from_dict(sample_cotizacion_data)

        assert cotizacion.variacion_porcentual == 2.35

    def test_rendimiento_diario(self, sample_cotizacion_data):
        """Verifica el calculo del rendimiento diario"""
        cotizacion = CotizacionTitulo.from_dict(sample_cotizacion_data)

        # (1250.50 - 1221.80) / 1221.80 * 100 = 2.349...
        assert cotizacion.rendimiento_diario > 0
        assert abs(cotizacion.rendimiento_diario - 2.349) < 0.1

    def test_rendimiento_diario_cierre_cero(self):
        """Verifica rendimiento cuando cierre anterior es cero"""
        data = {"cierreAnterior": 0}
        cotizacion = CotizacionTitulo.from_dict(data)

        assert cotizacion.rendimiento_diario == 0.0

    def test_str_representation(self, sample_cotizacion_data):
        """Verifica la representacion string"""
        cotizacion = CotizacionTitulo.from_dict(sample_cotizacion_data)

        str_repr = str(cotizacion)
        assert "Grupo Financiero Galicia" in str_repr
        assert "1250.5" in str_repr
        assert "2.35" in str_repr


class TestDatosTitulo:
    """Tests para el modelo DatosTitulo"""

    def test_from_dict(self, sample_datos_titulo_data):
        """Verifica la creacion de DatosTitulo desde diccionario"""
        datos = DatosTitulo.from_dict(sample_datos_titulo_data)

        assert datos.simbolo == "GGAL"
        assert datos.descripcion == "Grupo Financiero Galicia S.A."
        assert datos.tipo == "ACCIONES"
        assert datos.pais == "argentina"
        assert datos.mercado == "bCBA"
        assert datos.moneda == "peso_Argentino"

    def test_from_dict_empty(self):
        """Verifica la creacion con diccionario vacio"""
        datos = DatosTitulo.from_dict({})

        assert datos.simbolo == ""
        assert datos.descripcion == ""


class TestInstrumentoPais:
    """Tests para el modelo InstrumentoPais"""

    def test_from_dict(self):
        """Verifica la creacion de InstrumentoPais desde diccionario"""
        data = {
            "instrumento": "acciones",
            "pais": "argentina",
        }
        instrumento = InstrumentoPais.from_dict(data)

        assert instrumento.instrumento == "acciones"
        assert instrumento.pais == "argentina"

    def test_from_dict_empty(self):
        """Verifica la creacion con diccionario vacio"""
        instrumento = InstrumentoPais.from_dict({})

        assert instrumento.instrumento == ""
        assert instrumento.pais == ""


class TestTituloCotizacion:
    """Tests para el modelo TituloCotizacion"""

    def test_from_dict(self):
        """Verifica la creacion de TituloCotizacion desde diccionario"""
        data = {
            "simbolo": "GGAL",
            "ultimoPrecio": 1250.50,
            "variacionPorcentual": 2.35,
            "cantidadNominal": 1000,
            "moneda": "peso_Argentino",
        }
        titulo = TituloCotizacion.from_dict(data)

        assert titulo.simbolo == "GGAL"
        assert titulo.ultimo_precio == 1250.50
        assert titulo.variacion_porcentual == 2.35

    def test_from_dict_empty(self):
        """Verifica la creacion con diccionario vacio"""
        titulo = TituloCotizacion.from_dict({})

        assert titulo.simbolo == ""
        assert titulo.ultimo_precio == 0.0


class TestCotizacionesMasivas:
    """Tests para el modelo CotizacionesMasivas"""

    def test_from_dict(self):
        """Verifica la creacion de CotizacionesMasivas desde diccionario"""
        data = {
            "titulos": [
                {"simbolo": "GGAL", "ultimoPrecio": 1250.50},
                {"simbolo": "YPF", "ultimoPrecio": 25000.00},
            ]
        }
        cotizaciones = CotizacionesMasivas.from_dict(data)

        assert len(cotizaciones.titulos) == 2
        assert cotizaciones.titulos[0].simbolo == "GGAL"
        assert cotizaciones.titulos[1].simbolo == "YPF"

    def test_from_dict_empty(self):
        """Verifica la creacion con diccionario vacio"""
        cotizaciones = CotizacionesMasivas.from_dict({})

        assert cotizaciones.titulos == []


class TestEstadoCuenta:
    """Tests para el modelo EstadoCuenta"""

    def test_from_dict(self, sample_estado_cuenta_data):
        """Verifica la creacion de EstadoCuenta desde diccionario"""
        estado = EstadoCuenta.from_dict(sample_estado_cuenta_data)

        assert len(estado.cuentas) == 1
        assert estado.cuentas[0].numero == "12345"
        assert estado.cuentas[0].estado == "operable"
        assert estado.cuentas[0].titulos_valorizados == 150000.00
        assert estado.total_en_pesos == 210000.00
        # Verificar estadisticas
        assert len(estado.estadisticas) == 2
        assert estado.estadisticas[0].descripcion == "Anterior"
        assert estado.estadisticas[0].cantidad == 0
        assert estado.estadisticas[1].descripcion == "Actual"
        assert estado.estadisticas[1].cantidad == 5
        assert estado.estadisticas[1].volumen == 12500.50

    def test_from_dict_empty(self):
        """Verifica la creacion con diccionario vacio"""
        estado = EstadoCuenta.from_dict({})

        assert estado.cuentas == []
        assert estado.estadisticas == []
        assert estado.total_en_pesos == 0.0


class TestPortafolio:
    """Tests para el modelo Portafolio"""

    def test_from_dict(self, sample_portafolio_data):
        """Verifica la creacion de Portafolio desde diccionario"""
        portafolio = Portafolio.from_dict(sample_portafolio_data)

        assert portafolio.pais == "argentina"
        assert len(portafolio.activos) == 1
        assert portafolio.total_en_pesos == 125050.00

    def test_from_dict_empty(self):
        """Verifica la creacion con diccionario vacio"""
        portafolio = Portafolio.from_dict({})

        # pais tiene valor por defecto "argentina" en from_dict
        assert portafolio.pais == "argentina"
        assert portafolio.activos == []
        assert portafolio.total_en_pesos == 0.0


# =============================================================================
# Tests de los helpers de conversión
# =============================================================================


class TestHelpers:
    """Tests para las funciones auxiliares de conversión numérica."""

    # ── _to_float ──────────────────────────────────────────────────────────

    def test_to_float_from_number(self):
        assert _to_float(42) == 42.0
        assert _to_float(42.5) == 42.5

    def test_to_float_from_string(self):
        assert _to_float("138.02") == 138.02
        assert _to_float("0.0") == 0.0

    def test_to_float_from_string_with_comma(self):
        """Las strings pueden venir con coma como separador decimal."""
        assert _to_float("1.250,50") == 1250.50

    def test_to_float_from_none(self):
        assert _to_float(None) == 0.0

    def test_to_float_default_override(self):
        assert _to_float(None, default=-1.0) == -1.0

    # ── _to_int ────────────────────────────────────────────────────────────

    def test_to_int_from_number(self):
        assert _to_int(42) == 42
        assert _to_int(42.9) == 42  # truncado

    def test_to_int_from_string(self):
        assert _to_int("42") == 42
        assert _to_int("100") == 100

    def test_to_int_from_string_with_comma(self):
        assert _to_int("1000") == 1000
        assert _to_int("1,000") == 1000  # coma como separador de miles

    def test_to_int_from_none(self):
        assert _to_int(None) == 0

    def test_to_int_default_override(self):
        assert _to_int(None, default=-1) == -1

    # ── _to_optional_float ─────────────────────────────────────────────────

    def test_to_optional_float_from_number(self):
        assert _to_optional_float(42.5) == 42.5

    def test_to_optional_float_from_string(self):
        assert _to_optional_float("138.02") == 138.02

    def test_to_optional_float_from_none(self):
        assert _to_optional_float(None) is None

    # ── _to_optional_int ───────────────────────────────────────────────────

    def test_to_optional_int_from_number(self):
        assert _to_optional_int(42) == 42

    def test_to_optional_int_from_string(self):
        assert _to_optional_int("42") == 42

    def test_to_optional_int_from_none(self):
        assert _to_optional_int(None) is None


# =============================================================================
# Tests del bug #4 — ComisionesCPD.from_dict con strings
# =============================================================================


class TestComisionesCPD:
    """Tests para el modelo ComisionesCPD (bug #4).

    La API de IOL retorna los valores de comisiones como strings
    (ej. ``"138.02"`` en lugar de ``138.02``), lo que causaba
    ``TypeError`` al hacer aritmética en ``from_dict`` y al formatear.
    """

    def test_from_dict_with_numbers(self):
        """Caso feliz: API retorna números nativos."""
        data = {
            "comision": 138.02,
            "ivaComision": 28.99,
            "derechosMercado": 9.33,
            "ivaDerechosMercado": 1.96,
        }
        c = ComisionesCPD.from_dict(data)
        assert c.comision == 138.02
        assert c.iva_comision == 28.99
        assert c.derechos_mercado == 9.33
        assert c.iva_derechos == 1.96
        assert c.total_gastos == pytest.approx(178.30)

    def test_from_dict_with_strings(self):
        """Escenario del bug #4: API retorna strings (ej. '138.02')."""
        data = {
            "comision": "138.02",
            "ivaComision": "28.99",
            "derechosMercado": "9.33",
            "ivaDerechosMercado": "1.96",
        }
        c = ComisionesCPD.from_dict(data)
        # Todos deben ser floats, sin TypeError
        assert isinstance(c.comision, float)
        assert isinstance(c.total_gastos, float)
        assert c.comision == 138.02
        assert c.iva_comision == 28.99
        assert c.derechos_mercado == 9.33
        assert c.iva_derechos == 1.96
        assert c.total_gastos == pytest.approx(178.30)

    def test_from_dict_with_mixed_types(self):
        """Mezcla de strings y números — la API podría ser inconsistente."""
        data = {
            "comision": "138.02",
            "ivaComision": 28.99,
            "derechos": "9.33",
            "ivaDerechosMercado": 1.96,
        }
        c = ComisionesCPD.from_dict(data)
        assert c.total_gastos == pytest.approx(178.30)

    def test_from_dict_total_provided(self):
        """Si total ya viene en la respuesta, no se recalcula."""
        data = {
            "comision": "100",
            "ivaComision": "21",
            "derechosMercado": "5",
            "ivaDerechosMercado": "1",
            "totalGastos": "200.00",
        }
        c = ComisionesCPD.from_dict(data)
        assert c.total_gastos == 200.00

    def test_from_dict_optional_fields(self):
        """Campos opcionales: arancel, otros gastos."""
        data = {
            "comision": "100",
            "ivaComision": "21",
            "derechosMercado": "5",
            "ivaDerechosMercado": "1",
            "arancel": "10",
            "otrosGastos": "5",
        }
        c = ComisionesCPD.from_dict(data)
        assert c.arancel == 10.0
        assert c.otros_gastos == 5.0
        assert c.total_gastos == 142.0  # 127 + 10 + 5

    def test_from_dict_empty(self):
        """Diccionario vacío — defaults seguros, sin TypeError."""
        c = ComisionesCPD.from_dict({})
        assert c.comision == 0.0
        assert c.iva_comision == 0.0
        assert c.derechos_mercado == 0.0
        assert c.iva_derechos == 0.0
        assert c.total_gastos == 0.0
        assert c.arancel is None
        assert c.otros_gastos is None

    def test_from_dict_alternative_keys(self):
        """Fallback keys: ej. 'comisiones' en vez de 'comision'."""
        data = {
            "comisiones": "50",
            "iva": "10.5",
            "derechos": "5",
        }
        c = ComisionesCPD.from_dict(data)
        assert c.comision == 50.0
        assert c.iva_comision == 10.5
        assert c.derechos_mercado == 5.0

    def test_str_representation(self):
        """__str__ no debe fallar con strings convertidos."""
        data = {
            "comision": "138.02",
            "ivaComision": "28.99",
            "derechosMercado": "9.33",
            "ivaDerechosMercado": "1.96",
        }
        c = ComisionesCPD.from_dict(data)
        s = str(c)
        assert "138.02" in s
        assert "28.99" in s
        assert "178.30" in s


# =============================================================================
# Tests de ResultadoOrden — patrón "numero > 0" que explota con strings
# =============================================================================


class TestResultadoOrden:
    """Tests para el modelo ResultadoOrden.

    ``numero > 0`` lanza TypeError en Python 3 si la API retorna
    el número de operación como string.
    """

    def test_from_dict_with_int_numero(self):
        data = {"numeroOperacion": 12345}
        r = ResultadoOrden.from_dict(data)
        assert r.numero_operacion == 12345
        assert r.ok is True

    def test_from_dict_with_string_numero(self):
        """Bug análogo a ComisionesCPD: string en vez de int."""
        data = {"numeroOperacion": "12345"}
        r = ResultadoOrden.from_dict(data)
        assert r.numero_operacion == 12345
        assert r.ok is True

    def test_from_dict_ok_false(self):
        data = {"ok": False, "mensaje": "Saldo insuficiente"}
        r = ResultadoOrden.from_dict(data)
        assert r.ok is False
        assert r.mensaje == "Saldo insuficiente"

    def test_from_dict_empty(self):
        r = ResultadoOrden.from_dict({})
        assert r.numero_operacion == 0
        assert r.ok is False  # numero=0 → ok=False


# =============================================================================
# Tests de EstimacionMEP — propiedad tipo_cambio_efectivo con strings
# =============================================================================


class TestEstimacionMEP:
    """Tests para EstimacionMEP.

    La propiedad ``tipo_cambio_efectivo`` hace división sobre
    ``monto_pesos / monto_dolares``. Si uno de los dos viene como
    string de la API, lanza TypeError.
    """

    def test_from_dict_with_numbers(self):
        data = {
            "montoPesos": 100000.0,
            "montoDolares": 80.0,
            "tipoCambio": 1250.0,
        }
        e = EstimacionMEP.from_dict(data)
        assert e.monto_pesos == 100000.0
        assert e.monto_dolares == 80.0
        assert e.tipo_cambio == 1250.0
        assert e.tipo_cambio_efectivo == 1250.0

    def test_from_dict_with_strings(self):
        """Strings de la API no deben romper tipo_cambio_efectivo."""
        data = {
            "montoPesos": "100000.00",
            "montoDolares": "80.00",
            "tipoCambio": "1250.00",
        }
        e = EstimacionMEP.from_dict(data)
        assert isinstance(e.monto_pesos, float)
        assert isinstance(e.monto_dolares, float)
        assert e.tipo_cambio_efectivo == 1250.0

    def test_tipo_cambio_efectivo_with_commission(self):
        """tipo_cambio_efectivo incluye costos en el monto total."""
        e = EstimacionMEP(
            monto_pesos=100500.0,
            monto_dolares=80.0,
            tipo_cambio=1250.0,
            comision=500.0,
        )
        assert e.tipo_cambio_efectivo == 1256.25

    def test_tipo_cambio_efectivo_zero_dollars(self):
        """Evita división por cero."""
        e = EstimacionMEP(
            monto_pesos=100000.0,
            monto_dolares=0.0,
            tipo_cambio=1250.0,
        )
        # monto_dolares=0 → no se cumple la condición → retorna tipo_cambio
        assert e.tipo_cambio_efectivo == 1250.0
