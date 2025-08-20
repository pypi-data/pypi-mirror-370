from __future__ import annotations

from pathlib import Path

from pymatgen.io.aims.sets.core import RelaxSetGenerator

from ..conftest import O2, Si, comp_system  # noqa: TID252

TEST_FILES_DIR = Path(__file__).parents[3] / "files/"

SPECIES_DIR = TEST_FILES_DIR / "io/aims/species_directory"
REF_PATH = TEST_FILES_DIR / "io/aims/aims_input_generator_ref"


def test_relax_si(tmp_path):
    params = {
        "species_dir": str(SPECIES_DIR / "light"),
        "k_grid": [2, 2, 2],
    }
    comp_system(Si, params, "relax-si/", tmp_path, REF_PATH, RelaxSetGenerator)


def test_relax_si_no_kgrid(tmp_path):
    params = {"species_dir": str(SPECIES_DIR / "light")}
    comp_system(Si, params, "relax-no-kgrid-si", tmp_path, REF_PATH, RelaxSetGenerator)


def test_relax_o2(tmp_path):
    params = {"species_dir": str(SPECIES_DIR / "light")}
    comp_system(O2, params, "relax-o2", tmp_path, REF_PATH, RelaxSetGenerator)
