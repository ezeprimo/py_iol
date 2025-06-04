"""
Cliente para la API de Invertir Online (IOL)
"""
import httpx
from typing import Optional, Dict, Any
from cachetools import cached, TTLCache
from .constants import TOKEN_URL, API_BASE_URL, USER_AGENT


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
    
    def get_stock_quote(self, symbol: str, market: str = "bCBA") -> Dict[str, Any]:
        """
        Obtiene la cotización actual de una acción
        
        Args:
            symbol: Símbolo de la acción
            market: Mercado (por defecto bCBA)
            
        Returns:
            Cotización actual de la acción
        """
        return self._make_authenticated_request("GET", f"/{market}/Titulos/{symbol}/Cotizacion")