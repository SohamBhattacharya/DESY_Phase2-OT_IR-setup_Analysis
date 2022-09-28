#!/bin/bash

NAME=$1

python -u python/analyze_profiles.py \
--datayml plots/$NAME/profiles.yml \
--outdir plots/analyze_profiles/$NAME \
--side top \
--skipCfoams \
    "R1/CF10" \
    "R3/CF11" "R3/CF12" \
    "R5/CF14" "R5/CF15" "R5/CF16" \
    "R7/CF16" "R7/CF17" "R7/CF18" \
    "R9/CF18" "R9/CF19" "R9/CF20" \
--title $NAME \
