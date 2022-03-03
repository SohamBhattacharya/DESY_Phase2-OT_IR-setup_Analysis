#!/bin/bash

NAME=$1

python -u python/analyze_profiles.py \
--datayml plots/$NAME/profiles.yml \
--outdir plots/analyze_profiles/$NAME \
--side bottom \
--title $NAME \
