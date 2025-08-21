from pathlib import Path
import pytest
from mdsa_tools.Data_gen_hbond import TrajectoryProcessor
from mdsa_tools.Convenience import unrestrained_residues
from mdsa_tools.Analysis import systems_analysis

DATA = Path(__file__).parent / "data" / "trajectories"
CASES = [
    (DATA / "CCU_GCU_10frames.mdcrd", DATA / "5JUP_N2_GCU_nowat.prmtop"),
    (DATA / "CCU_CGU_10frames.mdcrd", DATA / "5JUP_N2_CGU_nowat.prmtop"),
]

@pytest.fixture(scope="session", params=CASES, ids=["GCU", "CGU"])# ids for nice reporting
def processor(request):
    traj, top = request.param
    return TrajectoryProcessor(traj, top)

@pytest.fixture(scope="session")
def systems(processor):
    return processor.create_system_representations()

@pytest.fixture(scope="session")
def filtered(processor):
    return processor.create_filtered_representations(residues_to_keep=unrestrained_residues)


# Theese get remade so we can use them both in a list for analyses
# We can use only the filtered because every test in datagen should have run checks to make sure
# that all of our dat works wether its filtered or the original full matrices
@pytest.fixture(scope="session")
def analysis_systems():
    trajs = [
        ("CCU_GCU_10frames.mdcrd", "5JUP_N2_GCU_nowat.prmtop"),
        ("CCU_CGU_10frames.mdcrd", "5JUP_N2_CGU_nowat.prmtop"),
    ]
    arrays = []
    for traj, top in trajs:
        tp = TrajectoryProcessor(DATA / traj, DATA / top)
        current_array=tp.create_filtered_representations(residues_to_keep=unrestrained_residues)
        arrays.append(current_array)
    return arrays

@pytest.fixture(scope="session")
def analyzer(analysis_systems):
    sa = systems_analysis(analysis_systems)  # give both at once
    sa.replicates_to_featurematrix()
    return sa