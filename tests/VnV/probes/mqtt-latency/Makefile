build-no-cache:
	docker build --no-cache -t easyglobalmarket/mqtt-latency .
build:
	docker build -t easyglobalmarket/mqtt-latency .	
push:
	docker push easyglobalmarket/mqtt-latency	
run:
	docker run --rm -e "IP=192.168.1.207" -e "PORT=1883" -e "TOPIC=test" -e "ROUNDS=20" -e "INTERVAL=10" -e "CLIENTS=5" -e "COUNT=1"  --name mqtt-latency -d easyglobalmarket/mqtt-latency
stop:
	docker stop mqtt-latency
