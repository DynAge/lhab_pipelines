import os, re
from glob import glob
import pandas as pd

from lhab_pipelines.behav.behav_utils import export_behav_with_new_id

s_id_lut = "/Volumes/lhab_raw/01_RAW/00_PRIVATE_sub_lists/new_sub_id_lut.tsv"

in_dir = "/Volumes/lhab_public/03_Data/99_Cleaning/01_Cognition/00_textfiles/04_ready2use/"
out_dir = "/Volumes/lhab_public/03_Data/99_Cleaning/01_Cognition/00_textfiles/05_ready2_use_newIDs/"
report_dir = "/Volumes/lhab_public/03_Data/99_Cleaning/01_Cognition/00_textfiles/99_report"

data_out_dir = os.path.join(out_dir, "data")
missing_out_dir = os.path.join(out_dir, "missing_info")

for p in [out_dir, data_out_dir, missing_out_dir]:
    if not os.path.exists(p):
        os.makedirs(p)

os.chdir(in_dir)

domains = sorted(glob("*"))
domains = [d for d in domains if os.path.isdir(d)]


for d in domains:
    df_long = pd.DataFrame([], columns=["subject_id", "session_id", "conversion_date", "file"])
    df_wide = pd.DataFrame([], columns=["subject_id", "session_id", "conversion_date"])
    missing_info = pd.DataFrame([], columns=["subject_id", "session_id", "conversion_date", "file"])

    os.chdir(os.path.join(in_dir, d))
    xl_list = sorted(glob("*_data.xlsx"))
    xl_list = [x for x in xl_list if "metadata" not in x]

    for orig_file in xl_list:
        print(orig_file)
        data_file = os.path.join(in_dir, d, orig_file)
        p = re.compile(r"(lhab_)(\w*?)(_data)")
        test_name = p.findall(os.path.basename(orig_file))[0][1]

        metadata_str = "lhab_{}_metadata.xlsx".format(test_name) #"_".join(orig_file.split("_")[:2]) + "*" + " \
                                                                                                   # ""_metadata.xlsx"
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

    # sort rows
    df_long.sort_values(["subject_id", "session_id"], inplace=True)
    df_wide.sort_values(["subject_id", "session_id"], inplace=True)
    missing_info.sort_values(["subject_id", "session_id"], inplace=True)

    out_file = os.path.join(data_out_dir, d + "_long.tsv")
    df_long.to_csv(out_file, index=None, sep="\t")

    out_file = os.path.join(data_out_dir, d + "_wide.tsv")
    df_wide.to_csv(out_file, index=None, sep="\t")

    out_file = os.path.join(missing_out_dir, d + "_missing_info.tsv")
    missing_info.to_csv(out_file, index=None, sep="\t")


# create a file with counts per testscore/session for checking

def create_session_count_file(root_path, out_path):
    if not os.path.isdir(out_path):
        os.makedirs(out_path)

    files = glob(os.path.join(root_path, "*_long.tsv"))
    df = pd.DataFrame([])
    for f in files:
        df_ = pd.read_csv(f, sep="\t")
        df = pd.concat((df, df_))

    n_test_per_session = df.groupby(["test_name", "score_name", "session_id"])[["subject_id"]].count()
    out_file = os.path.join(out_path, "n_test_per_session.xlsx")
    n_test_per_session.to_excel(out_file)
    print("Created report with session counts {}".format(out_file))

    out_file = os.path.join(out_path, "lhab_all_cog_tests.tsv")
    df.to_csv(out_file, index=False, sep="\t")
    print("Created file with all tests {}".format(out_file))

create_session_count_file(os.path.join(out_dir, "data"), report_dir)