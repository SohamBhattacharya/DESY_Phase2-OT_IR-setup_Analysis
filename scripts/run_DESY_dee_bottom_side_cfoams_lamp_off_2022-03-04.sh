python -u python/stitch_images.py \
    --inputDir "/media/soham/D/Programs/DESY/IR-setup/Data/2022-03-04/DESY_dee/bottom_side/lamp_off" \
    --inputPattern "cfoam_m25deg-chiller_m11deg-dee_lampoff_XXX_YYY.asc" \
    --geomFile "data/geometry_carbonFoam.xlsx" \
    --moduleType "PS" \
    --side "bottom" \
    --ringOpt "odd" \
    --originX 0 \
    --originY 0 \
    --motorRefX 23538.75 0 \
    --motorRefY 248953 -80 \
    --stepxtomm 1920/34949 \
    --stepytomm 895/712360 \
    --mmtopix 310/55.26 \
    --cadImage "data/DESY_dee_cad_bottom_side.png" \
    --cadImageOrigin 1487 105 \
    --mmtopixCad 2492/1920 \