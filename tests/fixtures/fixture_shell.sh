#!/bin/bash
# @file fixture_shell.sh
# @brief Comprehensive Shell/Bash test fixture for parser validation.
# @details Covers arrays, associative arrays, parameter expansion,
#          here documents, process substitution, traps, getopts,
#          case statements, arithmetic, and here strings.
# Single line comment

# ── Variables and exports ─────────────────────────────────────────────

# @brief Greeting message template.
MY_VAR="hello"

# @brief Extended PATH including local binary directory.
export PATH_EXT="/usr/local/bin"

# @brief Immutable maximum iteration counter.
readonly MAX_COUNT=10

# @brief Build version set via declare.
declare -r BUILD_VERSION="1.0.0"

# @brief Debug mode flag (0=off, 1=on).
DEBUG_MODE=0

# ── Arrays ────────────────────────────────────────────────────────────

# @brief Indexed array of supported languages.
declare -a LANGUAGES=("python" "rust" "go" "java" "typescript")

# @brief Associative array mapping extensions to languages.
declare -A EXT_MAP=(
    [py]="python"
    [rs]="rust"
    [go]="go"
    [java]="java"
    [ts]="typescript"
)

# ── Functions ─────────────────────────────────────────────────────────

# @brief Greet a user by name on stdout.
# @param $1 The user's name.
function greet() {
    local name="${1:?Name required}"
    # Validate non-empty name
    if [[ -z "$name" ]]; then
        echo "Error: empty name" >&2
        return 1
    fi
    echo "Hello ${name}!"
}

# @brief Remove temporary files and directories.
# @details Called by trap on EXIT for cleanup.
cleanup() {
    local tmp_dir="${TMPDIR:-/tmp}/myapp_$$"
    if [[ -d "$tmp_dir" ]]; then
        # Remove temp directory and all contents
        rm -rf "$tmp_dir"
    fi
    echo "Cleanup complete"
}

# @brief Parse command-line options using getopts.
# @param $@ Command-line arguments.
# @return Sets global variables based on parsed options.
parse_args() {
    local opt
    while getopts "vdhf:o:" opt; do
        case "$opt" in
            v)
                # Enable verbose output
                VERBOSE=1
                ;;
            d)
                # Enable debug mode
                DEBUG_MODE=1
                ;;
            f)
                # Set input file path
                INPUT_FILE="$OPTARG"
                ;;
            o)
                # Set output file path
                OUTPUT_FILE="$OPTARG"
                ;;
            h)
                echo "Usage: $0 [-v] [-d] [-f file] [-o output] [-h]"
                return 0
                ;;
            *)
                echo "Unknown option: $opt" >&2
                return 1
                ;;
        esac
    done
    shift $((OPTIND - 1))
}

# @brief Process a file with error handling and logging.
# @param $1 Path to the input file.
# @param $2 Optional output path (defaults to stdout).
# @return 0 on success, 1 on failure.
process_file() {
    local input="$1"
    local output="${2:-/dev/stdout}"

    # Verify input file exists and is readable
    if [[ ! -f "$input" ]]; then
        echo "Error: file not found: $input" >&2
        return 1
    fi

    if [[ ! -r "$input" ]]; then
        echo "Error: file not readable: $input" >&2
        return 1
    fi

    # Count lines using wc
    local line_count
    line_count=$(wc -l < "$input")
    echo "Processing $input ($line_count lines)" >&2

    # Transform and write output
    while IFS= read -r line; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        echo "$line"
    done < "$input" > "$output"

    return 0
}

# @brief Execute a command with retry logic.
# @param $1 Maximum number of retry attempts.
# @param $@ The command and arguments to execute.
# @return Exit code of the final attempt.
retry_command() {
    local max_attempts="$1"
    shift
    local attempt=1

    while (( attempt <= max_attempts )); do
        # Attempt the command
        if "$@"; then
            return 0
        fi
        echo "Attempt $attempt/$max_attempts failed" >&2
        (( attempt++ ))
        # Exponential backoff
        sleep $(( 2 ** (attempt - 1) ))
    done

    echo "All $max_attempts attempts failed" >&2
    return 1
}

# @brief Log a message with timestamp prefix.
# @param $1 Log level (INFO, WARN, ERROR).
# @param $@ Message text.
log_message() {
    local level="$1"
    shift
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $*" >&2
}

# @brief Generate a temporary file and return its path.
# @return Path to the created temporary file.
make_temp() {
    local tmpfile
    tmpfile=$(mktemp "${TMPDIR:-/tmp}/myapp_XXXXXX")
    echo "$tmpfile"
}

# ── Traps ─────────────────────────────────────────────────────────────

# @brief Register cleanup function on script exit.
trap cleanup EXIT

# @brief Handle interrupt signal gracefully.
trap 'echo "Interrupted"; exit 130' INT TERM

# ── Here document ─────────────────────────────────────────────────────

# @brief Generate a configuration file using heredoc.
generate_config() {
    cat <<EOF
# Auto-generated configuration
version=${BUILD_VERSION}
debug=${DEBUG_MODE}
max_count=${MAX_COUNT}
EOF
}

# ── Arithmetic and parameter expansion ────────────────────────────────

# @brief Compute factorial iteratively.
# @param $1 Non-negative integer.
# @return Factorial result.
factorial() {
    local n="${1:-1}"
    local result=1
    local i
    for (( i = 2; i <= n; i++ )); do
        # Multiply accumulator
        (( result *= i ))
    done
    echo "$result"
}

# ── Source external configuration ─────────────────────────────────────

# @brief Load external configuration script if present.
if [[ -f ./config.sh ]]; then
    source ./config.sh
fi
