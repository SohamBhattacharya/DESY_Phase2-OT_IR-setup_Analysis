python -u python/stitch_images.py \
    --inputDir "/media/soham/D/Programs/DESY/IR-setup/Data/2022-02-25/DESY_dee/top_side/lamp_off" \
    --inputPattern "cfoam_m25deg-chiller_lampoff_XXX_YYY.asc" \
    --geomFile "data/geometry_carbonFoam.xlsx" \
    --moduleType "PS" \
    --side "top" \
    --ringOpt "odd" \
    --originX 0 \
    --originY 0 \
    --motorRefX 23550 0 \
    --motorRefY 247706.5 -80 \
    --stepxtomm 1920/34948 \
    --stepytomm 895/713813.5 \
    --mmtopix 287/55.26 \
    --cadImage "data/DESY_dee_cad_top_side.png" \
    --cadImageOrigin 1487 105 \
    --mmtopixCad 2492/1920 \