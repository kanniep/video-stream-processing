build-image:
	docker build -t kannie/proto-builder .

build-protos:
	protofiles=""
	for i in common/protos/*.proto; do \
		protofiles="$$protofiles $$i"; \
	done; \
	docker_command="docker run -it --rm -v $$PWD:/protos kannie/proto-builder python -m grpc_tools.protoc --proto_path=./common/protos --python_out=. --grpc_python_out=. $$protofiles"; \
	eval $$docker_command
