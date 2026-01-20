# pyIOL

Cliente Python para interactuar con la API REST de **Invertir Online (IOL)**, una plataforma de trading e inversiones de Argentina.

## Disclaimer

> **ADVERTENCIA IMPORTANTE**
>
> Esta libreria **NO es oficial** de Invertir Online. Es un proyecto independiente desarrollado por la comunidad.
>
> **El desarrollador NO se hace responsable** por cualquier dano, perdida financiera, o perjuicio que pueda ocasionar el uso de esta libreria, incluyendo pero no limitado a:
> - Perdidas economicas por operaciones ejecutadas
> - Errores en la interpretacion de datos
> - Fallos en la ejecucion de ordenes
> - Cualquier otro problema derivado del uso de este software
>
> Esta libreria **puede contener bugs no descubiertos**. Usela bajo su propia responsabilidad y con extrema precaucion, especialmente en operaciones que involucren dinero real.
>
> **Se recomienda encarecidamente** probar primero en el entorno sandbox de IOL antes de usar en produccion.

## Objetivos

- Proporcionar una interfaz Python simple y tipada para la API de IOL
- Facilitar la automatizacion de consultas de cotizaciones y datos de mercado
- Permitir la gestion programatica de portafolios e inversiones
- Ofrecer modelos de datos tipados para una mejor experiencia de desarrollo

## Caracteristicas

- Autenticacion OAuth2 con cache automatico de tokens
- Modelos de datos tipados (dataclasses) para todas las respuestas
- Soporte para multiples mercados (BCBA, NYSE, NASDAQ, etc.)
- Metodos para cotizaciones, portafolio, operaciones, FCI, y mas
- Context manager para manejo seguro de conexiones

## Requisitos

- Python >= 3.8
- Cuenta activa en Invertir Online con API habilitada

## Instalacion

### Desde el repositorio

```bash
# Clonar el repositorio
git clone https://github.com/ezeprimo/py_iol.git
cd py_iol

# Instalar con uv (recomendado)
uv sync

# O con pip en modo desarrollo
pip install -e ".[dev]"
```

### Dependencias

- `httpx>=0.24.0` - Cliente HTTP
- `cachetools>=5.0.0` - Cache para tokens

## Configuracion

1. Crear archivo `.env` en la raiz del proyecto:

```bash
cp .env.example .env
```

2. Editar `.env` con tus credenciales de IOL:

```env
IOL_USERNAME=tu_usuario_iol
IOL_PASSWORD=tu_password_iol
```

## Uso Basico

### Consultar Cotizaciones

```python
from pyIol import IOLClient, Markets, SettlementTerms

# Crear cliente (usa context manager para cerrar conexion automaticamente)
with IOLClient("usuario", "password") as client:
    # Cotizacion de GGAL
    cotizacion = client.get_stock_quote("GGAL")
    print(f"GGAL: ${cotizacion.ultimo_precio}")
    print(f"Variacion: {cotizacion.variacion}%")
    
    # Cotizacion con plazo T2
    cotizacion_t2 = client.get_stock_quote(
        "GGAL", 
        settlement_term=SettlementTerms.T2
    )
```

### Consultar Portafolio

```python
from pyIol import IOLClient, Countries

with IOLClient("usuario", "password") as client:
    # Obtener portafolio de Argentina
    portafolio = client.get_portfolio(Countries.ARGENTINA)
    
    print(f"Total valorizado: ${portafolio.total_valorizado:,.2f}")
    print(f"Ganancia total: ${portafolio.total_ganancia:,.2f}")
    
    # Listar posiciones
    for titulo in portafolio.todos_los_titulos:
        print(f"{titulo.simbolo}: {titulo.cantidad} unidades")
        print(f"  Ganancia: {titulo.ganancia_porcentaje:+.2f}%")
```

### Cotizaciones Masivas

