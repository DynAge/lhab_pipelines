# s
```
dsv=v1.0.0
image_id=b1158577-0200-48f1-ab36-81c3b6cbf7e2

screen bidswrapps_start.py \
fliem/freesurfer_lgi:dev4 \
/data.nfs/ds114/LGI_test/ds114_test2 /data.nfs/ds114/LGI_test/ds114_test2_freesurfer_precomp_v6.0.0 participant \
-ra "--license_key ~/fs.key --n_cpus 1" \
--image_id ${image_id} \
--instance_type 1cpu-4ram-hpc \
--volume /usr/local/MATLAB/R2016a:/usr/local/MATLAB/from-host \
-s cloudsessions/ds114.freesurfer_lgi.${dsv} -o /data.nfs/ds114/LGI_test/logfiles/freesurfer_lgi_${dsv} -w 60hours -C 15 -c 1
```