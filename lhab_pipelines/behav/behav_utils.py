import numpy as np
import pandas as pd
import re, os
from glob import glob
from lhab_pipelines.nii_conversion.utils import get_public_sub_id


def long_to_wide(long, index, columns, values, nonumeric=False):
    if nonumeric:
        wide = long.pivot_table(index=index, columns=columns, values=values, aggfunc="first")  # aggfunc=lambda x: ',
        # '.join(x.unique()))
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


def load_data_excel(orig_file, s_id_lut, tp_string_last=True):
    """
    tp_string_last: if True: expects columns of type: <name>_tp1
                    if False: expects columns of type: tp1_<name> (e.g., missing files)

    """

    df_orig = pd.read_excel(orig_file, na_values=["NA01", "NA02", "NA03", "NA04", "NA4", "NA1", "NA2", "TL", "X", 888,
                                                  999])
    # na_values seems not to catch numbers consistently
    df_orig.replace({888: np.nan, 999: np.nan}, inplace=True)

    # ensure that numerical-only subject ids are treated as strings
    df_orig = df_orig.astype({"vp_code": str})

    if (df_orig.columns.tolist() == ['no missings']) & (df_orig.shape == (0, 1)):  # metadata file with no missings
        df_orig = None
        df_long = None
    else:
        df_orig.dropna(subset=["vp_code"], inplace=True)
        df_orig.rename(columns={"vp_code": "private_subject_id"}, inplace=True)

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

        if tp_string_last:
            df_long["session_id"] = df_long["test_session_id"].apply(lambda s: s.split("_")[-1])
            df_long["score_name"] = df_long["test_session_id"].apply(lambda s: "_".join(s.split("_")[0:-1]))
        else:
            df_long["session_id"] = df_long["test_session_id"].apply(lambda s: s.split("_")[0])
            df_long["score_name"] = df_long["test_session_id"].apply(lambda s: "_".join(s.split("_")[1:]))
        df_long.drop("test_session_id", axis=1, inplace=True)
        df_long.dropna(inplace=True)

    return df_orig, df_long


def prepare_missing_df(df_meta_long):
    "Takes metadata df, retains only scores that are missing and replaces them with text info"
    lookup_dict = {
        2: "medical_reasons",
        3: "instructions_not_understood",
        4: "test_termination_by_subject",
        5: "environmental_circumstance",
        6: "test_supervisor_error",
        7: "unknown_reasons",
        8: "Time reasons"
    }

    missing_info = df_meta_long[df_meta_long.score_name == "missing"]
    missing_details = df_meta_long[df_meta_long.score_name == "missing_text"]
    missing = pd.merge(missing_info, missing_details, how="outer", on=["subject_id", "session_id"],
                       suffixes=("_info", "_details"))
    missing = missing[missing.score_value_info > 0]

    # disambiguate subjects with whole time point not available ("1") into
    #   - entire timepoint missing and
    #   - entire timepoint missing because not invited (tp4) and
    #   -dropout
    missing["info"] = np.nan
    missing.replace({"score_value_details": {"missing tp": "missing_tp"}}, inplace=True)

    missing.loc[missing.score_value_info == 1, "info"] = missing.score_value_details
    missing.loc[((missing.score_value_info == 1) & (missing.session_id == "tp4")), "info"] = "missing_tp_not_invited"

    # for all other cases take numeric info and replace with text
    missing.loc[missing.score_value_info > 1, "info"] = missing.score_value_info
    missing.replace({"info": lookup_dict}, inplace=True)

    missing = missing[["subject_id", "session_id", "info"]]
    missing["data_missing"] = True
    missing.sort_values(by=["subject_id", "session_id"], inplace=True)
    return missing


def set_invalid_values_to_nan(df_long, df_meta_long):
    missing_full_info = prepare_missing_df(df_meta_long)

    # remove scores that are there but are invalid
    missing = missing_full_info[["subject_id", "session_id", "data_missing"]].copy()
    df_long_clean = pd.merge(df_long, missing, on=["subject_id", "session_id"], how="left")
    df_long_clean.loc[df_long_clean["data_missing"] == True, "score_value"] = np.nan

    n = df_long_clean.loc[df_long_clean["data_missing"] == True].shape[0]
    if n > 0:
        print("removed {} invalid values".format(n))
    df_long_clean.drop(["data_missing"], axis=1, inplace=True)
    df_long_clean.dropna(inplace=True)
    return missing_full_info, df_long_clean


def export_behav_with_new_id(orig_file, metadata_file, s_id_lut):
    p = re.compile(r"(lhab_)(\w*?)(_data)")
    test_name = p.findall(os.path.basename(orig_file))[0][1]

    df_orig, df_long = load_data_excel(orig_file, s_id_lut)
    df_meta_orig, df_meta_long = load_data_excel(metadata_file, s_id_lut, tp_string_last=False)

    if not df_meta_long is None:
        # remove values that should be missing but are not
        missing_full_info, df_long_clean = set_invalid_values_to_nan(df_long, df_meta_long)
    else:  # if no missing
        missing_full_info = pd.DataFrame([])
        df_long_clean = df_long

    df_wide_clean = long_to_wide(df_long_clean, ["subject_id", "session_id"], ["score_name"], ["score_value"])
    df_wide_clean.rename(columns=lambda c: c.split("test_score_")[-1], inplace=True)

    df_wide_clean.sort_values(by=["subject_id", "session_id"], inplace=True)
    df_long_clean.sort_values(by=["subject_id", "session_id"], inplace=True)

    df_long_clean["test_name"] = test_name
    missing_full_info["test_name"] = test_name

    return df_long_clean, df_wide_clean, missing_full_info


