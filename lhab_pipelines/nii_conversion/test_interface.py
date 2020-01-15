from .interface import Dcm2niix_par
import tempfile


def test_dcm2niix_par():
    par_file = tempfile.NamedTemporaryFile(suffix=".par")
    out_dir = tempfile.TemporaryDirectory()
    converter = Dcm2niix_par()
    converter.inputs.source_names = [par_file.name]
    converter.inputs.output_dir = out_dir.name
    expected = f"dcm2niix -b y -z y -x n -t n -m n -o {out_dir.name} -s n -v n {par_file.name}"
    assert converter.cmdline == expected
    par_file.close()
    out_dir.cleanup()