# GeneLens: Intelligent DEG Analysis & Biomarker Prediction

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![PyPI Version](https://img.shields.io/pypi/v/genelens)](https://pypi.org/project/genelens/)

## Overview

**GeneLens** is a Python package for functional analysis of differentially expressed genes (DEGs) and biomarker prediction, integrating:
- Machine learning-based biomarker identification
- Graph-based prediction of gene function via protein-protein interaction networks analysis

Key applications:
- Identification of biomarkers
- Analysis of gene-gene networks

## Features

### Core Modules

1. **FSelector**
   - Machine learning pipeline for biomarker discovery
   - Features:
     - Automatic Monte Carlo simulation of stable models
     - Automated model training/tuning
     - Feature importance analysis
     - Customizable thresholds

2. **NetAnalyzer**
   - Implements graph-based algorithm (Osmak et al. 2020, 2021)
   - Predicts genes functions via topological analysis of molecular networks
   - Features:
     - Automated network construction
     - Pathway enrichment
     - Integration with Feature importance from FSelector

### Additional Capabilities
- Standardized analysis pipelines
- Interactive network visualizations
- Support for multi-omics data integration

## Installation

```bash
pip install genelens
```

## Example of use FeatureSelector

```python
from genelens.fselector import FeatureSelector, get_feature_space, fsplot
from genelens import netanalyzer, enrichment
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import networkx as nx
from importlib.resources import files
```


```python
# data load
data = pd.read_csv(files("genelens").joinpath("data/exampl_data/train_test.csv"), index_col=0)
X = data.drop('index', axis=1)
y = list(map(int, data['index'] == 'HCM'))
```

```python
# FeatureSelector initialization
FS_model = FeatureSelector(X, y,
                           C = None, 
                           C_space=np.linspace(0.0001, 1, 20), #bigger space -> more precision, more processor time
                           C_finder_iter=10,
                           cut_off_frac_estimation=True,
                           cut_off_frac_model=0,
                           cut_off_estim_params={'max_feature': 50}) # This parameter implements early stopping. Bigger feature space -> more precision, more processor time
```

```python
FS_model.fit(max_iter=2700, log=True, feature_resample=0) #more max_iter -> more precision, more processor time
```

```python
fsplots = fsplot(FS_model)
fsplots.plot_all(fontsize=25, labels=['a.', 'b.', 'c.', 'd.', 'e.', 'f.'], 
                left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.5, wspace=0.5)
plt.show()
```
    
Output example:
![https://github.com/GJOsmak/GeneLens/blob/f8b452aa50831742cf5dcc4819f02c58d71376ad/images/output_4_0.png](https://github.com/GJOsmak/GeneLens/blob/f8b452aa50831742cf5dcc4819f02c58d71376ad/images/output_4_0.png)
    

```python
FS_model.best_features

# return:    
# {'RASD1': np.float64(0.9510623822037754),
#  'MYH6': np.float64(0.8420449794132905)}
```

## Network Enrichment Analysis

```python
GenGenNetwork = netanalyzer.GeneralNet() #Load String db and create gene-gene interaction network
GenGenNetwork.get_LCC() #get the largest connected component from the network
GenGenNetwork.minimum_connected_subgraph(FS_model.best_features)

# output:
# RASD1 absent from LCC, excluded from further analysis
# CDC42EP4 absent from LCC, excluded from further analysis
#
# mst-graph was extracted
# Initial core feature=1, mst-graph cardinality=0
```

#### If Two of the three selected genes are missing from the version of the String database we are using, it is not possible to construct an mst-graph. To continue the analysis, we will select the top 10 genes sorted by their Score


```python
GenGenNetwork.minimum_connected_subgraph(dict(list(FS_model.all_features.items())[:10]))

# output: 
# RASD1 absent from LCC, excluded from further analysis
# CDC42EP4 absent from LCC, excluded from further analysis
# ZFP36 absent from LCC, excluded from further analysis
#
# mst-graph was extracted
# Initial core feature=7, mst-graph cardinality=17
```


```python
pos = nx.circular_layout(GenGenNetwork.mst_subgraph)

nx.draw(
    GenGenNetwork.mst_subgraph,
    pos,
    with_labels=True,       
    node_color='skyblue',   
    edge_color='gray',      
    node_size=2000,         
    font_size=15            
)
plt.show()
```


Output example:
![https://github.com/GJOsmak/GeneLens/blob/f8b452aa50831742cf5dcc4819f02c58d71376ad/images/output_12_0.png](https://github.com/GJOsmak/GeneLens/blob/f8b452aa50831742cf5dcc4819f02c58d71376ad/images/output_12_0.png)
    



```python
enrichment.dendro_reactome_plot(list(GenGenNetwork.mst_subgraph.nodes()), FS_model.all_features, species='Homo sapiens')
```

Output example:  
![https://github.com/GJOsmak/GeneLens/blob/f8b452aa50831742cf5dcc4819f02c58d71376ad/images/output_13_1.png](https://github.com/GJOsmak/GeneLens/blob/f8b452aa50831742cf5dcc4819f02c58d71376ad/images/output_13_1.png)
    


#### The color gradient from gray to red in the signatures reflects the increase in the weight of genes according to their calculated Score. The redder the signature, the higher the weight.

## Example of use NetAnalyzer

```python
from genelens.netanalyzer import GeneralNet, Targets, KeyNodesExtractor, tissue_selector
MirNet = GeneralNet(interactome_path_db=None) # Load String db from path and create gene-gene interaction network.
                                      # If path=None than built-in String version loaded.
MirNet.get_LCC()                      # get the largest connected component from the network
miRNA_targets = Targets(path_to_miRTarBase=None) #create dict from miRTarBase
target_genes = miRNA_targets.get_targets('miR-375')
MirNet.select_nodes(target_genes)        # select the part of LCC containing only the miRNA target genes
tis_gene_set = tissue_selector(ans=0, tissue_id=23) #In case of ans=None, tissue_id=None the choice will be offered interactively
MirNet.select_nodes(tis_gene_set)     # select the part of LCC containing only the tissue target genes
MirNet.get_LCC()
extractor = KeyNodesExtractor()
extractor(MirNet)
```
#### We can also make a miRNA key genes extraction function (Pipeline):
```python
from genelens.netanalyzer import GeneralNet, Targets, KeyNodesExtractor

miRTargets = Targets()
def miRNAkey_extractor_pipeline(miRNA):
    GNet = GeneralNet(verbose=False)
    Extractor = KeyNodesExtractor()
    GNet.select_nodes(miRTargets.get_targets(miRNA, verbose=False))
    GNet.get_LCC(verbose=False)
    if len(GNet.LCC) > 0:
        return Extractor(GNet)
    else:
        return dict()
```
### More information can be found in our publications:

1.	Pisklova, M., Osmak, G. (2024). Unveiling MiRNA-124 as a biomarker in hypertrophic cardiomyopathy: An innovative approach using machine learning and intelligent data analysis. International Journal of Cardiology, 410, 132220.
2.	Osmak, G., Baulina, N., Kiselev, I., & Favorova, O. (2021). MiRNA-regulated pathways for hypertrophic cardiomyopathy: network-based approach to insight into pathogenesis. Genes, 12(12), 2016.
3.	Osmak, G., Kiselev, I., Baulina, N., & Favorova, O. (2020). From miRNA target gene network to miRNA function: miR-375 might regulate apoptosis and actin dynamics in the heart muscle via Rho-GTPases-dependent pathways. International Journal of Molecular Sciences, 21(24), 9670.
4. Osmak, G. J., Pisklova, M.V. (2025). Transcriptomics and the “Curse of Dimensionality”: Monte Carlo Simulations of ML-Models as a Tool for Analyzing Multidimensional Data in Tasks of Searching Markers of Biological Processes. Molecular Biology, 59, 143-149.
