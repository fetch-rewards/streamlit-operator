#!/bin/sh


pip install -r ./src/requirements.txt
python -m kopf run ./src/main.py
