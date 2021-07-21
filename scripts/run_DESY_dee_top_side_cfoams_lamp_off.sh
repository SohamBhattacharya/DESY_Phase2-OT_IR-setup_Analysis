python -u python/stitch_images.py \
    --inputDir "/media/soham/D/Programs/DESY/IR-setup/Data/2021-06-21/DESY_dee_top_side/lamp_off" \
    --inputPattern "cfoam_m15deg_lampoff_XXX_YYY.asc" \
    --geomFile "data/geometry_carbonFoam.xlsx" \
    --moduleType "PS" \
    --ringOpt "odd" \
    --originX 3640 \
    --originY 227 \
    --stepxtomm 1920/34952 \
    --stepytomm 895/716059 \
    --mmtopix 319/55.26 \
