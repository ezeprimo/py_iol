# pyIOL - Guia para Agentes de IA

## Descripcion del Proyecto

**pyIOL** es una libreria cliente Python para interactuar con la API REST de **Invertir Online (IOL)**, una plataforma de trading e inversiones de Argentina. Permite automatizar consultas de cotizaciones, datos de titulos, opciones financieras y mas.

| Campo | Valor |
|-------|-------|
| Nombre del paquete | `pyiol` |
| Version | 0.1.0 |
| Python requerido | >=3.8 |
| Autor | Ezequiel Primon |
| Repositorio | https://github.com/ezeprimo/py_iol.git |

---

## Estructura del Proyecto

```
py_iol/
|-- pyproject.toml          # Configuracion del proyecto y dependencias
|-- uv.lock                  # Lock file de dependencias (gestor uv)
|-- .env.example             # Ejemplo de credenciales
|-- .env                     # Credenciales reales (NO COMMITEAR)
|
|-- pyIol/                   # Paquete principal
|   |-- __init__.py          # Exports publicos
|   |-- client.py            # Cliente HTTP para la API de IOL
|   |-- models.py            # Dataclasses para respuestas tipadas
|   |-- constants.py         # URLs, mercados, plazos
|
|-- xdoc/                    # Documentacion y ejemplos (ignorado por git)
|   |-- iol_api_doc.MD       # Documentacion completa de la API
|   |-- test_pyiol.ipynb     # Notebook de pruebas interactivo
|   |-- ejemplo_modelos.py   # Ejemplo de uso de modelos
|   |-- TROUBLESHOOTING.md   # Solucion de problemas
```

---

## Dependencias

### Runtime
- `httpx>=0.24.0` - Cliente HTTP asincrono/sincrono
- `cachetools>=5.0.0` - Cache TTL para tokens

### Desarrollo
- `jupyter>=1.0.0` - Notebooks para pruebas
- `python-dotenv>=1.0.0` - Variables de entorno

---

## Arquitectura

### Patron de Diseno
Cliente API con Modelos de Datos Tipados:

1. **`IOLClient`** - Clase principal:
   - Autenticacion OAuth2 con cache de tokens (TTL 14.5 min)
   - Context manager (`with` statement)
   - Metodos para cada endpoint
   - Versiones "raw" (dict) y tipadas (dataclass)

2. **Modelos** - Dataclasses tipadas:
   - Cotizaciones: `CotizacionTitulo`, `CotizacionDetallada`, `Punta`, `PuntasCotizacion`, `TituloCotizacion`, `CotizacionesMasivas`
   - Titulos: `DatosTitulo`, `OpcionTitulo`, `InstrumentoPais`
   - Perfil: `DatosPerfil`
   - Cuenta: `EstadoCuenta`, `Estadistica`, `Cuenta`, `Saldo`, `Portafolio`, `TituloPortafolio`
   - Operaciones: `Operacion`, `OperacionDetalle`, `OrdenOperacion`, `ResultadoOrden`
   - FCI: `FondoComunInversion`, `FCIDetalle`, `TipoFondo`, `AdministradoraFCI`
   - Trading: `OrdenEspecieD`, `OrdenFCI`, `ResultadoFCI`
   - MEP: `EstimacionMEP`, `ParametrosMEP`, `ValidacionMEP`, `ResultadoMEP`
   - CPD: `PuedeOperarCPD`, `ChequeCPD`, `ComisionesCPD`, `OrdenCPD`, `ResultadoCPD`

3. **Constantes**:
   - `Markets` - Mercados (BCBA, NYSE, NASDAQ, AMEX, BCS, ROFX)
   - `SettlementTerms` - Plazos (T0, T1, T2, T3)

### Flujo de Autenticacion
```
1. IOLClient(username, password)
2. POST /token obtiene access_token
3. Token cacheado 14.5 min (expira a los 15 min)
4. Requests usan Bearer token
```

---

## Endpoints Implementados

| Metodo | Descripcion | Retorna |
|--------|-------------|---------|
| `test_authentication()` | Prueba autenticacion | `bool` |
| `get_profile_data()` | Datos del perfil | `DatosPerfil` |
| `get_mep_dollar_rate(symbol)` | Dolar MEP | `dict` |
| `get_stock_quote(symbol, market, settlement_term)` | Cotizacion de accion | `CotizacionTitulo` |
| `get_stock_data(symbol, market)` | Datos del titulo | `DatosTitulo` |
| `get_stock_options(symbol, market)` | Opciones de un titulo | `List[OpcionTitulo]` |
| `get_market_instruments(pais)` | Instrumentos por pais | `List[InstrumentoPais]` |
| `get_massive_quotes(instrumento, pais)` | Cotizaciones masivas | `CotizacionesMasivas` |
| `get_panel_quotes(instrumento, panel, pais)` | Panel de cotizaciones | `CotizacionesMasivas` |
| `get_stock_quote_detailed(simbolo, mercado)` | Cotizacion detallada | `CotizacionDetallada` |

> Cada metodo tiene su version `_raw()` que retorna `dict` en lugar del modelo tipado.

---

## Como Instalar

```bash
# Clonar repositorio
git clone https://github.com/ezeprimo/py_iol.git
cd py_iol

# Instalar con uv (recomendado)
uv sync

# O con pip en modo desarrollo
pip install -e ".[dev]"
```

---

## Configuracion

```bash
# Copiar ejemplo de credenciales
cp .env.example .env

# Editar .env con credenciales de IOL
IOL_USERNAME=tu_usuario_iol
IOL_PASSWORD=tu_password_iol
```

---

## Como Probar

