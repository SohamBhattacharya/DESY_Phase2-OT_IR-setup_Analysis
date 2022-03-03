python -u python/stitch_images.py \
    --inputDir "/media/soham/D/Programs/DESY/IR-setup/Data/2021-11-11/Lyon_dee/no-disk2disk-connector_side/lamp_off" \
    --inputPattern "cfoam_m25deg-chiller_m10deg-dee_lampoff_XXX_YYY.asc" \
    --geomFile "data/geometry_carbonFoam.xlsx" \
    --moduleType "PS" \
    --ringOpt "odd" \
    --side "top" \
    --originX 0 \
    --originY 245 \
    --motorRefX 23503 0\
    --stepxtomm 1565.44/28506 \
    --stepytomm 626.78/499919 \
    --mmtopix 311.67/55.26 \
    --cadImage "data/Lyon_Dee_cad_no-disk-to-disk-connector_side.png" \
    --cadImageOrigin 595 33 \
    --mmtopixCad 780/1565.44 \

