import os, pandas as pd
from glob import glob
from lhab_pipelines.nii_conversion.utils import get_public_sub_id


def export_behav_with_new_id(orig_file, s_id_lut, out_dir):
    df_orig = pd.read_excel(orig_file, na_values=["NA01", "NA02", "NA03", "NA04"])
    #fixme remove na counts in last line
    df_orig.dropna(subset=["vp_code"], inplace=True)
    df_orig.rename(columns={"vp_code": "private_subject_id"}, inplace=True)
    df_orig["private_subject_id"].replace({"vcp4 ": "vcp4"}, inplace=True)
    score_cols = df_orig.columns.drop(['private_subject_id', 'tp_avail'])

    df_orig["subject_id"] = get_public_sub_id(["lhab_" + str(s) for s in df_orig["private_subject_id"]], s_id_lut)
    if df_orig.subject_id.isnull().any():
        df_orig.to_clipboard()
        raise Exception("something went wrong with subject_id transformation")
    df_orig.drop("private_subject_id", axis=1, inplace=True)

    score_names = list(set(["_".join(s.split("_")[:-1]) for s in score_cols]))
    if len(score_names) > 1:
        raise NotImplementedError()

    df_long = pd.melt(df_orig, id_vars=["subject_id"],
                      value_vars=score_cols,
                      var_name='session_id', value_name=score_names[0])
    rename_ses = {}
    for s in score_cols:
        rename_ses[s] = s.split("_")[-1]

    df_long["session_id"].replace(rename_ses, inplace=True)
    df_long.dropna(inplace=True)
    df_long.to_csv(os.path.join(out_dir, os.path.basename(orig_file).split(".")[0] + ".tsv"), index=None, sep="\t")


s_id_lut = "/Volumes/lhab_raw/01_RAW/00_PRIVATE_sub_lists/new_sub_id_lut.tsv"
file_list = [
    "/Volumes/lhab_public/03_Data/99_CleaningT1T2T3/01_Cognition/textfiles/03_ready2use/03_processingspeed/lhab_tmta_tp1_tp2_tp3_23052017.xlsx",
    "/Volumes/lhab_public/03_Data/99_CleaningT1T2T3/01_Cognition/textfiles/01_ready4check/06_digsymbol_tp1_tp2_tp3.xlsx",
    "/Volumes/lhab_public/03_Data/99_CleaningT1T2T3/01_Cognition/textfiles/01_ready4check/12_lps14_tp1_tp2_tp3.xlsx",
    "/Volumes/lhab_public/03_Data/99_CleaningT1T2T3/01_Cognition/textfiles/01_ready4check/07_ipt_tp1_tp2_tp3.xlsx"
    ]
out_dir = "/Users/franzliem/Dropbox/OHBM2017/analysis/lhab/prepare_behav"

for orig_file in file_list:
    export_behav_with_new_id(orig_file, s_id_lut, out_dir)

os.chdir(out_dir)
df = pd.DataFrame([], columns=["subject_id", "session_id"])
for f in sorted(glob("*.tsv")):
    df_ = pd.read_csv(f, sep="\t")
    df = df.merge(df_, how="outer", on=["subject_id", "session_id"])
df.to_csv("speed.tsv", index=None, sep="\t")
