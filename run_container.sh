#docker container run -it --device /dev/video0:/dev/video0 -v "$PWD"/sm:/sm ubuntu bash
docker container run -it --device /dev/video0:/dev/video0 registry:5000/predictord:1.0.16
