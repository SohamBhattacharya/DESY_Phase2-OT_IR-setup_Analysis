#!/bin/bash

#NAME="DESY_dee_bottom_side_cfoams_lamp_off_2021-06-16_5-profiles"
NAME=$1

python -u python/analyze_profiles.py \
--datayml plots/$NAME/profiles.yml \
--outdir plots/analyze_profiles/$NAME \
--side bottom \
--skipCfoams "R1/CF10" "R3/CF12" "R5/CF14" "R5/CF16" "R7/CF16" "R7/CF18" "R9/CF18" "R9/CF20" \
--title $NAME \
