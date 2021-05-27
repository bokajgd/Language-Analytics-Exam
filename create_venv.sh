#!/usr/bin/env bash

VENVNAME=lang_analytics_venv

python3 -m venv $VENVNAME
source $VENVNAME/bin/activate
pip install --upgrade pip

test -f requirements.txt && pip install -r requirements.txt

python -m spacy download en_core_web_sm

echo "finished building $VENVNAME"
