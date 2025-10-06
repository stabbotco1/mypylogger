#!/usr/bin/env bash
set -euo pipefail

OUTPUT_FILE="z_kiro_docs.txt"
MODE="${1:-full}"  # full, summary, or tree-only

echo "Generating Kiro documentation snapshot (mode: $MODE)..."

# Clear output file
> "$OUTPUT_FILE"

# Add tree structure at top
echo "==============================================================================" >> "$OUTPUT_FILE"
echo "KIRO DIRECTORY STRUCTURE" >> "$OUTPUT_FILE"
echo "==============================================================================" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
tree .kiro/ >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

if [[ "$MODE" == "tree-only" ]]; then
    echo "Tree-only mode complete: $OUTPUT_FILE"
    exit 0
fi

echo "==============================================================================" >> "$OUTPUT_FILE"
echo "KIRO DOCUMENTATION CONTENTS" >> "$OUTPUT_FILE"
echo "==============================================================================" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Find all files in .kiro/ recursively, sorted
find .kiro/ -type f | sort | while read -r filepath; do
    echo "------------------------------------------------------------------------------" >> "$OUTPUT_FILE"
    echo "FILE: $filepath" >> "$OUTPUT_FILE"
    filesize=$(wc -l < "$filepath")
    echo "SIZE: $filesize lines" >> "$OUTPUT_FILE"
    echo "------------------------------------------------------------------------------" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if [[ "$MODE" == "summary" ]]; then
        head -n 20 "$filepath" >> "$OUTPUT_FILE"
        if [[ $filesize -gt 20 ]]; then
            echo "... [truncated $(($filesize - 20)) lines] ..." >> "$OUTPUT_FILE"
        fi
    else
        cat "$filepath" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
done

echo "Documentation snapshot created: $OUTPUT_FILE"
echo "Total size: $(wc -l < "$OUTPUT_FILE") lines"
