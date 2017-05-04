import pandas as pd
from glob import glob
import os, shutil, datetime

source_path = "/Users/franzliem/Desktop/in_test/sourcedata"
mri_qc_path = "/Users/franzliem/Desktop/in_test/derivates/mriqc"
move_path = "/Users/franzliem/Desktop/cp_test"

exclusion_file = "/Volumes/lhab_raw/Documentation/v1.1.0_overview/qc_t1w/visu_ratings_fl_20170503.xlsx"


def move_excluded_t1w_scans(source_path, mri_qc_path, exclusion_path, exclusion_file):
    """ Funktion takes exclusion file moves t1w/json and mriqc files to exclusion_path
    exclusion file: (excel file with exclue ({nan, 1}) column and excludes exclude==1 scans
    subject_id	session_id	run_id	report_file	exclude
    lhabXX1	tp1	1	sub-lhabXX1_ses-tp1_run-1_T1w.html	1
    lhabXX2	tp3	2	sub-lhabXX2_ses-tp3_run-2_T1w.html

    """
    log_file = os.path.join(exclusion_path, "00_log.txt")
    log = ["\n\n*************", str(datetime.datetime.now()), "\n", exclusion_file, "\n"]

    df = pd.read_excel(exclusion_file)
    bad_scans = df[df.exclude == 1]

    for i in range(len(bad_scans)):
        df_subject = bad_scans.iloc[[i]]
        bad_scan = df_subject.report_file.tolist()[0].split(".")[0]
        subject = "sub-" + df_subject.subject_id.tolist()[0]

        move_files = {}
        paths = {"anat": os.path.join(source_path, subject, "*/*"),
                 "qc_derivatives": os.path.join(mri_qc_path, "derivatives"),
                 "qc_reports": os.path.join(mri_qc_path, "reports")}

        # create folder structure
        for kind, p in paths.items():
            target_path = os.path.join(exclusion_path, kind)
            if not os.path.exists(target_path):
                os.makedirs(target_path)

        # we expect 4 files (nii, json, qc report, qc derivatives)
        n_files_expected = 4
        for kind, p in paths.items():
            search_str = os.path.join(p, bad_scan + "*")
            search_files = sorted(glob(search_str))
            if search_files:
                move_files[kind] = search_files
            else:
                target_path = os.path.join(exclusion_path, kind)
                search_str = os.path.join(target_path, bad_scan + "*")
                search_files = sorted(glob(search_str))
                if search_files:
                    print("files already moved: %s" % search_str)
                    n_files_expected -= len(search_files)
                else:
                    raise Exception("files not found in source or target folder: %s. STOPPING" % search_str)

        # check that expected number of file are moved
        n_files = 0
        for v in move_files.values():
            n_files += len(v)
        if n_files != n_files_expected:
            raise Exception("len move_files:%s\n %s" % (n_files, df_subject))

        # move files and remove line from scans file
        for kind, source_files in move_files.items():
            target_path = os.path.join(exclusion_path, kind)

            # remove line from scans file
            if kind == "anat":
                scans_file = os.path.join(source_path, subject, subject + "_scans.tsv")
                scans = pd.read_csv(scans_file, sep="\t")
                removed_line = scans[scans.filename.str.contains(bad_scan)]
                scans = scans[~scans.filename.str.contains(bad_scan)]
                scans.to_csv(scans_file, sep="\t", index=False)
                log.append("removed " + bad_scan + " from " + scans_file + "\n")

            # move files
            for source_file in source_files:
                filename = os.path.basename(source_file)
                if os.path.exists():
                    raise Exception(
                        "file already exists, something went wrong: %s" % os.path.join(target_path, filename))
                shutil.move(source_file, os.path.join(target_path, filename))
                log.append("moved " + source_file + " to " + os.path.join(target_path, filename) + "\n")

        log.append("\n")

    with open(log_file, "a") as fi:
        fi.write(" ".join(log))
