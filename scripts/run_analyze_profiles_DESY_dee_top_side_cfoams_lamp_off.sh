#!/bin/bash

NAME=$1

python -u python/analyze_profiles.py \
--datayml plots/$NAME/profiles.yml \
--outdir plots/analyze_profiles/$NAME \
--side top \
--skipCfoams "R3/CF11" "R5/CF15" "R7/CF17" "R9/CF19" \
--title $NAME \
