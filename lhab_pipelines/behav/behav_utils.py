import numpy as np
import pandas as pd

from lhab_pipelines.nii_conversion.utils import get_public_sub_id


def long_to_wide(long, index, columns, values, nonumeric=False):
    if nonumeric:
        wide = long.pivot_table(index=index, columns=columns, values=values, aggfunc=lambda x: ', '.join(x.unique()))
    else:
        wide = long.pivot_table(index=index, columns=columns, values=values)
    l = wide.columns.labels
    le = wide.columns.levels
    o = []
    out_cols = []

    for i, ii in enumerate(l):
        o.append(le[i][l[i]])
    o = np.array(o)

    for i in o.T:
        out_cols.append("_".join(i))
    out_cols = [s.replace("score_value_", "") for s in out_cols]
    out_cols = [s.replace("z_", "") + "_z" if s.startswith("z_") else s for s in out_cols]

    wide.columns = out_cols
    wide.reset_index(inplace=True)
    return wide


def export_behav_with_new_id(orig_file, s_id_lut):
    df_orig = pd.read_excel(orig_file, na_values=["NA01", "NA02", "NA03", "NA04", "NA4", "NA1", "NA2", "TL", "X", 888,
                                                  999])
    # na_values seems not to catch numbers consistently
    df_orig.replace({888: np.nan, 999: np.nan}, inplace=True)

    # fixme remove na counts in last line
    df_orig.dropna(subset=["vp_code"], inplace=True)
    df_orig.rename(columns={"vp_code": "private_subject_id"}, inplace=True)
    # df_orig["private_subject_id"].replace({"vcp4 ": "vcp4"}, inplace=True)
    df_orig["private_subject_id"] = df_orig["private_subject_id"].str.strip()
    score_cols = df_orig.columns.drop(['private_subject_id']).tolist()
    if "tp_avail" in score_cols:
        score_cols = score_cols.drop("tp_avail")

    df_orig["subject_id"] = get_public_sub_id(["lhab_" + str(s) for s in df_orig["private_subject_id"]], s_id_lut)
    if df_orig.subject_id.isnull().any():
        df_orig.to_clipboard()
        raise Exception("something went wrong with subject_id transformation")
    df_orig.drop("private_subject_id", axis=1, inplace=True)

    df_long = pd.melt(df_orig, id_vars=["subject_id"],
                      value_vars=score_cols,
                      var_name='test_session_id', value_name="score_value")  # score_names[0])
    df_long["session_id"] = df_long["test_session_id"].apply(lambda s: s.split("_")[-1])
    df_long["score_name"] = df_long["test_session_id"].apply(lambda s: "_".join(s.split("_")[0:-1]))
    df_long.drop("test_session_id", axis=1, inplace=True)
    df_long.dropna(inplace=True)
    df_wide = long_to_wide(df_long, ["subject_id", "session_id"], ["score_name"], ["score_value"])
    df_wide.rename(columns=lambda c: c.split("test_score_")[-1], inplace=True)

    df_wide.sort_values(by=["subject_id", "session_id"], inplace=True)
    df_long.sort_values(by=["subject_id", "session_id"], inplace=True)

    df_long["conversion_date"] = pd.datetime.now().date().isoformat()
    df_wide["conversion_date"] = pd.datetime.now().date().isoformat()
    return df_long, df_wide