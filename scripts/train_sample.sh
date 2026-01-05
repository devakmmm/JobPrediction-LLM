#!/bin/bash
# Quick training script for sample data

python ml/train.py \
  --csv data/processed/software_engineer_new_york,ny.csv \
  --role "Software Engineer" \
  --location "New York, NY" \
  --window 12 \
  --epochs 50
