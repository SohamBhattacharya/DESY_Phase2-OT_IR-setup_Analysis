python -u python/stitch_images.py \
    --inputDir "/media/soham/D/Programs/DESY/IR-setup/Data/2021-12-02/Lyon_dee/disk2disk-connector_side/lamp_off" \
    --inputPattern "2Sinserts_m25deg-chiller_m10deg-dee_lampoff_XXX_YYY.asc" \
    --geomFile "data/geometry_carbonFoam.xlsx" \
    --moduleType "2S" \
    --ringOpt "odd" \
    --side "bottom" \
    --isPrototype \
    --originX 0 \
    --originY 232 \
    --motorRefX 23543 0 \
    --stepxtomm 1565.44/28502 \
    --stepytomm 626.78/500178.5 \
    --mmtopix 364/93 \
    --cadImage "data/Lyon_Dee_cad_with-disk-to-disk-connector_side.png" \
    --cadImageOrigin 595 33 \
    --mmtopixCad 780/1565.44 \
    --coolCircFiles "data/coolingCircuit_2Sinserts_Lyon-dee-prototype.yml" \

