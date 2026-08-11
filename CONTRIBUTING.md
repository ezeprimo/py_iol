# Guia de Contribucion

Gracias por tu interes en contribuir a pyIOL. Esta guia te ayudara a entender el proceso de desarrollo y publicacion.

## Tabla de Contenidos

- [Configuracion del Entorno](#configuracion-del-entorno)
- [Flujo de Trabajo](#flujo-de-trabajo)
- [Sistema de Versionado](#sistema-de-versionado)
- [Publicacion a PyPI](#publicacion-a-pypi)
- [CI/CD](#cicd)
- [Estandares de Codigo](#estandares-de-codigo)

---

## Configuracion del Entorno

### Requisitos

- Python >= 3.8
- [uv](https://docs.astral.sh/uv/) (recomendado) o pip
- Git

### Instalacion para Desarrollo

```bash
# Clonar el repositorio
git clone https://github.com/ezeprimo/py_iol.git
cd py_iol

# Instalar dependencias con uv (recomendado)
uv sync

# O con pip en modo desarrollo
pip install -e ".[dev]"

# Configurar credenciales de IOL
cp .env.example .env
# Editar .env con tus credenciales
```

### Instalar Git Hooks (Opcional)

Para validar tags automaticamente antes de push:

```bash
# Linux/macOS
cp scripts/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push

# Windows (Git Bash)
cp scripts/pre-push .git/hooks/pre-push
```

---

## Flujo de Trabajo

### 1. Crear una Rama

```bash
git checkout -b feature/mi-nueva-funcionalidad
```

### 2. Hacer Cambios

- Sigue los [Estandares de Codigo](#estandares-de-codigo)
- Agrega tests si es necesario
- Actualiza la documentacion

### 3. Commit

```bash
git add .
git commit -m "Agrega nueva funcionalidad X"
```

### 4. Pull Request

```bash
git push origin feature/mi-nueva-funcionalidad
```

Luego abre un Pull Request en GitHub.

---

## Sistema de Versionado

pyIOL usa [Semantic Versioning](https://semver.org/) (SemVer):

```
MAJOR.MINOR.PATCH[-PRERELEASE]
```

### Tipos de Version

| Formato | Ejemplo | Tipo | Destino |
|---------|---------|------|---------|
| `X.Y.Z` | `1.0.0` | Produccion | TestPyPI + PyPI |
| `X.Y.Z-alpha` | `1.0.0-alpha` | Alpha | Solo TestPyPI |
| `X.Y.Z-alpha.N` | `1.0.0-alpha.1` | Alpha | Solo TestPyPI |
| `X.Y.Z-beta.N` | `1.0.0-beta.1` | Beta | Solo TestPyPI |
| `X.Y.Z-rc.N` | `1.0.0-rc.1` | Release Candidate | Solo TestPyPI |
| `X.Y.Z-dev.N` | `1.0.0-dev.1` | Development | Solo TestPyPI |

### Cuando Incrementar

- **MAJOR**: Cambios incompatibles con versiones anteriores
- **MINOR**: Nueva funcionalidad compatible con versiones anteriores
- **PATCH**: Correcciones de bugs compatibles con versiones anteriores

### Flujo de Prereleases

Para probar una version antes de lanzarla a produccion:

```bash
# 1. Actualizar version en pyproject.toml
version = "0.2.0-beta.1"

# 2. Commit
git add pyproject.toml
git commit -m "Bump version to 0.2.0-beta.1"

# 3. Crear tag
git tag v0.2.0-beta.1

# 4. Push
git push origin main --tags
```

Esto publicara solo en TestPyPI para pruebas.

### Flujo de Produccion

Una vez probado, lanzar a produccion:

```bash
# 1. Actualizar version en pyproject.toml (sin sufijo prerelease)
version = "0.2.0"

# 2. Commit
git add pyproject.toml
git commit -m "Release version 0.2.0"

# 3. Crear tag
git tag v0.2.0

# 4. Push
git push origin main --tags
```

Esto publicara en TestPyPI Y en PyPI.

---

## Publicacion a PyPI

### Requisitos Previos (Solo Mantenedores)

1. **Configurar GitHub Environments**:
   - Crear environment `testpypi`
   - Crear environment `pypi`

2. **Configurar Trusted Publisher en PyPI**:
   - En [PyPI](https://pypi.org): Account Settings > Publishing > Add a new publisher
   - En [TestPyPI](https://test.pypi.org): Mismo proceso
   - Configurar:
     - Owner: `ezeprimo`
     - Repository: `py_iol`
     - Workflow: `publish.yml`
     - Environment: `pypi` o `testpypi`

### Proceso de Release

1. **Actualizar version** en `pyproject.toml`
2. **Commit** los cambios
3. **Crear tag** con formato `vX.Y.Z` o `vX.Y.Z-prerelease`
4. **Push** tag y commits

El workflow de GitHub Actions se encargara del resto:
- Validar que el tag coincida con `pyproject.toml`
- Build del paquete
- Publicacion a TestPyPI (siempre)
- Publicacion a PyPI (solo versiones de produccion)

### Validar Version Localmente

Antes de crear un tag, puedes validar:

```bash
# Validar version actual en pyproject.toml
python scripts/validate_version.py

# Validar un tag especifico
python scripts/validate_version.py v0.2.0
```

### Instalar desde TestPyPI

Para probar un prerelease:

```bash
pip install -i https://test.pypi.org/simple/ pyiol-client==0.2.0b1
```

> Nota: pip normaliza versiones, `0.2.0-beta.1` se convierte en `0.2.0b1`

---

## CI/CD

El proyecto usa GitHub Actions para integracion continua y publicacion.

### Workflows

| Workflow | Trigger | Descripcion |
|----------|---------|-------------|
| `ci.yml` | Push a main, PRs | Build y lint con ruff |
| `publish.yml` | Push de tags `v*` | Publicacion a PyPI/TestPyPI |

### CI (`ci.yml`)

- Build en Python 3.8, 3.9, 3.10, 3.11, 3.12
- Lint con [ruff](https://github.com/astral-sh/ruff)

### Publish (`publish.yml`)

1. **validate**: Valida que el tag coincida con `pyproject.toml`
2. **build**: Construye el paquete wheel y sdist
3. **publish-testpypi**: Publica a TestPyPI (siempre)
4. **publish-pypi**: Publica a PyPI (solo produccion)

---

## Estandares de Codigo

### Linting

Usamos [ruff](https://github.com/astral-sh/ruff) para linting y formateo:

```bash
# Verificar errores
ruff check .

# Corregir errores automaticamente
ruff check --fix .

# Formatear codigo
ruff format .
```

### Convenciones

1. **Nombres de metodos**: `get_` para lecturas, snake_case, en ingles
2. **Documentacion**: Docstrings en espanol o ingles, consistente
3. **Tipado**: Type hints en todos los parametros y retornos
4. **Modelos**: Todos los modelos deben tener `from_dict()` como classmethod
5. **Versiones raw**: Todo endpoint tipado debe tener su version `_raw()`

### Estructura de un Nuevo Endpoint

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

# En client.py - Metodo tipado
def get_nuevo_endpoint(self, param: str) -> NuevoModelo:
    """Descripcion del endpoint."""
    data = self._make_authenticated_request("GET", f"/api/v2/endpoint/{param}")
    return NuevoModelo.from_dict(data)

# En client.py - Metodo raw
def get_nuevo_endpoint_raw(self, param: str) -> Dict[str, Any]:
    """Version JSON del endpoint."""
    return self._make_authenticated_request("GET", f"/api/v2/endpoint/{param}")

# En __init__.py - Exportar el modelo
from .models import NuevoModelo
```

---

## Recursos

- [Documentacion de la API de IOL](./doc/iol_api_doc.MD)
- [Notebooks de ejemplo](./doc/notebooks/)
- [AGENTS.md](./AGENTS.md) - Guia para agentes de IA

---

## Preguntas Frecuentes

### El CI falla por version mismatch

El tag debe coincidir exactamente con la version en `pyproject.toml`:

```bash
# 1. Actualizar pyproject.toml primero
version = "0.2.0"

# 2. Commit
git commit -am "Bump version to 0.2.0"

# 3. Crear tag
git tag v0.2.0

# 4. Push commits y tag
git push origin main --tags
```

### Como eliminar un tag erroneo

```bash
# Eliminar tag local
git tag -d v0.2.0

# Eliminar tag remoto (si ya se pusheo)
git push origin :refs/tags/v0.2.0
```

### Como probar el build localmente

```bash
# Con uv
uv build

# Con pip
pip install build
python -m build
```

Los archivos se generan en `dist/`.
