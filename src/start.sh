#!/bin/sh


pip install -r ./src/requirements.txt
python -m kopf run --namespace=streamlit ./src/main.py
