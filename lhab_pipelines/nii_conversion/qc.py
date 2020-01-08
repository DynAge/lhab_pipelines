import pandas as pd
import shutil, datetime
from pathlib import Path


def write_log(log_file, log):
    with open(log_file, "a") as fi:
        fi.write(" ".join(log))


def move_excluded_scans(source_path, exclusion_path, exclusion_file, participant_label=None):
    """ Function takes exclusion file moves scans(and additional files json/bvec...) to exclusion_path
    exclusion file excel with following columns:
        - exclude: ({nan, 1}); excludes exclude==1
        - base_path: path of pattern to be excluded from source path e.g.,
            if participant_label is given, subject is extracted from base_path
        - can include other columns (e.g., info) that will be ignored
    e.g.,
    base_path	                                                exclude	    info
    sub-lhabX0/ses-tp1/dwi/sub-lhabX0_ses-tp1_acq-ap_run-1_dwi	1	        SIMULTAED

    writes a logfile to exclusion_path / 00_log.txt
    """
    df = pd.read_excel(exclusion_file)
    # if given, only work with selected participant_label
    if participant_label:
        participant_label = [s if s.startswith("sub-") else f"sub-{s}" for s in participant_label]
        df["subject"] = df.base_path.str.split("/").str[0]
        df = df.loc[df.subject.isin(participant_label)]
    bad_scans = df.loc[df.exclude == 1]

    source_path = Path(source_path)
    exclusion_path = Path(exclusion_path)
    exclusion_path.mkdir(exist_ok=True, parents=True)

    log_file = exclusion_path / "00_log.txt"
    log = [f"\n\n*************\n{datetime.datetime.now()}\n{exclusion_file}, {source_path}, {exclusion_path}, \
           {participant_label}\n"]
    write_log(log_file, log)

    for base_path in bad_scans.base_path:
        base_path = Path(base_path)
        target_path = exclusion_path / base_path.parent
        target_path.mkdir(exist_ok=True, parents=True)

        candidate_files_source = list(source_path.glob(str(base_path) + "*"))
        candidate_files_target = list(exclusion_path.glob(str(base_path) + "*"))

        if not candidate_files_source:
            if len(candidate_files_target) > 0:
                print(f"No files found in sourcefolder. These files have already been moved {candidate_files_target}")
            else:
                raise Exception(f"files not found in source or target folder: {base_path}. STOPPING")

        for source_file in candidate_files_source:
            target_file = target_path / source_file.name
            if target_file.is_file():
                raise FileExistsError(target_file)

            target_file.parent.mkdir(exist_ok=True, parents=True)
            shutil.move(str(source_file), str(target_file))
            log = [f"moved {source_file} to {target_file} \n"]
            write_log(log_file, log)

        if candidate_files_source:
            # remove source modality folder if its not empty
            source_modality_path = candidate_files_source[0].parent
            dir_empty = len(list(source_modality_path.glob("*"))) == 0
            if dir_empty:
                source_modality_path.rmdir()
                log = [f"{source_modality_path} removed\n"]
                write_log(log_file, log)
    print("DONE")
