#!/bin/bash
# Batch Analysis Example
# Demonstrates batch processing of Z-stack images with various algorithms

set -e

# Configuration
INPUT_DIR="${1:-./data/raw}"
OUTPUT_DIR="${2:-./results}"
ALGORITHM="${3:-segmentation_3d}"
PARALLEL_WORKERS=8

echo "======================================"
echo "Z-Stack Analyzer - Batch Analysis"
echo "======================================"
echo ""
echo "Input Directory:  $INPUT_DIR"
echo "Output Directory: $OUTPUT_DIR"
echo "Algorithm:        $ALGORITHM"
echo "Parallel Workers: $PARALLEL_WORKERS"
echo ""

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Input directory does not exist: $INPUT_DIR"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Count files
FILE_COUNT=$(find "$INPUT_DIR" -name "*.tif" -o -name "*.tiff" | wc -l | tr -d ' ')
echo "Found $FILE_COUNT TIFF files to process"
echo ""

# Run batch analysis
echo "Starting batch analysis..."
zstack analyze batch \
    "$INPUT_DIR" \
    --output "$OUTPUT_DIR" \
    --algorithm "$ALGORITHM" \
    --parallel "$PARALLEL_WORKERS" \
    --format json \
    --pattern "*.tif"

echo ""
echo "======================================"
echo "Batch Analysis Complete!"
echo "======================================"
echo ""
echo "Results saved to: $OUTPUT_DIR"
echo ""

# Generate summary
echo "Generating summary..."
ls -lh "$OUTPUT_DIR" | tail -n +2 | wc -l | xargs echo "Total files created:"
du -sh "$OUTPUT_DIR" | cut -f1 | xargs echo "Total size:"

echo ""
echo "To view results:"
echo "  ls $OUTPUT_DIR"
echo "  cat $OUTPUT_DIR/batch_results_${ALGORITHM}.csv"
