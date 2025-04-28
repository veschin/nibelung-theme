#!/bin/bash

# Function with parameters
file_backup() {
    local src=$1
    local dest="${src}.bak.$(date +%s)"
    cp "$src" "$dest" && echo "Backup created: $dest"
}

# Check arguments
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <file>"
    exit 1
fi

# Process input file
input_file=$1
if [[ -f "$input_file" ]]; then
    # Read file line by line
    counter=0
    while IFS= read -r line; do
        echo "Processing line $((++counter)): ${line:0:20}..."
    done < "$input_file"

    # Create backup
    file_backup "$input_file"
else
    echo "Error: File not found" >&2
    exit 2
fi
