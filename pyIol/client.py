"""
Cliente para la API de Invertir Online (IOL)
"""
import httpx
from typing import Optional, Dict, Any, List, List
from cachetools import cached, TTLCache
from .constants import TOKEN_URL, API_BASE_URL, USER_AGENT, DEFAULT_MARKET, DEFAULT_SETTLEMENT_TERM
from .models import (
    CotizacionTitulo, DatosTitulo, OpcionTitulo, InstrumentoPais, 
    CotizacionesMasivas, CotizacionDetallada,
    EstadoCuenta, Portafolio, Operacion, OperacionDetalle,
    OrdenOperacion, ResultadoOrden, OrdenEspecieD,
    FondoComunInversion, FCIDetalle, TipoFondo, AdministradoraFCI, ResultadoFCI,
    EstimacionMEP, ParametrosMEP, ValidacionMEP, ResultadoMEP,
    PuedeOperarCPD, ChequeCPD, ComisionesCPD, ResultadoCPD,
    MovimientosAsesor, TestInversor, PerfilInversor, ResultadoOperacionAsesor
)


class IOLAPIError(Exception):
    """Excepción personalizada para errores de la API de IOL"""
    pass


class IOLClient:
    """Cliente principal para interactuar con la API de Invertir Online"""
    
    def __init__(self, username: str, password: str):
        """
        Inicializa el cliente IOL
        
        Args:
            username: Nombre de usuario de IOL
            password: Contraseña de IOL
        """
        self.username = username
        self.password = password
        self._session = httpx.Client()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()
        
    def close(self):
        """Cierra la sesión HTTP"""
        self._session.close()
    
    @cached(cache=TTLCache(maxsize=3, ttl=870))  # Cache por 14.5 minutos (tokens duran 15 min)
    def _get_auth_token(self) -> str:
        """
        Obtiene el token de autenticación de la API
        
        Returns:
            Token de acceso
            
        Raises:
            IOLAPIError: Si hay error en la autenticación
        """
        payload = {
            "username": self.username,
            "password": self.password,
            "grant_type": "password"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT
        }
        
        try:
            response = self._session.post(TOKEN_URL, data=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if "access_token" not in data:
                raise IOLAPIError("No se recibió token de acceso")
                
            return data["access_token"]
            
        except httpx.HTTPError as e:
            raise IOLAPIError(f"Error al obtener token: {e}")
        except Exception as e:
            raise IOLAPIError(f"Error inesperado al autenticar: {e}")
    
    def _make_authenticated_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Realiza una petición autenticada a la API
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint de la API (sin la URL base)
            **kwargs: Argumentos adicionales para la petición
            
        Returns:
            Respuesta JSON de la API
            
        Raises:
            IOLAPIError: Si hay error en la petición
        """
        token = self._get_auth_token()
        headers = kwargs.get("headers", {})
        headers.update({
            "Authorization": f"Bearer {token}",
            "User-Agent": USER_AGENT
        })
        kwargs["headers"] = headers
        
        url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            response = self._session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            raise IOLAPIError(f"Error en petición a {endpoint}: {e}")
        except Exception as e:
            raise IOLAPIError(f"Error inesperado en petición: {e}")
    
    def test_authentication(self) -> bool:
        """
        Prueba la autenticación con la API
        
        Returns:
            True si la autenticación es exitosa
        """
        try:
            self._get_auth_token()
            return True
        except IOLAPIError:
            return False
    
    def get_profile_data(self) -> Dict[str, Any]:
        """
        Obtiene los datos del perfil del usuario autenticado
        
        Returns:
            Datos del perfil del usuario
        """
        return self._make_authenticated_request("GET", "/datos-perfil")
    
    def get_mep_dollar_rate(self, symbol: str = "AL30") -> Dict[str, Any]:
        """
        Obtiene la cotización del dólar MEP a través de un bono específico
        
        Args:
            symbol: Símbolo del bono para calcular MEP (por defecto AL30)
            
        Returns:
            Cotización del dólar MEP
        """
        return self._make_authenticated_request("GET", f"/Cotizaciones/MEP/{symbol}")
    
    def get_stock_quote(self, symbol: str, market: str = DEFAULT_MARKET, settlement_term: str = DEFAULT_SETTLEMENT_TERM) -> CotizacionTitulo:
        """
        Obtiene la cotización actual de una acción
        
        Args:
            symbol: Símbolo de la acción
            market: Mercado (por defecto bCBA). Usar Markets.* para valores válidos
            settlement_term: Plazo de liquidación (por defecto t1). Usar SettlementTerms.* para valores válidos
            
        Returns:
            Objeto CotizacionTitulo con la cotización actual de la acción
        """
        params = {
            "mercado": market,
            "simbolo": symbol,
            "model.simbolo": symbol,
            "model.mercado": market,
            "model.plazo": settlement_term
        }
        
        data = self._make_authenticated_request(
            "GET", 
            f"/{market}/Titulos/{symbol}/Cotizacion",
            params=params
        )
        return CotizacionTitulo.from_dict(data)
    
    def get_stock_quote_raw(self, symbol: str, market: str = DEFAULT_MARKET, settlement_term: str = DEFAULT_SETTLEMENT_TERM) -> Dict[str, Any]:
        """
        Obtiene la cotización actual de una acción en formato JSON crudo
        
        Args:
            symbol: Símbolo de la acción
            market: Mercado (por defecto bCBA). Usar Markets.* para valores válidos
            settlement_term: Plazo de liquidación (por defecto t1). Usar SettlementTerms.* para valores válidos
            
        Returns:
            Diccionario con la cotización actual de la acción (formato JSON original)
        """
        params = {
            "mercado": market,
            "simbolo": symbol,
            "model.simbolo": symbol,
            "model.mercado": market,
            "model.plazo": settlement_term
        }
        
        return self._make_authenticated_request(
            "GET", 
            f"/{market}/Titulos/{symbol}/Cotizacion",
            params=params
        )
    
    def get_stock_data(self, symbol: str, market: str = DEFAULT_MARKET) -> DatosTitulo:
        """
        Obtiene los datos básicos de un título
        
        Args:
            symbol: Símbolo del título
            market: Mercado (por defecto bCBA). Usar Markets.* para valores válidos
            
        Returns:
            Objeto DatosTitulo con los datos básicos del título
        """
        data = self._make_authenticated_request(
            "GET", 
            f"/{market}/Titulos/{symbol}"
        )
        return DatosTitulo.from_dict(data)
    
    def get_stock_data_raw(self, symbol: str, market: str = DEFAULT_MARKET) -> Dict[str, Any]:
        """
        Obtiene los datos básicos de un título en formato JSON crudo
        
        Args:
            symbol: Símbolo del título
            market: Mercado (por defecto bCBA). Usar Markets.* para valores válidos
            
        Returns:
            Diccionario con los datos básicos del título (formato JSON original)
        """
        return self._make_authenticated_request(
            "GET", 
            f"/{market}/Titulos/{symbol}"
        )
    
    def get_stock_options(self, symbol: str, market: str = DEFAULT_MARKET) -> List[OpcionTitulo]:
        """
        Obtiene las opciones disponibles para un título
        
        Args:
            symbol: Símbolo del título subyacente (ej: ALUA, GGAL)
            market: Mercado (por defecto bCBA). Usar Markets.* para valores válidos
            
        Returns:
            Lista de objetos OpcionTitulo con las opciones disponibles
            
        Raises:
            IOLAPIError: Si hay error en la petición a la API
        """
        try:
            data = self._make_authenticated_request(
                "GET", 
                f"/{market}/Titulos/{symbol}/Opciones"
            )
            
            # Manejar diferentes tipos de respuesta
            if data is None:
                return []
            elif isinstance(data, list):
                return [OpcionTitulo.from_dict(option_data) for option_data in data if option_data]
            elif isinstance(data, dict):
                # Si la API devuelve un objeto en lugar de una lista
                if 'opciones' in data and isinstance(data['opciones'], list):
                    return [OpcionTitulo.from_dict(option_data) for option_data in data['opciones'] if option_data]
                elif data:  # Si es un solo objeto de opción
                    return [OpcionTitulo.from_dict(data)]
            
            return []
            
        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                # Endpoint no existe para este símbolo
                return []
            else:
                # Re-lanzar otros errores
                raise
    
    def get_stock_options_raw(self, symbol: str, market: str = DEFAULT_MARKET) -> List[Dict[str, Any]]:
        """
        Obtiene las opciones disponibles para un título en formato JSON crudo
        
        Args:
            symbol: Símbolo del título subyacente (ej: ALUA, GGAL)
            market: Mercado (por defecto bCBA). Usar Markets.* para valores válidos
            
        Returns:
            Lista de diccionarios con las opciones disponibles (formato JSON original)
            
        Raises:
            IOLAPIError: Si hay error en la petición a la API
        """
        try:
            data = self._make_authenticated_request(
                "GET", 
                f"/{market}/Titulos/{symbol}/Opciones"
            )
            
            # Manejar diferentes tipos de respuesta
            if data is None:
                return []
            elif isinstance(data, list):
                return [option_data for option_data in data if option_data]
            elif isinstance(data, dict):
                # Si la API devuelve un objeto en lugar de una lista
                if 'opciones' in data and isinstance(data['opciones'], list):
                    return data['opciones']
                elif data:  # Si es un solo objeto de opción
                    return [data]
            
            return []
            
        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                # Endpoint no existe para este símbolo
                return []
            else:
                # Re-lanzar otros errores
                raise
    
    def get_market_instruments(self, pais: str = "argentina") -> List[InstrumentoPais]:
        """
        Obtiene los instrumentos de cotización disponibles para un país
        
        Args:
            pais: Código del país (por defecto 'bCBA' para Argentina)
            
        Returns:
            Lista de objetos InstrumentoPais con los instrumentos disponibles
            
        Raises:
            IOLAPIError: Si hay error en la petición a la API
        """
        try:
            data = self.get_market_instruments_raw(pais)
            
            # Manejar diferentes tipos de respuesta
            if not data:
                return []
            
            # Convertir cada diccionario a un objeto InstrumentoPais
            instrumentos = []
            for instrument_data in data:
                if instrument_data:  # Asegurar que no es None o vacío
                    instrumentos.append(InstrumentoPais.from_dict(instrument_data))
            
            return instrumentos
            
        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                # Endpoint no existe para este país
                return []
            else:
                # Re-lanzar otros errores
                raise

    def get_market_instruments_raw(self, pais: str = "argentina") -> List[Dict[str, Any]]:
        """
        Obtiene los instrumentos de cotización disponibles para un país (datos en crudo)
        
        Args:
            pais: Código del país (por defecto 'bCBA' para Argentina)
            
        Returns:
            Lista de diccionarios con los instrumentos disponibles (formato JSON original)
            
        Raises:
            IOLAPIError: Si hay error en la petición a la API
        """
        try:
            data = self._make_authenticated_request(
                "GET", 
                f"/{pais}/Titulos/Cotizacion/Instrumentos"
            )
            
            # Manejar diferentes tipos de respuesta
            if data is None:
                return []
            elif isinstance(data, list):
                return [instrument_data for instrument_data in data if instrument_data]
            elif isinstance(data, dict):
                # Si la API devuelve un objeto en lugar de una lista
                if 'instrumentos' in data and isinstance(data['instrumentos'], list):
                    return data['instrumentos']
                elif data:  # Si es un solo objeto de instrumento
                    return [data]
            
            return []
            
        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                # Endpoint no existe para este país
                return []
            else:
                # Re-lanzar otros errores
                raise
    
    def get_massive_quotes(self, instrumento: str, pais: str = "argentina") -> CotizacionesMasivas:
        """
        Obtiene todas las cotizaciones de un país y tipo de instrumento
        
        Args:
            instrumento: Tipo de instrumento. Valores válidos:
                        'acciones', 'cedears', 'opciones', 'aDRs', 'titulosPublicos', 
                        'cauciones', 'cHPD', 'futuros', 'obligacionesNegociables', 'letras'
            pais: País (por defecto 'argentina')
            
        Returns:
            Objeto CotizacionesMasivas con todas las cotizaciones del instrumento y país
            
        Raises:
            IOLAPIError: Si hay error en la petición a la API
        """
        try:
            # Mapear algunos alias comunes
            instrumento_map = {
                'stocks': 'acciones',
                'bonds': 'titulosPublicos',
                'options': 'opciones',
                'futures': 'futuros'
            }
            
            instrumento_final = instrumento_map.get(instrumento.lower(), instrumento)
            
            # Construir los parámetros de la query
            params = {
                f'cotizacionInstrumentoModel.instrumento': instrumento_final,
                f'cotizacionInstrumentoModel.pais': pais
            }
            
            data = self._make_authenticated_request(
                "GET",
                f"/Cotizaciones/{instrumento_final}/{pais}/Todos",
                params=params
            )
            
            return CotizacionesMasivas.from_dict(data)
            
        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                # Si no se encuentra el endpoint, devolver objeto vacío
                return CotizacionesMasivas(titulos=[])
            else:
                # Re-lanzar otros errores
                raise

    def get_massive_quotes_raw(self, instrumento: str, pais: str = "argentina") -> dict:
        """
        Obtiene todas las cotizaciones de un país y tipo de instrumento en formato JSON crudo
        
        Args:
            instrumento: Tipo de instrumento. Valores válidos:
                        'acciones', 'cedears', 'opciones', 'aDRs', 'titulosPublicos', 
                        'cauciones', 'cHPD', 'futuros', 'obligacionesNegociables', 'letras'
            pais: País (por defecto 'argentina')
            
        Returns:
            Diccionario con todas las cotizaciones del instrumento y país (formato JSON original)
            
        Raises:
            IOLAPIError: Si hay error en la petición a la API
        """
        try:
            # Mapear algunos alias comunes
            instrumento_map = {
                'stocks': 'acciones',
                'bonds': 'titulosPublicos',
                'options': 'opciones',
                'futures': 'futuros'
            }
            
            instrumento_final = instrumento_map.get(instrumento.lower(), instrumento)
            
            # Construir los parámetros de la query
            params = {
                f'cotizacionInstrumentoModel.instrumento': instrumento_final,
                f'cotizacionInstrumentoModel.pais': pais
            }
            
            return self._make_authenticated_request(
                "GET",
                f"/Cotizaciones/{instrumento_final}/{pais}/Todos",
                params=params
            )
            
        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                # Si no se encuentra el endpoint, devolver diccionario vacío
                return {"titulos": []}
            else:
                # Re-lanzar otros errores
                raise
    
    def get_panel_quotes(self, instrumento: str, panel: str, pais: str = "argentina") -> CotizacionesMasivas:
        """
        Obtiene las cotizaciones de un panel específico
        
        Args:
            instrumento: Tipo de instrumento. Valores válidos:
                        'acciones', 'cedears', 'opciones', 'aDRs', 'titulosPublicos', 
                        'cauciones', 'cHPD', 'futuros', 'obligacionesNegociables', 'letras'
            panel: Nombre del panel (ej: 'merval', 'general', 'lideres')
            pais: País (por defecto 'argentina')
            
        Returns:
            Objeto CotizacionesMasivas con las cotizaciones del panel específico
            
        Raises:
            IOLAPIError: Si hay error en la petición a la API
        """
        try:
            # Mapear algunos alias comunes
            instrumento_map = {
                'stocks': 'acciones',
                'bonds': 'titulosPublicos',
                'options': 'opciones',
                'futures': 'futuros'
            }
            
            instrumento_final = instrumento_map.get(instrumento.lower(), instrumento)
            
            # Construir los parámetros de la query
            params = {
                f'panelCotizacion.instrumento': instrumento_final,
                f'panelCotizacion.panel': panel,
                f'panelCotizacion.pais': pais
            }
            
            data = self._make_authenticated_request(
                "GET",
                f"/Cotizaciones/{instrumento_final}/{panel}/{pais}",
                params=params
            )
            
            return CotizacionesMasivas.from_dict(data)
            
        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                # Si no se encuentra el endpoint, devolver objeto vacío
                return CotizacionesMasivas(titulos=[])
            else:
                # Re-lanzar otros errores
                raise

    def get_panel_quotes_raw(self, instrumento: str, panel: str, pais: str = "argentina") -> dict:
        """
        Obtiene las cotizaciones de un panel específico en formato JSON crudo
        
        Args:
            instrumento: Tipo de instrumento. Valores válidos:
                        'acciones', 'cedears', 'opciones', 'aDRs', 'titulosPublicos', 
                        'cauciones', 'cHPD', 'futuros', 'obligacionesNegociables', 'letras'
            panel: Nombre del panel (ej: 'merval', 'general', 'lideres')
            pais: País (por defecto 'argentina')
            
        Returns:
            Diccionario con las cotizaciones del panel específico (formato JSON original)
            
        Raises:
            IOLAPIError: Si hay error en la petición a la API
        """
        try:
            # Mapear algunos alias comunes
            instrumento_map = {
                'stocks': 'acciones',
                'bonds': 'titulosPublicos',
                'options': 'opciones',
                'futures': 'futuros'
            }
            
            instrumento_final = instrumento_map.get(instrumento.lower(), instrumento)
            
            # Construir los parámetros de la query
            params = {
                f'panelCotizacion.instrumento': instrumento_final,
                f'panelCotizacion.panel': panel,
                f'panelCotizacion.pais': pais
            }
            
            return self._make_authenticated_request(
                "GET",
                f"/Cotizaciones/{instrumento_final}/{panel}/{pais}",
                params=params
            )
            
        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                # Si no se encuentra el endpoint, devolver diccionario vacío
                return {"titulos": []}
            else:
                # Re-lanzar otros errores
                raise
    
    def get_stock_quote_detailed(self, simbolo: str, mercado: str = "bCBA") -> 'CotizacionDetallada':
        """
        Obtiene la cotización detallada de un título específico
        
        Args:
            simbolo: Símbolo del título (ej: "ALUA", "GGAL")
            mercado: Mercado del título (por defecto "bCBA")
            
        Returns:
            CotizacionDetallada con información completa del título
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        from .models import CotizacionDetallada
        
        try:
            endpoint = f"{mercado}/Titulos/{simbolo}/CotizacionDetalle"
            data = self._make_authenticated_request("GET", endpoint)
            
            if data:
                return CotizacionDetallada.from_dict(data)
            else:
                raise IOLAPIError(f"No se pudo obtener cotización detallada para {simbolo}")
                
        except Exception as e:
            raise IOLAPIError(f"Error obteniendo cotización detallada de {simbolo}: {str(e)}")

    def get_stock_quote_detailed_raw(self, simbolo: str, mercado: str = "bCBA") -> dict:
        """
        Obtiene la cotización detallada de un título en formato JSON crudo
        
        Args:
            simbolo: Símbolo del título (ej: "ALUA", "GGAL") 
            mercado: Mercado del título (por defecto "bCBA")
            
        Returns:
            Diccionario con la respuesta JSON cruda de la API
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        try:
            endpoint = f"{mercado}/Titulos/{simbolo}/CotizacionDetalle"
            return self._make_authenticated_request("GET", endpoint)
                
        except Exception as e:
            raise IOLAPIError(f"Error obteniendo cotización detallada RAW de {simbolo}: {str(e)}")

    # =========================================================================
    # ESTADO DE CUENTA Y PORTAFOLIO
    # =========================================================================
    
    def get_account_status(self) -> 'EstadoCuenta':
        """
        Obtiene el estado de cuenta completo del usuario
        
        Returns:
            Objeto EstadoCuenta con todas las cuentas y saldos
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        from .models import EstadoCuenta
        
        data = self._make_authenticated_request("GET", "/estadocuenta")
        return EstadoCuenta.from_dict(data)
    
    def get_account_status_raw(self) -> Dict[str, Any]:
        """
        Obtiene el estado de cuenta completo en formato JSON crudo
        
        Returns:
            Diccionario con el estado de cuenta
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        return self._make_authenticated_request("GET", "/estadocuenta")
    
    def get_portfolio(self, pais: str = "argentina") -> 'Portafolio':
        """
        Obtiene el portafolio de inversiones del usuario
        
        Args:
            pais: País del portafolio ('argentina' o 'estados_Unidos')
            
        Returns:
            Objeto Portafolio con todos los activos y títulos
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        from .models import Portafolio
        
        data = self._make_authenticated_request("GET", f"/portafolio/{pais}")
        return Portafolio.from_dict(data, pais=pais)
    
    def get_portfolio_raw(self, pais: str = "argentina") -> Dict[str, Any]:
        """
        Obtiene el portafolio en formato JSON crudo
        
        Args:
            pais: País del portafolio ('argentina' o 'estados_Unidos')
            
        Returns:
            Diccionario con el portafolio
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        return self._make_authenticated_request("GET", f"/portafolio/{pais}")
    
    def get_operations(
        self,
        estado: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        pais: Optional[str] = None,
        numero: Optional[int] = None
    ) -> List['Operacion']:
        """
        Obtiene la lista de operaciones con filtros opcionales
        
        Args:
            estado: Estado de las operaciones ('todas', 'pendientes', 'terminadas', 'canceladas')
            fecha_desde: Fecha desde (formato: 'YYYY-MM-DD')
            fecha_hasta: Fecha hasta (formato: 'YYYY-MM-DD')
            pais: País ('argentina' o 'estados_Unidos')
            numero: Número específico de operación
            
        Returns:
            Lista de objetos Operacion
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        from .models import Operacion
        
        # Construir parámetros de filtro
        params = {}
        if estado:
            params['filtro.estado'] = estado
        if fecha_desde:
            params['filtro.fechaDesde'] = fecha_desde
        if fecha_hasta:
            params['filtro.fechaHasta'] = fecha_hasta
        if pais:
            params['filtro.pais'] = pais
        if numero:
            params['filtro.numero'] = numero
        
        data = self._make_authenticated_request("GET", "/operaciones", params=params)
        
        # La respuesta puede ser una lista directa o un objeto con 'operaciones'
        if isinstance(data, list):
            return [Operacion.from_dict(op) for op in data]
        elif isinstance(data, dict) and 'operaciones' in data:
            return [Operacion.from_dict(op) for op in data['operaciones']]
        
        return []
    
    def get_operations_raw(
        self,
        estado: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        pais: Optional[str] = None,
        numero: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de operaciones en formato JSON crudo
        
        Args:
            estado: Estado de las operaciones ('todas', 'pendientes', 'terminadas', 'canceladas')
            fecha_desde: Fecha desde (formato: 'YYYY-MM-DD')
            fecha_hasta: Fecha hasta (formato: 'YYYY-MM-DD')
            pais: País ('argentina' o 'estados_Unidos')
            numero: Número específico de operación
            
        Returns:
            Lista de diccionarios con las operaciones
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        # Construir parámetros de filtro
        params = {}
        if estado:
            params['filtro.estado'] = estado
        if fecha_desde:
            params['filtro.fechaDesde'] = fecha_desde
        if fecha_hasta:
            params['filtro.fechaHasta'] = fecha_hasta
        if pais:
            params['filtro.pais'] = pais
        if numero:
            params['filtro.numero'] = numero
        
        data = self._make_authenticated_request("GET", "/operaciones", params=params)
        
        # Normalizar respuesta
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'operaciones' in data:
            return data['operaciones']
        
        return []
    
    def get_operation_detail(self, numero: int) -> 'OperacionDetalle':
        """
        Obtiene el detalle completo de una operación específica
        
        Args:
            numero: Número de la operación
            
        Returns:
            Objeto OperacionDetalle con toda la información de la operación
            
        Raises:
            IOLAPIError: Si hay error en la consulta o la operación no existe
        """
        from .models import OperacionDetalle
        
        data = self._make_authenticated_request("GET", f"/operaciones/{numero}")
        return OperacionDetalle.from_dict(data)
    
    def get_operation_detail_raw(self, numero: int) -> Dict[str, Any]:
        """
        Obtiene el detalle de una operación en formato JSON crudo
        
        Args:
            numero: Número de la operación
            
        Returns:
            Diccionario con el detalle de la operación
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        return self._make_authenticated_request("GET", f"/operaciones/{numero}")
    
    def cancel_operation(self, numero: int) -> bool:
        """
        Cancela una operación pendiente
        
        Args:
            numero: Número de la operación a cancelar
            
        Returns:
            True si la operación fue cancelada exitosamente
            
        Raises:
            IOLAPIError: Si hay error en la cancelación o la operación no puede cancelarse
        """
        try:
            self._make_authenticated_request("DELETE", f"/operaciones/{numero}")
            return True
        except IOLAPIError:
            raise
        except Exception as e:
            raise IOLAPIError(f"Error cancelando operación {numero}: {str(e)}")
    
    def cancel_operation_raw(self, numero: int) -> Dict[str, Any]:
        """
        Cancela una operación y retorna la respuesta en formato JSON crudo
        
        Args:
            numero: Número de la operación a cancelar
            
        Returns:
            Diccionario con la respuesta de la API
            
        Raises:
            IOLAPIError: Si hay error en la cancelación
        """
        return self._make_authenticated_request("DELETE", f"/operaciones/{numero}")

    # =========================================================================
    # TRADING - COMPRA Y VENTA
    # =========================================================================
    
    def buy(
        self,
        simbolo: str,
        cantidad: int,
        precio: float,
        mercado: str = DEFAULT_MARKET,
        plazo: str = DEFAULT_SETTLEMENT_TERM,
        validez: Optional[str] = None
    ) -> 'ResultadoOrden':
        """
        Ejecuta una orden de compra de títulos
        
        IMPORTANTE: Esta operación impacta en el entorno REAL de IOL.
        Verificar que el símbolo, cantidad, precio y demás parámetros sean correctos.
        
        Args:
            simbolo: Símbolo del título a comprar (ej: "GGAL", "ALUA")
            cantidad: Cantidad de títulos a comprar
            precio: Precio límite de compra (la orden se ejecuta a ese precio o menor)
            mercado: Mercado donde operar (por defecto bCBA). Usar Markets.*
            plazo: Plazo de liquidación (por defecto t1). Usar SettlementTerms.*
            validez: Fecha de validez de la orden en formato ISO (ej: "2025-12-31T23:59:59")
                    Si no se especifica, la orden es válida solo por el día.
            
        Returns:
            Objeto ResultadoOrden con el número de operación asignado
            
        Raises:
            IOLAPIError: Si hay error en la operación (fondos insuficientes, mercado cerrado, etc.)
            
        Example:
            >>> resultado = client.buy("GGAL", 100, 150.50)
            >>> if resultado.ok:
            ...     print(f"Orden enviada: {resultado.numero_operacion}")
        """
        from .models import ResultadoOrden
        
        payload = {
            "mercado": mercado,
            "simbolo": simbolo,
            "cantidad": cantidad,
            "precio": precio,
            "plazo": plazo
        }
        
        if validez:
            payload["validez"] = validez
        
        data = self._make_authenticated_request(
            "POST",
            "/operar/Comprar",
            json=payload
        )
        
        return ResultadoOrden.from_dict(data)
    
    def buy_raw(
        self,
        simbolo: str,
        cantidad: int,
        precio: float,
        mercado: str = DEFAULT_MARKET,
        plazo: str = DEFAULT_SETTLEMENT_TERM,
        validez: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta una orden de compra y retorna la respuesta en formato JSON crudo
        
        Args:
            simbolo: Símbolo del título a comprar
            cantidad: Cantidad de títulos a comprar
            precio: Precio límite de compra
            mercado: Mercado donde operar (por defecto bCBA)
            plazo: Plazo de liquidación (por defecto t1)
            validez: Fecha de validez de la orden en formato ISO
            
        Returns:
            Diccionario con la respuesta de la API
            
        Raises:
            IOLAPIError: Si hay error en la operación
        """
        payload = {
            "mercado": mercado,
            "simbolo": simbolo,
            "cantidad": cantidad,
            "precio": precio,
            "plazo": plazo
        }
        
        if validez:
            payload["validez"] = validez
        
        return self._make_authenticated_request(
            "POST",
            "/operar/Comprar",
            json=payload
        )
    
    def sell(
        self,
        simbolo: str,
        cantidad: int,
        precio: float,
        mercado: str = DEFAULT_MARKET,
        plazo: str = DEFAULT_SETTLEMENT_TERM,
        validez: Optional[str] = None
    ) -> 'ResultadoOrden':
        """
        Ejecuta una orden de venta de títulos
        
        IMPORTANTE: Esta operación impacta en el entorno REAL de IOL.
        Verificar que tenga suficientes títulos en cartera y que el precio sea correcto.
        
        Args:
            simbolo: Símbolo del título a vender (ej: "GGAL", "ALUA")
            cantidad: Cantidad de títulos a vender
            precio: Precio límite de venta (la orden se ejecuta a ese precio o mayor)
            mercado: Mercado donde operar (por defecto bCBA). Usar Markets.*
            plazo: Plazo de liquidación (por defecto t1). Usar SettlementTerms.*
            validez: Fecha de validez de la orden en formato ISO (ej: "2025-12-31T23:59:59")
                    Si no se especifica, la orden es válida solo por el día.
            
        Returns:
            Objeto ResultadoOrden con el número de operación asignado
            
        Raises:
            IOLAPIError: Si hay error en la operación (títulos insuficientes, mercado cerrado, etc.)
            
        Example:
            >>> resultado = client.sell("GGAL", 50, 160.00)
            >>> if resultado.ok:
            ...     print(f"Orden de venta enviada: {resultado.numero_operacion}")
        """
        from .models import ResultadoOrden
        
        payload = {
            "mercado": mercado,
            "simbolo": simbolo,
            "cantidad": cantidad,
            "precio": precio,
            "plazo": plazo
        }
        
        if validez:
            payload["validez"] = validez
        
        data = self._make_authenticated_request(
            "POST",
            "/operar/Vender",
            json=payload
        )
        
        return ResultadoOrden.from_dict(data)
    
    def sell_raw(
        self,
        simbolo: str,
        cantidad: int,
        precio: float,
        mercado: str = DEFAULT_MARKET,
        plazo: str = DEFAULT_SETTLEMENT_TERM,
        validez: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta una orden de venta y retorna la respuesta en formato JSON crudo
        
        Args:
            simbolo: Símbolo del título a vender
            cantidad: Cantidad de títulos a vender
            precio: Precio límite de venta
            mercado: Mercado donde operar (por defecto bCBA)
            plazo: Plazo de liquidación (por defecto t1)
            validez: Fecha de validez de la orden en formato ISO
            
        Returns:
            Diccionario con la respuesta de la API
            
        Raises:
            IOLAPIError: Si hay error en la operación
        """
        payload = {
            "mercado": mercado,
            "simbolo": simbolo,
            "cantidad": cantidad,
            "precio": precio,
            "plazo": plazo
        }
        
        if validez:
            payload["validez"] = validez
        
        return self._make_authenticated_request(
            "POST",
            "/operar/Vender",
            json=payload
        )
    
    def buy_dollar_bond(
        self,
        simbolo: str,
        cantidad: int,
        precio: float,
        mercado: str = DEFAULT_MARKET,
        plazo: str = DEFAULT_SETTLEMENT_TERM,
        validez: Optional[str] = None
    ) -> 'ResultadoOrden':
        """
        Ejecuta una orden de compra de bonos en Especie D (dólares)
        
        IMPORTANTE: Esta operación impacta en el entorno REAL de IOL.
        Se utiliza para comprar bonos denominados en dólares (ej: AL30D, GD30D).
        Requiere tener dólares disponibles en la cuenta.
        
        Args:
            simbolo: Símbolo del bono en especie D (ej: "AL30D", "GD30D")
            cantidad: Cantidad de bonos a comprar (valor nominal)
            precio: Precio límite de compra en dólares
            mercado: Mercado donde operar (por defecto bCBA). Usar Markets.*
            plazo: Plazo de liquidación (por defecto t1). Usar SettlementTerms.*
            validez: Fecha de validez de la orden en formato ISO
            
        Returns:
            Objeto ResultadoOrden con el número de operación asignado
            
        Raises:
            IOLAPIError: Si hay error en la operación (dólares insuficientes, etc.)
            
        Example:
            >>> resultado = client.buy_dollar_bond("AL30D", 1000, 35.50)
            >>> if resultado.ok:
            ...     print(f"Compra de bono en USD enviada: {resultado.numero_operacion}")
        """
        from .models import ResultadoOrden
        
        payload = {
            "mercado": mercado,
            "simbolo": simbolo,
            "cantidad": cantidad,
            "precio": precio,
            "plazo": plazo
        }
        
        if validez:
            payload["validez"] = validez
        
        data = self._make_authenticated_request(
            "POST",
            "/operar/ComprarEspecieD",
            json=payload
        )
        
        return ResultadoOrden.from_dict(data)
    
    def buy_dollar_bond_raw(
        self,
        simbolo: str,
        cantidad: int,
        precio: float,
        mercado: str = DEFAULT_MARKET,
        plazo: str = DEFAULT_SETTLEMENT_TERM,
        validez: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta una orden de compra de bonos Especie D y retorna JSON crudo
        
        Args:
            simbolo: Símbolo del bono en especie D
            cantidad: Cantidad de bonos a comprar
            precio: Precio límite de compra en dólares
            mercado: Mercado donde operar
            plazo: Plazo de liquidación
            validez: Fecha de validez de la orden
            
        Returns:
            Diccionario con la respuesta de la API
            
        Raises:
            IOLAPIError: Si hay error en la operación
        """
        payload = {
            "mercado": mercado,
            "simbolo": simbolo,
            "cantidad": cantidad,
            "precio": precio,
            "plazo": plazo
        }
        
        if validez:
            payload["validez"] = validez
        
        return self._make_authenticated_request(
            "POST",
            "/operar/ComprarEspecieD",
            json=payload
        )
    
    def sell_dollar_bond(
        self,
        simbolo: str,
        cantidad: int,
        precio: float,
        mercado: str = DEFAULT_MARKET,
        plazo: str = DEFAULT_SETTLEMENT_TERM,
        validez: Optional[str] = None
    ) -> 'ResultadoOrden':
        """
        Ejecuta una orden de venta de bonos en Especie D (dólares)
        
        IMPORTANTE: Esta operación impacta en el entorno REAL de IOL.
        Se utiliza para vender bonos denominados en dólares (ej: AL30D, GD30D).
        Los dólares de la venta se acreditarán en la cuenta en USD.
        
        Args:
            simbolo: Símbolo del bono en especie D (ej: "AL30D", "GD30D")
            cantidad: Cantidad de bonos a vender (valor nominal)
            precio: Precio límite de venta en dólares
            mercado: Mercado donde operar (por defecto bCBA). Usar Markets.*
            plazo: Plazo de liquidación (por defecto t1). Usar SettlementTerms.*
            validez: Fecha de validez de la orden en formato ISO
            
        Returns:
            Objeto ResultadoOrden con el número de operación asignado
            
        Raises:
            IOLAPIError: Si hay error en la operación (bonos insuficientes, etc.)
            
        Example:
            >>> resultado = client.sell_dollar_bond("AL30D", 1000, 36.00)
            >>> if resultado.ok:
            ...     print(f"Venta de bono en USD enviada: {resultado.numero_operacion}")
        """
        from .models import ResultadoOrden
        
        payload = {
            "mercado": mercado,
            "simbolo": simbolo,
            "cantidad": cantidad,
            "precio": precio,
            "plazo": plazo
        }
        
        if validez:
            payload["validez"] = validez
        
        data = self._make_authenticated_request(
            "POST",
            "/operar/VenderEspecieD",
            json=payload
        )
        
        return ResultadoOrden.from_dict(data)
    
    def sell_dollar_bond_raw(
        self,
        simbolo: str,
        cantidad: int,
        precio: float,
        mercado: str = DEFAULT_MARKET,
        plazo: str = DEFAULT_SETTLEMENT_TERM,
        validez: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta una orden de venta de bonos Especie D y retorna JSON crudo
        
        Args:
            simbolo: Símbolo del bono en especie D
            cantidad: Cantidad de bonos a vender
            precio: Precio límite de venta en dólares
            mercado: Mercado donde operar
            plazo: Plazo de liquidación
            validez: Fecha de validez de la orden
            
        Returns:
            Diccionario con la respuesta de la API
            
        Raises:
            IOLAPIError: Si hay error en la operación
        """
        payload = {
            "mercado": mercado,
            "simbolo": simbolo,
            "cantidad": cantidad,
            "precio": precio,
            "plazo": plazo
        }
        
        if validez:
            payload["validez"] = validez
        
        return self._make_authenticated_request(
            "POST",
            "/operar/VenderEspecieD",
            json=payload
        )

    # =========================================================================
    # FONDOS COMUNES DE INVERSIÓN (FCI)
    # =========================================================================
    
    def get_fci_list(self) -> List['FondoComunInversion']:
        """
        Obtiene la lista de todos los Fondos Comunes de Inversión disponibles
        
        Returns:
            Lista de objetos FondoComunInversion con la información de cada fondo
            
        Raises:
            IOLAPIError: Si hay error en la consulta
            
        Example:
            >>> fondos = client.get_fci_list()
            >>> for fondo in fondos[:5]:
            ...     print(f"{fondo.simbolo}: {fondo.nombre}")
        """
        from .models import FondoComunInversion
        
        data = self._make_authenticated_request("GET", "/Titulos/FCI")
        
        # La respuesta puede ser una lista directa o un objeto con 'fondos'
        if isinstance(data, list):
            return [FondoComunInversion.from_dict(fci) for fci in data]
        elif isinstance(data, dict):
            fondos_data = data.get('fondos', data.get('titulos', []))
            return [FondoComunInversion.from_dict(fci) for fci in fondos_data]
        
        return []
    
    def get_fci_list_raw(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de FCI disponibles en formato JSON crudo
        
        Returns:
            Lista de diccionarios con la información de cada fondo
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        data = self._make_authenticated_request("GET", "/Titulos/FCI")
        
        # Normalizar respuesta
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get('fondos', data.get('titulos', []))
        
        return []
    
    def get_fci_detail(self, simbolo: str) -> 'FCIDetalle':
        """
        Obtiene el detalle completo de un Fondo Común de Inversión
        
        Args:
            simbolo: Símbolo del FCI (ej: "ALPHA AHORRO")
            
        Returns:
            Objeto FCIDetalle con la información completa del fondo
            
        Raises:
            IOLAPIError: Si hay error en la consulta o el fondo no existe
            
        Example:
            >>> fondo = client.get_fci_detail("ALPHA AHORRO")
            >>> print(f"Valor cuotaparte: ${fondo.valor_cuotaparte}")
            >>> print(f"Rendimiento anual: {fondo.rendimiento_anio}%")
        """
        from .models import FCIDetalle
        
        data = self._make_authenticated_request("GET", f"/Titulos/FCI/{simbolo}")
        return FCIDetalle.from_dict(data)
    
    def get_fci_detail_raw(self, simbolo: str) -> Dict[str, Any]:
        """
        Obtiene el detalle de un FCI en formato JSON crudo
        
        Args:
            simbolo: Símbolo del FCI
            
        Returns:
            Diccionario con la información del fondo
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        return self._make_authenticated_request("GET", f"/Titulos/FCI/{simbolo}")
    
    def get_fci_types(self) -> List['TipoFondo']:
        """
        Obtiene los tipos de fondos disponibles
        
        Returns:
            Lista de objetos TipoFondo con los tipos de fondos disponibles
            
        Raises:
            IOLAPIError: Si hay error en la consulta
            
        Example:
            >>> tipos = client.get_fci_types()
            >>> for tipo in tipos:
            ...     print(f"{tipo.id}: {tipo.nombre}")
        """
        from .models import TipoFondo
        
        data = self._make_authenticated_request("GET", "/Titulos/FCI/TipoFondos")
        
        # La respuesta puede ser una lista directa o un objeto con 'tipoFondos'
        if isinstance(data, list):
            return [TipoFondo.from_dict(tipo) for tipo in data]
        elif isinstance(data, dict):
            tipos_data = data.get('tipoFondos', data.get('tipos', []))
            return [TipoFondo.from_dict(tipo) for tipo in tipos_data]
        
        return []
    
    def get_fci_types_raw(self) -> List[Dict[str, Any]]:
        """
        Obtiene los tipos de fondos en formato JSON crudo
        
        Returns:
            Lista de diccionarios con los tipos de fondos
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        data = self._make_authenticated_request("GET", "/Titulos/FCI/TipoFondos")
        
        # Normalizar respuesta
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get('tipoFondos', data.get('tipos', []))
        
        return []
    
    def get_fci_managers(self) -> List['AdministradoraFCI']:
        """
        Obtiene la lista de administradoras de FCI
        
        Returns:
            Lista de objetos AdministradoraFCI con las administradoras disponibles
            
        Raises:
            IOLAPIError: Si hay error en la consulta
            
        Example:
            >>> administradoras = client.get_fci_managers()
            >>> for admin in administradoras:
            ...     print(f"{admin.id}: {admin.nombre}")
        """
        from .models import AdministradoraFCI
        
        data = self._make_authenticated_request("GET", "/Titulos/FCI/Administradoras")
        
        # La respuesta puede ser una lista directa o un objeto con 'administradoras'
        if isinstance(data, list):
            return [AdministradoraFCI.from_dict(admin) for admin in data]
        elif isinstance(data, dict):
            admin_data = data.get('administradoras', [])
            return [AdministradoraFCI.from_dict(admin) for admin in admin_data]
        
        return []
    
    def get_fci_managers_raw(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de administradoras de FCI en formato JSON crudo
        
        Returns:
            Lista de diccionarios con las administradoras
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        data = self._make_authenticated_request("GET", "/Titulos/FCI/Administradoras")
        
        # Normalizar respuesta
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get('administradoras', [])
        
        return []
    
    def get_fci_types_by_manager(self, administradora: str) -> List['TipoFondo']:
        """
        Obtiene los tipos de fondos disponibles para una administradora específica
        
        Args:
            administradora: Nombre o ID de la administradora
            
        Returns:
            Lista de objetos TipoFondo disponibles para esa administradora
            
        Raises:
            IOLAPIError: Si hay error en la consulta
            
        Example:
            >>> tipos = client.get_fci_types_by_manager("Alpha")
            >>> for tipo in tipos:
            ...     print(f"{tipo.nombre}")
        """
        from .models import TipoFondo
        
        data = self._make_authenticated_request(
            "GET", 
            f"/Titulos/FCI/Administradoras/{administradora}/TipoFondos"
        )
        
        if isinstance(data, list):
            return [TipoFondo.from_dict(tipo) for tipo in data]
        elif isinstance(data, dict):
            tipos_data = data.get('tipoFondos', data.get('tipos', []))
            return [TipoFondo.from_dict(tipo) for tipo in tipos_data]
        
        return []
    
    def get_fci_types_by_manager_raw(self, administradora: str) -> List[Dict[str, Any]]:
        """
        Obtiene los tipos de fondos por administradora en formato JSON crudo
        
        Args:
            administradora: Nombre o ID de la administradora
            
        Returns:
            Lista de diccionarios con los tipos de fondos
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        data = self._make_authenticated_request(
            "GET", 
            f"/Titulos/FCI/Administradoras/{administradora}/TipoFondos"
        )
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get('tipoFondos', data.get('tipos', []))
        
        return []
    
    def subscribe_fci(
        self,
        simbolo: str,
        monto: float,
        solo_validar: bool = False
    ) -> 'ResultadoFCI':
        """
        Suscribe (invierte) en un Fondo Común de Inversión
        
        IMPORTANTE: Esta operación impacta en el entorno REAL de IOL.
        El monto se debita de la cuenta en pesos y se acreditan cuotapartes.
        
        Args:
            simbolo: Símbolo del FCI a suscribir (ej: "ALPHA AHORRO")
            monto: Monto en pesos a invertir en el fondo
            solo_validar: Si es True, solo valida sin ejecutar la operación
            
        Returns:
            Objeto ResultadoFCI con el resultado de la operación
            
        Raises:
            IOLAPIError: Si hay error en la operación (fondos insuficientes, etc.)
            
        Example:
            >>> # Primero validar
            >>> validacion = client.subscribe_fci("ALPHA AHORRO", 10000, solo_validar=True)
            >>> if validacion.ok:
            ...     # Ejecutar la suscripción real
            ...     resultado = client.subscribe_fci("ALPHA AHORRO", 10000)
            ...     print(f"Operación: {resultado.numero_operacion}")
        """
        from .models import ResultadoFCI
        
        payload = {
            "simbolo": simbolo,
            "monto": monto
        }
        
        if solo_validar:
            payload["soloValidar"] = True
        
        data = self._make_authenticated_request(
            "POST",
            "/operar/suscripcion/fci",
            json=payload
        )
        
        return ResultadoFCI.from_dict(data)
    
    def subscribe_fci_raw(
        self,
        simbolo: str,
        monto: float,
        solo_validar: bool = False
    ) -> Dict[str, Any]:
        """
        Suscribe en un FCI y retorna la respuesta en formato JSON crudo
        
        Args:
            simbolo: Símbolo del FCI a suscribir
            monto: Monto en pesos a invertir
            solo_validar: Si es True, solo valida sin ejecutar
            
        Returns:
            Diccionario con la respuesta de la API
            
        Raises:
            IOLAPIError: Si hay error en la operación
        """
        payload = {
            "simbolo": simbolo,
            "monto": monto
        }
        
        if solo_validar:
            payload["soloValidar"] = True
        
        return self._make_authenticated_request(
            "POST",
            "/operar/suscripcion/fci",
            json=payload
        )
    
    def redeem_fci(
        self,
        simbolo: str,
        cantidad: Optional[float] = None,
        monto: Optional[float] = None,
        solo_validar: bool = False
    ) -> 'ResultadoFCI':
        """
        Rescata (retira) cuotapartes de un Fondo Común de Inversión
        
        IMPORTANTE: Esta operación impacta en el entorno REAL de IOL.
        Las cuotapartes se debitan y el monto se acredita en la cuenta en pesos
        según el plazo de liquidación del fondo (generalmente T+1 a T+3).
        
        Args:
            simbolo: Símbolo del FCI a rescatar (ej: "ALPHA AHORRO")
            cantidad: Cantidad de cuotapartes a rescatar (usar cantidad O monto, no ambos)
            monto: Monto en pesos a rescatar (el sistema calcula las cuotapartes)
            solo_validar: Si es True, solo valida sin ejecutar la operación
            
        Returns:
            Objeto ResultadoFCI con el resultado de la operación
            
        Raises:
            IOLAPIError: Si hay error en la operación (cuotapartes insuficientes, etc.)
            ValueError: Si no se especifica cantidad ni monto, o si se especifican ambos
            
        Example:
            >>> # Rescatar por cantidad de cuotapartes
            >>> resultado = client.redeem_fci("ALPHA AHORRO", cantidad=100.5)
            >>> 
            >>> # O rescatar por monto
            >>> resultado = client.redeem_fci("ALPHA AHORRO", monto=50000)
        """
        from .models import ResultadoFCI
        
        if cantidad is None and monto is None:
            raise ValueError("Debe especificar 'cantidad' o 'monto' para el rescate")
        if cantidad is not None and monto is not None:
            raise ValueError("Especifique solo 'cantidad' o 'monto', no ambos")
        
        payload = {"simbolo": simbolo}
        
        if cantidad is not None:
            payload["cantidad"] = cantidad
        if monto is not None:
            payload["monto"] = monto
        if solo_validar:
            payload["soloValidar"] = True
        
        data = self._make_authenticated_request(
            "POST",
            "/operar/rescate/fci",
            json=payload
        )
        
        return ResultadoFCI.from_dict(data)
    
    def redeem_fci_raw(
        self,
        simbolo: str,
        cantidad: Optional[float] = None,
        monto: Optional[float] = None,
        solo_validar: bool = False
    ) -> Dict[str, Any]:
        """
        Rescata cuotapartes de un FCI y retorna la respuesta en formato JSON crudo
        
        Args:
            simbolo: Símbolo del FCI a rescatar
            cantidad: Cantidad de cuotapartes a rescatar
            monto: Monto en pesos a rescatar
            solo_validar: Si es True, solo valida sin ejecutar
            
        Returns:
            Diccionario con la respuesta de la API
            
        Raises:
            IOLAPIError: Si hay error en la operación
            ValueError: Si no se especifica cantidad ni monto, o si se especifican ambos
        """
        if cantidad is None and monto is None:
            raise ValueError("Debe especificar 'cantidad' o 'monto' para el rescate")
        if cantidad is not None and monto is not None:
            raise ValueError("Especifique solo 'cantidad' o 'monto', no ambos")
        
        payload = {"simbolo": simbolo}
        
        if cantidad is not None:
            payload["cantidad"] = cantidad
        if monto is not None:
            payload["monto"] = monto
        if solo_validar:
            payload["soloValidar"] = True
        
        return self._make_authenticated_request(
            "POST",
            "/operar/rescate/fci",
            json=payload
        )

    # =========================================================================
    # DÓLAR MEP SIMPLIFICADO
    # =========================================================================
    
    def get_mep_buy_estimate(self, monto: float) -> 'EstimacionMEP':
        """
        Obtiene la estimación de montos para compra de dólar MEP simplificado
        
        Esta operación NO ejecuta la compra, solo calcula los montos estimados.
        
        Args:
            monto: Monto en PESOS a invertir para comprar dólares MEP
            
        Returns:
            Objeto EstimacionMEP con los montos y tipo de cambio estimados
            
        Raises:
            IOLAPIError: Si hay error en la consulta
            
        Example:
            >>> estimacion = client.get_mep_buy_estimate(100000)
            >>> print(f"Por ${estimacion.monto_pesos:,.0f} ARS")
            >>> print(f"Recibirás USD {estimacion.monto_dolares:,.2f}")
            >>> print(f"Tipo de cambio: ${estimacion.tipo_cambio:,.2f}")
        """
        from .models import EstimacionMEP
        
        data = self._make_authenticated_request(
            "GET",
            f"/OperatoriaSimplificada/MontosEstimados/{monto}"
        )
        
        return EstimacionMEP.from_dict(data)
    
    def get_mep_buy_estimate_raw(self, monto: float) -> Dict[str, Any]:
        """
        Obtiene la estimación de compra MEP en formato JSON crudo
        
        Args:
            monto: Monto en pesos a invertir
            
        Returns:
            Diccionario con la estimación
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        return self._make_authenticated_request(
            "GET",
            f"/OperatoriaSimplificada/MontosEstimados/{monto}"
        )
    
    def get_mep_sell_estimate(self, monto: float) -> 'EstimacionMEP':
        """
        Obtiene la estimación de montos para venta de dólar MEP simplificado
        
        Esta operación NO ejecuta la venta, solo calcula los montos estimados.
        
        Args:
            monto: Monto en DÓLARES a vender
            
        Returns:
            Objeto EstimacionMEP con los montos y tipo de cambio estimados
            
        Raises:
            IOLAPIError: Si hay error en la consulta
            
        Example:
            >>> estimacion = client.get_mep_sell_estimate(100)
            >>> print(f"Por USD {estimacion.monto_dolares:,.2f}")
            >>> print(f"Recibirás ${estimacion.monto_pesos:,.0f} ARS")
            >>> print(f"Tipo de cambio: ${estimacion.tipo_cambio:,.2f}")
        """
        from .models import EstimacionMEP
        
        data = self._make_authenticated_request(
            "GET",
            f"/OperatoriaSimplificada/VentaMepSimple/MontosEstimados/{monto}"
        )
        
        return EstimacionMEP.from_dict(data)
    
    def get_mep_sell_estimate_raw(self, monto: float) -> Dict[str, Any]:
        """
        Obtiene la estimación de venta MEP en formato JSON crudo
        
        Args:
            monto: Monto en dólares a vender
            
        Returns:
            Diccionario con la estimación
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        return self._make_authenticated_request(
            "GET",
            f"/OperatoriaSimplificada/VentaMepSimple/MontosEstimados/{monto}"
        )
    
    def get_mep_parameters(self, id_tipo_operatoria: int = 1) -> 'ParametrosMEP':
        """
        Obtiene los parámetros de la operatoria MEP simplificada
        
        Args:
            id_tipo_operatoria: ID del tipo de operatoria (por defecto 1 para MEP)
            
        Returns:
            Objeto ParametrosMEP con los límites y configuración
            
        Raises:
            IOLAPIError: Si hay error en la consulta
            
        Example:
            >>> params = client.get_mep_parameters()
            >>> print(f"Monto mínimo: ${params.monto_minimo:,.0f}")
            >>> print(f"Monto máximo: ${params.monto_maximo:,.0f}")
            >>> print(f"Disponible: {params.disponible}")
        """
        from .models import ParametrosMEP
        
        data = self._make_authenticated_request(
            "GET",
            f"/OperatoriaSimplificada/{id_tipo_operatoria}/Parametros"
        )
        
        return ParametrosMEP.from_dict(data)
    
    def get_mep_parameters_raw(self, id_tipo_operatoria: int = 1) -> Dict[str, Any]:
        """
        Obtiene los parámetros de operatoria MEP en formato JSON crudo
        
        Args:
            id_tipo_operatoria: ID del tipo de operatoria
            
        Returns:
            Diccionario con los parámetros
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        return self._make_authenticated_request(
            "GET",
            f"/OperatoriaSimplificada/{id_tipo_operatoria}/Parametros"
        )
    
    def validate_mep_operation(
        self, 
        monto: float, 
        id_tipo_operatoria: int = 1
    ) -> 'ValidacionMEP':
        """
        Valida si una operación MEP puede ejecutarse
        
        Esta operación NO ejecuta la compra, solo valida los parámetros.
        
        Args:
            monto: Monto en pesos a operar
            id_tipo_operatoria: ID del tipo de operatoria (por defecto 1 para MEP)
            
        Returns:
            Objeto ValidacionMEP indicando si la operación es válida
            
        Raises:
            IOLAPIError: Si hay error en la validación
            
        Example:
            >>> validacion = client.validate_mep_operation(100000)
            >>> if validacion.valido:
            ...     print("Operación válida, puede proceder")
            >>> else:
            ...     print(f"Error: {validacion.mensaje}")
        """
        from .models import ValidacionMEP
        
        data = self._make_authenticated_request(
            "GET",
            f"/OperatoriaSimplificada/Validar/{monto}/{id_tipo_operatoria}"
        )
        
        return ValidacionMEP.from_dict(data)
    
    def validate_mep_operation_raw(
        self, 
        monto: float, 
        id_tipo_operatoria: int = 1
    ) -> Dict[str, Any]:
        """
        Valida una operación MEP y retorna JSON crudo
        
        Args:
            monto: Monto en pesos a operar
            id_tipo_operatoria: ID del tipo de operatoria
            
        Returns:
            Diccionario con el resultado de la validación
            
        Raises:
            IOLAPIError: Si hay error en la validación
        """
        return self._make_authenticated_request(
            "GET",
            f"/OperatoriaSimplificada/Validar/{monto}/{id_tipo_operatoria}"
        )
    
    def buy_mep_simplified(
        self,
        monto: float,
        id_tipo_operatoria: int = 1
    ) -> 'ResultadoMEP':
        """
        Ejecuta una compra de dólar MEP simplificada
        
        IMPORTANTE: Esta operación impacta en el entorno REAL de IOL.
        El sistema compra y vende automáticamente el bono para obtener dólares.
        
        Se recomienda usar primero:
        - get_mep_buy_estimate(monto) para ver los montos estimados
        - validate_mep_operation(monto) para validar antes de ejecutar
        
        Args:
            monto: Monto en PESOS a invertir para comprar dólares MEP
            id_tipo_operatoria: ID del tipo de operatoria (por defecto 1)
            
        Returns:
            Objeto ResultadoMEP con el resultado de la operación
            
        Raises:
            IOLAPIError: Si hay error en la operación (fondos insuficientes, mercado cerrado, etc.)
            
        Example:
            >>> # Primero estimar y validar
            >>> estimacion = client.get_mep_buy_estimate(100000)
            >>> print(f"Recibirás aprox USD {estimacion.monto_dolares:,.2f}")
            >>> 
            >>> validacion = client.validate_mep_operation(100000)
            >>> if validacion.valido:
            ...     # Ejecutar la compra
            ...     resultado = client.buy_mep_simplified(100000)
            ...     if resultado.ok:
            ...         print(f"Compra exitosa: {resultado.numero_operacion}")
        """
        from .models import ResultadoMEP
        
        payload = {
            "monto": monto,
            "idTipoOperatoria": id_tipo_operatoria
        }
        
        data = self._make_authenticated_request(
            "POST",
            "/OperatoriaSimplificada/Comprar",
            json=payload
        )
        
        return ResultadoMEP.from_dict(data)
    
    def buy_mep_simplified_raw(
        self,
        monto: float,
        id_tipo_operatoria: int = 1
    ) -> Dict[str, Any]:
        """
        Ejecuta una compra MEP simplificada y retorna JSON crudo
        
        IMPORTANTE: Esta operación impacta en el entorno REAL de IOL.
        
        Args:
            monto: Monto en pesos a invertir
            id_tipo_operatoria: ID del tipo de operatoria
            
        Returns:
            Diccionario con el resultado de la operación
            
        Raises:
            IOLAPIError: Si hay error en la operación
        """
        payload = {
            "monto": monto,
            "idTipoOperatoria": id_tipo_operatoria
        }
        
        return self._make_authenticated_request(
            "POST",
            "/OperatoriaSimplificada/Comprar",
            json=payload
        )

    # =========================================================================
    # CHEQUES DE PAGO DIFERIDO (CPD)
    # =========================================================================
    
    def can_operate_cpd(self) -> 'PuedeOperarCPD':
        """
        Verifica si el usuario puede operar con Cheques de Pago Diferido (CPD)
        
        Esta operación consulta si la cuenta tiene habilitada la operatoria
        de cheques de pago diferido en el mercado.
        
        Returns:
            Objeto PuedeOperarCPD indicando si puede operar y mensajes asociados
            
        Raises:
            IOLAPIError: Si hay error en la consulta
            
        Example:
            >>> habilitacion = client.can_operate_cpd()
            >>> if habilitacion.puede_operar:
            ...     print("Operatoria CPD habilitada")
            >>> else:
            ...     print(f"No habilitado: {habilitacion.motivo}")
        """
        from .models import PuedeOperarCPD
        
        data = self._make_authenticated_request("GET", "/operar/CPD/PuedeOperar")
        return PuedeOperarCPD.from_dict(data)
    
    def can_operate_cpd_raw(self) -> Dict[str, Any]:
        """
        Verifica si puede operar CPD y retorna JSON crudo
        
        Returns:
            Diccionario con el resultado de la verificación
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        return self._make_authenticated_request("GET", "/operar/CPD/PuedeOperar")
    
    def get_cpd_list(
        self, 
        estado: str = "vigentes",
        segmento: str = "avalados"
    ) -> List['ChequeCPD']:
        """
        Obtiene la lista de Cheques de Pago Diferido disponibles
        
        Args:
            estado: Estado de los cheques. Valores posibles:
                   - 'vigentes': Cheques vigentes para operar
                   - 'vencidos': Cheques vencidos
                   - 'todos': Todos los cheques
            segmento: Segmento de los cheques. Valores posibles:
                     - 'avalados': Cheques avalados por SGR
                     - 'patrocinados': Cheques patrocinados
                     - 'garantizados': Cheques garantizados
                     - 'todos': Todos los segmentos
            
        Returns:
            Lista de objetos ChequeCPD con los cheques disponibles
            
        Raises:
            IOLAPIError: Si hay error en la consulta
            
        Example:
            >>> cheques = client.get_cpd_list("vigentes", "avalados")
            >>> for cheque in cheques[:5]:
            ...     print(f"#{cheque.numero_cheque}: ${cheque.importe:,.2f} - Tasa {cheque.tasa}%")
        """
        from .models import ChequeCPD
        
        data = self._make_authenticated_request(
            "GET", 
            f"/operar/CPD/{estado}/{segmento}"
        )
        
        # La respuesta puede ser una lista directa o un objeto con 'cheques'
        if isinstance(data, list):
            return [ChequeCPD.from_dict(cpd) for cpd in data]
        elif isinstance(data, dict):
            cheques_data = data.get('cheques', data.get('items', []))
            return [ChequeCPD.from_dict(cpd) for cpd in cheques_data]
        
        return []
    
    def get_cpd_list_raw(
        self, 
        estado: str = "vigentes",
        segmento: str = "avalados"
    ) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de CPD en formato JSON crudo
        
        Args:
            estado: Estado de los cheques ('vigentes', 'vencidos', 'todos')
            segmento: Segmento ('avalados', 'patrocinados', 'garantizados', 'todos')
            
        Returns:
            Lista de diccionarios con los cheques disponibles
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        data = self._make_authenticated_request(
            "GET", 
            f"/operar/CPD/{estado}/{segmento}"
        )
        
        # Normalizar respuesta
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get('cheques', data.get('items', []))
        
        return []
    
    def get_cpd_commissions(
        self,
        importe: float,
        plazo: int,
        tasa: float
    ) -> 'ComisionesCPD':
        """
        Calcula las comisiones para una operación con CPD
        
        Esta operación NO ejecuta la compra, solo calcula los costos.
        
        Args:
            importe: Importe nominal del cheque en pesos
            plazo: Plazo en días hasta el vencimiento
            tasa: Tasa de descuento anual en porcentaje
            
        Returns:
            Objeto ComisionesCPD con el detalle de costos
            
        Raises:
            IOLAPIError: Si hay error en el cálculo
            
        Example:
            >>> comisiones = client.get_cpd_commissions(100000, 90, 45.5)
            >>> print(f"Comisión: ${comisiones.comision:,.2f}")
            >>> print(f"Total gastos: ${comisiones.total_gastos:,.2f}")
        """
        from .models import ComisionesCPD
        
        data = self._make_authenticated_request(
            "GET",
            f"/operar/CPD/Comisiones/{importe}/{plazo}/{tasa}"
        )
        
        return ComisionesCPD.from_dict(data)
    
    def get_cpd_commissions_raw(
        self,
        importe: float,
        plazo: int,
        tasa: float
    ) -> Dict[str, Any]:
        """
        Calcula las comisiones para CPD y retorna JSON crudo
        
        Args:
            importe: Importe nominal del cheque
            plazo: Plazo en días hasta el vencimiento
            tasa: Tasa de descuento anual
            
        Returns:
            Diccionario con el detalle de comisiones
            
        Raises:
            IOLAPIError: Si hay error en el cálculo
        """
        return self._make_authenticated_request(
            "GET",
            f"/operar/CPD/Comisiones/{importe}/{plazo}/{tasa}"
        )
    
    def operate_cpd(
        self,
        numero_cheque: str,
        precio: float,
        cantidad: int = 1
    ) -> 'ResultadoCPD':
        """
        Ejecuta una operación de compra de Cheque de Pago Diferido
        
        IMPORTANTE: Esta operación impacta en el entorno REAL de IOL.
        Al comprar un CPD, se debita el monto de la cuenta y se adquiere
        el derecho a cobrar el cheque en la fecha de vencimiento.
        
        Se recomienda usar primero:
        - can_operate_cpd() para verificar habilitación
        - get_cpd_list() para ver cheques disponibles
        - get_cpd_commissions() para calcular costos
        
        Args:
            numero_cheque: Número del cheque a comprar
            precio: Precio de compra (valor presente después del descuento)
            cantidad: Cantidad de cheques a comprar (normalmente 1)
            
        Returns:
            Objeto ResultadoCPD con el resultado de la operación
            
        Raises:
            IOLAPIError: Si hay error en la operación (fondos insuficientes,
                        cheque no disponible, cuenta no habilitada, etc.)
            
        Example:
            >>> # Verificar habilitación primero
            >>> if client.can_operate_cpd().puede_operar:
            ...     # Ver cheques disponibles
            ...     cheques = client.get_cpd_list("vigentes", "avalados")
            ...     if cheques:
            ...         cheque = cheques[0]
            ...         # Comprar el cheque
            ...         resultado = client.operate_cpd(
            ...             cheque.numero_cheque, 
            ...             cheque.valor_presente
            ...         )
            ...         if resultado.ok:
            ...             print(f"Compra exitosa: Op #{resultado.numero_operacion}")
        """
        from .models import ResultadoCPD
        
        payload = {
            "numeroCheque": numero_cheque,
            "precio": precio,
            "cantidad": cantidad
        }
        
        data = self._make_authenticated_request(
            "POST",
            "/operar/CPD",
            json=payload
        )
        
        return ResultadoCPD.from_dict(data)
    
    def operate_cpd_raw(
        self,
        numero_cheque: str,
        precio: float,
        cantidad: int = 1
    ) -> Dict[str, Any]:
        """
        Ejecuta una compra de CPD y retorna JSON crudo
        
        IMPORTANTE: Esta operación impacta en el entorno REAL de IOL.
        
        Args:
            numero_cheque: Número del cheque a comprar
            precio: Precio de compra
            cantidad: Cantidad de cheques
            
        Returns:
            Diccionario con el resultado de la operación
            
        Raises:
            IOLAPIError: Si hay error en la operación
        """
        payload = {
            "numeroCheque": numero_cheque,
            "precio": precio,
            "cantidad": cantidad
        }
        
        return self._make_authenticated_request(
            "POST",
            "/operar/CPD",
            json=payload
        )

    # =========================================================================
    # ASESORES
    # =========================================================================
    
    def get_advisor_movements(
        self,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        id_cliente: Optional[str] = None,
        pagina: int = 1,
        registros_por_pagina: int = 50
    ) -> 'MovimientosAsesor':
        """
        Obtiene los movimientos históricos de clientes del asesor
        
        NOTA: Este endpoint requiere que el usuario tenga rol de asesor.
        Si no tiene permisos, la API devolverá un error.
        
        Args:
            fecha_desde: Fecha desde en formato 'YYYY-MM-DD'
            fecha_hasta: Fecha hasta en formato 'YYYY-MM-DD'
            id_cliente: ID del cliente específico (opcional, si no se especifica trae todos)
            pagina: Número de página para paginación (por defecto 1)
            registros_por_pagina: Cantidad de registros por página (por defecto 50)
            
        Returns:
            Objeto MovimientosAsesor con los movimientos de clientes
            
        Raises:
            IOLAPIError: Si hay error en la consulta o no tiene permisos de asesor
            
        Example:
            >>> movimientos = client.get_advisor_movements(
            ...     fecha_desde="2025-01-01",
            ...     fecha_hasta="2025-01-31"
            ... )
            >>> for mov in movimientos.movimientos[:5]:
            ...     print(f"{mov.fecha}: {mov.tipo_movimiento} - ${mov.monto:,.2f}")
        """
        from .models import MovimientosAsesor
        
        payload = {
            "pagina": pagina,
            "registrosPorPagina": registros_por_pagina
        }
        
        if fecha_desde:
            payload["fechaDesde"] = fecha_desde
        if fecha_hasta:
            payload["fechaHasta"] = fecha_hasta
        if id_cliente:
            payload["idCliente"] = id_cliente
        
        data = self._make_authenticated_request(
            "POST",
            "/Asesor/Movimientos",
            json=payload
        )
        
        return MovimientosAsesor.from_dict(data)
    
    def get_advisor_movements_raw(
        self,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        id_cliente: Optional[str] = None,
        pagina: int = 1,
        registros_por_pagina: int = 50
    ) -> Dict[str, Any]:
        """
        Obtiene los movimientos de clientes del asesor en formato JSON crudo
        
        Args:
            fecha_desde: Fecha desde en formato 'YYYY-MM-DD'
            fecha_hasta: Fecha hasta en formato 'YYYY-MM-DD'
            id_cliente: ID del cliente específico
            pagina: Número de página
            registros_por_pagina: Cantidad de registros por página
            
        Returns:
            Diccionario con los movimientos
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        payload = {
            "pagina": pagina,
            "registrosPorPagina": registros_por_pagina
        }
        
        if fecha_desde:
            payload["fechaDesde"] = fecha_desde
        if fecha_hasta:
            payload["fechaHasta"] = fecha_hasta
        if id_cliente:
            payload["idCliente"] = id_cliente
        
        return self._make_authenticated_request(
            "POST",
            "/Asesor/Movimientos",
            json=payload
        )
    
    def get_investor_test_questions(self) -> 'TestInversor':
        """
        Obtiene las preguntas del test de perfil de inversor
        
        NOTA: Este endpoint requiere que el usuario tenga rol de asesor.
        
        Las preguntas se usan para calcular el perfil de inversión de un cliente.
        Cada pregunta tiene opciones de respuesta con valores asociados.
        
        Returns:
            Objeto TestInversor con todas las preguntas y opciones
            
        Raises:
            IOLAPIError: Si hay error en la consulta o no tiene permisos
            
        Example:
            >>> test = client.get_investor_test_questions()
            >>> print(f"Test con {len(test.preguntas)} preguntas")
            >>> for pregunta in test.preguntas:
            ...     print(f"P{pregunta.numero}: {pregunta.texto}")
            ...     for opcion in pregunta.opciones or []:
            ...         print(f"  [{opcion.id}] {opcion.texto}")
        """
        from .models import TestInversor
        
        data = self._make_authenticated_request("GET", "/asesores/test-inversor")
        return TestInversor.from_dict(data)
    
    def get_investor_test_questions_raw(self) -> Dict[str, Any]:
        """
        Obtiene las preguntas del test de inversor en formato JSON crudo
        
        Returns:
            Diccionario o lista con las preguntas del test
            
        Raises:
            IOLAPIError: Si hay error en la consulta
        """
        return self._make_authenticated_request("GET", "/asesores/test-inversor")
    
    def calculate_investor_profile(
        self,
        respuestas: List[Dict[str, int]]
    ) -> 'PerfilInversor':
        """
        Calcula el perfil de inversor basado en las respuestas al test
        
        NOTA: Este endpoint requiere que el usuario tenga rol de asesor.
        Esta operación solo calcula el perfil, NO lo guarda en ningún cliente.
        
        Args:
            respuestas: Lista de respuestas, cada una con:
                       - 'idPregunta': ID de la pregunta
                       - 'idRespuesta': ID de la respuesta seleccionada
                       Ejemplo: [{"idPregunta": 1, "idRespuesta": 3}, ...]
            
        Returns:
            Objeto PerfilInversor con el perfil calculado
            
        Raises:
            IOLAPIError: Si hay error en el cálculo o no tiene permisos
            
        Example:
            >>> # Primero obtener las preguntas
            >>> test = client.get_investor_test_questions()
            >>> 
            >>> # Luego construir las respuestas
            >>> respuestas = [
            ...     {"idPregunta": 1, "idRespuesta": 2},
            ...     {"idPregunta": 2, "idRespuesta": 3},
            ...     # ... más respuestas
            ... ]
            >>> 
            >>> perfil = client.calculate_investor_profile(respuestas)
            >>> print(f"Perfil calculado: {perfil.perfil}")
        """
        from .models import PerfilInversor
        
        payload = {
            "respuestas": respuestas
        }
        
        data = self._make_authenticated_request(
            "POST",
            "/asesores/test-inversor",
            json=payload
        )
        
        return PerfilInversor.from_dict(data)
    
    def calculate_investor_profile_raw(
        self,
        respuestas: List[Dict[str, int]]
    ) -> Dict[str, Any]:
        """
        Calcula el perfil de inversor y retorna JSON crudo
        
        Args:
            respuestas: Lista de respuestas al test
            
        Returns:
            Diccionario con el perfil calculado
            
        Raises:
            IOLAPIError: Si hay error en el cálculo
        """
        payload = {
            "respuestas": respuestas
        }
        
        return self._make_authenticated_request(
            "POST",
            "/asesores/test-inversor",
            json=payload
        )
    
    def save_investor_profile(
        self,
        id_cliente: str,
        respuestas: List[Dict[str, int]]
    ) -> 'PerfilInversor':
        """
        Calcula y guarda el perfil de inversor de un cliente asesorado
        
        IMPORTANTE: Esta operación GUARDA el perfil en el cliente.
        Solo usar cuando se quiera actualizar el perfil del cliente.
        
        NOTA: Este endpoint requiere que el usuario tenga rol de asesor
        y que el cliente esté vinculado a su cartera de asesorados.
        
        Args:
            id_cliente: ID del cliente asesorado donde guardar el perfil
            respuestas: Lista de respuestas, cada una con:
                       - 'idPregunta': ID de la pregunta
                       - 'idRespuesta': ID de la respuesta seleccionada
            
        Returns:
            Objeto PerfilInversor con el perfil calculado y guardado
            
        Raises:
            IOLAPIError: Si hay error o el cliente no pertenece al asesor
            
        Example:
            >>> # Calcular y guardar perfil de un cliente
            >>> respuestas = [
            ...     {"idPregunta": 1, "idRespuesta": 2},
            ...     {"idPregunta": 2, "idRespuesta": 1},
            ...     # ... todas las respuestas
            ... ]
            >>> 
            >>> # CUIDADO: Esto modifica el perfil del cliente
            >>> perfil = client.save_investor_profile("123456", respuestas)
            >>> if perfil.guardado:
            ...     print(f"Perfil {perfil.perfil} guardado para cliente {perfil.id_cliente}")
        """
        from .models import PerfilInversor
        
        payload = {
            "respuestas": respuestas
        }
        
        data = self._make_authenticated_request(
            "POST",
            f"/asesores/test-inversor/{id_cliente}",
            json=payload
        )
        
        # Marcar como guardado y agregar id_cliente
        result = PerfilInversor.from_dict(data)
        result.guardado = True
        result.id_cliente = id_cliente
        return result
    
    def save_investor_profile_raw(
        self,
        id_cliente: str,
        respuestas: List[Dict[str, int]]
    ) -> Dict[str, Any]:
        """
        Calcula y guarda el perfil de inversor en formato JSON crudo
        
        IMPORTANTE: Esta operación GUARDA el perfil en el cliente.
        
        Args:
            id_cliente: ID del cliente asesorado
            respuestas: Lista de respuestas al test
            
        Returns:
            Diccionario con el resultado
            
        Raises:
            IOLAPIError: Si hay error en la operación
        """
        payload = {
            "respuestas": respuestas
        }
        
        return self._make_authenticated_request(
            "POST",
            f"/asesores/test-inversor/{id_cliente}",
            json=payload
        )
    
    def advisor_sell_dollar_bond(
        self,
        id_cliente: str,
        simbolo: str,
        cantidad: int,
        precio: float,
        mercado: str = DEFAULT_MARKET,
        plazo: str = DEFAULT_SETTLEMENT_TERM,
        validez: Optional[str] = None
    ) -> 'ResultadoOperacionAsesor':
        """
        Ejecuta una orden de venta de bonos Especie D como asesor para un cliente
        
        IMPORTANTE: Esta operación impacta en el entorno REAL de IOL.
        La venta se ejecuta en la cuenta del cliente asesorado, no del asesor.
        
        NOTA: Requiere rol de asesor y que el cliente esté vinculado.
        
        Args:
            id_cliente: ID del cliente asesorado donde ejecutar la venta
            simbolo: Símbolo del bono en especie D (ej: "AL30D", "GD30D")
            cantidad: Cantidad de bonos a vender (valor nominal)
            precio: Precio límite de venta en dólares
            mercado: Mercado donde operar (por defecto bCBA). Usar Markets.*
            plazo: Plazo de liquidación (por defecto t1). Usar SettlementTerms.*
            validez: Fecha de validez de la orden en formato ISO
            
        Returns:
            Objeto ResultadoOperacionAsesor con el número de operación
            
        Raises:
            IOLAPIError: Si hay error en la operación (bonos insuficientes, etc.)
            
        Example:
            >>> # CUIDADO: Esto ejecuta una venta real en la cuenta del cliente
            >>> # resultado = client.advisor_sell_dollar_bond(
            >>> #     id_cliente="123456",
            >>> #     simbolo="AL30D",
            >>> #     cantidad=1000,
            >>> #     precio=36.00
            >>> # )
            >>> # if resultado.ok:
            >>> #     print(f"Venta ejecutada: Op #{resultado.numero_operacion}")
        """
        from .models import ResultadoOperacionAsesor
        
        payload = {
            "idClienteAsesorado": id_cliente,
            "mercado": mercado,
            "simbolo": simbolo,
            "cantidad": cantidad,
            "precio": precio,
            "plazo": plazo
        }
        
        if validez:
            payload["validez"] = validez
        
        data = self._make_authenticated_request(
            "POST",
            "/asesores/operar/VenderEspecieD",
            json=payload
        )
        
        result = ResultadoOperacionAsesor.from_dict(data)
        result.id_cliente = id_cliente
        result.simbolo = simbolo
        result.cantidad = cantidad
        result.precio = precio
        return result
    
    def advisor_sell_dollar_bond_raw(
        self,
        id_cliente: str,
        simbolo: str,
        cantidad: int,
        precio: float,
        mercado: str = DEFAULT_MARKET,
        plazo: str = DEFAULT_SETTLEMENT_TERM,
        validez: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta venta de bonos Especie D como asesor en formato JSON crudo
        
        IMPORTANTE: Esta operación impacta en el entorno REAL de IOL.
        
        Args:
            id_cliente: ID del cliente asesorado
            simbolo: Símbolo del bono en especie D
            cantidad: Cantidad de bonos a vender
            precio: Precio límite de venta en dólares
            mercado: Mercado donde operar
            plazo: Plazo de liquidación
            validez: Fecha de validez de la orden
            
        Returns:
            Diccionario con el resultado de la operación
            
        Raises:
            IOLAPIError: Si hay error en la operación
        """
        payload = {
            "idClienteAsesorado": id_cliente,
            "mercado": mercado,
            "simbolo": simbolo,
            "cantidad": cantidad,
            "precio": precio,
            "plazo": plazo
        }
        
        if validez:
            payload["validez"] = validez
        
        return self._make_authenticated_request(
            "POST",
            "/asesores/operar/VenderEspecieD",
            json=payload
        )