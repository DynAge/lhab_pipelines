import os
from glob import glob
import pandas as pd

from lhab_pipelines.behav.behav_utils import export_behav_with_new_id

s_id_lut = "/Volumes/lhab_raw/01_RAW/00_PRIVATE_sub_lists/new_sub_id_lut.tsv"
# fixme
in_dir = "/Volumes/lhab_public/03_Data/99_CleaningT1T2T3/01_Cognition/textfiles/04_ready2use_test_fl/"
# fixme
# out_dir = "/Volumes/lhab_public/03_Data/99_CleaningT1T2T3/01_Cognition/textfiles/05_ready2_use_newIDs/"
out_dir = "/Volumes/lhab_public/03_Data/99_CleaningT1T2T3/01_Cognition/textfiles/05_ready2_use_newIDs_test/"

data_out_dir = os.path.join(out_dir, "data")
missing_out_dir = os.path.join(out_dir, "missing_info")

for p in [out_dir, data_out_dir, missing_out_dir]:
    if not os.path.exists(p):
        os.makedirs(p)

os.chdir(in_dir)

domains = sorted(glob("*"))


for d in domains:
    df_long = pd.DataFrame([], columns=["subject_id", "session_id", "conversion_date", "file"])
    df_wide = pd.DataFrame([], columns=["subject_id", "session_id", "conversion_date"])
    missing_info = pd.DataFrame([], columns=["subject_id", "session_id", "conversion_date", "file"])

    os.chdir(os.path.join(in_dir, d))
    xl_list = sorted(glob("*.xlsx"))
    xl_list = [x for x in xl_list if "metadata" not in x]

    for orig_file in xl_list:
        print(orig_file)
        data_file = os.path.join(in_dir, d, orig_file)

        metadata_str = "_".join(orig_file.split("_")[:2]) + "*" + "_metadata.xlsx"
        g = glob(metadata_str)
        if len(g) > 1:
            raise Exception("More than one meta data file found: {}".format(g))
        elif len(g) == 0:
            raise Exception("No meta data file found: {}".format(metadata_str))
        else:
            metadata_file = g[0]
        data_file_path = os.path.join(in_dir, d, metadata_file)

        df_long_, df_wide_, missing_info_ = export_behav_with_new_id(data_file,data_file_path, s_id_lut)
        df_long_["file"] = orig_file
        missing_info_["file"] = metadata_file

        df_long = df_long.append(df_long_)
        df_wide = df_wide.merge(df_wide_, how="outer", on=["subject_id", "session_id", "conversion_date"])
        missing_info = missing_info.append(missing_info_)

    # sort columns
    c = df_long.columns.drop(["subject_id", "session_id", "file", "conversion_date"]).tolist()
    df_long = df_long[["subject_id", "session_id"] + c + ["file", "conversion_date"]]
    c = df_wide.columns.drop(["subject_id", "session_id", "conversion_date"]).tolist()
    df_wide = df_wide[["subject_id", "session_id"] + c + ["conversion_date"]]
    c = missing_info.columns.drop(["subject_id", "session_id", "file", "conversion_date"]).tolist()
    missing_info = missing_info[["subject_id", "session_id"] + c + ["file", "conversion_date"]]

    out_file = os.path.join(data_out_dir, d + "_long.tsv")
    df_long.to_csv(out_file, index=None, sep="\t")

    out_file = os.path.join(data_out_dir, d + "_wide.tsv")
    df_wide.to_csv(out_file, index=None, sep="\t")

    out_file = os.path.join(missing_out_dir, d + "_missing_info.tsv")
    missing_info.to_csv(out_file, index=None, sep="\t")
