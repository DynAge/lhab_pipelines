import os
from glob import glob
import shutil

def mkdir(p):
    if not os.path.isdir(p):
        os.makedirs(p)

in_dir = "/data.nfs/camcan/dl/cc700/mri/pipeline/release004/BIDSsep"
out_dir = "/data.nfs/camcan/bids"
mods = ["anat", "dwi"]

mkdir(out_dir)

for m in mods:
    m_dir = os.path.join(in_dir, m)
    os.chdir(m_dir)
    subs = sorted(glob("sub-*"))

    for s in subs:
        sub_out_dir = os.path.join(out_dir, s)
        mkdir(sub_out_dir)
        source_dir = os.path.join(m_dir, s, m)
        target_dir = os.path.join(out_dir, s, m)
        if not os.path.isdir(target_dir):
            print("{} {} copy".format(source_dir, target_dir))
            shutil.copytree(source_dir, target_dir)
        else:
            print("{} {} already found".format(source_dir, target_dir))


lold = len(glob(os.path.join(in_dir, "*/*/*/*nii.gz")))
lnew = len(glob(os.path.join(out_dir, "*/*/*nii.gz")))
print(lold, lnew)
assert lold==lnew, "count doesnt match"