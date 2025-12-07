#!/bin/bash
# Sync core files from desktop repo to mobile repo

DESKTOP_REPO="/workspaces/Astronomical-watch"
MOBILE_REPO="/workspaces/Astronomical-watch-mobile"

echo "========================================"
echo "  SYNCING CORE FILES TO MOBILE REPO"
echo "========================================"
echo ""

# Check if mobile repo exists
if [ ! -d "$MOBILE_REPO" ]; then
    echo "ERROR: Mobile repo not found at $MOBILE_REPO"
    exit 1
fi

# Function to copy files and preserve structure
copy_module() {
    local module=$1
    echo "Copying $module..."
    
    if [ -d "$DESKTOP_REPO/src/astronomical_watch/$module" ]; then
        rsync -av --delete \
            "$DESKTOP_REPO/src/astronomical_watch/$module/" \
            "$MOBILE_REPO/src/astronomical_watch/$module/" \
            --exclude="__pycache__" \
            --exclude="*.pyc"
        echo "  ✓ $module synced"
    else
        echo "  ✗ $module not found in desktop repo"
    fi
}

# Copy main __init__.py
echo "Copying main __init__.py..."
cp "$DESKTOP_REPO/src/astronomical_watch/__init__.py" \
   "$MOBILE_REPO/src/astronomical_watch/__init__.py"
echo "  ✓ __init__.py synced"
echo ""

# Copy core modules
copy_module "core"
copy_module "astro"
copy_module "solar"
copy_module "net"
copy_module "offline"

# Copy translate if it exists in mobile (might be 'lang' there)
if [ -d "$MOBILE_REPO/src/astronomical_watch/lang" ]; then
    echo "Copying translations to lang/..."
    rsync -av --delete \
        "$DESKTOP_REPO/src/astronomical_watch/translate/" \
        "$MOBILE_REPO/src/astronomical_watch/lang/" \
        --exclude="__pycache__" \
        --exclude="*.pyc"
    echo "  ✓ translations synced to lang/"
else
    copy_module "translate"
fi

# Copy scripts folder (VSOP87 coefficients)
echo "Copying scripts..."
rsync -av \
    "$DESKTOP_REPO/src/astronomical_watch/scripts/" \
    "$MOBILE_REPO/src/astronomical_watch/scripts/" \
    --exclude="__pycache__" \
    --exclude="*.pyc"
echo "  ✓ scripts synced"
echo ""

# Copy documentation
echo "Copying documentation..."
cp "$DESKTOP_REPO/LICENSE.CORE" "$MOBILE_REPO/"
cp "$DESKTOP_REPO/LICENSE.MIT" "$MOBILE_REPO/"
cp "$DESKTOP_REPO/SPEC.md" "$MOBILE_REPO/"
cp "$DESKTOP_REPO/VSOP87D_SYSTEM.md" "$MOBILE_REPO/"
cp "$DESKTOP_REPO/CORE_FILES.md" "$MOBILE_REPO/"
echo "  ✓ documentation synced"
echo ""

echo "========================================"
echo "  SYNC COMPLETE!"
echo "========================================"
echo ""
echo "Changed files in mobile repo:"
cd "$MOBILE_REPO"
git status --short
echo ""
echo "To commit and push changes:"
echo "  cd $MOBILE_REPO"
echo "  git add ."
echo "  git commit -m 'Sync core improvements from desktop repo'"
echo "  git push"

