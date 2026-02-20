"""
Tests para pyIol.client
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from pyIol.client import IOLAPIError, IOLClient


class TestIOLClientInit:
    """Tests para la inicializacion del cliente"""

    def test_init_with_credentials(self):
        """Verifica la inicializacion con credenciales"""
        client = IOLClient("test_user", "test_password")

        assert client.username == "test_user"
        assert client.password == "test_password"
        client.close()

    def test_context_manager(self):
        """Verifica que funcione como context manager"""
        with IOLClient("test_user", "test_password") as client:
            assert client.username == "test_user"
            assert client._session is not None


class TestIOLClientAuthentication:
    """Tests para autenticacion del cliente"""

    @patch.object(httpx.Client, "post")
    def test_get_auth_token_success(self, mock_post, sample_auth_response):
        """Verifica la obtencion exitosa del token"""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_auth_response
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        with IOLClient("test_user", "test_password") as client:
            # Limpiar cache para forzar nueva autenticacion
            client._get_auth_token.cache_clear()
            token = client._get_auth_token()

            assert token == "test_token_123456789"
            mock_post.assert_called_once()

    @patch.object(httpx.Client, "post")
    def test_get_auth_token_no_token(self, mock_post):
        """Verifica error cuando no hay token en respuesta"""
        mock_response = MagicMock()
        mock_response.json.return_value = {}  # Sin access_token
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        with IOLClient("test_user", "test_password") as client:
            client._get_auth_token.cache_clear()

            with pytest.raises(IOLAPIError, match="No se recibió token"):
                client._get_auth_token()

    @patch.object(httpx.Client, "post")
    def test_get_auth_token_http_error(self, mock_post):
        """Verifica manejo de error HTTP en autenticacion"""
        mock_post.side_effect = httpx.HTTPError("Connection error")

        with IOLClient("test_user", "test_password") as client:
            client._get_auth_token.cache_clear()

            with pytest.raises(IOLAPIError, match="Error al obtener token"):
                client._get_auth_token()

    @patch.object(httpx.Client, "post")
    def test_test_authentication_success(self, mock_post, sample_auth_response):
        """Verifica test_authentication exitoso"""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_auth_response
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        with IOLClient("test_user", "test_password") as client:
            client._get_auth_token.cache_clear()
            result = client.test_authentication()

            assert result is True

    @patch.object(httpx.Client, "post")
    def test_test_authentication_failure(self, mock_post):
        """Verifica test_authentication fallido"""
        mock_post.side_effect = httpx.HTTPError("Auth failed")

        with IOLClient("test_user", "test_password") as client:
            client._get_auth_token.cache_clear()
            result = client.test_authentication()

            assert result is False


class TestIOLClientRequests:
    """Tests para peticiones autenticadas"""

    @patch.object(httpx.Client, "request")
    @patch.object(httpx.Client, "post")
    def test_make_authenticated_request_success(
        self, mock_post, mock_request, sample_auth_response
    ):
        """Verifica peticion autenticada exitosa"""
        # Mock autenticacion
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = sample_auth_response
        mock_auth_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_auth_response

        # Mock peticion
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response

        with IOLClient("test_user", "test_password") as client:
            client._get_auth_token.cache_clear()
            result = client._make_authenticated_request("GET", "/test/endpoint")

            assert result == {"data": "test"}
            mock_request.assert_called_once()

            # Verificar que se incluyo el token
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})
            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test_token_123456789"

    @patch.object(httpx.Client, "request")
    @patch.object(httpx.Client, "post")
    def test_make_authenticated_request_http_error(
        self, mock_post, mock_request, sample_auth_response
    ):
        """Verifica manejo de error HTTP en peticion"""
        # Mock autenticacion
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = sample_auth_response
        mock_auth_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_auth_response

        # Mock peticion con error
        mock_request.side_effect = httpx.HTTPError("Request failed")

        with IOLClient("test_user", "test_password") as client:
            client._get_auth_token.cache_clear()

            with pytest.raises(IOLAPIError, match="Error en petición"):
                client._make_authenticated_request("GET", "/test/endpoint")


class TestIOLClientGetMethods:
    """Tests para metodos GET del cliente"""

    @patch.object(IOLClient, "_make_authenticated_request")
    def test_get_profile_data(self, mock_request):
        """Verifica get_profile_data"""
        mock_request.return_value = {
            "nombre": "Test",
            "apellido": "User",
            "numeroCuenta": "12345",
            "dni": "12.345.678",
            "cuitCuil": "20123456789",
            "sexo": "Masculino",
            "perfilInversor": "Moderado",
            "email": "test@example.com",
            "cuentaAbierta": True,
            "actualizarDDJJ": False,
            "actualizarTestInversor": False,
            "esBajaArrepentimiento": False,
            "actualizarTyC": False,
            "actualizarTyCApp": False,
        }

        with IOLClient("test_user", "test_password") as client:
            result = client.get_profile_data()

            assert result.nombre == "Test"
            assert result.apellido == "User"
            assert result.email == "test@example.com"
            assert result.perfil_inversor == "Moderado"
            mock_request.assert_called_once_with("GET", "/datos-perfil")

    @patch.object(IOLClient, "_make_authenticated_request")
    def test_get_stock_quote(self, mock_request, sample_cotizacion_data):
        """Verifica get_stock_quote"""
        mock_request.return_value = sample_cotizacion_data

        with IOLClient("test_user", "test_password") as client:
            result = client.get_stock_quote("GGAL")

            assert result.ultimo_precio == 1250.50
            assert result.descripcion_titulo == "Grupo Financiero Galicia S.A."

    @patch.object(IOLClient, "_make_authenticated_request")
    def test_get_stock_quote_with_params(self, mock_request, sample_cotizacion_data):
        """Verifica get_stock_quote con parametros opcionales"""
        mock_request.return_value = sample_cotizacion_data

        with IOLClient("test_user", "test_password") as client:
            from pyIol.constants import Markets, SettlementTerms

            result = client.get_stock_quote(
                "GGAL", market=Markets.BCBA, settlement_term=SettlementTerms.T2
            )

            assert result.ultimo_precio == 1250.50
            # Verificar que se llamo con el simbolo correcto
            call_args = mock_request.call_args
            assert "GGAL" in call_args[0][1]

    @patch.object(IOLClient, "_make_authenticated_request")
    def test_get_stock_quote_raw(self, mock_request, sample_cotizacion_data):
        """Verifica get_stock_quote_raw retorna diccionario"""
        mock_request.return_value = sample_cotizacion_data

        with IOLClient("test_user", "test_password") as client:
            result = client.get_stock_quote_raw("GGAL")

            assert isinstance(result, dict)
            assert result["ultimoPrecio"] == 1250.50

    @patch.object(IOLClient, "_make_authenticated_request")
    def test_get_stock_data(self, mock_request, sample_datos_titulo_data):
        """Verifica get_stock_data"""
        mock_request.return_value = sample_datos_titulo_data

        with IOLClient("test_user", "test_password") as client:
            result = client.get_stock_data("GGAL")

            assert result.simbolo == "GGAL"
            assert result.descripcion == "Grupo Financiero Galicia S.A."

    @patch.object(IOLClient, "_make_authenticated_request")
    def test_get_massive_quotes(self, mock_request):
        """Verifica get_massive_quotes"""
        mock_request.return_value = {
            "titulos": [
                {"simbolo": "GGAL", "ultimoPrecio": 1250.50},
                {"simbolo": "YPF", "ultimoPrecio": 25000.00},
            ]
        }

        with IOLClient("test_user", "test_password") as client:
            result = client.get_massive_quotes("acciones", "argentina")

            assert len(result.titulos) == 2
            assert result.titulos[0].simbolo == "GGAL"

    @patch.object(IOLClient, "_make_authenticated_request")
    def test_get_account_status(self, mock_request, sample_estado_cuenta_data):
        """Verifica get_account_status"""
        mock_request.return_value = sample_estado_cuenta_data

        with IOLClient("test_user", "test_password") as client:
            result = client.get_account_status()

            assert len(result.cuentas) == 1
            assert result.total_en_pesos == 210000.00

    @patch.object(IOLClient, "_make_authenticated_request")
    def test_get_portfolio(self, mock_request, sample_portafolio_data):
        """Verifica get_portfolio"""
        mock_request.return_value = sample_portafolio_data

        with IOLClient("test_user", "test_password") as client:
            from pyIol.constants import Countries

            result = client.get_portfolio(Countries.ARGENTINA)

            assert result.pais == "argentina"
            assert len(result.activos) == 1


class TestIOLClientTradingValidez:
    """Tests de validez por defecto en métodos de trading"""

    @pytest.mark.parametrize(
        "method_name,is_advisor",
        [
            ("buy", False),
            ("buy_raw", False),
            ("sell", False),
            ("sell_raw", False),
            ("buy_dollar_bond", False),
            ("buy_dollar_bond_raw", False),
            ("sell_dollar_bond", False),
            ("sell_dollar_bond_raw", False),
            ("advisor_sell_dollar_bond", True),
            ("advisor_sell_dollar_bond_raw", True),
        ],
    )
    @patch.object(IOLClient, "_make_authenticated_request")
    def test_usa_validez_default_si_no_se_envia(
        self, mock_request, method_name: str, is_advisor: bool
    ):
        """Verifica que se envía validez default (+3h) cuando no se pasa el argumento"""
        mock_request.return_value = {"numeroOperacion": 12345, "ok": True}
        validez_default = "2026-02-20T16:03:34"

        with IOLClient("test_user", "test_password") as client:
            with patch.object(client, "_get_default_validez", return_value=validez_default) as mock_val:
                method = getattr(client, method_name)

                if is_advisor:
                    method(id_cliente="123", simbolo="AL30D", cantidad=1, precio=50.0)
                else:
                    method(simbolo="GGAL", cantidad=1, precio=7500.0)

                sent_payload = mock_request.call_args.kwargs["json"]
                assert sent_payload["validez"] == validez_default
                mock_val.assert_called_once()

    @pytest.mark.parametrize(
        "method_name,is_advisor",
        [
            ("buy", False),
            ("buy_raw", False),
            ("sell", False),
            ("sell_raw", False),
            ("buy_dollar_bond", False),
            ("buy_dollar_bond_raw", False),
            ("sell_dollar_bond", False),
            ("sell_dollar_bond_raw", False),
            ("advisor_sell_dollar_bond", True),
            ("advisor_sell_dollar_bond_raw", True),
        ],
    )
    @patch.object(IOLClient, "_make_authenticated_request")
    def test_respeta_validez_explicita_si_se_envia(
        self, mock_request, method_name: str, is_advisor: bool
    ):
        """Verifica que una validez explícita tiene prioridad sobre el default"""
        mock_request.return_value = {"numeroOperacion": 12345, "ok": True}
        validez_explicita = "2026-03-01T10:00:00"

        with IOLClient("test_user", "test_password") as client:
            with patch.object(client, "_get_default_validez", return_value="NO-DEBERIA-USARSE") as mock_val:
                method = getattr(client, method_name)

                if is_advisor:
                    method(
                        id_cliente="123",
                        simbolo="AL30D",
                        cantidad=1,
                        precio=50.0,
                        validez=validez_explicita,
                    )
                else:
                    method(simbolo="GGAL", cantidad=1, precio=7500.0, validez=validez_explicita)

                sent_payload = mock_request.call_args.kwargs["json"]
                assert sent_payload["validez"] == validez_explicita
                mock_val.assert_not_called()


class TestIOLAPIError:
    """Tests para la excepcion IOLAPIError"""

    def test_exception_creation(self):
        """Verifica la creacion de IOLAPIError"""
        error = IOLAPIError("Test error message")

        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_exception_raise(self):
        """Verifica que se pueda lanzar y capturar"""
        with pytest.raises(IOLAPIError) as exc_info:
            raise IOLAPIError("Test error")

        assert "Test error" in str(exc_info.value)
