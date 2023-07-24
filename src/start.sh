#!/bin/sh


pip install -r ./app/requirements.txt
python -m kopf run ./app/main.py