from __future__ import annotations

from pathlib import Path

from pymatgen.io.aims.sets.core import StaticSetGenerator

from ..conftest import O2, Si, comp_system  # noqa: TID252

TEST_FILES_DIR = Path(__file__).parents[3] / "files/"

REF_PATH = TEST_FILES_DIR / "io/aims/aims_input_generator_ref"
SPECIES_DIR = TEST_FILES_DIR / "io/aims/species_directory"


def test_static_si(tmp_path):
    parameters = {
        "species_dir": str(SPECIES_DIR / "light"),
        "k_grid": [2, 2, 2],
    }
    comp_system(Si, parameters, "static-si", tmp_path, REF_PATH, StaticSetGenerator)


def test_static_o2_charge():
    parameters = {
        "species_dir": str(SPECIES_DIR / "light"),
        "k_grid": [2, 2, 2],
    }
    Si.set_charge(1)
    generator = StaticSetGenerator(parameters, use_structure_charge=True)
    input_set = generator.get_input_set(Si)
    assert "charge                                            1" in input_set.control_in


def test_static_si_no_kgrid(tmp_path):
    parameters = {"species_dir": str(SPECIES_DIR / "light")}
    Si_supercell = Si.make_supercell([1, 2, 3], in_place=False)
    for site in Si_supercell:
        # round site.coords to ignore floating point errors
        site.coords = [round(x, 15) for x in site.coords]
    comp_system(
        Si_supercell,
        parameters,
        "static-no-kgrid-si",
        tmp_path,
        REF_PATH,
        StaticSetGenerator,
    )


def test_static_o2(tmp_path):
    parameters = {"species_dir": str(SPECIES_DIR / "light")}
    comp_system(O2, parameters, "static-o2", tmp_path, REF_PATH, StaticSetGenerator)
