set -e

if [ -z "$1" ]; then
    echo "Error: invalid version number (./package.sh x.y.z)"
    exit 1
fi

NEW_VERSION=$1
PYPROJECT_FILE="pyproject.toml"

echo "Updating version in $PYPROJECT_FILE to $NEW_VERSION..."

sed -i '' -e "s/^version = \"[0-9.]*\"/version = \"$NEW_VERSION\"/" "$PYPROJECT_FILE"
rm -rf dist/*

/opt/homebrew/opt/python@3.11/bin/python3.11 -m build
twine upload dist/*

echo "Successfully published version $NEW_VERSION!"