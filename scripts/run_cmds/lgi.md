# s
```
dsv=v1.1.1
image_id=b1158577-0200-48f1-ab36-81c3b6cbf7e2

screen bidswrapps_start.py \
fliem/freesurfer_lgi:dev4 \
/data.nfs/LHAB/NIFTI/LHAB_${dsv}/sourcedata/ /data.nfs/LHAB/NIFTI/LHAB_${dsv}/derivates/freesurfer participant \
-ra "--license_key ~/fs.key --n_cpus 1" \
--image_id ${image_id} \
--instance_type 4cpu-16ram-hpc \
--volume /usr/local/MATLAB/R2016a:/usr/local/MATLAB/from-host \
-s cloudsessions/lhab.freesurfer_lgi.${dsv} -o /data.nfs/LHAB/logfiles/freesurfer_lgi_${dsv} -w 60hours -C 15 -c 1
```