from pathlib import Path
import shutil
import os


def rel_link(source, target):
    target.symlink_to(os.path.relpath(source, target.parent))


def expand_mapping_parrec_orig(mapping_parrec_orig):
    mapping_parrec = {}
    for k in mapping_parrec_orig:
        mapping_parrec[k + ".par"] = f"{pref}{mapping_parrec_orig[k]}{suf}.par"
        mapping_parrec[k + ".rec"] = f"{pref}{mapping_parrec_orig[k]}{suf}.rec"
    return mapping_parrec


base_path = Path("/Users/franzliem/Desktop/Phantom/")
in_dir = base_path / "orig/2018"
out_base_dir = base_path / "RAW"
out_base_dir.mkdir(exist_ok=True, parents=True)
os.chdir(base_path)
###

slist_dir = out_base_dir / "00_PRIVATE_sub_lists"
slist_dir.mkdir(parents=True, exist_ok=True)

(slist_dir / "new_sub_id_lut.tsv").write_text("old_id\tnew_id\nlhab_phan\tlhabX9999\n")
(slist_dir / "phan_id_list.tsv").write_text("sub_id\nlhab_phan")

bvecs_dir = out_base_dir / "00_bvecs"
if bvecs_dir.is_dir():
    shutil.rmtree(bvecs_dir)
bvecs_dir.mkdir(exist_ok=True)
source = base_path / "orig/00_bvecs" / "bvecs.fromscanner"
target = bvecs_dir / "bvecs.fromscanner"
rel_link(source, target)

####

sub_path = "T5/01_noIF/lhab_phan_t5_raw"
pref = "lhab_phan_"
suf = "_T5"
mapping_parrec_orig = {
    'ph_20181019_130724_2_1_wipt1w_3d_tfe_puk': "t1w_a",
    'ph_20181019_131612_3_1_wipresting_pa': "fmri_pa",
    'ph_20181019_131706_4_1_wipresting2000_tarasense': "fmri",
    'ph_20181019_132549_5_1_wipdti_nodif_ap': "dti_ap",
    'ph_20181019_132654_6_1_wipdti_nodif_pa': "dti_pa",
    'ph_20181019_132758_7_1_wipdti_high_iso_e': "dti",
    'ph_20181019_134245_8_1_wipflair_longtr': "2dflair",
    'ph_20181019_134814_9_1_wipt1w_3d_tfe_puk': "t1w_b",
    'ph_20181019_135559_10_1_wip3d_brain_view_flair_sh': "3dflair"
}
touch = [
    f"{pref}fmri{suf}_physio.log"
]

mapping_parrec = expand_mapping_parrec_orig(mapping_parrec_orig)

sub_dir = out_base_dir / sub_path
if sub_dir.is_dir():
    shutil.rmtree(sub_dir)
sub_dir.mkdir(exist_ok=True, parents=True)

for source, target in mapping_parrec.items():
    rel_link(in_dir / source, sub_dir / target)

for t in touch:
    (sub_dir / t).touch()
########


sub_path = "T6/01_noIF/lhab_01_ph_t6"
pref = ""
suf = ""
filenames = ['ph_20181019_130724_2_1_wipt1w_3d_tfe_puk',
             'ph_20181019_131612_3_1_wipresting_pa',
             'ph_20181019_131706_4_1_wipresting2000_tarasense',
             'ph_20181019_132549_5_1_wipdti_nodif_ap',
             'ph_20181019_132654_6_1_wipdti_nodif_pa',
             'ph_20181019_132758_7_1_wipdti_high_iso_e',
             'ph_20181019_134245_8_1_wipflair_longtr',
             'ph_20181019_134814_9_1_wipt1w_3d_tfe_puk',
             'ph_20181019_135559_10_1_wip3d_brain_view_flair_sh']

mapping_parrec_orig = {k: k for k in filenames}

touch = []  # ["SCANPHYSLOG_ph_20181019_131706_4_1_wipresting2000_tarasense.log"]

mapping_parrec = expand_mapping_parrec_orig(mapping_parrec_orig)

sub_dir = out_base_dir / sub_path
if sub_dir.is_dir():
    shutil.rmtree(sub_dir)
sub_dir.mkdir(exist_ok=True, parents=True)

for source, target in mapping_parrec.items():
    rel_link(in_dir / source, sub_dir / target)

for t in touch:
    (sub_dir / t).touch()
