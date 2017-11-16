# This script takes tap raw files and cleans them up and tries to estimate the session label
# it's a first step to clean the tap data. output of this script has to be checked manually
# output: 1 file with all subjects where session label has been estimated
#        1 file with all subjects where this has not been possible

import pandas as pd
import numpy as np
import os
from glob import glob


def merge_dfs(search_str):
    df = pd.DataFrame([])
    g = glob(search_str)
    for file in g:
        # print(file)
        try:
            df_ = pd.read_csv(file, sep=";")
            df_["file"] = os.path.basename(file)
            df = pd.concat((df, df_))
        except pd.errors.EmptyDataError:
            print("Empty file:", file)
    return df


def convert_dates(df):
    # convert 'BIRTH' and all columns ending with '_DATE' to datetime
    date_cols = df.filter(like='_DATE').columns.tolist()
    date_cols.append("BIRTH")
    print(date_cols)

    for c in date_cols:
        df[c] = pd.to_datetime(df[c])

    return df


def tronic_id(df):
    # tronic subjects with 01_XX_2 id, where only 01_XX is important
    ind = df.SUBJECT.str.split("_").str.len() > 2
    df["tronic_session"] = False
    df.loc[ind, "tronic_session"] = True
    df.loc[ind, "SUBJECT"] = df[ind].SUBJECT.str.split("_").str[:2].str.join("_")

    #  rename tronic ids
    tr = pd.read_excel("/Users/franzliem/Desktop/lhab_tronic.xlsx")
    rename_dict = tr.set_index("tronic").to_dict()["lhab"]

    df.SUBJECT.replace(rename_dict, inplace=True)
    return df


def id_cleaning(df):
    #############
    # ID cleaning
    df = tronic_id(df)

    # remove test subjects
    ind = ~(df["SUBJECT"].str.lower().str.contains("test"))
    df = df[ind].copy()

    # remove time stubs of type abcd_t3
    ind = df.SUBJECT.str.lower().str.contains('\w{4}_t.', regex=True)
    df.loc[ind, "SUBJECT"] = df.loc[ind, "SUBJECT"].str.split("_").str[0]

    # remove time stubs of type abcd_2
    ind = df.SUBJECT.str.lower().str.contains('\w{4}_2', regex=True)
    df.loc[ind, "SUBJECT"] = df.loc[ind, "SUBJECT"].str.split("_").str[0]

    # drop 'neuer_Proband'
    ind = ~(df.SUBJECT == "neuer_Proband")
    df = df[ind]

    return df


# In[6]:


def date_correction(df):
    # correct time offset for dates < 2010
    date_col = df.filter(like="_DATE").columns.tolist()[0]
    ind = df[date_col] < pd.to_datetime("2010-01-01")
    time_offset = pd.Timedelta('4377 days')
    df[date_col] = df[date_col]
    df.loc[ind, date_col] = df.loc[ind, date_col] + time_offset

    # add cont session for merge
    df.sort_values(["SUBJECT", date_col], inplace=True)

    return df


def drop_dups(df):
    # if subject has been run twice at a date, keep last
    date_col = df.filter(like="_DATE").columns.tolist()[0]
    df.drop_duplicates(["SUBJECT", date_col], keep="last", inplace=True)
    return df


def get_session_labels(df):
    # prepare real session dates
    testdates = pd.read_excel(
        "/Volumes/lhab_public/03_Data/03_ComputerTests/02_TAP/10_TAP_export_Nov17/testdates.xlsx")
    testdates = pd.wide_to_long(testdates, ["date_tp"], i="subject", j="session")
    testdates.reset_index(inplace=True)
    testdates["session"] = "tp" + testdates["session"]
    testdates.sort_values(["subject", "session"], inplace=True)
    testdates.rename({"subject": "SUBJECT"}, axis=1, inplace=True)

    #  prepare TAP dates
    date_col = df.filter(like="_DATE").columns.tolist()[0]
    df.sort_values(["SUBJECT", date_col], inplace=True)
    tap_dates = df[["SUBJECT", date_col]].copy()

    # get session mapping
    sessions = pd.merge(testdates, tap_dates, on="SUBJECT", how="outer")
    sessions["delta"] = (sessions[date_col] - sessions["date_tp"]).abs()
    sessions = sessions[sessions.delta < pd.Timedelta("5 days")]
    if len(sessions[sessions[["SUBJECT", "session"]].duplicated()]) != 0:
        raise Exception("sessions not unique")
    sessions.drop("delta", axis=1, inplace=True)

    # merge
    df = pd.merge(df, sessions, on=["SUBJECT", date_col], how="outer")

    # fill in tronic sessions as tp4
    df.loc[df.tronic_session, "session"] = "tp4"
    df.sort_values(["SUBJECT", "session"], inplace=True)

    return df


def format_output(df):
    df.rename(columns=str.lower, inplace=True)

    df.drop(["tronic_session", "age"], axis=1, inplace=True)

    # sort columns
    date_col = df.filter(like="_date").columns.tolist()[0]
    date_col
    time_col = df.filter(like="_time").columns.tolist()[0]
    time_col
    front_cols = ["subject", "session", "date_tp", date_col, time_col, "birth"]
    all_cols = df.columns
    back_cols = [x for x in all_cols if x not in front_cols]
    c = front_cols + back_cols
    df = df[c]

    return df


def prepare_TAP_data(search_str):
    df = merge_dfs(search_str)

    df = convert_dates(df)

    df = id_cleaning(df)

    df = date_correction(df)

    df = drop_dups(df)

    # remove young subjects
    df["age"] = (pd.datetime.now() - df.BIRTH).dt.days / 365
    df = df[df.age > 60]

    df = get_session_labels(df)

    df = format_output(df)
    return df


# merge files
root_path = "/Volumes/lhab_public/03_Data/03_ComputerTests/02_TAP/10_TAP_export_Nov17/TAP_Export_Nov2017"
out_root_path = "/Volumes/lhab_public/03_Data/03_ComputerTests/02_TAP/10_TAP_export_Nov17/TAP_cleaned_DONTEDIT"

test_names = ["al", "da", "gonogo", "wm3"]

if not os.path.isdir(out_root_path):
    os.makedirs(out_root_path)

for test_name in test_names:
    f = "*/export_nov2017_{}_*_*.csv".format(test_name)
    search_str = os.path.join(root_path, f)

    df = prepare_TAP_data(search_str)

    # output
    seems_ok = df[~df.session.isnull()]
    problems = df[df.session.isnull()]

    out_file = os.path.join(out_root_path, "TAP_{}_ok.tsv".format(test_name))
    seems_ok.to_csv(out_file, sep="\t", index=False)

    out_file = os.path.join(out_root_path, "TAP_{}_session_missing.tsv".format(test_name))
    problems.to_csv(out_file, sep="\t", index=False)
