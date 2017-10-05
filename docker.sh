docker build -t hacky .
docker run -it --net="host" -v $(pwd)/outcomes:/home/hack4dk/outcomes hacky