### Uso Basico en Python
```python
from pyIol import IOLClient, Markets, SettlementTerms

with IOLClient("usuario", "password") as client:
    # Cotizacion de GGAL
    cotizacion = client.get_stock_quote("GGAL")
    print(f"Precio: ${cotizacion.ultimo_precio}")
    print(f"Variacion: {cotizacion.variacion}%")
    
    # Con plazo T2
    cotizacion_t2 = client.get_stock_quote("GGAL", settlement_term=SettlementTerms.T2)
    
    # Todas las acciones argentinas
    cotizaciones = client.get_massive_quotes("acciones", "argentina")
    for titulo in cotizaciones.titulos[:5]:
        print(f"{titulo.simbolo}: ${titulo.ultimo_precio}")
```

### Ejecutar Ejemplos
```bash
cd xdoc
uv run python ejemplo_modelos.py
uv run python ejemplo_mercados_plazos.py
```

### Notebook Interactivo
```bash
cd xdoc
jupyter notebook test_pyiol.ipynb
```

### Verificar Autenticacion
```python
from pyIol import IOLClient
from dotenv import load_dotenv
import os

load_dotenv()
with IOLClient(os.getenv("IOL_USERNAME"), os.getenv("IOL_PASSWORD")) as client:
    print("Autenticacion:", "OK" if client.test_authentication() else "FALLO")
```

---

## Pautas para Agentes de IA

### Archivos Clave a Modificar

| Archivo | Cuando Modificar |
|---------|------------------|
| `pyIol/client.py` | Agregar nuevos endpoints |
| `pyIol/models.py` | Agregar nuevos modelos de datos |
| `pyIol/constants.py` | Agregar constantes nuevas |
| `pyIol/__init__.py` | Exportar nuevas clases/funciones |

### Patron para Agregar un Nuevo Endpoint

```python
# En models.py - Crear el modelo
@dataclass
class NuevoModelo:
    campo1: str
    campo2: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NuevoModelo":
        return cls(
            campo1=data.get("campo1", ""),
            campo2=data.get("campo2")
        )

# En client.py - Agregar metodo tipado
def get_nuevo_endpoint(self, param: str) -> NuevoModelo:
    """
    Descripcion del endpoint.
    
    Args:
        param: Descripcion del parametro
        
    Returns:
        Objeto NuevoModelo con los datos
    """
    data = self._make_authenticated_request("GET", f"/api/v2/endpoint/{param}")
    return NuevoModelo.from_dict(data)

# En client.py - Agregar metodo raw
def get_nuevo_endpoint_raw(self, param: str) -> Dict[str, Any]:
    """Version JSON del endpoint."""
    return self._make_authenticated_request("GET", f"/api/v2/endpoint/{param}")

# En __init__.py - Exportar el modelo
from .models import NuevoModelo
```

### Convenciones de Codigo

1. **Nombres de metodos**: Usar `get_` para lecturas, snake_case, en ingles
2. **Documentacion**: Docstrings en espanol o ingles, consistente con el resto
3. **Tipado**: Usar type hints en todos los parametros y retornos
4. **Modelos**: Todos los modelos deben tener `from_dict()` como classmethod
5. **Versiones raw**: Todo endpoint tipado debe tener su version `_raw()`

### Notas Importantes

- **NO COMMITEAR** `.env` - contiene credenciales
- La carpeta `xdoc/` esta en `.gitignore`
- Los tokens expiran en 15 minutos, el cache renueva a los 14.5
- La API puede tener rate limiting (no documentado)
- Mercados como NYSE/NASDAQ pueden requerir permisos especiales
- Usar `IOLAPIError` para errores de la API

### Documentacion de Referencia

- **API de IOL**: `xdoc/iol_api_doc.MD` - Documentacion completa de endpoints
- **Troubleshooting**: `xdoc/TROUBLESHOOTING.md` - Problemas comunes
- **Ejemplos**: `xdoc/ejemplo_*.py` - Scripts de ejemplo

### Mercados Disponibles

```python
Markets.BCBA    # "bCBA" - Bolsa de Buenos Aires
Markets.NYSE    # "nYSE" - New York Stock Exchange
Markets.NASDAQ  # "nASDAQ"
Markets.AMEX    # "aMEX"
Markets.BCS     # "bCS" - Bolsa de Santiago
Markets.ROFX    # "rOFX" - Rosario Futures Exchange
```

### Plazos de Liquidacion

```python
SettlementTerms.T0  # "t0" - Inmediata
SettlementTerms.T1  # "t1" - 1 dia (default)
SettlementTerms.T2  # "t2" - 2 dias
SettlementTerms.T3  # "t3" - 3 dias
```

---

## Comandos Utiles

```bash
# Sincronizar dependencias
uv sync

# Ejecutar script
uv run python script.py

# Instalar en modo desarrollo
pip install -e ".[dev]"

# Ver estructura del proyecto
tree -I "__pycache__|.venv|.git"
```

---

## Errores Comunes

### ImportError de modelos
Si los cambios en modelos no se reflejan, limpiar cache:
```bash
rm -rf pyIol/__pycache__
```

### Error de autenticacion
Verificar que `.env` tenga credenciales correctas y que la cuenta IOL este activa.

### Timeout en requests
La API de IOL puede ser lenta. Considerar aumentar timeout en httpx.

---

## Historial de Desarrollo

El proyecto ha evolucionado agregando endpoints progresivamente:
1. Autenticacion y cotizacion basica
2. Constantes de mercados y plazos
3. Datos de titulos
4. Opciones de titulos
5. Instrumentos por pais
6. Cotizaciones masivas
7. Paneles de cotizaciones
8. Cotizaciones detalladas

---

## Contacto

- **Autor**: Ezequiel Primon
- **Email**: ezeprimo@gmail.com
- **GitHub**: https://github.com/ezeprimo/py_iol
