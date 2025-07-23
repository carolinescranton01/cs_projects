#!/usr/bin/env bash

# Directory with samples
SAMPLES_DIR="./"  # Adjust if needed

# Output base directory
OUTPUT_BASE="kneaddata_out"

# Create output directory base if it does not exist
mkdir -p "${OUTPUT_BASE}"

# Loop over all _R1.fastq.gz files
for R1_FILE in "${SAMPLES_DIR}"*_R1.fastq.gz; do
  # Check if file exists (in case no matches)
  [ -e "$R1_FILE" ] || continue

  # Extract sample prefix (remove _R1.fastq.gz)
  SAMPLE_PREFIX=$(basename "$R1_FILE" _R1.fastq.gz)

  # Construct R2 filename
  R2_FILE="${SAMPLES_DIR}${SAMPLE_PREFIX}_R2.fastq.gz"

  # Check if R2 file exists
  if [ ! -f "$R2_FILE" ]; then
    echo "Warning: R2 file $R2_FILE not found for sample $SAMPLE_PREFIX. Skipping."
    continue
  fi

  # Define output directory per sample to avoid overwriting
  SAMPLE_OUTPUT="${OUTPUT_BASE}/${SAMPLE_PREFIX}"

  # Run kneaddata command
  kneaddata --input1 "$R1_FILE" --input2 "$R2_FILE" -db "$KNEADDATA_DB" --output "$SAMPLE_OUTPUT" --threads 4

done
