#!/bin/bash

NAME=$1

python -u python/analyze_profiles.py \
--datayml plots/$NAME/profiles.yml \
--lyonDTfile measurements/Lyon-dee_PS_Lyon-measurements_no-connector-side.txt \
--outdir plots/analyze_profiles/$NAME \
--side top \
--title $NAME \
