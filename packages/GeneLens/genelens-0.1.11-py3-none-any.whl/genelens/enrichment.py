"""
Module for conducting analysis of overrepresentation of gene sets in all signal pathways of Reactome 
with construction of dendrogram of intersection of overrepresented pathways taking 
into account weight parameter
"""

from reactome2py import analysis
import requests  # HTTP Client for Python
import json  # Standard JSON library
from py2cytoscape import util as cy
import networkx as nx
import pandas as pd
import io
import itertools as itt
from scipy.spatial.distance import pdist
import scipy.cluster
import matplotlib.pyplot as plt
from colour import Color
import numpy as np
from importlib.resources import files

def _reactome_enrichment(gene_set, species='Homo sapiens'):
    """the function receives data from Reactome via reactome2py.analysis"""

    target_set = ",".join(gene_set)

    result = analysis.identifiers(ids=target_set)
    token = result['summary']['token']

    token_result = analysis.token(token, species=species, page_size='-1', page='-1', sort_by='ENTITIES_FDR',
                                  order='ASC', resource='TOTAL', p_value='0.05', include_disease=False,
                                  min_entities=2, max_entities=None)

    return token_result


def _reac_pars(token_result):
    """parsing reactome output"""

    ReactomeRes.token = token_result['summary']['token']
    ReactomeRes.max_p_value = 0
    ReactomeRes.min_p_value = 99999
    ReactomeRes.max_ratio = 0
    ReactomeRes.min_ratio = 99999
    ReactomeRes.min_found = 99999
    ReactomeRes.max_found = 0
    ReactomeRes.react_dict = dict()

    for item in token_result['pathways']:

        if item['entities']['found'] < 2:
            continue

        ReactomeRes.react_dict[item['stId']] = {'name': item['name'],
                                      'fdr': item['entities']['fdr'],
                                      'p_value': item['entities']['pValue'],
                                      'found': item['entities']['found'],
                                      'ration': item['entities']['ratio']}

        #   for Networks

        if item['entities']['found'] < ReactomeRes.min_found:
            ReactomeRes.min_found = item['entities']['found']
        if item['entities']['found'] > ReactomeRes.max_found:
            ReactomeRes.max_found = item['entities']['found']

        if item['entities']['ratio'] < ReactomeRes.min_ratio:
            ReactomeRes.min_ratio = item['entities']['ratio']
        if item['entities']['ratio'] > ReactomeRes.max_ratio:
            ReactomeRes.max_ratio = item['entities']['ratio']

        if item['entities']['pValue'] < ReactomeRes.min_p_value:
            ReactomeRes.min_p_value = item['entities']['ratio']
        if item['entities']['pValue'] > ReactomeRes.max_p_value:
            ReactomeRes.max_p_value = item['entities']['ratio']

    return ReactomeRes


def _get_net(ReactomeRes):
    """Graph of pathway construction"""
    reactome_linkege = pd.read_csv(files("genelens").joinpath("data/miRNET/baseData/ReactomePathwaysRelation.txt"), sep='\t', header=None)
    reactome_linkege.columns = ['Source', 'Target']

    G = nx.from_pandas_edgelist(reactome_linkege, source='Source', target='Target')
    G_enrich = G.subgraph(ReactomeRes.react_dict.keys())

    # removing network components that contain less than two nodes

    G_enrich = nx.Graph(G_enrich)

    for CC in list(nx.connected_components(G_enrich)):
        if len(CC) < 3:
            G_enrich.remove_nodes_from(CC)

    # add Statistics to Network

    for nods, dct in G_enrich.nodes(data=True):
        dct['label'] = ReactomeRes.react_dict[nods]['name']
        dct['fdr'] = ReactomeRes.react_dict[nods]['fdr']
        dct['found'] = ReactomeRes.react_dict[nods]['found']
        dct['ration'] = ReactomeRes.react_dict[nods]['ration']
        dct['p_value'] = ReactomeRes.react_dict[nods]['p_value']

    return G_enrich


def _dendro_reactome_to_pandas(ReactomeRes, G, species='Homo sapiens'):
    """
    Create DataFrame for dendrogram ploting
    
    Attributes:
    -----
    ReactomeRes : result of _reac_pars()
    G : result of _get_net()
    """
    url = 'https://reactome.org/AnalysisService/download/' + ReactomeRes.token + \
          '/pathways/TOTAL/result.csv'
    res = requests.get(url).content
    reactome_df = pd.read_csv(io.StringIO(res.decode('utf-8')))
    reactome_df = reactome_df[reactome_df['Entities pValue'] < 0.05]
    if (reactome_df['#Entities found'] >= 2).shape[0]:
        reactome_df = reactome_df[reactome_df['#Entities found'] >= 2]
    reactome_df = reactome_df[reactome_df['Species name'] == species]
    reactome_df = reactome_df[reactome_df['Pathway identifier'].isin(G.nodes)]

    return reactome_df, res

# Dendrograms


