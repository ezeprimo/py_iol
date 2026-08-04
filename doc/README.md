# pyIOL Documentation

This folder contains documentation and examples for pyIOL.

## Start Here

- **[Agent guide](./agent-guide.md)** - setup, authentication, typed/raw usage, safety, and application architecture.
- **[API reference](./api-reference.md)** - source-derived public `IOLClient` method reference.
- **[Recipes](./recipes/)** - small read-only Python examples.

## Existing Reference

### REST API Notes

- **[iol_api_doc.MD](./iol_api_doc.MD)** - Documentacion completa de la API REST de Invertir Online, incluyendo:
  - Autenticacion y tokens
  - Endpoints disponibles por categoria
  - Parametros y respuestas
  - Ejemplos de uso con curl
  - Enumeraciones y constantes

### Example Notebooks

La carpeta `notebooks/` contiene Jupyter notebooks interactivos para probar cada funcionalidad de la libreria:

| Notebook | Descripcion |
|----------|-------------|
| [01_autenticacion.ipynb](./notebooks/01_autenticacion.ipynb) | Configuracion inicial, autenticacion y datos de perfil |
| [02_cotizaciones_basicas.ipynb](./notebooks/02_cotizaciones_basicas.ipynb) | Dolar MEP, cotizaciones, datos de titulos, opciones |
| [03_cotizaciones_avanzadas.ipynb](./notebooks/03_cotizaciones_avanzadas.ipynb) | Cotizaciones masivas, paneles, cotizacion detallada |
| [04_cuenta_portafolio.ipynb](./notebooks/04_cuenta_portafolio.ipynb) | Estado de cuenta, portafolio, operaciones |
| [05_trading.ipynb](./notebooks/05_trading.ipynb) | Compra y venta de acciones y bonos |
| [06_fci.ipynb](./notebooks/06_fci.ipynb) | Fondos Comunes de Inversion |
| [07_mep_simplificado.ipynb](./notebooks/07_mep_simplificado.ipynb) | Operaciones MEP simplificadas |
| [08_cpd.ipynb](./notebooks/08_cpd.ipynb) | Cheques de Pago Diferido |
| [09_asesores.ipynb](./notebooks/09_asesores.ipynb) | Operaciones de asesores |

## Como usar los notebooks

### Requisitos previos

1. Tener las dependencias de desarrollo instaladas:
   ```bash
   uv sync
   # o
   pip install -e ".[dev]"
   ```

2. Configurar las credenciales en el archivo `.env` en la raiz del proyecto:
   ```env
   IOL_USERNAME=tu_usuario_iol
   IOL_PASSWORD=tu_password_iol
   ```

### Ejecutar los notebooks

```bash
# Desde la raiz del proyecto
cd doc/notebooks
jupyter notebook
```

O abrir directamente en VS Code con la extension de Jupyter.

### Estructura de cada notebook

Cada notebook sigue una estructura consistente:

1. **Configuracion inicial** - Imports y carga de credenciales
2. **Creacion del cliente** - Instancia de `IOLClient`
3. **Ejemplos de uso** - Celdas con ejemplos de cada endpoint
4. **Metodos RAW** - Referencia a metodos que devuelven JSON crudo
5. **Limpieza** - Cierre del cliente

## Notas importantes

- Las operaciones que modifican datos (compra, venta, suscripcion FCI, etc.) estan **comentadas por seguridad** en los notebooks
- Siempre verificar las operaciones antes de descomentar y ejecutar
- La librería no configura un sandbox de ejecución separado; usa mocks para pruebas y cualquier entorno sandbox que IOL habilite para la cuenta
- Los notebooks asumen que el archivo `.env` esta en la raiz del proyecto (`../../.env` relativo a los notebooks)

## Contribuir a la documentacion

Si encuentras errores o quieres mejorar la documentacion:

1. Fork el repositorio
2. Realiza tus cambios
3. Envia un Pull Request

Toda contribucion es bienvenida.
