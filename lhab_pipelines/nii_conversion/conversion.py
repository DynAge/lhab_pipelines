import datetime as dt
import os
import shutil
from glob import glob
from os.path import join as oj

import numpy as np
from pathlib import Path
import pandas as pd
import getpass

from .interface import Dcm2niix_par
from nipype.interfaces.fsl import Reorient2Std

import lhab_pipelines
from lhab_pipelines.utils import add_info_to_json, concat_tsvs
from .utils import get_public_sub_id, get_clean_ses_id, get_clean_subject_id, \
    deface_data, dwi_treat_bvecs, add_additional_bids_parameters_from_par, \
    add_flip_angle_from_par, add_total_readout_time_from_par, parse_physio, save_physio, get_par_info, get_image_acq
from .post_conversion_utils import calc_demos, calc_session_duration, get_scan_duration, \
    compare_par_nii, reduce_sub_files


def submit_single_subject(old_subject_id, ses_id_list, raw_dir, output_dir, info_list, info_out_dir,
                          bvecs_from_scanner_file=None, public_output=True, use_new_ids=True,
                          new_id_lut_file=None, tp6_raw_lut=None, dry_run=False, session_duration_min=120):
    """
    Loops through raw folders and identifies old_subject_id in tps.
    Pipes available tps into convert_modality
    public_output: if True: strips all info about original subject_id, file, date
    use_new_ids: if True, uses new id from mapping file
    """
    unconverted_out_dir = info_out_dir / "unconverted_files"
    unconverted_out_dir.mkdir(parents=True, exist_ok=True)
    # fixme
    print(old_subject_id, ses_id_list)

    if public_output:
        assert use_new_ids, "Public output requested, but retaining old subject ids; Doesn't sound good."
    if use_new_ids:
        public_sub_id = get_public_sub_id(old_subject_id, new_id_lut_file)
    else:
        public_sub_id = None
    if tp6_raw_lut:
        try:  # some old_subjects are not in tp6
            tp6_raw_id = get_public_sub_id(old_subject_id, tp6_raw_lut, from_col="old_id", to_col="tp6_id")
        except KeyError:
            tp6_raw_id = None
    else:
        tp6_raw_id = None

    some_data_found = False
    for old_ses_id in ses_id_list:
        session_folder = os.path.join(raw_dir, old_ses_id, "01_noIF")
        os.chdir(session_folder)

        if old_ses_id == "T6":
            folder_subject_id = tp6_raw_id
        else:
            folder_subject_id = old_subject_id

        if (old_ses_id == "T6") & (not tp6_raw_id):  # if subject not in tp6
            subject_folder = []
        else:
            subject_folder = sorted(glob(folder_subject_id + "*"))
        assert len(subject_folder) < 2, "more than one subject folder %s" % old_subject_id

        converted_par_files, converted_physio_files, mapping = [], [], []
        if subject_folder:
            some_data_found = True
            subject_folder = subject_folder[0]
            abs_subject_folder = os.path.abspath(subject_folder)
            os.chdir(abs_subject_folder)

            for infodict in info_list:
                converted_par_files_, converted_physio_files_, mapping_ = \
                    convert_modality(old_subject_id,
                                     old_ses_id,
                                     output_dir,
                                     info_out_dir,
                                     bvecs_from_scanner_file=bvecs_from_scanner_file,
                                     public_sub_id=public_sub_id,
                                     public_output=public_output,
                                     **infodict,
                                     dry_run=dry_run)
                converted_par_files.extend(converted_par_files_)
                converted_physio_files.extend(converted_physio_files_)
                mapping.extend(mapping_)

            subject = public_sub_id if public_sub_id else old_subject_id
            session = old_ses_id.replace("T", "tp")
            df_unconverted = check_unconverted_files(converted_par_files, converted_physio_files, subject, session)
            df_unconverted.to_csv(unconverted_out_dir / f"sub-{subject}_ses-{session}_unconverted.tsv", sep="\t",
                                  index=False)

            mapping_dir = info_out_dir / "parrec_mapping_PRIVATE"
            mapping_dir.mkdir(parents=True, exist_ok=True)
            mapping_df = pd.DataFrame(mapping, columns=["from", "to"])
            mapping_df.to_csv(mapping_dir / f"sub-{subject}_ses-{session}_par2nii_mapping.tsv", sep="\t", index=False)

            if converted_par_files:
                acq_times = get_image_acq(converted_par_files)
                duration_minutes = (acq_times["acq_time"].max() - acq_times["acq_time"].min()).total_seconds() / 60.
                acq_times_dir = info_out_dir / "acq_time_PRIVATE"
                acq_times_dir.mkdir(parents=True, exist_ok=True)
                acq_times.to_csv(acq_times_dir / f"sub-{subject}_ses-{session}_acq_times.tsv", sep="\t", index=False)
                if session_duration_min > 0:
                    assert duration_minutes < session_duration_min, f"Session too long. Check {subject} {session}"
                else:
                    print("session_duration_min set to <= 0. Skipping duration test")

    if not some_data_found:
        raise FileNotFoundError("No data found for %s. Check again. Stopping..." % old_subject_id)


