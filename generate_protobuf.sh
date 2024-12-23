mkdir -p com

cd proto
protoc --python_out=../com *.proto
protol --create-package --in-place --python-out=../com protoc --proto-path=. *.proto 
