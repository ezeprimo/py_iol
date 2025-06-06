"""
Cliente para la API de Invertir Online (IOL)
"""
import httpx
from typing import Optional, Dict, Any, List, List
from cachetools import cached, TTLCache
from .constants import TOKEN_URL, API_BASE_URL, USER_AGENT, DEFAULT_MARKET, DEFAULT_SETTLEMENT_TERM
from .models import CotizacionTitulo, DatosTitulo, OpcionTitulo, InstrumentoPais, CotizacionesMasivas, CotizacionDetallada


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