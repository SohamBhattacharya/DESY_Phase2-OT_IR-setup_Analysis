#!/bin/bash

NAME=$1

python -u python/analyze_2Smodules.py \
--coolYml "plots/$NAME/coolingCircuits.yml" \
--outdir "plots/analyze_2Smodules/$NAME" \
--coolXls "data/CoolingPipeRoadMap_DESY-dee-prototype.xlsx" \
--side "top" \
--skipCircuits "circuit_9h" \
--title $NAME \

