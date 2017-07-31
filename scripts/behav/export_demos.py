import os, pandas as pd
from glob import glob
from lhab_pipelines.nii_conversion.utils import get_public_sub_id
import numpy as np

if __name__ == "__main__":
    s_id_lut = "/Volumes/lhab_raw/01_RAW/00_PRIVATE_sub_lists/new_sub_id_lut.tsv"
    in_dir = "/Volumes/lhab_public/03_Data/99_CleaningT1T2T3/04_Demographic"
    out_dir = "/Volumes/lhab_public/03_Data/99_CleaningT1T2T3/04_Demographic/demographics_new_ids"

    os.chdir(in_dir)
    files = sorted(glob("*.xlsx"))

    for f in files:
        df = pd.read_excel(f)
        df["ID"] = get_public_sub_id(["lhab_" + str(s) for s in df["ID"]], s_id_lut)
        df.sort_values("ID", inplace=True)

        if f.startswith("Gender"):
            df.replace({"Gender": {1: "M", 2: "F"}}, inplace=True)

        out_file = os.path.join(out_dir, f)
        df.to_excel(out_file, na_rep="NA", index=False)
