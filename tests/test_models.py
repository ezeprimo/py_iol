"""
Tests para pyIol.models
"""

from datetime import datetime

from pyIol.models import (
    CotizacionesMasivas,
    CotizacionTitulo,
    DatosTitulo,
    EstadoCuenta,
    InstrumentoPais,
    Portafolio,
    Punta,
    TituloCotizacion,
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
