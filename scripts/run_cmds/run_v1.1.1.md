## run_nii_conversion.py
performs the parrec 2 nifti conversion (on sc)

```
swv=v1.1.1
dsv=v1.1.0
sfile=lhab_all_subjects.tsv
image_id=2b0bc6f8-23a5-4654-9229-f3aef5fd5c32
instance_type=4cpu-16ram-hpc

screen bidswrapps_start.py \
fliem/lhab_pipelines:${swv} \
/data.nfs/LHAB/01_RAW /data.nfs/LHAB/NIFTI participant \
-pf /data.nfs/LHAB/01_RAW/00_PRIVATE_sub_lists/${sfile} \
--runscript_cmd "python /code/lhab_pipelines/scripts/nii_conversion/run_nii_conversion.py" \
-ra "--no-public_output --ds_version ${dsv}" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.conv.private.${dsv} -o /data.nfs/LHAB/logfiles/${dsv}/logs_private -C 15 -c 1 -v -J 660


screen bidswrapps_start.py \
fliem/lhab_pipelines:${swv} \
/data.nfs/LHAB/01_RAW /data.nfs/LHAB/NIFTI participant \
-pf /data.nfs/LHAB/01_RAW/00_PRIVATE_sub_lists/${sfile} \
--runscript_cmd "python /code/lhab_pipelines/scripts/nii_conversion/run_nii_conversion.py" \
-ra "--ds_version ${dsv}" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.conv.public.${dsv} -o /data.nfs/LHAB/logfiles/${dsv}/logs_public -C 15 -c 1 -v -J 660


```




## run_post_conversion_routines.py
checks data and reduces subjects data

```
swv=v1.1.1
dsv=v1.1.0
vshort=v1.1.0
sfile=lhab_all_subjects.tsv


docker run --rm -ti \
-v /Volumes/lhab_raw/01_RAW:/data/in \
-v /Volumes/lhab_raw/Nifti/${vshort}/:/data/out \
fliem/lhab_pipelines:${swv} python /code/lhab_pipelines/scripts/nii_conversion/run_post_conversion_routines.py /data/in /data/out --participant_file /data/in/00_PRIVATE_sub_lists/${sfile} --ds_version ${dsv}



docker run --rm -ti \
-v /Volumes/lhab_raw/01_RAW:/data/in \
-v /Volumes/lhab_raw/Nifti/${vshort}/:/data/out \
fliem/lhab_pipelines:${swv} python /code/lhab_pipelines/scripts/nii_conversion/run_post_conversion_routines.py /data/in /data/out --participant_file /data/in/00_PRIVATE_sub_lists/${sfile} --ds_version ${dsv} --no-public_output
```


## mriqc
```
dsv=v1.1.0
image_id=2b0bc6f8-23a5-4654-9229-f3aef5fd5c32
instance_type=4cpu-16ram-hpc

screen bidswrapps_start.py \
poldracklab/mriqc:0.9.1 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/mriqc participant \
--image_id ${image_id} \
--instance_type ${instance_type} \
-ra "--n_procs 4 --mem_gb 16" \
-s cloudsessions/lhab.mriqc.${dsv} -o /data.nfs/LHAB/logfiles/mriqc.${dsv} -w 60hours -C 15 -c 4 -m 4GB -v

screen bidswrapps_start.py \
poldracklab/mriqc:0.9.1 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/mriqc/derivatives /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/mriqc/ group \
--image_id ${image_id} \
--instance_type ${instance_type} \
-ra "--n_procs 4 --mem_gb 16" \
-s cloudsessions/lhab.mriqc.${dsv}.group -o /data.nfs/LHAB/logfiles/mriqc.${dsv}.group -w 60hours -C 15 -c 4 -v

```
#

## freesurfer
```
dsv=v1.1.0
image_id=2b0bc6f8-23a5-4654-9229-f3aef5fd5c32
instance_type=8cpu-32ram-hpc
screen bidswrapps_start.py \
bids/freesurfer:v6.0.0-2 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer participant \
-ra "--license_key ~/fs.key --n_cpus 8" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.freesurfer.${dsv} -o /data.nfs/LHAB/logfiles/freesurfer_${dsv} -w 60hours -C 15 -c 8


screen bidswrapps_start.py \
bids/freesurfer:v6.0.0-2 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer group2 \
-ra "--license_key ~/fs.key --n_cpus 8 --parcellations aparc aparc.a2009s --measurements area volume thickness thicknessstd meancurv gauscurv foldind curvind" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.freesurfer.group2.${dsv} -o /data.nfs/LHAB/logfiles/freesurfer_${dsv}.group2 -w 60hours -C 15 -c 8

```


## tracula
```
dsv=v1.1.0
image_id=2b0bc6f8-23a5-4654-9229-f3aef5fd5c32
instance_type=2cpu-8ram-hpc

screen bidswrapps_start.py \
bids/tracula:v6.0.0-2 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/tracula participant \
-ra "--license_key ~/fs.key --freesurfer_dir /data/freesurfer" \
--volume /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer/:/data/freesurfer \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.tracula.${dsv} -o /data.nfs/LHAB/logfiles/tracula_${dsv} -w 60hours -C 15 -c 2


screen bidswrapps_start.py \
bids/tracula:v6.0.0-2 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/tracula group1 \
-ra "--license_key ~/fs.key --freesurfer_dir /data/freesurfer" \
--volume /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer/:/data/freesurfer \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.tracula.group1.${dsv} -o /data.nfs/LHAB/logfiles/tracula_${dsv}_group1 -w 60hours -C 15 -c 2 -v

screen bidswrapps_start.py \
bids/tracula:v6.0.0-2 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/tracula group2 \
-ra "--license_key ~/fs.key --freesurfer_dir /data/freesurfer" \
--volume /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer/:/data/freesurfer \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.tracula.group2.${dsv} -o /data.nfs/LHAB/logfiles/tracula_${dsv}_group2 -w 60hours -C 15 -c 2 -v

```