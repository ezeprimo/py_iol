# pyIOL 0.1.1 Release Candidate Checklist

This checklist prepares `pyiol-client` version `0.1.1` for release. It is written for the
repository maintainer and does not publish artifacts, create tags, or push changes by itself.

## Quick Path

1. Complete the manual maintainer checks and resolve every unchecked blocker.
2. Run the local validation commands in this document from a clean working tree.
3. Commit the release changes and create `v0.1.1` only after maintainer approval.
4. Let the tag-triggered workflow publish to TestPyPI, verify the installation, then promote to
   PyPI.

## Version And Changelog

- [ ] **Maintainer:** Confirm the intended release version is `0.1.1`.
- [ ] Confirm `pyproject.toml` has `version = "0.1.1"`.
- [ ] Confirm `pyIol/__init__.py` has `__version__ = "0.1.1"`.
- [ ] Confirm `README.md` identifies the current release as `0.1.1`.
- [ ] Confirm `CHANGELOG.md` has a dated `0.1.1` entry with accurate changes and links.
- [ ] **Maintainer:** Review the changelog for omissions, compatibility notes, and user-visible
      changes.
- [ ] **Maintainer:** Confirm the release date in `CHANGELOG.md` is correct before publishing.

Useful local checks:

```powershell
python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"
python -c "import pyIol; print(pyIol.__version__)"
python scripts/validate_version.py 0.1.1
```

## Community Contacts

- [ ] **Maintainer:** Configure a real private vulnerability-reporting channel in `SECURITY.md`
      or enable GitHub private vulnerability reporting.
- [ ] **Maintainer:** Configure a real enforcement contact in `CODE_OF_CONDUCT.md`.
- [ ] Confirm that no placeholder contact remains before publication.
- [ ] **Maintainer:** Verify the GitHub Security and Code of Conduct settings match those files.

Do not add an email address, account, secret, or URL until the maintainer has verified it.

## Secrets And Artifacts

- [ ] Run `git status --short --ignored` and inspect ignored files for credentials or release data.
- [ ] Confirm `.env`, `.env.*`, virtual environments, caches, coverage files, `dist/`, build
      directories, and `*.egg-info/` are ignored and are not tracked.
- [ ] Search tracked files for credential-like material:

```powershell
git grep -n -I -E '(IOL_PASSWORD|IOL_USERNAME|API_KEY|SECRET|TOKEN|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY)'
```

- [ ] **Maintainer:** Revoke and rotate any credential exposed in repository history or local
      files before release.
- [ ] **Maintainer:** Confirm the release source does not include private notebooks, account data,
      or local build artifacts.

## Local Validation

Run these commands from the repository root. Record the exact command and result in the release
notes or the release issue.

- [ ] Tests:

```powershell
uv run python -m pytest tests/ -v --cov=pyIol --cov-report=term-missing
```

- [ ] Ruff lint and formatting:

```powershell
uv run ruff check pyIol/ tests/
uv run ruff format --check pyIol/ tests/
```

- [ ] Build fresh distributions into a temporary output directory without reusing old artifacts:

```powershell
$releaseOut = Join-Path $env:TEMP 'pyiol-release-0.1.1'
Remove-Item -Recurse -Force $releaseOut -ErrorAction SilentlyContinue
uv run --with build --with twine python -m build --outdir $releaseOut
```

- [ ] Validate both distribution metadata files:

```powershell
uv run --with twine python -m twine check (Get-ChildItem -LiteralPath $releaseOut -File).FullName
```

- [ ] Confirm the generated filenames and metadata are exactly `0.1.1`:

```powershell
Get-ChildItem $releaseOut
uv run python -c "from importlib.metadata import version; print(version('pyiol-client'))"
```

- [ ] Install and import only the fresh wheel in a clean environment:

```powershell
$wheelCheck = Join-Path $env:TEMP 'pyiol-wheel-check-0.1.1'
Remove-Item -Recurse -Force $wheelCheck -ErrorAction SilentlyContinue
uv venv $wheelCheck
& "$wheelCheck\Scripts\python.exe" -m pip install --upgrade pip
& "$wheelCheck\Scripts\python.exe" -m pip install (Get-ChildItem "$releaseOut\*.whl").FullName
& "$wheelCheck\Scripts\python.exe" -c "import pyIol; assert pyIol.__version__ == '0.1.1'; print('clean wheel import OK')"
```

- [ ] **Maintainer:** Review the wheel contents and confirm that only intended package files are
      included:

```powershell
uv run python -c "import zipfile,glob; p=glob.glob(r'$releaseOut\\*.whl')[0]; print(*zipfile.ZipFile(p).namelist(),sep='\n')"
```

## GitHub Actions And Trusted Publishing

- [ ] Confirm `.github/workflows/publish.yml` is unchanged and triggers only on `v*` tags.
- [ ] Confirm the workflow validates the tag against `pyproject.toml` and runs tests, Ruff,
      version validation, build, `twine check`, and clean-wheel verification.
