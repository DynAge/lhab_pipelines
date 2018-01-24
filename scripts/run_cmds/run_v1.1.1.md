## move_excluded_t1w_data.py
This version takes data from v1.1.0 and removes t1w images
```
swv=v1.1.4
dsv=v1.1.1
image_id=395115ed-d2c3-4e9f-89ee-6ed5c245d60a
instance_type=4cpu-16ram-hpc

screen bidswrapps_start.py \
fliem/lhab_pipelines:${swv} \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/excluded/ group \
--volume /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/mriqc:/data/mriqc /data.nfs/LHAB/Documentation/v1.1.0_overview/qc_t1w/:/data/rating \
--runscript_cmd "python /code/lhab_pipelines/scripts/qc/move_excluded_t1w_data.py" \
-ra "--mri_qc_path /data/mriqc --exclusion_file /data/rating/visu_ratings_fl_20170503.xlsx" \
--image_id ${image_id} \
--instance_type ${instance_type} \
--no-input-folder-ro \
-s ~/cloudsessions/lhab.exclude_t1w.${dsv} -o /data.nfs/LHAB/logfiles/${dsv}/exclude_t1w -C 15 -c 1 -v
```

## move_excluded_dwi_data.py
```
swv=v1.1.5
dsv=v1.1.1
image_id=395115ed-d2c3-4e9f-89ee-6ed5c245d60a
instance_type=4cpu-16ram-hpc

screen bidswrapps_start.py \
fliem/lhab_pipelines:${swv} \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/excluded/ group \
--volume /data.nfs/LHAB/Documentation/v1.1.0_overview/qc_dwi/:/data/rating \
--runscript_cmd "python /code/lhab_pipelines/scripts/qc/move_excluded_dwi_data.py" \
-ra "--exclusion_file /data/rating/remove_dwi_fl_20170511.xlsx" \
--image_id ${image_id} \
--instance_type ${instance_type} \
--no-input-folder-ro \
-s ~/cloudsessions/lhab.exclude_dwi.${dsv} -o /data.nfs/LHAB/logfiles/${dsv}/exclude_dwi -C 15 -c 1 -v
```


## run_post_conversion_routines.py
checks data and reduces subjects data

```
swv=v1.1.7
dsv=v1.1.1
vshort=v1.1.1
sfile=lhab_all_subjects.tsv


docker run --rm -ti \
-v /Volumes/lhab_raw/01_RAW:/data/in \
-v /Volumes/lhab_raw/Nifti/${vshort}/:/data/out \
fliem/lhab_pipelines:${swv} python /code/lhab_pipelines/scripts/nii_conversion/run_post_conversion_routines.py /data/in /data/out --participant_file /data/in/00_PRIVATE_sub_lists/${sfile} --ds_version ${dsv}
```


## mriqc
Rerun group step
```
dsv=v1.1.1
image_id=395115ed-d2c3-4e9f-89ee-6ed5c245d60a
instance_type=4cpu-16ram-hpc

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
dsv=v1.1.1
image_id=40757134-9756-4054-9ec2-8eeaa1d8d677
instance_type=8cpu-32ram-hpc
screen bidswrapps_start.py \
bids/freesurfer:v6.0.0-2 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer_v6.0.0-2 participant \
-ra "--license_key ~/fs.key --n_cpus 8" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.freesurfer.${dsv} -o /data.nfs/LHAB/logfiles/freesurfer_${dsv} -w 120hours -C 15 -c 8
s


screen bidswrapps_start.py \
bids/freesurfer:v6.0.1-3 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer_v6.0.0-2 group2 \
-ra "--license_file  /opt/freesurfer/.license --n_cpus 8 --parcellations aparc aparc.a2009s --measurements area volume thickness thicknessstd meancurv gauscurv foldind curvind" \
--image_id ${image_id} \
--instance_type ${instance_type} \
--volume /data.nfs/license.txt:/opt/freesurfer/.license \
-pel lhabX0110 \
-s cloudsessions/lhab.freesurfer.group2.${dsv} -o /data.nfs/LHAB/logfiles/freesurfer_${dsv}.group2 -w 60hours -C 15 -c 8

```
For the group2 step version 6.0.1-3 is used to extract euler numbers.


#### QCACHE
    dsv=v1.1.1
    image_id=4313d605-12f1-4c8b-979b-afb5cb2d2faf
    instance_type=16cpu-64ram-hpc
    screen bidswrapps_start.py \
    fliem/freesurfer_utils:v0.9.1 \
    /data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer_v6.0.0-2 participant \
    -ra "--license_key ~/fs.key --n_cpus 4 --workflow qcache --stream long --measurements thickness area volume " \
    --image_id ${image_id} \
    --instance_type ${instance_type} \
    -s cloudsessions/lhab.fs_utils.qcache -o /data.nfs/LHAB/logfiles/fs_utils.qcache -w 120hours -C 15 -c 4 -J 150 -v