```python
from pyIol import IOLClient

with IOLClient("usuario", "password") as client:
    # Todas las acciones argentinas
    cotizaciones = client.get_massive_quotes("acciones", "argentina")
    
    for titulo in cotizaciones.titulos[:5]:
        print(f"{titulo.simbolo}: ${titulo.ultimo_precio}")
    
    # Panel MERVAL
    merval = client.get_panel_quotes("acciones", "merval", "argentina")
    for titulo in merval.titulos:
        print(f"{titulo.simbolo}: {titulo.variacion_porcentual:+.2f}%")
```

### Consultar Operaciones

```python
from pyIol import IOLClient, OperationStates
from datetime import datetime, timedelta

with IOLClient("usuario", "password") as client:
    # Operaciones de los ultimos 30 dias
    operaciones = client.get_operations(
        estado=OperationStates.ALL,
        fecha_desde=datetime.now() - timedelta(days=30),
        fecha_hasta=datetime.now()
    )
    
    for op in operaciones:
        print(f"#{op.numero}: {op.tipo} {op.simbolo} - {op.estado}")
```

### Usando Variables de Entorno

```python
import os
from dotenv import load_dotenv
from pyIol import IOLClient

load_dotenv()

with IOLClient(
    os.getenv("IOL_USERNAME"), 
    os.getenv("IOL_PASSWORD")
) as client:
    if client.test_authentication():
        print("Autenticacion exitosa!")
```

## Estructura del Proyecto

```
py_iol/
├── pyIol/                  # Paquete principal
│   ├── __init__.py         # Exports publicos
│   ├── client.py           # Cliente HTTP para la API
│   ├── models.py           # Dataclasses para respuestas
│   └── constants.py        # URLs, mercados, plazos
├── xdoc/                   # Documentacion y ejemplos
│   ├── notebooks/          # Jupyter notebooks de prueba
│   └── iol_api_doc.MD      # Documentacion de la API
├── pyproject.toml          # Configuracion del proyecto
├── .env.example            # Ejemplo de credenciales
└── README.md               # Este archivo
```

## Endpoints Disponibles

| Categoria | Metodos |
|-----------|---------|
| Autenticacion | `test_authentication()` |
| Perfil | `get_profile_data()` |
| Cotizaciones | `get_stock_quote()`, `get_stock_data()`, `get_stock_options()`, `get_massive_quotes()`, `get_panel_quotes()`, `get_stock_quote_detailed()` |
| Cuenta | `get_account_status()`, `get_portfolio()` |
| Operaciones | `get_operations()`, `get_operation_detail()` |
| Trading | `buy_stock()`, `sell_stock()` |
| FCI | `get_fci_list()`, `get_fci_detail()`, `subscribe_fci()`, `rescue_fci()` |
| Dolar MEP | `get_mep_dollar_rate()`, `estimate_mep_operation()` |

> Cada metodo tiene su version `_raw()` que retorna el JSON original de la API.

## Constantes Disponibles

### Mercados

```python
from pyIol import Markets

Markets.BCBA    # Bolsa de Buenos Aires
Markets.NYSE    # New York Stock Exchange
Markets.NASDAQ  # NASDAQ
Markets.AMEX    # American Stock Exchange
Markets.BCS     # Bolsa de Santiago
Markets.ROFX    # ROFEX (Futuros)
```

### Plazos de Liquidacion

```python
from pyIol import SettlementTerms

SettlementTerms.T0  # Contado inmediato
SettlementTerms.T1  # 24 horas
SettlementTerms.T2  # 48 horas (default)
SettlementTerms.T3  # 72 horas
```

### Estados de Operacion

```python
from pyIol import OperationStates

OperationStates.ALL        # Todas
OperationStates.PENDING    # Pendientes
OperationStates.FINISHED   # Terminadas
OperationStates.CANCELLED  # Canceladas
```

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

Este proyecto esta bajo la licencia especificada en el archivo `LICENCE`.

## Autor

**Ezequiel Primon** - [ezeprimo@gmail.com](mailto:ezeprimo@gmail.com)

## Enlaces

- [Repositorio GitHub](https://github.com/ezeprimo/py_iol)
- [Invertir Online](https://www.invertironline.com/)

---

**Recuerda**: Esta libreria interactua con sistemas financieros reales. Usala con responsabilidad y siempre verifica las operaciones antes de ejecutarlas.
