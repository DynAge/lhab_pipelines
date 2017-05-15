
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
image_id=36b38ba4-83a4-41e5-938b-8c1a9b0ff45c
instance_type=4cpu-16ram-hpc
screen bidswrapps_start.py \
fliem/freesurfer:v6.0.0-3-FSv5.3.0-1 \
/data.nfs/camcan/dl/cc700/mri/pipeline/release004/BIDSsep/anat /data.nfs/camcan/output/freesurfer_v53 participant \
-ra "--license_key ~/fs.key --n_cpus 4" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/camcan.freesurfer.participants -o /data.nfs/camcan/logfiles/camcan.freesurfer.participants -w 120hours -C 15 -c 4 -J 350 -v



image_id=36b38ba4-83a4-41e5-938b-8c1a9b0ff45c
instance_type=4cpu-16ram-hpc
screen bidswrapps_start.py \
fliem/freesurfer:v6.0.0-3-FSv5.3.0-1 \
/data.nfs/camcan/dl/cc700/mri/pipeline/release004/BIDSsep/anat /data.nfs/camcan/output/freesurfer_v53 group2 \
-ra "--license_key ~/fs.key --n_cpus 4 --parcellations aparc aparc.a2009s --measurements area volume thickness thicknessstd meancurv gauscurv foldind curvind" \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/camcan.freesurfer.group2 -o /data.nfs/camcan/logfiles/camcan.freesurfer.group2 -w 60hours -C 15 -c 8 -v
```