def _create_similarity_matrix(gene_sets):
        """Create a similarity matrix for a given pathway-geneset dataset.
        :param dict gene_sets: pathway gene set dictionary
        :rtype: pandas.DataFrame
        :returns: similarity matrix
        """
        index = sorted(gene_sets.keys())
        similarity_dataframe = pd.DataFrame(0.0, index=index, columns=index)

        for pathway_1, pathway_2 in itt.product(index, index):
            intersection = len(gene_sets[pathway_1].intersection(gene_sets[pathway_2]))
            smaller_set = min(len(gene_sets[pathway_1]), len(gene_sets[pathway_2]))

            similarity = float(intersection / smaller_set)  # Formula to calculate similarity

            #similarity_dataframe[pathway_1][pathway_2] = similarity
            similarity_dataframe.loc[pathway_2, pathway_1] = similarity

        return similarity_dataframe


def _get_dendro(dt, key_nodes_dict, out_path='./'):

    gene_set_dict = {dt.iloc[row]['Pathway identifier']: set(dt.iloc[row]['Submitted entities found'].split(';')) for
                     row in range(0, dt.shape[0])}
    dtid2name = {dt.iloc[row]['Pathway identifier']: set(dt.iloc[row]['Pathway name'].split(';')) for row in
                 range(0, dt.shape[0])}

    similarity_matrix = _create_similarity_matrix(gene_set_dict)
    if similarity_matrix.empty:
        print('similarity_matrix is empty. No intersections found. Dendrogram could not be constructed.')
        return dt
    distance_matrix = pdist(similarity_matrix, metric='correlation')
    # Замена NaN на 0
    distance_matrix = np.nan_to_num(distance_matrix, nan=0.0)

    # Cluster hierarchicaly using scipy
    clusters = scipy.cluster.hierarchy.linkage(distance_matrix, method='single')
    T = scipy.cluster.hierarchy.to_tree(clusters, rd=False)

    # Create dictionary for labeling nodes by their IDs
    labels = list(similarity_matrix.columns)
    id2name = dict(zip(range(len(labels)), labels))

    def getlabel(x):
        return '{}: ({})'.format(''.join(dtid2name[id2name[x]]), ', '.join(gene_set_dict[id2name[x]]))

    # Draw dendrogram using matplotlib to scipy-dendrogram.pdf
    my_dpi = 10
    plt.figure(figsize=(2400 / my_dpi, 2400 / my_dpi), dpi=my_dpi)
    fig, axes = plt.subplots()
    scipy.cluster.hierarchy.dendrogram(clusters,
                                       leaf_label_func=getlabel,
                                       orientation='right')
    fig.set_figwidth(10)
    fig.set_figheight(16)
    plt.tight_layout()

    """
    set a label color as the normalised cumulative betweenness {sum(betweenness)/len(gene_set)}
    """
    top5centralNods = key_nodes_dict

    ylbls = axes.get_ymajorticklabels()

    # create label to normalised cumulative betweenness dictionary

    label_to_BC = dict()
    for lbl in ylbls:
        local_label = (lbl.get_text().split(': ('))[0]  # get path name
        gene_set = (lbl.get_text().split(': ('))[1][:-1].split(', ')  # get gene set
        for gene in gene_set:
            if gene not in top5centralNods:
                top5centralNods[gene] = 0
        sum_BC = sum([top5centralNods[gene] for gene in gene_set]) / len(gene_set)
        label_to_BC[local_label] = sum_BC

    label_to_BC_sort = {k: v for k, v in sorted(label_to_BC.items(), key=lambda item: item[1], reverse=False)}

    # create gradient (grey_to_red hist path
    grey = Color('grey')
    colors = list(grey.range_to(Color("red"), len(label_to_BC_sort)))
    for label, tmp_color in zip(label_to_BC_sort.keys(), colors):
        color = str(tmp_color)
        if len(color) < 7 and color[0] == '#':
            color = color + (7 - len(color)) * color[len(color) - 1]
        label_to_BC_sort[label] = color

    # apply gradient to labels
    for lbl in ylbls:
        local_label = (lbl.get_text().split(': ('))[0]
        lbl.set_color(label_to_BC_sort[local_label])

    plt.savefig(out_path + "enrichment_dendrogram.png", dpi=300)

def dendro_reactome_plot(gene_set, gene_weights, species='Homo sapiens', out_path='./'):
    """
    The function performs an overrepresentation analysis and draws a dendrogram of signaling pathways 
    taking into account the weight of the genes included in them.

    Attributes:
    -----
    gene_set : list of genes
    gene_weights : dict {gene:weights}
    species : str, species in Reactome
    out_path : str, where the plot will be saved

    """
    enrich_res = _reactome_enrichment(gene_set, species=species)
    enrich_res = _reac_pars(enrich_res)
    G_enrich = _get_net(enrich_res) #граф сигнальных путей
    reactome_df, raw_res = _dendro_reactome_to_pandas(enrich_res, G_enrich)
    _get_dendro(gene_set=reactome_df, gene_weights=gene_weights, out_path=out_path)
