# mdsa-tools: Tools for systems-level analysis of Molecular Dynamics (MD) simulations

![CI (Docs)](https://github.com/zeper-eng/mdsa-tools/actions/workflows/docs.yml/badge.svg?branch=main)
[![Read the Docs](https://readthedocs.org/projects/mdsa-tools/badge/?version=latest)](https://mdsa-tools.readthedocs.io/en/latest/)
![Last commit](https://img.shields.io/github/last-commit/zeper-eng/mdsa-tools)
[![PyPI version](https://img.shields.io/pypi/v/mdsa-tools.svg)](https://pypi.org/project/mdsa-tools/)
[![Python versions](https://img.shields.io/pypi/pyversions/mdsa-tools.svg)](https://pypi.org/project/mdsa-tools/)
[![License](https://img.shields.io/pypi/l/mdsa-tools.svg)](https://github.com/zeper-eng/mdsa-tools/blob/main/LICENSE)

## Pipeline overview
![Pipeline](https://raw.githubusercontent.com/zeper-eng/workspace/main/resources/Pipelineflic.png)

We start from an MD trajectory and generate per-frame interaction networks (graphs/adjacency matrices). Adjacencies are flattened (row-wise) into vectors; stacking these per-frame vectors yields a feature matrix suitable for clustering (e.g., k-means) and dimensionality reduction (PCA/UMAP). Results can be visualized with graphs, scatter plots, MDCcircos plots (residue H-bonding), or replicate maps of frame-level measurements of interest.

An additional module uses cluster assignments as candidate substates for Markov state model (MSM) analysis.

## Install

```bash
pip install mdsa-tools
# Optional:
# pip install "mdsa-tools[docs]"   # if you want to build the docs locally
# pip install "mdsa-tools[examples]"  # if you define this extra for demo deps
```

## Systems Problem Area:

![System panel](https://raw.githubusercontent.com/zeper-eng/workspace/main/resources/PanelA_summerposter.png)
At the Weir Lab at Wesleyan University, we perform molecular dynamics (MD) simulations of a ribosomal subsystem to study tuning of protein translation by the CAR interaction surface- a ribosomal interface identified by the lab that interacts with the +1 codon (poised to enter the ribosome A site). Our "computational genetics" research focuses on modifying adjacent codon identities at the A-site and the +1 positions to model how changes at these sites influence the behavior of the CAR surface and corellate with translation rate variations.


## Quickstart example (see examples for more use-cases;contour plots, UMAP, MSM, etc):
Google collab viewer: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zeper-eng/mdsa-tools/blob/main/notebooks/mdsa_tools_demo.ipynb) Jupyter notebook env: [![Binder](https://mybinder.org/badge_logo.svg)](
https://mybinder.org/v2/gh/zeper-eng/mdsa-tools/HEAD?labpath=notebooks/mdsa_tools_demo.ipynb)

```python
from mdsa_tools.Data_gen_hbond import trajectory
from mdsa_tools.Analysis import systems_analysis
import numpy as np

# --- Load trajectories (replace with your own paths) ---
top1 = "/path/to/system1.prmtop"
traj1 = "/path/to/system1.mdcrd"
top2 = "/path/to/system2.prmtop"
traj2 = "/path/to/system2.mdcrd"

sys1 = trajectory(trajectory_path=traj1, topology_path=top1).create_system_representations()
sys2 = trajectory(trajectory_path=traj2, topology_path=top2).create_system_representations()

# Optionally save for reuse
# np.save("example_systems/system_one.npy", sys1)
# np.save("example_systems/system_two.npy", sys2)

# --- Analyze ---
analyzer = systems_analysis([sys1, sys2])

# Clustering
sil_labels, elbow_labels, sil_centers, elbow_centers = analyzer.cluster_system_level(
    outfile_path="out/syskmeans/", max_clusters=25
)
print("Clustering successfully completed.")

# Dimensionality reduction (PCA or UMAP); color by cluster labels
analyzer.reduce_systems_representations(
    outfile_path="out/PCA/test_", 
    method="PCA",
    colormappings=sil_labels
)
print("PCA reduction successful.")
```




