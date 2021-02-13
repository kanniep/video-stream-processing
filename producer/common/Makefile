build-image:
	docker build -t kannie/proto-builder .
build-protos:
	docker run -it --rm -v ${PWD}:/protos kannie/proto-builder python -m grpc_tools.protoc --proto_path=./protos --python_out=./proto_models --grpc_python_out=./proto_models $(find protos/*.proto -type f -printf "protos/%f ")
