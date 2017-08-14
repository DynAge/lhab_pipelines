# s
```
dsv=v1.1.1
image_id=7ce8ca35-c757-4d76-8435-670e23894748
screen bidswrapps_start.py \
fliem/freesurfer_lgi:dev16 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer_v6.0.0-2/ participant \
-ra "--license_key ~/fs.key --n_cpus 2 --wait-for-nfs" \
--image_id ${image_id} \
--instance_type 8cpu-32ram-hpc \
--volume /usr/local/MATLAB/R2016a:/usr/local/MATLAB/from-host \
-s cloudsessions/lhab.freesurfer_lgi.${dsv}.redoall.dev16.fix2 -o /data.nfs/LHAB/logfiles/freesurfer_lgi_${dsv}.redoall.dev16.fix2 -w 120hours -C 15 -c 2 -J 200 -v
```


```
dsv=v1.1.1
image_id=4313d605-12f1-4c8b-979b-afb5cb2d2faf
instance_type=4cpu-16ram-hpc

screen bidswrapps_start.py \
fliem/freesurfer_utils:v0.9.0 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer_v6.0.0-2/ participant \
-ra "--license_key ~/fs.key --n_cpus 4 --workflow qcache --measurements pial_lgi --stream long " \
--image_id ${image_id} \
--instance_type ${instance_type} \
-s cloudsessions/lhab.fs_utils.lgi -o /data.nfs/LHAB/logfiles/fs_utils.lgi -w 120hours -C 15 -c 4 -J 150 -v
```
