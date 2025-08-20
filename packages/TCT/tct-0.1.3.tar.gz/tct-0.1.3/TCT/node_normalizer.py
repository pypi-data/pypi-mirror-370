"""
This is a wrapper around the Node Normalizer API.

API docs: https://nodenorm.transltr.io/docs
"""
import urllib.parse

import requests

from .translator_node import TranslatorNode


URL = 'https://nodenorm.transltr.io/'

def get_normalized_nodes(query: str | list[str],
        return_equivalent_identifiers:bool=False,
        **kwargs):
    """
    A wrapper around the `get_normalized_nodes` api endpoint. Given a CURIE or a list of CURIEs, this returns a list of normalized identifiers.
    
    Parameters
    ----------
    query : str
        Query CURIE
    return_equivalent_identifiers : bool
        Whether or not to return a list of equivalent identifiers along with the TranslatorNode. Default: False
    **kwargs
        Other arguments to `get_normalized_nodes` (e.g. `conflate` for gene-protein conflation, `drug_chemical_conflate` for drug-chemical conflation)

    Returns
    -------
    If query is a single CURIE, returns a single TranslatorNode.

    If query is a list of CURIEs, a dict of CURIE id to TranslatorNode for every node in the query.

    Examples
    --------
    >>> get_normalized_nodes('MESH:D014867', return_equivalent_identifiers=False)
    TranslatorNode(curie='CHEBI:15377', label='Water', types=['biolink:SmallMolecule', 'biolink:MolecularEntity', 'biolink:ChemicalEntity', 'biolink:PhysicalEssence', 'biolink:ChemicalOrDrugOrTreatment', 'biolink:ChemicalEntityOrGeneOrGeneProduct', 'biolink:ChemicalEntityOrProteinOrPolypeptide', 'biolink:NamedThing', 'biolink:PhysicalEssenceOrOccurrent'], synonyms=None, curie_synonyms=None)
    """
    path = urllib.parse.urljoin(URL, 'get_normalized_nodes')
    # default parameters: true for gene-protein conflation, false for drug-chemical conflation
    response = requests.get(path, params={'curie': query, **kwargs})
    if response.status_code == 200:
        result = response.json()
        if len(result) == 0:
            raise LookupError('No matches found for the given input: ' + query)
        else:
            normalized_dict = {}
            for k, node in result.items():
                n = TranslatorNode(node['id']['identifier'])
                if 'label' in node['id']:
                    n.label = node['id']['label']
                if 'type' in node:
                    n.types = node['type']
                if return_equivalent_identifiers and 'equivalent_identifiers' in node:
                    synonyms = []
                    curie_synonyms = []
                    for eq in node['equivalent_identifiers']:
                        if 'label' in eq:
                            synonyms.append(eq['label'])
                        else:
                            synonyms.append(None)
                        curie_synonyms.append(eq['identifier'])
                    n.synonyms = synonyms
                    n.curie_synonyms = curie_synonyms
                normalized_dict[k] = n
            if isinstance(query, str):
                return normalized_dict[query]
            return normalized_dict
    else:
        raise requests.RequestException('Response from server had error, code ' + str(response.status_code))
