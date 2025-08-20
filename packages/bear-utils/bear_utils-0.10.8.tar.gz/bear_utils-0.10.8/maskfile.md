# Singleton Mask File

## clean

> This command cleans the build artifacts

```bash
rm -rf dist/
```

## bump (patch_version)

> Bump the version of the local project specifying the patch level: `minor`, `major`, `patch`

```bash
uv sync
current_version=$(python3 -m bear_utils._internal.cli get-version)
echo "Current version: ${current_version}"
if [ -z "${patch_version}" ]; then
    echo "Please specify a patch version: minor, major, or patch"
    exit 1
fi
if [ "${patch_version}" != "minor" ] && [ "${patch_version}" != "major" ] && [ "${patch_version}" != "patch" ]; then
    echo "Invalid patch version specified. Use minor, major, or patch."
    exit 1
fi
# Ensure the current version is set
if [ -z "${current_version}" ]; then
    echo "Current version is not set. Please run 'uv run get-version' first."
    exit 1
fi
new_version=$(python3 -m bear_utils._internal.cli bump-version "${patch_version}")
if [ $? -ne 0 ]; then
    echo "Failed to bump version. Please check the current version and try again."
    exit 1
fi
if [ -z "${new_version}" ]; then
    echo "Failed to bump version. Please check the current version and try again."
    exit 1
fi
echo "New version: ${new_version}"  
git tag -a "v${new_version}" -m "Bump version to v${new_version}"
git push origin "v${new_version}"
uv pip install pyqt6
```

## build

> This command builds the project via uv

```bash
uv build
```

## test

> This command runs the tests using pytest

```bash
pytest -s
```

## publish (publish_location)

> This command publishes the package to PyPI (or locally) officially, isn't that great?

```bash
if [ "${publish_location}" = "twine" ]; then
    twine upload -r local dist/* # uploads to a local repository
else
    export UV_PUBLISH_TOKEN=$(op read "op://Private/PyPI Prod/api_key")
    uv publish --index pypi dist/* --token $UV_PUBLISH_TOKEN
fi
```

## full (patch_version) (publish_location)

> This command runs the full build and publish process

```bash
$MASK clean
$MASK bump ${patch_version}
$MASK build
$MASK publish ${publish_location}
```
