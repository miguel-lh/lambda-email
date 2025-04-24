#!/bin/bash

set -e

if [ ! -d "build" ]; then
    mkdir -p build
    echo "build folder created"
fi

echo "Installing requests library"
pip install requests -t ./build

if [ ! -d "src" ]; then
    echo "Error: src/ does not exist"
    exit 1
fi

if [ ! "$(ls -A src/*.py 2>/dev/null)" ]; then
    echo ".py files not found in src/"
    exit 0
fi

cp src/*.py build/

if [ $? -eq 0 ]; then
    echo ".py copied successfully in build/"
    echo "files copied:"
    ls -la build/*.py
else
    echo "Error copying files"
    exit 1
fi

zip_filename="build_package_$(date +%Y%m%d_%H%M%S).zip"
cd build && zip -r "../$zip_filename" .
cd ..

if [ $? -eq 0 ]; then
    echo "File $zip_filename created successfully"
    echo "zip size:"
    ls -lh "$zip_filename" | awk '{print $5}'
else
    echo "Error creating zip file"
    exit 1
fi
