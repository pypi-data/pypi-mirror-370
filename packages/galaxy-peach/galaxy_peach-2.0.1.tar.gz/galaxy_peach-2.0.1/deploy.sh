docker image build --no-cache --platform linux/amd64 -t galaxy .
docker tag galaxy ghcr.io/eth-peach-lab/galaxy/galaxy:latest
docker push ghcr.io/eth-peach-lab/galaxy/galaxy:latest