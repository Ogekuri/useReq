#!/bin/bash

# Define base directory (default: current directory)
TARGET_DIR="${1:-.}"

# List of common cache directories to search for
# You can add or remove entries from this list based on your needs
CACHE_DIRS=(
    "__pycache__"       # Python
    ".pytest_cache"     # Python (Pytest)
    ".mypy_cache"       # Python (MyPy)
    ".cache"            # Generic / Pip / Various tools
    ".npm"              # Node (local npm cache)
    ".parcel-cache"     # Node (Parcel)
    ".eslintcache"      # Node (ESLint)
    ".sass-cache"       # Sass/SCSS
    ".terragrunt-cache" # Terraform/Terragrunt
    "htmlcov"           # Coverage reports
    # "node_modules"    # Uncomment if you want to nuke node_modules too (use with caution)
)

echo "--- Searching for cache directories in: $TARGET_DIR ---"
echo "Please wait, scanning..."

# Array to store found paths
FOUND_DIRS=()

# Loop to find directories matching the names in the list
for dir_name in "${CACHE_DIRS[@]}"; do
    # 'find' searches recursively
    # The while loop with IFS and -print0 handles filenames with spaces correctly
    while IFS= read -r -d '' found; do
        FOUND_DIRS+=("$found")
    done < <(find "$TARGET_DIR" -type d -name "$dir_name" -print0 2>/dev/null)
done

# Check if anything was found
if [ ${#FOUND_DIRS[@]} -eq 0 ]; then
    echo "No cache directories found."
    exit 0
fi

# Display what was found
echo ""
echo "Found the following directories:"
echo "---------------------------------"
for path in "${FOUND_DIRS[@]}"; do
    echo " -> $path"
done
echo "---------------------------------"
echo "Total directories found: ${#FOUND_DIRS[@]}"
echo ""

# Request confirmation
read -p "WARNING: Are you sure you want to permanently DELETE these directories? (y/N): " confirm

if [[ "$confirm" =~ ^[yY]$ ]]; then
    echo ""
    echo "Deleting..."
    count=0
    for path in "${FOUND_DIRS[@]}"; do
        rm -rf "$path"
        ((count++))
        echo "Deleted: $path"
    done
    echo ""
    echo "Cleanup complete! $count directories removed."
else
    echo ""
    echo "Operation aborted. No files were touched."
fi
