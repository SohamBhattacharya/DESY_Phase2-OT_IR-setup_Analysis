python -u python/stitch_images.py \
    --inputDir "/media/soham/D/Programs/DESY/IR-setup/Data/2021-11-26/Lyon_dee/disk2disk-connector_side/lamp_off" \
    --inputPattern "cfoam_m25deg-chiller_m11deg-dee_lampoff_XXX_YYY.asc" \
    --geomFile "data/geometry_carbonFoam.xlsx" \
    --moduleType "PS" \
    --ringOpt "odd" \
    --side "bottom" \
    --originX 0 \
    --originY 245 \
    --motorRefX 23658 0\
    --stepxtomm 1565.44/28506 \
    --stepytomm 626.78/499613 \
    --mmtopix 310./55.26 \
    --cadImage "data/Lyon_Dee_cad_with-disk-to-disk-connector_side.png" \
    --cadImageOrigin 595 33 \
    --mmtopixCad 780/1565.44 \

