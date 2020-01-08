import os
from glob import glob
import pandas as pd
import numpy as np

from lhab_pipelines.nii_conversion.utils import get_public_sub_id
from lhab_pipelines.utils import read_protected_file, to_tsv, read_tsv
from bids import BIDSLayout
from pathlib import Path


def get_subject_duration(subject):
    """
    calculates the duration of each session by checking the <subject>_scans.tsv file
    """
    scans_file = os.path.join(subject, subject + "_scans.tsv")
    df = pd.read_csv(scans_file, sep="\t", parse_dates=["acq_time"])
    g = df.groupby("session_id")

    duration = pd.DataFrame(
        {"duration_minutes": g["acq_time"].apply(lambda x: x.max() - x.min()).dt.total_seconds() / 60.})
    duration["subject_id"] = subject
    duration["session_id"] = duration.index
    duration.set_index("subject_id", inplace=True, drop=True)
    return duration


def calc_session_duration(bids_dir, info_out_dir):
    """
    looks for subjects in output_dir and checks session durations
    raises Exception if duration is longer 2h
    """
    os.chdir(bids_dir)
    subjects_list = sorted(glob("sub*"))
    if not subjects_list:
        raise Exception("No subjects found in %s" % bids_dir)

    df = pd.DataFrame([])
    for subject in subjects_list:
        subject_duration = get_subject_duration(subject)
        df = df.append(subject_duration)

    out_file = os.path.join(info_out_dir, "session_duration.tsv")
    print(out_file)
    df.to_csv(out_file, sep="\t")

    if df["duration_minutes"].max() > 120:
        raise Exception("something with the data is probably off. max duration of %s" % df["duration_minutes"].max())


def get_acq_dates(info_out_dir):
    df = pd.DataFrame()
    info_out_dir = Path(info_out_dir)
    acq_dir = info_out_dir / "acq_time_PRIVATE"
    acq_files = list(acq_dir.glob("sub-*"))
    for file in acq_files:
        df_ = read_tsv(file)
        df_["acq_date"] = pd.to_datetime(df_.acq_time).dt.date
        subject, session, *_ = file.name.split("_")
        df = df.append(pd.DataFrame({"participant_id": subject,
                                     "session_id": session,
                                     "acq_date": df_.iloc[0].acq_date},
                                    index=[0]))
    df = df.sort_values(by=["participant_id", "session_id"])
    df = df.reset_index(drop=True)
    return df


def calc_demos(output_dir, info_out_dir, demo_file, pwd, new_id_lut_file=None):
    '''
    Calcluates demos from acq_time
    '''
    # get qcq_dates
    acq_dates = get_acq_dates(info_out_dir)

    assert pwd != "", "password empty"
    demo_df = read_protected_file(demo_file, pwd, "demos.txt").reset_index().rename(columns={"subject_id":
                                                                                                 "old_participant_id"})
    demo_df["participant_id"] = get_public_sub_id(demo_df.old_participant_id, new_id_lut_file)
    demo_df["participant_id"] = "sub-" + demo_df["participant_id"]

    demo_df = demo_df.drop(columns=["old_participant_id"])
    df = pd.merge(acq_dates, demo_df, how="left", on="participant_id")
    df["dob"] = pd.to_datetime(df.dob)
    df["acq_date"] = pd.to_datetime(df.acq_date)
    df["age"] = ((df.acq_date - df.dob).dt.days / 365.25).apply(np.round, decimals=1)

    df = df[["participant_id", "session_id", "sex", "age"]]
    to_tsv(df, output_dir / "participants.tsv")

    subjects = df.participant_id.unique()
    print(f"\n\n\n\nDONE.\nExported demos for {len(subjects)} subjects.\n {subjects}")


def get_scan_duration(output_dir, modality="func", task="rest"):
    layout = BIDSLayout(output_dir)
    df = layout.to_df()
    scans_df = df.query("datatype==@modality & task==@task & extension=='nii.gz'")

    scan_durations = []
    for file in scans_df.path:
        scan_durations.append(layout.get_metadata(file)["ScanDurationSec"])
    scans_df["scan_duration"] = scan_durations
    scans_df.reset_index(drop=True, inplace=True)

    out_str = modality
    if task:
        out_str += "_" + task
    output_file = os.path.join(output_dir, "scan_duration_%s.tsv" % out_str)
    print("Writing scan duration to %s" % output_file)
    to_tsv(scans_df, output_file)


def reduce_sub_files(bids_dir, output_file, sub_file):
    df = pd.DataFrame([])
    layout = BIDSLayout(bids_dir)
    files = layout.get(extension=sub_file)
    for file in [f.filename for f in files]:
        print(file)
        df_ = read_tsv(file)
        df = pd.concat((df, df_))

    to_tsv(df, os.path.join(bids_dir, output_file))
