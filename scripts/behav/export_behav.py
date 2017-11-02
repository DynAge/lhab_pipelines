import os
from glob import glob

import pandas as pd

from lhab_pipelines.behav.behav_utils import export_behav_with_new_id

s_id_lut = "/Volumes/lhab_raw/01_RAW/00_PRIVATE_sub_lists/new_sub_id_lut.tsv"

in_dir = "/Volumes/lhab_public/03_Data/99_CleaningT1T2T3/01_Cognition/textfiles/04_ready2use/"
out_dir = "/Volumes/lhab_public/03_Data/99_CleaningT1T2T3/01_Cognition/textfiles/05_ready2_use_newIDs/"


if not os.path.exists(out_dir):
    os.makedirs(out_dir)

os.chdir(in_dir)

domains = sorted(glob("*"))

for d in domains:
    df_long = pd.DataFrame([], columns=["subject_id", "session_id", "file"])
    df_wide = pd.DataFrame([], columns=["subject_id", "session_id"])

    os.chdir(os.path.join(in_dir, d))
    xl_list = sorted(glob("*.xlsx"))
    xl_list = [x for x in xl_list if "metadata" not in x]

    for orig_file in xl_list:
        print(orig_file)
        df_long_, df_wide_ = export_behav_with_new_id(os.path.join(in_dir, d, orig_file), s_id_lut)
        df_long_["file"] = orig_file

        df_long = df_long.append(df_long_)
        df_wide = df_wide.merge(df_wide_, how="outer", on=["subject_id", "session_id"])


    c = df_long.columns.drop(["subject_id", "session_id", "file"]).tolist()
    df_long = df_long[["subject_id", "session_id"] + c + ["file"]]

    out_file = os.path.join(out_dir, d + "_long.tsv")
    df_long.to_csv(out_file, index=None, sep="\t")

    out_file = os.path.join(out_dir, d + "_wide.tsv")
    df_wide.to_csv(out_file, index=None, sep="\t")