## freesurfer qc
```
dsv=v1.1.1
image_id=395115ed-d2c3-4e9f-89ee-6ed5c245d60a
instance_type=4cpu-16ram-hpc

screen bidswrapps_start.py \
fliem/freesurfer:qc_nb \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer_v6.0.0-2 participant \
--docker_opt "--entrypoint=/code/run_qc.py" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.freesurfer.${dsv}.qc -o /data.nfs/LHAB/logfiles/freesurfer_${dsv}.qc -w 120hours -C 15 -c 1 -J 250

screen bidswrapps_start.py \
fliem/freesurfer:qc_nb \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer_v6.0.0-2 group \
--docker_opt "--entrypoint=/code/run_qc.py" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.freesurfer.${dsv}.qc.group -o /data.nfs/LHAB/logfiles/freesurfer_${dsv}.qc.group -w 120hours -C 15 -c 1 -J 250
```



## tracula
```
dsv=v1.1.1
image_id=395115ed-d2c3-4e9f-89ee-6ed5c245d60a
instance_type=8cpu-32ram-hpc

screen bidswrapps_start.py \
bids/tracula:v6.0.0-4 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/tracula_v6.0.0-4 participant \
-ra "--license_key ~/fs.key --freesurfer_dir /data/freesurfer --n_cpus 4" \
--volume /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer_v6.0.0-2/:/data/freesurfer \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.tracula_v6.0.0-4_${dsv} -o /data.nfs/LHAB/logfiles/tracula_v6.0.0-4_${dsv} -w 120hours -C 15 -c 4


screen bidswrapps_start.py \
bids/tracula:v6.0.0-4 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/tracula_v6.0.0-4 group1 \
-ra "--license_key ~/fs.key --freesurfer_dir /data/freesurfer --n_cpus 4" \
--volume /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer_v6.0.0-2/:/data/freesurfer \
--image_id ${image_id} \
--instance_type ${instance_type} \
-pel lhabX0042 lhabX0150 lhabX0161 \
-s cloudsessions/lhab.tracula_v6.0.0-4_group1.${dsv} -o /data.nfs/LHAB/logfiles/tracula_v6.0.0-4_${dsv}_group1 -w 60hours -C 15 -c 4 -v

screen bidswrapps_start.py \
bids/tracula:v6.0.0-4 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/tracula_v6.0.0-4 group2 \
-ra "--license_key ~/fs.key --freesurfer_dir /data/freesurfer --n_cpus 4" \
--volume /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer_v6.0.0-2/:/data/freesurfer \
--image_id ${image_id} \
--instance_type ${instance_type} \
-pel lhabX0042 lhabX0150 lhabX0161 \
-s cloudsessions/lhab.tracula_v6.0.0-4_group2.${dsv} -o /data.nfs/LHAB/logfiles/tracula_v6.0.0-4_${dsv}_group2 -w 60hours -C 15 -c 4 -v

```




## baracus
```

dsv=v1.1.1
image_id=09650c64-6818-47c3-b744-6db02e352466
instance_type=4cpu-16ram-hpc
screen bidswrapps_start.py \
fliem/baracus:0.1.4.dev \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer_v53 /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/baracus participant \
--image_id ${image_id} \
--instance_type ${instance_type} \
--no-input-folder-ro \
-s cloudsessions/lhab.baracus.participants -o /data.nfs/LHAB/logfiles/lhab.baracus.participants -w 120hours -C 15 -c 1 -J 350 -v

screen bidswrapps_start.py \
fliem/baracus:0.1.4.dev \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer_v53 /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/baracus group \
--image_id ${image_id} \
--instance_type ${instance_type} \
--no-input-folder-ro \
-s cloudsessions/lhab.baracus.group -o /data.nfs/LHAB/logfiles/lhab.baracus.group -w 120hours -C 15 -c 1 -J 450 -v
```


## extract_FA
```
dsv=v1.1.1
image_id=5e159afe-41de-4724-8f47-244d45d6a014
instance_type=8cpu-32ram-hpc #
screen bidswrapps_start.py \
fliem/extract_fa:v2.1 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/extract_fa_v2 group \
--image_id ${image_id} \
--instance_type ${instance_type} \
-ra "--n_cpus 4" \
-s ~/cloudsessions/lhab.extract_fa_v2.group -o /data.nfs/LHAB/logfiles/lhab.extract_fa_v2.group -w 120hours -C 15 -c 4 -J 350 -v


dsv=v1.1.1
image_id=05b806d7-dc4d-47c9-979d-a5d6fbcc2f30
instance_type=8cpu-32ram-hpc #
screen bidswrapps_start.py \
fliem/extract_fa:v2 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/extract_fa_v2 participant \
--image_id ${image_id} \
--instance_type ${instance_type} \
-ra "--n_cpus 4" \
-s ~/cloudsessions/lhab.extract_fa_v2.participants -o /data.nfs/LHAB/logfiles/lhab.extract_fa_v2.participants -w 120hours -C 15 -c 4 -J 350 -v
```