def check_unconverted_files(converted_par_files, converted_physio_files, subject, session):
    found_source_dir_files = list(glob("*"))
    found_parrec_files = set([Path(f).stem for f in found_source_dir_files if f.endswith((".par", ".rec"))])
    converted_par_files = set([Path(f).stem for f in converted_par_files])
    unconverted_parrec_files = list(found_parrec_files - converted_par_files)

    found_nonparrec_files = set([Path(f).name for f in found_source_dir_files
                                 if not f.endswith((".par", ".rec"))])
    unconverted_nonparrec_files = list(found_nonparrec_files - set(converted_physio_files))
    df = pd.DataFrame({"subject": subject, "session": session, "files": unconverted_parrec_files, "kind": "parrec"})
    df = df.append(pd.DataFrame({"subject": subject, "session": session, "files": unconverted_nonparrec_files,
                                 "kind": "nonparrec"}))
    return df


def convert_modality(old_subject_id, old_ses_id, output_dir, info_out_dir, bids_name, bids_modality,
                     search_str, bvecs_from_scanner_file=None, public_sub_id=None, public_output=True,
                     reorient2std=True, task=None, direction=None, acq=None,
                     only_use_last=False, deface=False, physio=False, add_info={}, dry_run=False,
                     post_glob_filter=None):
    """
    runs conversion for one subject and one modality
    public_output: if True: strips all info about original subject_id, file, date
    """
    if (public_output and bids_modality == "anat" and not deface):
        raise Exception("Public output requested, but anatomical images not defaced. exit. %s %s %s" % (
            old_subject_id, old_ses_id, bids_name))

    new_ses_id = get_clean_ses_id(old_ses_id)
    bids_ses = "ses-" + new_ses_id
    if public_sub_id:
        bids_sub = "sub-" + public_sub_id
    else:
        bids_sub = "sub-" + get_clean_subject_id(old_subject_id)

    if isinstance(search_str, str):
        search_str = [search_str]

    par_file_list = []
    for s_str in search_str:
        par_file_list += sorted(glob("*" + s_str + "*.par"))

    if post_glob_filter:
        par_file_list = list(filter(post_glob_filter, par_file_list))

    physio_in_file_list = []

    mapping = []
    if par_file_list:
        sub_output_dir = os.path.join(output_dir, bids_sub)
        nii_output_dir = os.path.join(sub_output_dir, bids_ses, bids_modality)

        if not os.path.exists(nii_output_dir):
            os.makedirs(nii_output_dir)

        if only_use_last:
            par_file_list = par_file_list[-1:]

        # sort files by acquision number
        par_acq_nr = np.array([get_par_info(par_file, "acquisition_nr")["acquisition_nr"] for par_file in
                               par_file_list])
        sort_index = np.argsort(par_acq_nr)

        for run_id, par_file in enumerate(np.array(par_file_list)[sort_index].tolist(), 1):
            # put together bids file name
            # bids run
            bids_run = "run-" + str(run_id)
            out_components = [bids_sub, bids_ses]

            # bids acq
            if acq:
                out_components += ["acq-%s" % acq]

            # bids task
            if task:
                out_components += ["task-%s" % task]

            # bids acq. direction
            if direction:
                out_components += ["dir-%s" % direction]

            out_components += [bids_run, bids_name]
            out_filename = "_".join(out_components)
            nii_file = os.path.join(nii_output_dir, out_filename + ".nii.gz")
            if not dry_run:
                assert not os.path.exists(nii_file), "file exists. STOP. %s" % nii_file

                bids_file, converter_results, mapping_ = run_dcm2niix(bids_name, bids_modality,
                                                                      bvecs_from_scanner_file, info_out_dir, nii_file,
                                                                      nii_output_dir, out_filename, par_file, task)
                mapping.append(mapping_)

                if reorient2std:
                    reorient = Reorient2Std()
                    reorient.inputs.in_file = converter_results.outputs.converted_files
                    reorient.inputs.out_file = converter_results.outputs.converted_files
                    reorient_results = reorient.run()

                if deface:
                    deface_data(nii_file, nii_output_dir, out_filename)
                add_info_to_json(bids_file, {"Defaced": deface})

                add_info_to_json(bids_file, add_info)

                # finally as a sanity check, check that converted nii exists
                assert os.path.exists(nii_file), "Something went wrong" \
                                                 "converted file does not exist. STOP. %s" % nii_file
            physio_in_file_list = []
            if physio:  # convert physiological data
                physio_search_str_list = [".".join(par_file.split(".")[:-1]) + "_*phys*.log",
                                          "SCANPHYSLOG_" + ".".join(par_file.split(".")[:-1]) + ".log"]
                physio_in_file_list = []
                for physio_search_str in physio_search_str_list:
                    physio_in_file_list += glob(physio_search_str)
                assert len(physio_in_file_list) < 2, "more than 1  phyio file found for %s" % physio_search_str

                if physio_in_file_list and not dry_run:
                    physio_out_file_base = os.path.join(nii_output_dir, out_filename + "_physio")
                    meta_data, physio_data = parse_physio(physio_in_file_list[0])
                    save_physio(physio_out_file_base, meta_data, physio_data)

    return par_file_list, physio_in_file_list, mapping


