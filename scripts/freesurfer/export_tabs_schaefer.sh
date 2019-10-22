#!/bin/bash
# run in python2 environment: source activate py2
# exports cortical volume for the 200 parcels / 17 NWs solution of Schaefer2018
# the fsaverage subjects needs the two annotation files in label/
# lh.Schaefer2018_200Parcels_17Networks_order.annot
# rh.Schaefer2018_200Parcels_17Networks_order.annot
# from
# https://github.com/ThomasYeoLab/CBIG/tree/v0.14.3-Update_Yeo2011_Schaefer2018_labelname/stable_projects/brain_parcellation/Schaefer2018_LocalGlobal/Parcellations/FreeSurfer5.3/fsaverage/label

# run via docker
# export SUBJECTS_DIR=/data.nfs/dynage/lhab_freesurfer_rw
#
# docker run --rm -ti \
# -v ./export_tabs_schaefer.sh:/code/export_tabs_schaefer.sh \
# -v $SUBJECTS_DIR:/data/:rw \
# -v /data.nfs/sc/license.txt:/opt/freesurfer/.license \
# --entrypoint=/bin/bash \
# bids/freesurfer:v6.0.1-5 -c "bash /code/export_tabs_schaefer.sh"

set -eu -o pipefail

fsd=/data
export SUBJECTS_DIR=$fsd
cd $fsd

odir=${fsd}/00_group_Schaefer2018
mkdir -p $odir


s=`echo *sub*long*`
parc=Schaefer2018_200Parcels_17Networks_order
echo $s
echo $parc
echo XXXXXXXXXXXXXXX

for subject in $s
do
  for h in lh rh
    do
      # step 1: map parc to subject space
      # http://www.mail-archive.com/freesurfer@nmr.mgh.harvard.edu/msg34518.html
      if [ ! -f $SUBJECTS_DIR/${subject}/label/${h}.${parc}.annot ]; then
        cmd="mri_surf2surf --srcsubject fsaverage --trgsubject $subject --hemi ${h} --sval-annot $SUBJECTS_DIR/fsaverage/label/${h}.${parc}.annot --tval $SUBJECTS_DIR/${subject}/label/${h}.${parc}.annot"
        echo $cmd
        $cmd
        echo
      fi

      # step 2: create .stat file
      if [ ! -f ${subject}/stats/${h}.${parc}.stats ]; then
        cmd="mris_anatomical_stats -mgz -cortex ${subject}/label/${h}.cortex.label -f ${subject}/stats/${h}.${parc}.stats -b -a ${subject}/label/${h}.${parc}.annot $subject ${h} white"
        echo $cmd
        $cmd
        echo
      fi
  done
done

# step 3: create group files
aparcstats2table --hemi lh --subjects $s --parc ${parc} --meas thickness --tablefile $odir/lh.${parc}.thickness.txt
aparcstats2table --hemi rh --subjects $s --parc ${parc} --meas thickness --tablefile $odir/rh.${parc}.thickness.txt
aparcstats2table --hemi lh --subjects $s --parc ${parc} --meas volume --tablefile $odir/lh.${parc}.volume.txt
aparcstats2table --hemi rh --subjects $s --parc ${parc} --meas volume --tablefile $odir/rh.${parc}.volume.txt
aparcstats2table --hemi lh --subjects $s --parc ${parc} --meas area --tablefile $odir/lh.${parc}.area.txt
aparcstats2table --hemi rh --subjects $s --parc ${parc} --meas area --tablefile $odir/rh.${parc}.area.txt
