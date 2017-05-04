import argparse
from lhab_pipelines.nii_conversion.qc import move_excluded_t1w_scans

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('source_path', help="Directory containing sourcedata")
    parser.add_argument('mri_qc_path', help="Directory containing mriqc data")
    parser.add_argument('exclusion_path', help="Directory where data will be moved")
    parser.add_argument('exclusion_file', help="file with scans that should be excluded")
    args = parser.parse_args()

    move_excluded_t1w_scans(args.source_path, args.mri_qc_path, args.exclusion_path, args.exclusion_file)