def run_dcm2niix(bids_name, bids_modality, bvecs_from_scanner_file, info_out_dir, nii_file, nii_output_dir,
                 out_filename, par_file, task):
    '''
    Converts one par/rec pair to nii.gz.
    Adds scan duration and dcm2niix & docker container version to bids file.
    '''

    abs_par_file = os.path.abspath(par_file)
    abs_rec_file = os.path.splitext(abs_par_file)[0] + ".rec"

    assert os.path.exists(abs_rec_file), "REC file does not exist %s" % abs_rec_file

    # run converter
    converter = Dcm2niix_par()
    converter.inputs.source_names = [abs_par_file]
    converter.inputs.bids_format = True
    converter.inputs.compress = 'i'
    converter.inputs.has_private = True
    converter.inputs.out_filename = out_filename
    converter.inputs.output_dir = nii_output_dir
    print("XXXXXXX running dcm2niix command")
    print(converter.cmdline)
    converter_results = converter.run()
    bids_file = [s for s in converter_results.outputs.bids if s.endswith(".json")]
    assert len(bids_file) == 1, bids_file
    bids_file = bids_file[0]

    # add additional information to json
    ## scan duration
    add_additional_bids_parameters_from_par(abs_par_file, bids_file, {"scan_duration": "ScanDurationSec",
                                                                      "technique": "PulseSequenceType",
                                                                      "protocol_name": "PulseSequenceDetails"})

    add_flip_angle_from_par(abs_par_file, bids_file)
    add_total_readout_time_from_par(abs_par_file, bids_file)

    ## lhab_pipelines
    add_info_to_json(bids_file, {"LhabPipelinesVersion": lhab_pipelines.__version__})

    ## task
    if task:
        add_info_to_json(bids_file, {"TaskName": task})

    ## time
    add_info_to_json(bids_file, {"ConversionTimestamp": str(dt.datetime.now())})

    # dcm_conversion_info
    dcm_conversion_info_dir = info_out_dir / "dcm2niix_conversion_PRIVATE"
    dcm_conversion_info_dir.mkdir(parents=True, exist_ok=True)
    dcm_conversion_info_file = dcm_conversion_info_dir / f"{out_filename}.txt"
    orig_file = Path(nii_output_dir) / f"{out_filename}.txt"
    shutil.move(str(orig_file), str(dcm_conversion_info_file))

    # rotate bvecs and add angulation to json for dwi
    if (bids_name == "dwi") & (bids_modality != "fmap"):
        dwi_treat_bvecs(abs_par_file, bids_file, bvecs_from_scanner_file, nii_output_dir, par_file)
        # remove _dwi_ADC.nii.gz file created by dcm2niix
        adc_file = glob(os.path.join(nii_output_dir, "*_dwi_ADC.nii.gz"))[0]
        os.remove(adc_file)

    mapping = [abs_par_file, nii_file]

    return bids_file, converter_results, mapping


