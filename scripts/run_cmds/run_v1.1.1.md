## move_excluded_t1w_data.py
This version takes data from v1.1.0 and removes t1w images
```
swv=v1.1.4
dsv=v1.1.1
image_id=2b0bc6f8-23a5-4654-9229-f3aef5fd5c32
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
image_id=2b0bc6f8-23a5-4654-9229-f3aef5fd5c32
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
swv=v1.1.5
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
image_id=2b0bc6f8-23a5-4654-9229-f3aef5fd5c32
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
image_id=2b0bc6f8-23a5-4654-9229-f3aef5fd5c32
instance_type=8cpu-32ram-hpc
screen bidswrapps_start.py \
bids/freesurfer:v6.0.0-2 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer participant \
-ra "--license_key ~/fs.key --n_cpus 8" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.freesurfer.${dsv} -o /data.nfs/LHAB/logfiles/freesurfer_${dsv} -w 120hours -C 15 -c 8
s

screen bidswrapps_start.py \
bids/freesurfer:v6.0.0-2 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer group2 \
-ra "--license_key ~/fs.key --n_cpus 8 --parcellations aparc aparc.a2009s --measurements area volume thickness thicknessstd meancurv gauscurv foldind curvind" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.freesurfer.group2.${dsv} -o /data.nfs/LHAB/logfiles/freesurfer_${dsv}.group2 -w 60hours -C 15 -c 8

```

## freesurfer qc
```
dsv=v1.1.1
image_id=eed83290-1d28-4392-a616-59a719c8f417
instance_type=4cpu-16ram-hpc

screen bidswrapps_start.py \
fliem/freesurfer:qc_nb \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer participant \
--docker_opt "--entrypoint=/code/run_qc.py" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.freesurfer.${dsv}.qc -o /data.nfs/LHAB/logfiles/freesurfer_${dsv}.qc -w 120hours -C 15 -c 1 -J 250

screen bidswrapps_start.py \
fliem/freesurfer:qc_nb \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer group \
--docker_opt "--entrypoint=/code/run_qc.py" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.freesurfer.${dsv}.qc.group -o /data.nfs/LHAB/logfiles/freesurfer_${dsv}.qc.group -w 120hours -C 15 -c 1 -J 250

```

## tracula
```
dsv=v1.1.1
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