- [ ] **Maintainer:** Create or verify GitHub Environments named `testpypi` and `pypi`.
- [ ] **Maintainer:** Configure environment protection rules, required reviewers, and branch/tag
      restrictions according to repository policy.
- [ ] **Maintainer:** Configure a TestPyPI Trusted Publisher for this repository and the exact
      workflow/environment names used by `publish.yml`.
- [ ] **Maintainer:** Configure a PyPI Trusted Publisher for this repository and the exact
      workflow/environment names used by `publish.yml`.
- [ ] **Maintainer:** Verify the repository owner, repository name, workflow filename, and
      environment names directly in GitHub and the package indexes. Do not infer them from this
      document.
- [ ] Confirm the workflow has `id-token: write` only on the publishing jobs and does not require
      long-lived PyPI API tokens.

## Tag Creation And TestPyPI Publication

- [ ] **Maintainer:** Confirm all intended release changes are committed and the working tree is
      clean:

```powershell
git status --short
```

- [ ] **Maintainer:** Create the local tag only after approval:

```powershell
git tag v0.1.1
git show --no-patch --decorate v0.1.1
```

- [ ] **Maintainer:** Push the tag using the repository's approved process. This is the action that
      starts the publish workflow; do not push until Trusted Publishing is verified.
- [ ] **Maintainer:** Confirm the workflow's `validate` and `checks` jobs pass before accepting
      TestPyPI publication.
- [ ] **Maintainer:** Confirm the TestPyPI project/version page and uploaded files using the
      repository's configured package URL. Do not assume that a URL or account exists.

The workflow command that performs publication is intentionally not run locally:

```text
pypa/gh-action-pypi-publish@release/v1 with repository-url=https://test.pypi.org/legacy/
```

## TestPyPI Installation Verification

- [ ] **Maintainer:** In a new environment, install exactly `0.1.1` from TestPyPI. Use the
      package's real dependency index or approved dependency strategy if TestPyPI does not host
      all runtime dependencies:

```powershell
python -m venv .release-testpypi
& ".\.release-testpypi\Scripts\python.exe" -m pip install --upgrade pip
& ".\.release-testpypi\Scripts\python.exe" -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyiol-client==0.1.1
& ".\.release-testpypi\Scripts\python.exe" -c "import pyIol; assert pyIol.__version__ == '0.1.1'; print('TestPyPI install OK')"
```

- [ ] **Maintainer:** Verify import, package version, metadata, and a safe read-only API scenario
      if credentials and an authorized test account are available. Do not execute trades.
- [ ] **Maintainer:** Remove the temporary environment after verification:

```powershell
Remove-Item -Recurse -Force .release-testpypi
```

## Promotion To PyPI

- [ ] **Maintainer:** Confirm TestPyPI installation verification passed and the exact artifacts
      are the ones approved for production.
- [ ] **Maintainer:** Confirm `0.1.1` is not already published to PyPI, or follow the package
      index procedure for an existing version. PyPI versions cannot be overwritten.
- [ ] **Maintainer:** Approve the protected `pypi` environment in GitHub Actions.
- [ ] **Maintainer:** Confirm the production publish job completes and verify the PyPI project and
      version pages using links shown by the workflow, not guessed account URLs.
- [ ] **Maintainer:** Verify installation from PyPI in a new environment:

```powershell
python -m venv .release-pypi
& ".\.release-pypi\Scripts\python.exe" -m pip install --upgrade pip
& ".\.release-pypi\Scripts\python.exe" -m pip install pyiol-client==0.1.1
& ".\.release-pypi\Scripts\python.exe" -c "import pyIol; assert pyIol.__version__ == '0.1.1'; print('PyPI install OK')"
```

## Rollback And Follow-Up

- [ ] **Maintainer:** If validation fails before publication, delete only the local tag if needed:

```powershell
git tag -d v0.1.1
```

- [ ] **Maintainer:** If a tag was pushed but publication must stop, disable or protect the
      publishing environments and document the reason; do not delete published artifacts.
- [ ] **Maintainer:** If a package issue is found after publication, publish a corrected higher
      version. PyPI releases are immutable; do not attempt to overwrite `0.1.1`.
- [ ] **Maintainer:** Record workflow URLs, package URLs, artifact hashes, verification commands,
      failures, approvals, and follow-up issues without recording credentials or personal data.
- [ ] **Maintainer:** Update the release notes and close the release issue only after production
      installation and monitoring checks pass.

## Manual Actions Summary

The following actions require maintainer intervention and are not performed by this checklist:

- Configuring security and Code of Conduct contacts.
- Reviewing secrets, repository history, and private release artifacts.
- Configuring GitHub Environments and Trusted Publishers.
- Approving and pushing the `v0.1.1` tag.
- Approving TestPyPI and PyPI publication.
- Verifying remote package pages, installation, monitoring, and rollback decisions.