def run_conversion(raw_dir, output_base_dir, analysis_level, info_out_dir, participant_label, session_label,
                   public_output, use_new_ids, ds_version, info_list, dataset_description, new_id_lut_file=None,
                   bvecs_from_scanner_file=None, tp6_raw_lut=None, dry_run=False, demo_file=None,
                   session_duration_min=120):
    # privacy settings
    private_str = "_PRIVATE" if not (public_output and use_new_ids) else ""
    output_dir = Path(output_base_dir) / f"LHAB_{ds_version}{private_str}" / "sourcedata"

    output_dir.mkdir(parents=True, exist_ok=True)
    info_out_dir = Path(info_out_dir) / "PRIVATE"
    info_out_dir.mkdir(parents=True, exist_ok=True)

    if analysis_level == "participant":
        for old_subject_id in participant_label:
            submit_single_subject(old_subject_id,
                                  session_label,
                                  raw_dir,
                                  output_dir,
                                  info_list,
                                  info_out_dir,
                                  bvecs_from_scanner_file=bvecs_from_scanner_file,
                                  public_output=public_output,
                                  use_new_ids=use_new_ids,
                                  new_id_lut_file=new_id_lut_file,
                                  tp6_raw_lut=tp6_raw_lut,
                                  dry_run=dry_run,
                                  session_duration_min=session_duration_min)
        print("\n\n\n\nDONE.\nConverted %d subjects." % len(participant_label))
        print(participant_label)

    elif analysis_level == "group":
        info_file = info_out_dir / "info.txt"
        s = f"""{dt.datetime.now()}
        public_output: {public_output}
        use_new_ids: {use_new_ids}
        info_list: {info_list}        
        """
        info_file.write_text(s)

        ds_desc_file = output_dir / "dataset_description.json"
        if ds_desc_file.is_file():
            ds_desc_file.unlink()
        dataset_description["DataSetVersion"] = ds_version
        add_info_to_json(ds_desc_file, dataset_description, create_new=True)

        print("\n Check that all subjecst are present and compare par and nii count, export nii count...")
        layout = compare_par_nii(output_dir, participant_label, use_new_ids, raw_dir, session_label, info_list,
                                 new_id_lut_file, excluded_dir="", tp6_raw_lut=tp6_raw_lut)
        layout.to_df().to_csv(output_dir / "layout.csv", index=False)

        # Demos
        print("Exporting demos...")
        pwd = getpass.getpass("Enter the Password for dob file:")
        calc_demos(output_dir, info_out_dir, session_label, raw_dir, demo_file, pwd, use_new_ids=use_new_ids,
                   new_id_lut_file=new_id_lut_file, tp6_raw_lut=tp6_raw_lut)

        print("Collecting scan durations...")
        get_scan_duration(output_dir)

        # concat notconverted files
        unconv_df = concat_tsvs(info_out_dir / "unconverted_files")
        unconv_df.to_csv(info_out_dir / "unconverted_files.tsv", sep="\t", index=False)
