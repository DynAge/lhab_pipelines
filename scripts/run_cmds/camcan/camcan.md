
## MRIQC

```
image_id=2b0bc6f8-23a5-4654-9229-f3aef5fd5c32
instance_type=4cpu-16ram-hpc

screen bidswrapps_start.py \
poldracklab/mriqc:0.9.1 \
/data.nfs/camcan/dl/cc700/mri/pipeline/release004/BIDSsep/anat /data.nfs/camcan/output/mriqc participant \
--image_id ${image_id} \
--instance_type ${instance_type} \
-ra "--n_procs 4 --mem_gb 16" \
-s cloudsessions/camcan.mriqc.participants -o /data.nfs/camcan/logfiles/camcan.mriqc.participants -w 120hours -C 15 -c 4 -m 4GB -v`
```

## FS


```
image_id=9f141c0a-3b41-483c-acd8-4975ad610a18
instance_type=4cpu-16ram-hpc
screen bidswrapps_start.py \
bids/freesurfer:v6.0.0-4 \
/data.nfs/camcan/bids /data.nfs/camcan/output/freesurfer_v6.0.0-4 participant \
-ra "--license_key ~/fs.key --n_cpus 4" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/camcan.freesurfer.participants -o /data.nfs/camcan/logfiles/camcan.freesurfer.participants -w 120hours -C 15 -c 4 -J 350 -v -N

screen bidswrapps_start.py \
bids/freesurfer:v6.0.0-4 \
/data.nfs/camcan/bids /data.nfs/camcan/output/freesurfer_v6.0.0-4 group2 \
-ra "--license_key ~/fs.key --n_cpus 4 --parcellations aparc aparc.a2009s --measurements area volume thickness thicknessstd meancurv gauscurv foldind curvind" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/camcan.freesurfer.group2 -o /data.nfs/camcan/logfiles/camcan.freesurfer.group2 -w 60hours -C 15 -c 8 -v
```

## Tracula
    image_id=395115ed-d2c3-4e9f-89ee-6ed5c245d60a
    instance_type=8cpu-32ram-hpc

    screen bidswrapps_start.py \
    bids/tracula:v6.0.0-4 \
    /data.nfs/camcan/bids /data.nfs/camcan/output/tracula_v6.0.0-4 participant \
    -ra "--license_key ~/fs.key --freesurfer_dir /data/freesurfer --n_cpus 4" \
    --volume /data.nfs/camcan/output/freesurfer_v6.0.0-4/:/data/freesurfer \
    --image_id ${image_id} \
    --instance_type ${instance_type} \
    -s cloudsessions/camcan.tracula.participants -o /data.nfs/camcan/logfiles/camcan.tracula.participants -w 120hours -C 15 -c 4 -v -J 150


    screen bidswrapps_start.py \
    bids/tracula:v6.0.0-4 \
    /data.nfs/camcan/bids /data.nfs/camcan/output/tracula_v6.0.0-4 group1 \
    -ra "--license_key ~/fs.key --freesurfer_dir /data/freesurfer --n_cpus 4" \
    --volume /data.nfs/camcan/output/freesurfer_v6.0.0-4/:/data/freesurfer \
    --image_id ${image_id} \
    --instance_type ${instance_type} \
    -s cloudsessions/camcan.tracula.group1 -o /data.nfs/camcan/logfiles/camcan.tracula.group1 -w 60hours -C 15 -c 4 -v

    screen bidswrapps_start.py \
    bids/tracula:v6.0.0-4 \
    /data.nfs/camcan/bids /data.nfs/camcan/output/tracula_v6.0.0-4 group2 \
    -ra "--license_key ~/fs.key --freesurfer_dir /data/freesurfer --n_cpus 4" \
    --volume /data.nfs/camcan/output/freesurfer_v6.0.0-4/:/data/freesurfer \
    --image_id ${image_id} \
    --instance_type ${instance_type} \
    -s cloudsessions/camcan.tracula.group2 -o /data.nfs/camcan/logfiles/camcan.tracula.group2  -w 60hours -C 15 -c 4 -v


    image_id=40757134-9756-4054-9ec2-8eeaa1d8d677
    instance_type=4cpu-16ram-hpc
    screen bidswrapps_start.py \
    bids/tracula:v6.0.0-4 \
    /data.nfs/CAMCAN/bids_dwi_reduced /data.nfs/CAMCAN/output/tracula_v6.0.0-4_32dirs participant \
    -ra "--license_key ~/fs.key --freesurfer_dir /data/freesurfer --n_cpus 4" \
    --volume /data.nfs/CAMCAN/output/freesurfer_v6.0.0-4/:/data/freesurfer \
    --image_id ${image_id} \
    --instance_type ${instance_type} \
    -s cloudsessions/camcan.tracula.participants.32dirs -o /data.nfs/camcan/logfiles/camcan.tracula.participants.32dirs -w 120hours -C 15 -c 4 -v -J 250


## Tracula 32 dirs


## FS 5.3
```
image_id=ede48e0b-512a-4da2-8300-631981f269de
instance_type=4cpu-16ram-hpc
screen bidswrapps_start.py \
fliem/freesurfer:v6.0.0-3-FSv5.3.0-1 \
/data.nfs/camcan/dl/cc700/mri/pipeline/release004/BIDSsep/anat /data.nfs/camcan/output/freesurfer_v53 participant \
-ra "--license_key ~/fs.key --n_cpus 4" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/camcan.freesurfer.participants -o /data.nfs/camcan/logfiles/camcan.freesurfer.participants -w 120hours -C 15 -c 4 -J 350 -v