def export_domain(in_dir, out_dir, s_id_lut, domain):
    data_out_dir = os.path.join(out_dir, "data")
    os.makedirs(data_out_dir, exist_ok=True)
    missing_out_dir = os.path.join(out_dir, "missing_info")
    os.makedirs(missing_out_dir, exist_ok=True)

    df_long = pd.DataFrame([], columns=["subject_id", "session_id", "conversion_date", "file"])
    df_wide = pd.DataFrame([], columns=["subject_id", "session_id", "conversion_date"])
    missing_info = pd.DataFrame([], columns=["subject_id", "session_id", "file"])

    os.chdir(os.path.join(in_dir, domain))
    xl_list = sorted(glob("*_data.xlsx"))
    xl_list = [x for x in xl_list if "metadata" not in x]
    xl_list = [x for x in xl_list if not x.startswith("~$")]

    for orig_file in xl_list:
        print(orig_file)
        data_file = os.path.join(in_dir, domain, orig_file)
        p = re.compile(r"(lhab_)(\w*?)(_data)")
        test_name = p.findall(os.path.basename(orig_file))[0][1]

        metadata_str = "lhab_{}_metadata.xlsx".format(test_name)  # "_".join(orig_file.split("_")[:2]) + "*" + " \
        # ""_metadata.xlsx"
        g = glob(metadata_str)
        if len(g) > 1:
            raise Exception("More than one meta data file found: {}".format(g))
        elif len(g) == 0:
            raise Exception("No meta data file found: {}".format(metadata_str))
        else:
            metadata_file = g[0]
        data_file_path = os.path.join(in_dir, domain, metadata_file)

        df_long_, df_wide_, missing_info_ = export_behav_with_new_id(data_file, data_file_path, s_id_lut)
        df_long_["file"] = orig_file
        missing_info_["file"] = metadata_file

        df_long = df_long.append(df_long_, sort=False)
        df_wide = df_wide.merge(df_wide_, how="outer", on=["subject_id", "session_id"])
        missing_info = missing_info.append(missing_info_, sort=False)

    # sort rows
    df_long.sort_values(["subject_id", "session_id"], inplace=True)
    df_wide.sort_values(["subject_id", "session_id"], inplace=True)
    missing_info.sort_values(["subject_id", "session_id"], inplace=True)

    # add conversion date in first row
    df_long["conversion_date"] = ""
    df_long.loc[df_long.index[0], "conversion_date"] = pd.datetime.now().date().isoformat()

    df_wide["conversion_date"] = ""
    df_wide.loc[df_wide.index[0], "conversion_date"] = pd.datetime.now().date().isoformat()

    # sort columns
    c = df_long.columns.drop(["subject_id", "session_id", "file", "conversion_date"]).tolist()
    df_long = df_long[["subject_id", "session_id"] + c + ["file", "conversion_date"]]
    c = df_wide.columns.drop(["subject_id", "session_id", "conversion_date"]).tolist()
    df_wide = df_wide[["subject_id", "session_id"] + c + ["conversion_date"]]
    c = missing_info.columns.drop(["subject_id", "session_id", "file"]).tolist()
    missing_info = missing_info[["subject_id", "session_id"] + c + ["file"]]

    out_file = os.path.join(data_out_dir, domain + "_long.tsv")
    df_long.to_csv(out_file, index=None, sep="\t")

    out_file = os.path.join(data_out_dir, domain + "_wide.tsv")
    df_wide.to_csv(out_file, index=None, sep="\t")

    out_file = os.path.join(missing_out_dir, domain + "_missing_info.tsv")
    missing_info.to_csv(out_file, index=None, sep="\t")


def create_session_count_file(root_path, out_path, group):
    files = glob(os.path.join(root_path, "*_long.tsv"))
    if files:
        os.makedirs(out_path, exist_ok=True)

        df = pd.DataFrame([])
        for f in files:
            df_ = pd.read_csv(f, sep="\t")
            df = pd.concat((df, df_))
        df.sort_values(["subject_id", "session_id", "test_name", "score_name"], inplace=True)

        n_test_per_session = df.groupby(["test_name", "score_name", "session_id"])[["subject_id"]].count()
        out_file = os.path.join(out_path, "n_test_per_session.xlsx")
        n_test_per_session.to_excel(out_file)
        print("Created report with session counts {}".format(out_file))

        out_file = os.path.join(out_path, "lhab_all_{}.tsv".format(group))
        df.to_csv(out_file, index=False, sep="\t")
        print("Created file with all tests {}".format(out_file))
