# Invertir Online (IOL) API - Documentacion Completa

Documentacion oficial de la API REST de Invertir Online (IOL) para Argentina.

> **IMPORTANTE**: Todas las acciones realizadas por este medio impactan en el entorno REAL.

## Tabla de Contenidos

- [Introduccion](#introduccion)
- [Requisitos](#requisitos)
- [Autenticacion](#autenticacion)
- [Base URL](#base-url)
- [Endpoints por Categoria](#endpoints-por-categoria)
  - [Perfil de Usuario](#perfil-de-usuario)
  - [Estado de Cuenta y Portafolio](#estado-de-cuenta-y-portafolio)
  - [Operaciones](#operaciones)
  - [Titulos y Cotizaciones](#titulos-y-cotizaciones)
  - [Fondos Comunes de Inversion (FCI)](#fondos-comunes-de-inversion-fci)
  - [Opciones](#opciones)
  - [Dolar MEP](#dolar-mep)
  - [Operatoria Simplificada](#operatoria-simplificada)
  - [Asesores](#asesores)
  - [Cheques de Pago Diferido (CPD)](#cheques-de-pago-diferido-cpd)
- [Enumeraciones](#enumeraciones)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Mejores Practicas](#mejores-practicas)

---

## Introduccion

IOL (Invertir Online) proporciona una API REST que permite a los desarrolladores interactuar con la plataforma de forma programatica. La API permite:

- Consultar cotizaciones en tiempo real
- Ejecutar operaciones de compra/venta
- Gestionar portafolios
- Operar con FCI, opciones, bonos y mas

### Entorno de Pruebas (Sandbox)

IOL cuenta con un entorno de pruebas (sandbox) que permite probar desarrollos en un ambiente seguro y aislado del mercado real. En el sandbox se pueden realizar operaciones simuladas de compra/venta y pedidos de cancelacion.

---

## Requisitos

Para usar las APIs se requiere:

1. **Cuenta de Inversion Abierta** en Invertir Online
2. **Activacion del servicio de APIs**:
   - Loguearse en el sitio de IOL
   - Ir a la seccion de mensajes y solicitar la activacion de APIs
   - Una vez confirmada la activacion, aceptar los terminos y condiciones en:
     **Mi Cuenta > Personalizacion > APIs**

---

## Autenticacion

La API usa autenticacion mediante **tokens digitales (OAuth2)**. Existen dos tipos de tokens:

| Token | Descripcion | Duracion |
|-------|-------------|----------|
| **Bearer Token** | Se envia en cada request para acceder a recursos | 15 minutos |
| **Refresh Token** | Se usa para renovar el bearer token sin re-autenticar | Variable |

### Obtener Token Inicial

```http
POST /token HTTP/1.1
Host: api.invertironline.com
Content-Type: application/x-www-form-urlencoded

username=MI_USUARIO&password=MI_PASSWORD&grant_type=password
```

**Respuesta exitosa:**
```json
{
  "access_token": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "token_type": "bearer",
  "expires_in": 899,
  "refresh_token": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  ".issued": "2024-01-15T10:00:00.000Z",
  ".expires": "2024-01-15T10:15:00.000Z"
}
```

### Usar el Token en Requests

```http
GET /api/v2/datos-perfil HTTP/1.1
Host: api.invertironline.com
Authorization: Bearer aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

### Renovar Token con Refresh Token

Cuando el bearer token expira (15 min), usar el refresh token:

```http
POST /token HTTP/1.1
Host: api.invertironline.com
Content-Type: application/x-www-form-urlencoded

refresh_token=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb&grant_type=refresh_token
```

---

## Base URL

```
https://api.invertironline.com
```

### Versiones de API

| Version | Base Path |
|---------|-----------|
| v1 | `/api/v1` |
| v2 | `/api/v2` (recomendada) |

---

## Endpoints por Categoria

### Perfil de Usuario

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/v2/datos-perfil` | Obtener datos del perfil del usuario autenticado |

**Respuesta ejemplo:**
```json
{
  "nombre": "Juan",
  "apellido": "Perez",
  "numeroCuenta": "123456",
  "dni": "12345678",
  "sexo": "Masculino",
  "perfilInversor": "Moderado"
}
```

---

### Estado de Cuenta y Portafolio

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/v2/estadocuenta` | Estado de cuenta completo |
| GET | `/api/v2/portafolio/{pais}` | Portafolio por pais |
| GET | `/api/v2/operaciones` | Lista de operaciones con filtros |
| GET | `/api/v2/operaciones/{numero}` | Detalle de una operacion especifica |
| DELETE | `/api/v2/operaciones/{numero}` | Cancelar una operacion |

**Parametros de pais:**
- `argentina`
- `estados_Unidos`

**Filtros para operaciones:**
- `filtro.numero` - Numero de operacion
- `filtro.estado` - `todas`, `pendientes`, `terminadas`, `canceladas`
- `filtro.fechaDesde` - Formato: `2024-01-01`
- `filtro.fechaHasta` - Formato: `2024-12-31`
- `filtro.pais` - `argentina`, `estados_Unidos`

---

### Operaciones

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | `/api/v2/operar/Comprar` | Ejecutar orden de compra |
| POST | `/api/v2/operar/Vender` | Ejecutar orden de venta |
| POST | `/api/v2/operar/ComprarEspecieD` | Comprar especie D (dolar) |
| POST | `/api/v2/operar/VenderEspecieD` | Vender especie D (dolar) |

**Body para compra/venta:**
```json
{
  "mercado": "bCBA",
  "simbolo": "GGAL",
  "cantidad": 100,
  "precio": 150.25,
  "plazo": "t2",
  "validez": "2024-12-31T23:59:59"
}
```

---

### Titulos y Cotizaciones

#### Datos de Titulos

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/v2/{mercado}/Titulos/{simbolo}` | Datos basicos de un titulo |
| GET | `/api/v2/{mercado}/Titulos/{simbolo}/Cotizacion` | Cotizacion de un titulo |
| GET | `/api/v2/{mercado}/Titulos/{simbolo}/CotizacionDetalle` | Cotizacion detallada |
| GET | `/api/v2/{mercado}/Titulos/{simbolo}/Opciones` | Opciones de un titulo |

**Parametros de mercado:**
- `bCBA` - Bolsa de Comercio de Buenos Aires
- `nYSE` - New York Stock Exchange
- `nASDAQ` - NASDAQ
- `aMEX` - American Stock Exchange
- `bCS` - Bolsa de Comercio de Santiago
- `rOFX` - ROFEX (futuros)

**Parametros de plazo:**
- `t0` - Contado inmediato
- `t1` - 24 horas
- `t2` - 48 horas (mas comun)
- `t3` - 72 horas

#### Cotizaciones Masivas

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/v2/{pais}/Titulos/Cotizacion/Instrumentos` | Listar instrumentos disponibles por pais |
| GET | `/api/v2/Cotizaciones/{instrumento}/{pais}/Todos` | Cotizaciones de todos los titulos de un instrumento |
| GET | `/api/v2/Cotizaciones/{instrumento}/{panel}/{pais}` | Cotizaciones por panel especifico |
| GET | `/api/v2/{pais}/Titulos/Cotizacion/Paneles/{instrumento}` | Listar paneles de un instrumento |

**Tipos de instrumento:**
- `acciones`
- `cedears`
- `opciones`
- `titulosPublicos` (bonos)
- `obligacionesNegociables`
- `letras`
- `cauciones`
- `futuros`
- `cHPD` (cheques de pago diferido)
- `aDRs`

---

### Fondos Comunes de Inversion (FCI)

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/v2/Titulos/FCI` | Listar todos los FCI disponibles |
| GET | `/api/v2/Titulos/FCI/{simbolo}` | Detalle de un FCI |
| GET | `/api/v2/Titulos/FCI/TipoFondos` | Tipos de fondos disponibles |
| GET | `/api/v2/Titulos/FCI/Administradoras` | Administradoras de FCI |
| GET | `/api/v2/Titulos/FCI/Administradoras/{administradora}/TipoFondos` | Tipos de fondos por administradora |
| POST | `/api/v2/operar/suscripcion/fci` | Suscribir a un FCI |
| POST | `/api/v2/operar/rescate/fci` | Rescatar de un FCI |

---

### Opciones

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/v2/{mercado}/Titulos/{simbolo}/Opciones` | Obtener opciones de un titulo |

**Respuesta ejemplo:**
```json
[
  {
    "simbolo": "GFGC450.FE",
    "descripcion": "CALL GGAL 450 FEB",
    "tipoOpcion": "Call",
    "fechaVencimiento": "2024-02-16",
    "precioEjercicio": 450.00,
    "cotizacion": {
      "ultimoPrecio": 25.50,
      "variacionPorcentual": 3.25,
      "puntas": {...}
    }
  }
]
```

---

### Dolar MEP

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/v2/Cotizaciones/MEP/{simbolo}` | Obtener cotizacion MEP de un titulo |
| POST | `/api/v2/Cotizaciones/MEP` | Obtener valor de referencia MEP |

---

### Operatoria Simplificada

Endpoints para operaciones simplificadas de dolar MEP:

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/v2/OperatoriaSimplificada/MontosEstimados/{monto}` | Estimar montos para compra MEP |
| GET | `/api/v2/OperatoriaSimplificada/VentaMepSimple/MontosEstimados/{monto}` | Estimar montos para venta MEP |
| GET | `/api/v2/OperatoriaSimplificada/{idTipoOperatoria}/Parametros` | Parametros de operatoria |
| GET | `/api/v2/OperatoriaSimplificada/Validar/{monto}/{idTipoOperatoria}` | Validar operacion |
| POST | `/api/v2/OperatoriaSimplificada/Comprar` | Ejecutar compra simplificada |

---

### Asesores

Endpoints para usuarios con rol de asesor:

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | `/api/v2/Asesor/Movimientos` | Movimientos historicos de clientes |
| GET | `/api/v2/asesores/test-inversor` | Obtener preguntas del test de inversor |
| POST | `/api/v2/asesores/test-inversor` | Calcular perfil sin guardar |
| POST | `/api/v2/asesores/test-inversor/{idClienteAsesorado}` | Calcular y guardar perfil |
| POST | `/api/v2/asesores/operar/VenderEspecieD` | Vender especie D como asesor |

---

### Cheques de Pago Diferido (CPD)

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/v2/operar/CPD/PuedeOperar` | Verificar si puede operar CPD |
| GET | `/api/v2/operar/CPD/{estado}/{segmento}` | Listar CPD por estado y segmento |
| GET | `/api/v2/operar/CPD/Comisiones/{importe}/{plazo}/{tasa}` | Calcular comisiones |
| POST | `/api/v2/operar/CPD` | Operar con CPD |

---

## Enumeraciones

### Mercados

| Valor | Descripcion |
|-------|-------------|
| `bCBA` | Bolsa de Comercio de Buenos Aires |
| `nYSE` | New York Stock Exchange |
| `nASDAQ` | NASDAQ |
| `aMEX` | American Stock Exchange |
| `bCS` | Bolsa de Comercio de Santiago |
| `rOFX` | ROFEX - Mercado de Futuros |

### Plazos de Liquidacion

| Valor | Descripcion |
|-------|-------------|
| `t0` | Contado inmediato |
| `t1` | 24 horas |
| `t2` | 48 horas (default para acciones) |
| `t3` | 72 horas |

### Paises

| Valor | Descripcion |
|-------|-------------|
| `argentina` | Argentina |
| `estados_Unidos` | Estados Unidos |

### Instrumentos

| Valor | Descripcion |
|-------|-------------|
| `acciones` | Acciones |
| `cedears` | CEDEARs |
| `opciones` | Opciones |
| `titulosPublicos` | Bonos/Titulos Publicos |
| `obligacionesNegociables` | Obligaciones Negociables |
| `letras` | Letras |
| `cauciones` | Cauciones |
| `futuros` | Futuros |
| `cHPD` | Cheques de Pago Diferido |
| `aDRs` | ADRs |

### Estados de Operacion

| Valor | Descripcion |
|-------|-------------|
| `todas` | Todas las operaciones |
| `pendientes` | Operaciones pendientes |
| `terminadas` | Operaciones terminadas |
| `canceladas` | Operaciones canceladas |

---

## Ejemplos de Uso

### Python - Obtener Token

```python
import httpx

def get_token(username: str, password: str) -> dict:
    response = httpx.post(
        "https://api.invertironline.com/token",
        data={
            "username": username,
            "password": password,
            "grant_type": "password"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    response.raise_for_status()
    return response.json()

token_data = get_token("mi_usuario", "mi_password")
access_token = token_data["access_token"]
```

### Python - Obtener Cotizacion

```python
def get_cotizacion(token: str, simbolo: str, mercado: str = "bCBA", plazo: str = "t1"):
    response = httpx.get(
        f"https://api.invertironline.com/api/v2/{mercado}/Titulos/{simbolo}/Cotizacion",
        params={"plazo": plazo},
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    return response.json()

cotizacion = get_cotizacion(access_token, "GGAL")
print(f"Ultimo precio: ${cotizacion['ultimoPrecio']}")
```

### Python - Ejecutar Compra

```python
def comprar(token: str, simbolo: str, cantidad: int, precio: float, 
            mercado: str = "bCBA", plazo: str = "t2"):
    response = httpx.post(
        "https://api.invertironline.com/api/v2/operar/Comprar",
        json={
            "mercado": mercado,
            "simbolo": simbolo,
            "cantidad": cantidad,
            "precio": precio,
            "plazo": plazo
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    response.raise_for_status()
    return response.json()
```

### cURL - Obtener Portafolio

```bash
curl -X GET "https://api.invertironline.com/api/v2/portafolio/argentina" \
  -H "Authorization: Bearer TU_TOKEN"
```

---

## Mejores Practicas

### 1. Manejo de Tokens

- Almacenar tokens de forma segura (nunca en codigo fuente)
- Implementar renovacion automatica antes de los 15 minutos
- Usar el refresh token para evitar re-autenticacion

### 2. Manejo de Errores

```python
try:
    response = client.get(url)
    response.raise_for_status()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        # Token expirado, renovar
        refresh_token()
    elif e.response.status_code == 429:
        # Rate limit, esperar
        time.sleep(60)
```

### 3. Rate Limiting

- La API puede tener limites de requests (no documentado oficialmente)
- Implementar backoff exponencial en caso de errores 429
- Evitar requests innecesarios cacheando datos cuando sea posible

### 4. Validacion de Datos

- Validar todos los datos antes de enviarlos a la API
- Verificar que los simbolos existan antes de operar
- Comprobar disponibilidad de fondos antes de comprar

### 5. Logging

- Registrar todas las operaciones de trading
- Guardar respuestas de la API para debugging
- Monitorear errores y latencias

### 6. Seguridad

- Usar HTTPS siempre
- No exponer credenciales en logs
- Usar variables de entorno para credenciales

---

## Codigos de Estado HTTP

| Codigo | Descripcion |
|--------|-------------|
| 200 | Exito |
| 400 | Bad Request - Parametros invalidos |
| 401 | Unauthorized - Token invalido o expirado |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no encontrado |
| 429 | Too Many Requests - Rate limit |
| 500 | Internal Server Error |

---

## Referencias

- **Documentacion Oficial**: https://api.invertironline.com/Help
- **Autenticacion**: https://api.invertironline.com/Help/Autenticacion
- **Swagger UI**: https://api.invertironline.com/Help (seleccionar version)
- **Soporte**: Contactar a traves de mensajeria en la plataforma IOL

---

*Documento actualizado: Enero 2025*
*Basado en API v2 de Invertir Online*
