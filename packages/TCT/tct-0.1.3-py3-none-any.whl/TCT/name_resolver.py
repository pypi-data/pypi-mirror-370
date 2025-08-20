"""
This is a wrapper around the Name Resolver API.

API docs: https://name-lookup.ci.transltr.io/docs
"""
import urllib.parse

import requests

from .translator_node import TranslatorNode

URL = 'https://name-lookup.ci.transltr.io/'
"""This is the root URL for the API."""


def lookup(query: str, return_top_response:bool=True, return_synonyms:bool=False, **kwargs):
    """
    A wrapper around the `lookup` api endpoint. Given a query string, this returns a TranslatorNode object or a list of TranslatorNode objects corresponding to the given name. 

    Parameters
    ----------
    query : str
        Query string
    return_top_response : bool
        If true, this returns only the top response. If false, this returns a list of all responses. Default: True
    return_synonyms : bool
        If true, the resulting TranslatorNode objects contain a list of synonyms. If false, they do not include synonyms. Default: False
    **kwargs
        Other arguments to `lookup`

    Returns
    -------
    TranslatorNode object if return_top_response is True, list of TranslatorNode objects if return_top_response is False

    Examples
    --------
    >>> lookup('AML')
    TranslatorNode(curie='MONDO:0018874', label='acute myeloid leukemia', types=['biolink:Disease', 'biolink:DiseaseOrPhenotypicFeature', 'biolink:BiologicalEntity', 'biolink:ThingWithTaxon', 'biolink:NamedThing', 'biolink:Entity'], synonyms=None, curie_synonyms=None)

    """
    path = urllib.parse.urljoin(URL, 'lookup')
    # set autocomplete to be false by default
    if 'autocomplete' not in kwargs:
        kwargs['autocomplete'] = False
    response = requests.get(path, params={'string': query, **kwargs})
    if response.status_code == 200:
        result = response.json()
        if len(result) == 0:
            raise LookupError('No matching CURIE found for the given string ' + query)
        else:
            if return_top_response:
                node = result[0]
                n = TranslatorNode(node['curie'])
                if 'label' in node:
                    n.label = node['label']
                if 'types' in node:
                    n.types = node['types']
                if return_synonyms and 'synonyms' in node:
                    n.synonyms = node['synonyms']
                return n
            else:
                all_nodes = []
                for node in result:
                    curie = node['curie']
                    n = TranslatorNode(curie)
                    if 'label' in node:
                        n.label = node['label']
                    if 'types' in node:
                        n.types = node['types']
                    if return_synonyms and 'synonyms' in node:
                        n.synonyms = node['synonyms']
                    all_nodes.append(n)
                return all_nodes
    else:
        raise requests.RequestException('Response from server had error, code ' + str(response.status_code) + ' ' + str(response))


def synonyms(query: str, **kwargs):
    """
    A wrapper around the `synonyms` api endpoint. Given a query string, this returns a dict of CURIE id : TranslatorNode for all synonyms for the given query. 

    Parameters
    ----------
    query : str
        Query CURIE
    **kwargs
        Other arguments to `synonyms`

    Returns
    -------
    Dict of CURIE id : TranslatorNode
    """
    path = urllib.parse.urljoin(URL, 'synonyms')
    # set autocomplete to be false by default
    response = requests.get(path, params={'preferred_curies': query, **kwargs})
    if response.status_code == 200:
        result = response.json()
        if len(result) == 0:
            raise LookupError('No matching CURIE found for the given string ' + query)
        else:
            all_nodes = {}
            for k, node in result.items():
                curie = node['curie']
                n = TranslatorNode(curie)
                if 'preferred_name' in node:
                    n.label = node['preferred_name']
                if 'types' in node:
                    n.types = node['types']
                if 'names' in node:
                    n.synonyms = node['names']
                all_nodes[k] = n
            return all_nodes
    else:
        raise requests.RequestException('Response from server had error, code ' + str(response.status_code) + ' ' + str(response))


def chunk_list(data:list, size:int):
    #Extra method to help chunk large files and avoid 504 error.
    chunks = []
    for i in range(0, len(data), size):
        chunks.append(data[i: i+size])
    return chunks


def batch_lookup(strings:list[str], size: int=25, return_top_response:bool=True, return_synonyms:bool=False, **kwargs) -> dict:
    """
    A wrapper around the `bulk-lookup` api endpoint. Given a list of query strings, this returns a TranslatorNode object or a list of TranslatorNode objects corresponding to the given name. 

    Parameters
    ----------
    strings : list[str]
        List of query strings.
    size : int
        Desired chunking size, default is 25.
    return_top_response : bool
        If true, this returns only the top response per string. If false, this returns a list of all responses per string. Default: True
    return_synonyms : bool
        If true, the resulting TranslatorNode objects contain a list of synonyms. If false, they do not include synonyms. Default: False
    **kwargs
        Other arguments to `bulk-lookup`

    Returns
    -------
    Dict of string : TranslatorNode object if return_top_response is True, list of TranslatorNode objects if return_top_response is False

    Examples
    --------
    >>> batch_lookup(['AML', 'CML'])
    {'AML': TranslatorNode(curie='MONDO:0018874', label='acute myeloid leukemia',...),
     'CML': TranslatorNode(curie='MONDO:0010809', label='familial chronic myelocytic leukemia-like syndrome',...)}
    """
    path = urllib.parse.urljoin(URL, 'bulk-lookup')
    curies = {}
    chunks = chunk_list(strings, size)
    for chunk in chunks:
        payload = {
            "strings": chunk,
            **kwargs
        }
        response = requests.post(path, json = payload)
        if response.status_code == 200:
            result = response.json()
            if(len(result) == 0):
                raise LookupError('No matching CURIE found for the given strings ' + str(strings))
            else:
                for s in chunk:
                    nodes = result.get(s, [])
                    translator_nodes = []
                    for node in nodes: 
                        n = TranslatorNode(node['curie'])
                        if 'label' in node:
                            n.label = node['label']
                        if 'types' in node:
                            n.types = node['types']
                        if return_synonyms and 'synonyms' in node:
                            n.synonyms = node['synonyms']
                        translator_nodes.append(n)
                    if return_top_response:
                        if translator_nodes:
                            curies[s] = translator_nodes[0]
                        else:
                            curies[s] = None
                    else:
                        curies[s] = translator_nodes
        else:
            raise requests.RequestException('Response from server had error, code ' + str(response.status_code) + ' ' + str(response))
    return curies
