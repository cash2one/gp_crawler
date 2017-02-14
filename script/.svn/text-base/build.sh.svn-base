#!/bin/sh

# prepare env
echo "prepare env..."
pip install enum34
pip install protobuf_to_dict

# compiler proto
echo "compiler proto files..."
cd proto > /dev/null
protoc -I. --python_out=. const.proto
protoc -I. --python_out=. app.proto
protoc -I. --python_out=. scan.proto
protoc -I. --python_out=. storage.proto
protoc -I. --python_out=. image.proto

cd - > /dev/null
