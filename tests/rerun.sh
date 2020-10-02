#!/usr/bin/env bash
# rm ~/Dropbox/Lego/PartCache/Thumbnails/*
cd ..
python setup.py install
cd tests
pytest -s
