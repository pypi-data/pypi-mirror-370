#!/usr/bin/env bash

MYDIR="${0%/*}"

pushd ${MYDIR}

echo [+] Creating venv...
virtualenv venv
cd venv
source bin/activate

echo
echo [+] Installing dependencies...
python3 -m pip install brightspace-api
python3 -m pip install bscli

echo
echo [+] Running upload script
python3 -m bscli upload

echo
echo [+] Removing venv
deactivate
cd ..
rm -rf venv/

popd
