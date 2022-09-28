python -u python/stitch_images.py \
    --inputDir "/media/soham/D/Programs/DESY/IR-setup/Data/2021-07-08/DESY_dee/top_side/lamp_off" \
    --inputPattern "2Sinserts_m15deg_lampoff_XXX_YYY.asc" \
    --geomFile "data/geometry_carbonFoam.xlsx" \
    --moduleType "2S" \
    --ringOpt "odd" \
    --side "top" \
    --originX 0 \
    --isPrototype \
    --originY 0 \
    --motorRefX 27732.5 0 \
    --motorRefY 254992.5 -80 \
    --stepxtomm 1920/34953 \
    --stepytomm 895/714133.5 \
    --mmtopix 361/93 \
    --cadImage "data/DESY_dee_cad_top_side.png" \
    --cadImageOrigin 1487 105 \
    --mmtopixCad 2492/1920 \
    --coolCircFiles "data/coolingCircuit_2Sinserts_DESY-dee-prototype.yml" \
#    --coolCircFiles "data/coolingCircuit_top_side_2Sinserts.yml" \
