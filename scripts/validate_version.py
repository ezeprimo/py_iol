#!/usr/bin/env python3
"""
Script para validar que la versión del tag coincide con pyproject.toml.

Uso:
    python scripts/validate_version.py v0.1.0
    python scripts/validate_version.py  # Usa el tag actual si existe

También se puede usar como pre-push hook para validar tags antes de push.
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def get_version_from_pyproject() -> str:
    """Extrae la versión de pyproject.toml"""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    if not pyproject_path.exists():
        print(f"Error: No se encontró {pyproject_path}")
        sys.exit(1)
    
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    
    if not match:
        print("Error: No se encontró la versión en pyproject.toml")
        sys.exit(1)
    
    return match.group(1)


def parse_version(version: str) -> Optional[Dict[str, Any]]:
    """
    Parsea una versión semántica.
    
    Formatos soportados:
        - 0.1.0 (producción)
        - 0.1.0-beta.1 (prerelease)
        - 0.1.0-alpha (prerelease)
        - 0.1.0-rc.2 (prerelease)
        - 0.1.0-dev.1 (prerelease)
    """
    # Patrón para semantic versioning con prerelease opcional
    pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-(alpha|beta|rc|dev)(?:\.(\d+))?)?$'
    match = re.match(pattern, version)
    
    if not match:
        return None
    
    groups = match.groups()
    return {
        "major": int(groups[0]),
        "minor": int(groups[1]),
        "patch": int(groups[2]),
        "prerelease_type": groups[3],  # alpha, beta, rc, dev or None
        "prerelease_num": int(groups[4]) if groups[4] else None,
        "is_prerelease": groups[3] is not None,
        "full": version
    }


def validate_version_format(version: str) -> bool:
    """Valida que la versión tenga formato semántico válido"""
    parsed = parse_version(version)
    return parsed is not None


def get_tag_from_ref(ref: str) -> Optional[str]:
    """Extrae el nombre del tag de una referencia git"""
    if ref.startswith("refs/tags/v"):
        return ref[len("refs/tags/v"):]
    elif ref.startswith("v"):
        return ref[1:]
    return None


def main():
    # Obtener versión del pyproject.toml
    pyproject_version = get_version_from_pyproject()
    print(f"Versión en pyproject.toml: {pyproject_version}")
    
    # Validar formato de la versión en pyproject.toml
    if not validate_version_format(pyproject_version):
        print(f"Error: La versión '{pyproject_version}' no tiene formato semántico válido")
        print("Formatos válidos: X.Y.Z, X.Y.Z-alpha, X.Y.Z-beta.N, X.Y.Z-rc.N, X.Y.Z-dev.N")
        sys.exit(1)
    
    # Si se proporciona un argumento, usarlo como tag
    if len(sys.argv) > 1:
        tag_arg = sys.argv[1]
        tag_version = get_tag_from_ref(tag_arg)
        if tag_version is None:
            tag_version = tag_arg  # Asumir que es directamente la versión
    else:
        # Intentar obtener el tag actual
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--exact-match", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            tag_version = get_tag_from_ref(result.stdout.strip())
        except subprocess.CalledProcessError:
            print("No hay tag en el commit actual.")
            print(f"La versión en pyproject.toml es: {pyproject_version}")
            print(f"\nPara crear un tag que coincida:")
            print(f"  git tag v{pyproject_version}")
            print(f"  git push origin v{pyproject_version}")
            sys.exit(0)
    
    if tag_version is None:
        print("Error: No se pudo determinar la versión del tag")
        sys.exit(1)
    
    print(f"Versión del tag: {tag_version}")
    
    # Validar formato del tag
    if not validate_version_format(tag_version):
        print(f"Error: El tag '{tag_version}' no tiene formato semántico válido")
        print("Formatos válidos: X.Y.Z, X.Y.Z-alpha, X.Y.Z-beta.N, X.Y.Z-rc.N, X.Y.Z-dev.N")
        sys.exit(1)
    
    # Comparar versiones
    if tag_version != pyproject_version:
        print("\nERROR: Las versiones no coinciden!")
        print(f"   Tag:           {tag_version}")
        print(f"   pyproject.toml: {pyproject_version}")
        print(f"\nPor favor, actualiza pyproject.toml a version = \"{tag_version}\"")
        print("O crea un tag que coincida con la versión actual:")
        print(f"  git tag v{pyproject_version}")
        sys.exit(1)
    
    # Mostrar información sobre el tipo de release
    parsed = parse_version(tag_version)
    if parsed["is_prerelease"]:
        prerelease_info = parsed["prerelease_type"]
        if parsed["prerelease_num"]:
            prerelease_info += f".{parsed['prerelease_num']}"
        print(f"\nOK: Version valida: {tag_version} (PRERELEASE: {prerelease_info})")
        print("   Se publicara solo en TestPyPI")
    else:
        print(f"\nOK: Version valida: {tag_version} (PRODUCCION)")
        print("   Se publicara en TestPyPI y PyPI")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