image_id=ede48e0b-512a-4da2-8300-631981f269de
instance_type=4cpu-16ram-hpc
screen bidswrapps_start.py \
fliem/freesurfer:v6.0.0-3-FSv5.3.0-1 \
/data.nfs/camcan/dl/cc700/mri/pipeline/release004/BIDSsep/anat /data.nfs/camcan/output/freesurfer_v53 group2 \
-ra "--license_key ~/fs.key --n_cpus 4 --parcellations aparc aparc.a2009s --measurements area volume thickness thicknessstd meancurv gauscurv foldind curvind" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/camcan.freesurfer.group2 -o /data.nfs/camcan/logfiles/camcan.freesurfer.group2 -w 60hours -C 15 -c 8 -v
```


## baracus
```
image_id=221affc1-f5ec-4212-a9c0-32a975737edb
instance_type=4cpu-16ram-hpc
screen bidswrapps_start.py \
fliem/baracus:0.1.5.dev.rc1 \
/data.nfs/camcan/output/freesurfer_v53 /data.nfs/camcan/output/baracus participant \
-ra "--models Liem2016__OCI_norm Liem2016__full_2samp_training" \
--image_id ${image_id} \
--instance_type ${instance_type} \
--no-input-folder-ro \
-s cloudsessions/camcan.baracus.participants -o /data.nfs/camcan/logfiles/camcan.baracus.participants -w 120hours -C 15 -c 1 -J 350 -v

screen bidswrapps_start.py \
fliem/baracus:0.1.5.dev.rc1 \
/data.nfs/camcan/output/freesurfer_v53 /data.nfs/camcan/output/baracus group \
--image_id ${image_id} \
--instance_type ${instance_type} \
--no-input-folder-ro \
-s cloudsessions/camcan.baracus.group -o /data.nfs/camcan/logfiles/camcan.baracus.group -w 120hours -C 15 -c 1 -J 350 -v

