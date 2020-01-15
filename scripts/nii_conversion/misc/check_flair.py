from pathlib import Path
import nibabel as nb

base_path = Path("/Volumes/lhab_raw/01_RAW")

flair_files = list(base_path.glob("T*/01_noIF/lhab_*/*_flair_*.par"))
flair_files = [f for f in flair_files if "3d_" not in str(f)]

print(len(flair_files), "\n")

ses = set([list(f.parents)[-5].name for f in flair_files])
print(ses, "\n")

print(flair_files)

for f in flair_files:
    i = nb.load(str(f))
    if i.shape != (560, 560, 32):
        raise Exception(f)
print("All _flair_ files are 2D")
