



# __mdsa-tools__ [![Docs Build](https://github.com/zeper-eng/mdsa-tools/actions/workflows/docs.yml/badge.svg?branch=main)](https://mdsa-tools.readthedocs.io/en/latest/)[![CI](https://github.com/zeper-eng/mdsa-tools/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/zeper-eng/mdsa-tools/actions/workflows/ci.yml)[![PyPI version](https://img.shields.io/pypi/v/mdsa-tools.svg)](https://pypi.org/project/mdsa-tools/)[![License](https://img.shields.io/pypi/l/mdsa-tools.svg)](https://github.com/zeper-eng/mdsa-tools/blob/main/LICENSE)

Tools for systems-level analysis of Molecular Dynamics (MD) simulations
## Pipeline overview

![Pipeline](https://raw.githubusercontent.com/zeper-eng/workspace/main/resources/Pipelineflic.png)

We start from an MD trajectory and generate per-frame interaction networks (graphs/adjacency matrices). Adjacencies are flattened (row-wise) into vectors; stacking these per-frame vectors yields a feature matrix suitable for clustering (e.g., k-means) and dimensionality reduction (PCA/UMAP). Results can be visualized with graphs, scatter plots, MDCcircos plots (residue H-bonding), or replicate maps of frame-level measurements of interest. These clustered states can then serve as candidate substates for constructing and analyzing Markov state models (MSMs), enabling exploration of long-timescale dynamics and transition pathways.

## Install

```bash
pip install mdsa-tools
# Optional:
# pip install "mdsa-tools[docs]"   # if you want to build the docs locally
# pip install "mdsa-tools[examples]"  # if you define this extra for demo deps
```

## Systems Problem Area:

![System panel](https://raw.githubusercontent.com/zeper-eng/workspace/main/resources/PanelA_summerposter.png)

In the Weir Group at Wesleyan University, we perform molecular dynamics (MD) simulations of a ribosomal subsystem to study tuning of protein translation by the CAR interaction surface- a ribosomal interface identified by the lab that interacts with the +1 codon (poised to enter the ribosome A site). Our "computational genetics" research focuses on modifying adjacent codon identities at the A-site and the +1 positions to model how changes at these sites influence the behavior of the CAR surface and corellate with translation rate variations.


## Quickstart example (see examples for more use-cases;contour plots, UMAP, MSM, etc):

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/zeper-eng/mdsa-tools/blob/main/notebooks/Quick_Start.ipynb)
[![Binder](https://mybinder.org/badge_logo.svg)](
https://mybinder.org/v2/gh/zeper-eng/mdsa-tools/HEAD?labpath=notebooks/Quick_Start.ipynb)
[![nbviewer](https://img.shields.io/badge/View%20Notebook-nbviewer-blue)](
https://nbviewer.org/github/zeper-eng/mdsa-tools/blob/main/notebooks/Quick_Start.ipynb)

```python
from mdsa_tools.Data_gen_hbond import TrajectoryProcessor as tp
import numpy as np
import os

###
### Datagen
###

#load in and test trajectory
system_one_topology = '../PDBs/5JUP_N2_CGU_nowat.prmtop'
system_one_trajectory = '../PDBs/CCU_CGU_10frames.mdcrd'


system_two_topology = '../PDBs/5JUP_N2_GCU_nowat.prmtop'
system_two_trajectory = '../PDBs/CCU_GCU_10frames.mdcrd'


test_trajectory_one = tp(trajectory_path=system_one_trajectory,topology_path=system_one_topology)
test_trajectory_two = tp(trajectory_path=system_two_trajectory,topology_path=system_two_topology)


#now that its loaded in try to make object
test_system_one_ = test_trajectory_one.create_system_representations()
test_system_two_ = test_trajectory_two.create_system_representations()


np.save('test_system_one',test_system_one_)
np.save('test_system_two',test_system_two_)

###
### Analysis
###

from mdsa_tools.Analysis import systems_analysis

all_systems=[test_system_one_,test_system_two_]
Systems_Analyzer = systems_analysis(all_systems)

#transform adjacency matrices preform clsutering and dimensional reduction and visualizing clusters
Systems_Analyzer.replicates_to_featurematrix()
optimal_k_silhouette_labels,optimal_k_elbow_labels,centers_sillohuette,centers_elbow = Systems_Analyzer.cluster_system_level(outfile_path='./test_',max_clusters=5)
print('clustering succesfully completed')
X_pca,weights,explained_variance_ratio_=Systems_Analyzer.reduce_systems_representations(method='PCA') #you could do method=PCA/UMAP here
print('reduction succesful')


###
### Visualization
###

import matplotlib.cm as cm
from mdsa_tools.Viz import visualize_reduction
#visualize embedding space with original clusters
visualize_reduction(X_pca,color_mappings=optimal_k_silhouette_labels,savepath='./PCA_',cmap=cm.plasma_r)

#If they exist map transitions between the various cluster assignments
from mdsa_tools.Viz import replicatemap_from_labels

replicatemap_from_labels(cmap=cm.plasma_r,frame_list=[9]*2,labels=optimal_k_silhouette_labels,savepath='./Repmap_')#9 frames each so 

