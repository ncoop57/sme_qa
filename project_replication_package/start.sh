#! /bin/sh

TAG=sme_qa

if [ $# -eq 1 ]; then
	if [ "$1" = "--build" ]; then
		# Build the docker container
		docker build -t $TAG .
	fi
fi


# Run the docker container
docker run -d --runtime=nvidia -v $(pwd)/main:/tf/main      \
	-v /mnt/data/sme_qa/models:/tf/data/models     \
	-v /mnt/data/sme_qa/datasets:/tf/data/datasets \
	-p 0.0.0.0:6007:6006 -p 8001:8888 $TAG
