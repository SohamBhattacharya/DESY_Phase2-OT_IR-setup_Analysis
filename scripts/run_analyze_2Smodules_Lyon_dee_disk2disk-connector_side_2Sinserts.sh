#!/bin/bash

NAME=$1

python -u python/analyze_2Smodules.py \
--coolYml "plots/$NAME/coolingCircuits.yml" \
--outdir "plots/analyze_2Smodules/$NAME" \
--coolXls "data/CoolingPipeRoadMap_Lyon-dee-prototype.xlsx" \
--side "bottom" \
--title $NAME \
--skipInsertsInFit \
    "R11/2S1_ins1" "R11/2S1_ins3" "R11/2S1_ins4" \
    "R13/2S1_ins1" "R13/2S1_ins3" "R13/2S1_ins4" \
    "R15/2S1_ins1" "R15/2S1_ins3" "R15/2S1_ins4" \
    "R11/2S26_ins2" "R11/2S26_ins3" "R11/2S26_ins5" \
    "R13/2S32_ins2" "R13/2S32_ins3" "R13/2S32_ins5" \
    "R15/2S38_ins2" "R15/2S38_ins3" "R15/2S38_ins5" \
