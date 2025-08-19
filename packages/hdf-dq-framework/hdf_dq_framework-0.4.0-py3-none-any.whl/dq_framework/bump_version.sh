#!/bin/bash

# Bump version and build script for DQ Framework
# Usage: ./bump_version.sh [patch|minor|major]

set -e

# Default to patch if no argument provided
BUMP_TYPE=${1:-patch}

echo "🔄 Bumping version ($BUMP_TYPE)..."
poetry version $BUMP_TYPE

echo "📦 Building package..."
poetry build

# Get the new version
NEW_VERSION=$(poetry version --short)
echo "✅ Successfully bumped to version $NEW_VERSION"

echo ""
echo "📋 Next steps:"
echo "  1. Commit changes: git add . && git commit -m 'Bump version to $NEW_VERSION'"
echo "  2. Create tag: git tag v$NEW_VERSION"
echo "  3. Push: git push && git push --tags"
echo "  4. Publish: poetry publish" 