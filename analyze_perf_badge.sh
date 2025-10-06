#!/bin/bash
# Capture all performance badge analysis data

OUTPUT="z_perf_analysis.txt"

echo "=== PERFORMANCE BADGE ANALYSIS ===" > "$OUTPUT"
echo "" >> "$OUTPUT"

echo "=== 1. Recent README commits ===" >> "$OUTPUT"
git log --oneline -10 -- README.md >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"

echo "=== 2. Current git status ===" >> "$OUTPUT"
git status >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"

echo "=== 3. Current README badge content ===" >> "$OUTPUT"
grep -A 1 "Performance Ubuntu" README.md >> "$OUTPUT" 2>&1
grep -A 1 "Performance macOS" README.md >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"

echo "=== 4. Last 2 performance workflow runs ===" >> "$OUTPUT"
gh run list --workflow="performance-badge-update.yml" --limit 2 --json conclusion,displayTitle,createdAt,databaseId,event >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"

echo "=== 5. Performance script existence ===" >> "$OUTPUT"
ls -la scripts/measure_performance.py >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"

echo "=== 6. Check if sed would match current README ===" >> "$OUTPUT"
echo "Testing sed pattern match on current README..." >> "$OUTPUT"
grep "Ubuntu-" README.md | head -1 >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"

echo "Analysis complete. Results in $OUTPUT"
