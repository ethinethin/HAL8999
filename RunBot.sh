#!/bin/bash
while [ 1 ]
do
	echo "[ Running HAL: python3 HAL8999.py ]"
	python3 HAL8999.py
	echo "[ Disconnected? Sleeping for 5 seconds... ]"
	sleep 5
done
