#!/bin/bash

set -e

echo "Zipping lambda function..."
zip -r lambda_function.zip src/ config/ -x "*/__pycache__/*" "*.pyc"
echo "Done."