```

# reduced dwi directions
```
image_id=40757134-9756-4054-9ec2-8eeaa1d8d677
instance_type=4cpu-16ram-hpc
screen bidswrapps_start.py \
bids/tracula:v6.0.0-4 \
/data.nfs/CAMCAN/bids_dwi_reduced /data.nfs/CAMCAN/output/tracula_v6.0.0-4_reduced participant \
-ra "--license_key ~/fs.key --freesurfer_dir /data/freesurfer --n_cpus 4" \
--volume /data.nfs/CAMCAN/output/freesurfer_v6.0.0-4/:/data/freesurfer \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/camcan.tracula.participants.reduced -o /data.nfs/CAMCAN/logfiles/camcan.tracula.participants.reduced -w 120hours -C 15 -c 4 -v -J 250



image_id=40757134-9756-4054-9ec2-8eeaa1d8d677
instance_type=4cpu-16ram-hpc
screen bidswrapps_start.py \
bids/tracula:v6.0.0-4 \
/data.nfs/CAMCAN/bids_dwi_reduced /data.nfs/CAMCAN/output/tracula_v6.0.0-4_reduced group1 \
-ra "--license_key ~/fs.key --freesurfer_dir /data/freesurfer --n_cpus 4" \
--volume /data.nfs/CAMCAN/output/freesurfer_v6.0.0-4/:/data/freesurfer \
--image_id ${image_id} \
--instance_type ${instance_type} \
-pel CC620121 CC620619 CC610568 CC721704 CC720941 CC620121 CC720941 CC721704 CC620619 CC610568 \
-s cloudsessions/camcan.tracula.group1.reduced -o /data.nfs/CAMCAN/logfiles/camcan.tracula.group1.reduced -w 120hours -C 15 -c 4 -v -J 250


image_id=40757134-9756-4054-9ec2-8eeaa1d8d677
instance_type=4cpu-16ram-hpc
screen bidswrapps_start.py \
bids/tracula:v6.0.0-4 \
/data.nfs/CAMCAN/bids_dwi_reduced /data.nfs/CAMCAN/output/tracula_v6.0.0-4_reduced group2 \
-ra "--license_key ~/fs.key --freesurfer_dir /data/freesurfer --n_cpus 4" \
--volume /data.nfs/CAMCAN/output/freesurfer_v6.0.0-4/:/data/freesurfer \
--image_id ${image_id} \
--instance_type ${instance_type} \
-pel CC620121 CC620619 CC610568 CC721704 CC720941 CC620121 CC720941 CC721704 CC620619 CC610568 \
-s cloudsessions/camcan.tracula.group2.reduced -o /data.nfs/CAMCAN/logfiles/camcan.tracula.group2.reduced -w 120hours -C 15 -c 4 -v -J 250
```

# extract_fa

    image_id=9c7e1df4-a42f-48ef-99cb-7ea781348821
    instance_type=8cpu-32ram-hpc #
    screen bidswrapps_start.py \
    fliem/extract_fa:v3 \
    /data.nfs/CAMCAN/bids /data.nfs/CAMCAN/output/extract_fa_v3 participant \
    --image_id ${image_id} \
    --instance_type ${instance_type} \
    -ra "--n_cpus 2" \
    -s ~/cloudsessions/camcan.extract_fa_v3.participant -o /data.nfs/CAMCAN/logfiles/camcan.extract_fa_v3.participant -w 120hours -C 15 -c 4 -J 350 -v


    image_id=9c7e1df4-a42f-48ef-99cb-7ea781348821
    instance_type=8cpu-32ram-hpc #
    screen bidswrapps_start.py \
    fliem/extract_fa:v3 \
    /data.nfs/CAMCAN/bids /data.nfs/CAMCAN/output/extract_fa_v3 group \
    --image_id ${image_id} \
    --instance_type ${instance_type} \
    -ra "--n_cpus 2" \
    -s ~/cloudsessions/camcan.extract_fa_v3.group -o /data.nfs/CAMCAN/logfiles/camcan.extract_fa_v3.group -w 120hours -C 15 -c 4 -J 350 -v