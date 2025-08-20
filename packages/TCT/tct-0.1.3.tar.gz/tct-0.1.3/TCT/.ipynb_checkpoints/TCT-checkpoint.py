import requests
import json
import pandas as pd
import  seaborn as sns
import matplotlib.pyplot as plt
import ipycytoscape
import networkx as nx
import numpy as np
import openai
import matplotlib
import matplotlib.pyplot as plt
import ipycytoscape


# plt.switch_backend('module://ipykernel.pylab.backend_inline')

from IPython.display import display


def TCT_help(func):
    print(func.__doc__)


    
# used. Jan 5, 2024
def get_Translator_APIs():
    Translator_APIs = []
    #Translator_apps_url = "https://smart-api.info/api/query?q=tags.name:translator&fields=info,_meta,tags&meta=1&size=500"
    Translator_apps_url = "https://dev.smart-api.info/api/query?q=tags.name:translator&fields=info,_meta,tags&meta=1&size=500"
    Translator_apps = requests.get(Translator_apps_url).json()['hits']
    for app in Translator_apps:
        Translator_APIs.append(app['info']['title'])
    return Translator_APIs

# used Dec 5, 2023 (Example_query_one_hop_with_category.ipynb)
def list_Translator_APIs():
    APInames = {
        'Automat-ctd(Trapi v1.4.0)':"https://automat.transltr.io/ctd/1.4/query",
        #'Automat-sri-reference-kg(Trapi v1.4.0)':"",
        #'Autonomous Relay System (ARS) TRAPI':"",
        #'BioLink API':"",
        #'BioThings AGR API':"",
        #'BioThings BioPlanet Pathway-Gene API':"",
        #'BioThings DDInter API':"",
        'BioThings Explorer (BTE) TRAPI':"https://bte.transltr.io/v1/query",
        #'BioThings FooDB API':"",
        #'BioThings FoodData Central API':"",
        #'BioThings GO Biological Process API':"",
        #'BioThings InnateDB API':"", # not in TRAPI standard
        #'BioThings RARe-SOURCE API':"",
        #'BioThings repoDB API':"",
        #'Biolink Lookup':"",
        'Biothings Therapeutic Target Database API':"https://biothings.ncats.io/ttd/query",
        #'COHD TRAPI':"https://cohd-api.transltr.io/api/query",
        #'Complex Portal Web Service':"",
        #'Curated Query Service':"",
        #'EBI Proteins API':"",
        #'Gene-List Network Enrichment Analysis':"",
        #'Knowledge Collaboratory API':"",
        #'LitVar API':"",
        #'RaMP API v1.0.1':"",
        #'SmartAPI API':"",
        #'Sri-answer-appraiser(Trapi v1.4.0)':"",
        #'Sri-name-resolver':"",
        #'Sri-node-normalizer(Trapi v1.3.0)':"",
        #'Sri-node-normalizer(Trapi v1.4.0)':"",
        #'Translator Annotation Service':"",
        #'Workflow-runner(Trapi v1.4.0)':"https://translator-workflow-runner.transltr.io/query",
        #'imProving Agent for TRAPI 1.4':"",
        #'mediKanren':'https://medikanren-trapi.transltr.io/query', #ARA
        #"BigGIM_BMG":"http://127.0.0.1:8000/find_path_by_predicate",
        "Aragorn(Trapi v1.4.0)":"https://aragorn.transltr.io/aragorn/query",
        #"ARAX Translator Reasoner - TRAPI 1.4.0":"https://arax.transltr.io/api/arax/v1.4/asyncquery",
        "ARAX Translator Reasoner - TRAPI 1.4.0":"https://arax.transltr.io/api/arax/v1.4/query",
        "RTX KG2 - TRAPI 1.4.0":"https://arax.ncats.io/api/rtxkg2/v1.4/query",
        "SPOKE KP for TRAPI 1.4":"https://spokekp.transltr.io/api/v1.4/query",
        "Multiomics BigGIM-DrugResponse KP API":"https://bte.test.transltr.io/v1/smartapi/adf20dd6ff23dfe18e8e012bde686e31/query",
        "Multiomics ClinicalTrials KP":"https://api.bte.ncats.io/v1/smartapi/d86a24f6027ffe778f84ba10a7a1861a/query",
        "Multiomics Wellness KP API":"https://api.bte.ncats.io/v1/smartapi/02af7d098ab304e80d6f4806c3527027/query",
        "Multiomics EHR Risk KP API":"https://api.bte.ncats.io/v1/smartapi/d86a24f6027ffe778f84ba10a7a1861a/query",
        "Biothings Explorer (BTE)":"https://bte.transltr.io/v1/query",
        "Service Provider TRAPI":"https://api.bte.ncats.io/v1/smartapi/978fe380a147a8641caf72320862697b/query",
        "Explanatory-agent":"https://explanatory-agent-creative.azurewebsites.net/ARA/v1.3/asyncquery", #403 error
        "MolePro":"https://translator.broadinstitute.org/molepro/trapi/v1.4/query",
        "Genetics KP":"https://genetics-kp.transltr.io/genetics_provider/trapi/v1.4/query",
        "medikanren-unsecret":"https://medikanren-trapi.transltr.io/query",
        "Text Mined Cooccurrence API":"https://api.bte.ncats.io/v1/smartapi/978fe380a147a8641caf72320862697b/query",
        "OpenPredict API":"https://openpredict.transltr.io/query",
        "Agrkb(Trapi v1.4.0)":"https://automat.transltr.io/genome-alliance/1.4/query",
        "Automat-biolink(Trapi v1.4.0)": "https://automat.renci.org/biolink/1.4/query",
        "Automat-cam-kp(Trapi v1.4.0)": "https://automat.ci.transltr.io/cam-kp/1.4/query?limit=100",
        #"Automat-ctd(Trapi v1.4.0)": "https://automat.renci.org/drugcentral/1.4/query",
        "Automat-drug-central(Trapi v1.4.0)": "https://automat.ci.renci.org/drugcentral/1.4/query",
        "Automat-gtex(Trapi v1.4.0)":"https://automat.renci.org/gtex/1.4/query",
        "Automat-gtopdb(Trapi v1.4.0)": "https://automat.renci.org/gtopdb/1.4/query",
        "Automat-gwas-catalog(Trapi v1.4.0)": "https://automat.renci.org/gwas-catalog/1.4/query",
        "Automat-hetio(Trapi v1.4.0)": "https://automat.ci.transltr.io/hetio/1.4/query",
        "Automat-hgnc(Trapi v1.4.0)": "https://automat.renci.org/hgnc/1.4/query",
        "Automat-hmdb(Trapi v1.4.0)": "https://automat.renci.org/hmdb/1.4/query",
        "Automat-human-goa(Trapi v1.4.0)": "https://automat.renci.org/human-goa/1.4/query",
        "Automat-icees-kg(Trapi v1.4.0)": "https://automat.renci.org/icees-kg/1.4/query",
        "Automat-intact(Trapi v1.4.0)": "https://automat.renci.org/intact/1.4/query",
        "Automat-panther(Trapi v1.4.0)": "https://automat.renci.org/panther/1.4/query",
        "Automat-pharos(Trapi v1.4.0)": "https://automat.renci.org/pharos/1.4/query",
        "Automat-robokop(Trapi v1.4.0)": "https://ars-prod.transltr.io/ara-robokop/api/runquery", #doesn't work
        "Automat-sri-reference-kp(Trapi v1.4.0)": "https://automat.ci.transltr.io/sri-reference-kp/1.4/query", #doesn't work
        "Automat-string-db(Trapi v1.4.0)": "https://automat.ci.transltr.io/string-db/1.4/query",
        "Automat-ubergraph(Trapi v1.4.0)": "https://automat.ci.transltr.io/ubergraph/1.4/query",
        "Automat-ubergraph-nonredundant(Trapi v1.4.0)": "https://automat.ci.transltr.io/ubergraph-nonredundant/1.4/query",
        "Automat-viral-proteome(Trapi v1.4.0)": "https://automat.ci.transltr.io/viral-proteome/1.4/query",
        #"COHD TRAPI":"https://cohd-api.transltr.io/api/query", # 500 error
        "CTD API":"https://automat.ci.transltr.io/ctd/1.4/query",
        "Connections Hypothesis Provider API":"https://chp-api.transltr.io/query", #no knowledge_graph is defined in the response
        "MyGene.info API":"https://api.bte.ncats.io/v1/smartapi/59dce17363dce279d389100834e43648/query", #check with chunlei
        "MyDisease.info API":"https://api.bte.ncats.io/v1/smartapi/671b45c0301c8624abbd26ae78449ca2/query", #check with chunlei
        "MyChem.info API":"https://api.bte.ncats.io/v1/8f08d1446e0bb9c2b323713ce83e2bd3/query", #check with chunlei
        "MyVariant.info API":"https://api.bte.ncats.io/v1/59dce17363dce279d389100834e43648/query", #check with chunlei
        "Ontology Lookup Service API":"https://api.bte.ncats.io/v1/1c056ffc7ed0dd1229e71c4752239465/query", #check with chunlei
        "PharmGKB REST API":"https://api.bte.ncats.io/v1/bde72db681ec0b8f9eeb67bb6b8dd72c/query", #need to check with chunlei/Andrew
        "QuickGO API":"https://api.bte.ncats.io/v1/1f277e1563fcfd124bfae2cc3c4bcdec/query",#pathways
        #"RaMP API v1.0.1":"",
        "Text Mining Targeted Association API":"https://api.bte.ncats.io/v1/smartapi/978fe380a147a8641caf72320862697b/query",
        "BioThings BindingDB API":"https://api.bte.ncats.io/v1/smartapi/38e9e5169a72aee3659c9ddba956790d/query",
        "BioThings BioPlanet Pathway-Disease API":"https://api.bte.ncats.io/v1/smartapi/55a223c6c6e0291dbd05f2faf27d16f4/query",
        "BioThings DDinter API":"https://api.bte.ncats.io/v1/smartapi/00fb85fc776279163199e6c50f6ddfc6/query",
        "BioThings DGIdb API":"https://api.bte.ncats.io/v1/smartapi/e3edd325c76f2992a111b43a907a4870/query",
        "BioThings DISEASES API":"https://api.bte.ncats.io/v1/smartapi/a7f784626a426d054885a5f33f17d3f8/query",
        "BioThings EBIgene2phenotype API":"https://api.bte.ncats.io/v1/smartapi/1f47552dabd67351d4c625adb0a10d00/query",
        "BioThings Biological Process API":"https://api.bte.ncats.io/v1/smartapi/cc857d5b7c8b7609b5bbb38ff990bfff/query",
        "BioThings GO Cellular Component API":"https://api.bte.ncats.io/v1/smartapi/f339b28426e7bf72028f60feefcd7465/query",
        "BioThings GO Molecular Function API":"https://api.bte.ncats.io/v1/smartapi/34bad236d77bea0a0ee6c6cba5be54a6/query",
        "BioThings GTRx API":"https://api.bte.ncats.io/v1/smartapi/316eab811fd9ef1097df98bcaa9f7361/query",
        "BioThings HPO API": "https://api.bte.ncats.io/v1/smartapi/d7d1cc9bbe04ad9936076ca5aea904fe/query",
        "BioThings IDISK API":"https://api.bte.ncats.io/v1/smartapi/32f36164fabed5d3abe6c2fd899c9418/query",
        "BioThings MGIgene2phenotype API":"https://api.bte.ncats.io/v1/smartapi/77ed27f111262d0289ed4f4071faa619/query",
        "BioThings PFOCR API":"https://api.bte.ncats.io/v1/smartapi/edeb26858bd27d0322af93e7a9e08761/query",
        "Biothings RARe-SOURCE API":"https://api.bte.ncats.io/v1/smartapi/b772ebfbfa536bba37764d7fddb11d6f/query",
        "BioThings Rhea API":"https://api.bte.ncats.io/v1/smartapi/03283cc2b21c077be6794e1704b1d230/query",
        "BioThings SEMMEDDB API":"https://api.bte.ncats.io/v1/smartapi/1d288b3a3caf75d541ffaae3aab386c8/query",
        "BioThings SuppKG API":"https://api.bte.ncats.io/v1/smartapi/b48c34df08d16311e3bca06b135b828d/query",
        "BioThings UBERON API":"https://api.bte.ncats.io/v1/smartapi/ec6d76016ef40f284359d17fbf78df20/query",
    }
    return(APInames)

# used Dec 5, 2023
def find_link(name):
    #pre = "https://dev.smart-api.info/api/metakg/consolidated?size=2000&q=%28api.x-translator.component%3AKP+AND+api.name%3A" # This works for the previous version
    pre = "https://smart-api.info/api/metakg/consolidated?size=2000&q=%28api.x-translator.component%3AKP+AND+api.name%3A" 
    end = "%5C%28Trapi+v1.4.0%5C%29%29"
    if '(Trapi v1.4.0)' in name:
        url = pre
        name_raw = name.split("(")[0]
        words = name_raw.split(" ")
    
        length = len(words)
        if length == 1:
            url = url + words[0] + end
        else:
            for i in range(0,length-1):
                url = url + words[i] + "+"
            url = url+words[length-1]+end
    
    else:
        words = name.split(" ")
        url = pre
        length = len(words)
        
        for i in range(0,length-1):
            url = url + words[i] + "+"
        url = url+words[length-1]+"%29"
    return(url)

# used
# Finalized version: Dec 5, 2023 (Example_query_one_hop_with_category.ipynb)
def get_KP_metadata(APInames):

    '''
    APInames = get_API_list()
    '''

    result_df = pd.DataFrame()
    API_list = []
    URL_list = []
    KG_category_list = []
    subject_list = []
    object_list = []
    url_list = []
    #for KP in KPnames:
    for KP in APInames.keys():
        json_text ={}
        if KP == "RTX KG2 - TRAPI 1.4.0": 
            #print("ARAX KG2 - TRAPI 1.4.0")
            text =requests.get("https://dev.smart-api.info/api/metakg/consolidated?size=20&q=%28api.x-translator.component%3AKP+AND+api.name%3ARTX+KG2+%5C-+TRAPI+1%5C.4%5C.0%29").text  # This works for the previous version
            #text =requests.get("https://smart-api.info/api/metakg/consolidated?size=20&q=%28api.x-translator.component%3AKP+AND+api.name%3ARTX+KG2+%5C-+TRAPI+1%5C.4%5C.0%29").text  # This works for the previous version
            json_text = json.loads(text)
        else:
            text = requests.get(find_link(KP)).text
            #text = requests.get(dic_KP_metadata[KP]).text
            json_text = json.loads(text)

        for i in (json_text['hits']):
            KG_category_list.append("biolink:"+i['_id'].split("-")[1])
            API_list.append(KP)
            subject_list.append('biolink:'+i['_id'].split("-")[0])
            object_list.append('biolink:'+i['_id'].split("-")[2])
            url_list.append(APInames[KP])

    result_df = pd.DataFrame({ 'API': API_list, 'KG_category': KG_category_list, "Subject":subject_list, "Object":object_list, "URL":url_list})
    #result_df.to_csv("KP_metadata.csv", index=False)
    return(result_df)

# used
def add_new_API_for_query(APInames, metaKG, newAPIname, newAPIurl, newAPIcategory, newAPIsubject, newAPIobject):

    '''
    This function is used to add a new API beyond the current list of APIs for query
    Example: APInames, metaKG = add_new_API_for_query(APInames, metaKG, "BigGIM_BMG", "http://127.0.0.1:8000/find_path_by_predicate", "Gene-physically_interacts_with-gene", "Gene", "Gene")

    '''
    APInames[newAPIname] = newAPIurl

    new_row = pd.DataFrame({"API":newAPIname,
                            "KG_category":newAPIcategory,
                            "Subject":newAPIsubject, "Object":newAPIobject,
                            "URL":newAPIurl}, index=[0])
    metaKG = pd.concat([metaKG, new_row], ignore_index=True)
    return APInames, metaKG

# used. Dec 5, 2023 (Example_query_one_hop_with_category.ipynb)
def select_API(sub_list,obj_list, metaKG):
    '''
    sub_list = ["biolink:Gene", "biolink:Protein"]
    obj_list = ["biolink:Gene", "biolink:Disease"]
    
    '''
    new_sub_list = sub_list
    new_obj_list = obj_list
    #for item in sub_list:
    #    new_sub_list.append(item.split(":")[1])
    #for item in obj_list:
    #    new_obj_list.append(item.split(":")[1])

    #metaKG = pd.read_csv("KP_metadata.csv")
    df1 = metaKG.loc[(metaKG['Subject'].isin(new_sub_list)) & (metaKG['Object'].isin(new_obj_list))]
    df2 = metaKG.loc[(metaKG['Subject'].isin(new_obj_list)) & (metaKG['Object'].isin(new_sub_list))]
    df = pd.concat([df1,df2])
    return(list(set(df['API'].values)))

# used. Dec 5, 2023  (Example_query_one_hop_with_category.ipynb)
def select_concept(sub_list,obj_list,metaKG):
    #result_df = pd.read_csv("KP_metadata.csv")
    df1 = metaKG.loc[(metaKG['Subject'].isin(sub_list)) & (metaKG['Object'].isin(obj_list))]
    df2 = metaKG.loc[(metaKG['Subject'].isin(obj_list)) & (metaKG['Object'].isin(sub_list))]
    df = pd.concat([df1,df2])
    return(set(list(df['KG_category'])))

# used. Dec 5, 2023 (Example_query_one_hop_with_category.ipynb)
def get_Translator_API_URL(API_sele, APInames):
    API_URL = []
    #API_URL = {}
    for name in API_sele:
        if name in APInames.keys():
            API_URL.append(APInames[name])
            #API_URL[name] = APInames[name]
        else:
            print(name + " : API name not found")
    return API_URL

# select APIs based on the predicates. Dec 10, 2023
def filter_APIs(sele_predicates, metaKG):
    if sele_predicates == []:
        sele_API_URL = list(metaKG['KG_category'].unique())    
    else:
        sele_API_URL = list(metaKG.loc[metaKG['KG_category'].isin(sele_predicates)]['URL'].unique())
    return sele_API_URL

def select_predicates_inKP(sub_list,obj_list,KPname,metaKG):
    '''sub_list = ["biolink:Gene", "biolink:Protein"]
      obj_list = ["biolink:Gene", "biolink:Disease"]
      KPname = "" # it should be one of the names in APInames
    '''

    new_sub_list = []
    new_obj_list = []
    for item in sub_list:
        new_sub_list.append(item.split(":")[1])
    for item in obj_list:
        new_obj_list.append(item.split(":")[1])

    #result_df = pd.read_csv("KP_metadata.csv")
    df1 = metaKG.loc[(metaKG['Subject'].isin(new_sub_list)) & (metaKG['Object'].isin(new_obj_list)) & (metaKG['API']==KPname)]
    df2 = metaKG.loc[(metaKG['Subject'].isin(new_obj_list)) & (metaKG['Object'].isin(new_sub_list)) & (metaKG['API']==KPname)]
    df = pd.concat([df1,df2])
    temp_set = (set(list(df['KG_category'])))
    final_set = []
    for concept in temp_set:
        #final_set.append("biolink:"+concept.split("-")[1])
        final_set.append(concept)
    return(final_set)

    
#def Generate_Gene_id_map():
#    id_file = open("../metaData/Homo_sapiens.gene_info", "r")
#    Gene_id_map = {}
#    for line in id_file:
#        line = line.strip()
#        Gene_id_map["NCBIGene:"+line.split("\t")[1]] = line.split("\t")[2]
#    id_file.close()
#    return(Gene_id_map)

# Used. Jan 5, 2024
def ID_convert_to_preferred_name_nodeNormalizer(id_list):
    dic_id_map = {}
    unrecoglized_ids = []
    recoglized_ids = []
    # To convert a CURIE to a preferred name, you don't need NameLookup at all -- NodeNorm can
    # do this by itself!
    NODENORM_BASE_URL = "https://nodenorm.transltr.io"  # Adjust this if you need NodeNorm TEST, CI or DEV.
    NODENORM_BATCH_LIMIT = 900                          # Adjust this if you start getting errors from NodeNorm.
    NODENORM_GENE_PROTEIN_CONFLATION = True             # Change to False if you don't want gene/protein conflation.
    NODENORM_DRUG_CHEMICAL_CONFLATION = False           # Change to True if you want drug/chemical conflation.

    # split id_list into batches of at most NODENORM_BATCH_LIMIT entries
    for index in range(0, len(id_list), NODENORM_BATCH_LIMIT):
        id_sublist = id_list[index:index + NODENORM_BATCH_LIMIT]

        # print(f"id_sublist: {id_sublist}")

        # Query NodeNorm with https://nodenorm.transltr.io/docs#/default/get_normalized_node_handler_get_normalized_nodes_get
        response = requests.post(NODENORM_BASE_URL + '/get_normalized_nodes', json={
            "curies": id_sublist,
            "description": False,   # Change to True if you want descriptions from any identifiers we know about.
            "conflate": NODENORM_GENE_PROTEIN_CONFLATION,
            "drug_chemical_conflate": NODENORM_DRUG_CHEMICAL_CONFLATION,
        })
        if not response.ok:
            raise RuntimeError("Error: NodeNorm request failed with status code " + str(response.status_code))

        results = response.json()
        for curie in id_sublist:
            if curie in results and results[curie]:
                identifier = results[curie].get('id', {})
                if 'identifier' in identifier and identifier['identifier'] != curie:
                    recoglized_ids.append(curie)
                    #print(f"NodeNorm normalized {curie} to {identifier['identifier']} " +
                    #      f"with gene-protein conflation {NODENORM_GENE_PROTEIN_CONFLATION} and " +
                    #      f"with drug-chemical conflation {NODENORM_DRUG_CHEMICAL_CONFLATION}.")
                label = identifier.get('label')
                dic_id_map[curie] = label
                if not label:
                    print(curie + ": no preferred name")
                    dic_id_map[curie] = curie
            else:
                unrecoglized_ids.append(curie)
                
                dic_id_map[curie] = curie
    if len(unrecoglized_ids) > 0:
        print("NodeNorm does not know about these identifiers: " + ",".join(unrecoglized_ids))
    
    return dic_id_map


def visulization_one_hop_ranking_input_as_list(result_ranked_by_primary_infores,result_parsed , 
                                 num_of_nodes = 20, 
                                 input_query = "NCBIGene:3845",
                                 fontsize = 6,
                                 title_fontsize = 12,
                                 output_png1="NE_heatmap1.png",
                                 output_png2="NE_heatmap2.png"
                                 ):
    # edited Dec 5, 2023
    predicates_list = []
    primary_infore_list = []
    aggregator_infore_list = []

    from io import BytesIO
    for i in range(0, result_ranked_by_primary_infores.shape[0]):
        oupput_node = result_ranked_by_primary_infores['output_node'][i]
        type_of_node = result_ranked_by_primary_infores['type_of_nodes'][i]
        if type_of_node == 'object':
            subject = input_query
            object = oupput_node
        else:
            subject = oupput_node
            object = input_query
            
        predicates_list = predicates_list + result_parsed[subject + "_" + object]['predicate']
        primary_infore_list = primary_infore_list + result_parsed[subject + "_" + object]['primary_knowledge_source']
        
        if 'aggregator_knowledge_source' in result_parsed[subject + "_" + object]:
            aggregator_infore_list = aggregator_infore_list + result_parsed[subject + "_" + object]['aggregator_knowledge_source']
            aggregator_infore_list = list(set(aggregator_infore_list))

        predicates_list = list(set(predicates_list))
        primary_infore_list = list(set(primary_infore_list))
        

    predicates_by_nodes = {}
    for predict in predicates_list:
        predicates_by_nodes[predict] = []

    primary_infore_by_nodes = {}
    for predict in primary_infore_list:
        primary_infore_by_nodes[predict] = []

    aggregator_infore_by_nodes = {}
    for predict in aggregator_infore_list:
        aggregator_infore_by_nodes[predict] = []
        
    names = []
    for i in range(0, result_ranked_by_primary_infores.shape[0]):
    #for i in range(0, 10):
        input_nodes = result_ranked_by_primary_infores['input_node'].values[i]

        oupput_node = result_ranked_by_primary_infores['output_node'].values[i]
        names.append(oupput_node)
        type_of_node = result_ranked_by_primary_infores['type_of_nodes'].values[i]
        if type_of_node == 'object':
            subject = input_query
            object = oupput_node
        else:
            subject = oupput_node
            object = input_query
        new_id = subject + "_" + object

        cur_primary_infore = result_parsed[new_id]['primary_knowledge_source']
        for predict in primary_infore_list:
            if predict in cur_primary_infore:
                primary_infore_by_nodes[predict].append(1)
            else:
                primary_infore_by_nodes[predict].append(0)



        cur_predicates = result_parsed[new_id]['predicate']
        for predict in predicates_list:
            if predict in cur_predicates:
                predicates_by_nodes[predict].append(1)
            else:
                predicates_by_nodes[predict].append(0)

    #convert = False

    #for item in colnames:
    #    if 'NCBIGene' in item:
    #        convert = True
    #if convert:
        #Gene_id_map = Gene_id_converter(colnames, "http://127.0.0.1:8000/query_name_by_id") # option 1
        #Gene_id_map = Generate_Gene_id_map() # option 2

    dic_id_map = ID_convert_to_preferred_name_nodeNormalizer(names)
    new_colnames = []
    for item in names:
        if item in dic_id_map:
            new_colnames.append(dic_id_map[item])
        else:
            new_colnames.append(item)    

    #else:
    #    new_colnames = colnames
            
    primary_infore_by_nodes_df = pd.DataFrame(primary_infore_by_nodes)
    primary_infore_by_nodes_df.index = new_colnames
    primary_infore_by_nodes_df = primary_infore_by_nodes_df.T


    predicates_by_nodes_df = pd.DataFrame(predicates_by_nodes)
    predicates_by_nodes_df.index = new_colnames
    predicates_by_nodes_df = predicates_by_nodes_df.T

    plot_heatmap(primary_infore_by_nodes_df, num_of_nodes, fontsize, title_fontsize,output_png1)
    plot_heatmap(predicates_by_nodes_df, num_of_nodes, fontsize, title_fontsize,output_png2)

    return(predicates_by_nodes_df)

# Used. Jan 5, 2024
def visulization_one_hop_ranking(result_ranked_by_primary_infores,result_parsed , 
                                 num_of_nodes = 20, 
                                 input_query = "NCBIGene:3845",
                                 fontsize = 6,
                                 title_fontsize = 12,
                                 output_png1="NE_heatmap1.png",
                                 output_png2="NE_heatmap2.png"
                                 ):
    # edited Dec 5, 2023
    predicates_list = []
    primary_infore_list = []
    aggregator_infore_list = []

    from io import BytesIO
    for i in range(0, result_ranked_by_primary_infores.shape[0]):
        oupput_node = result_ranked_by_primary_infores['output_node'][i]
        type_of_node = result_ranked_by_primary_infores['type_of_nodes'][i]
        if type_of_node == 'object':
            subject = input_query
            object = oupput_node
        else:
            subject = oupput_node
            object = input_query
            
        predicates_list = predicates_list + result_parsed[subject + "_" + object]['predicate']
        primary_infore_list = primary_infore_list + result_parsed[subject + "_" + object]['primary_knowledge_source']
        
        if 'aggregator_knowledge_source' in result_parsed[subject + "_" + object]:
            aggregator_infore_list = aggregator_infore_list + result_parsed[subject + "_" + object]['aggregator_knowledge_source']
            aggregator_infore_list = list(set(aggregator_infore_list))

        predicates_list = list(set(predicates_list))
        primary_infore_list = list(set(primary_infore_list))
        

    predicates_by_nodes = {}
    for predict in predicates_list:
        predicates_by_nodes[predict] = []

    primary_infore_by_nodes = {}
    for predict in primary_infore_list:
        primary_infore_by_nodes[predict] = []

    aggregator_infore_by_nodes = {}
    for predict in aggregator_infore_list:
        aggregator_infore_by_nodes[predict] = []
        
    names = []
    for i in range(0, result_ranked_by_primary_infores.shape[0]):
    #for i in range(0, 10):
        oupput_node = result_ranked_by_primary_infores['output_node'].values[i]
        names.append(oupput_node)
        type_of_node = result_ranked_by_primary_infores['type_of_nodes'].values[i]
        if type_of_node == 'object':
            subject = input_query
            object = oupput_node
        else:
            subject = oupput_node
            object = input_query
        new_id = subject + "_" + object

        cur_primary_infore = result_parsed[new_id]['primary_knowledge_source']
        for predict in primary_infore_list:
            if predict in cur_primary_infore:
                primary_infore_by_nodes[predict].append(1)
            else:
                primary_infore_by_nodes[predict].append(0)



        cur_predicates = result_parsed[new_id]['predicate']
        for predict in predicates_list:
            if predict in cur_predicates:
                predicates_by_nodes[predict].append(1)
            else:
                predicates_by_nodes[predict].append(0)

    #convert = False

    #for item in colnames:
    #    if 'NCBIGene' in item:
    #        convert = True
    #if convert:
        #Gene_id_map = Gene_id_converter(colnames, "http://127.0.0.1:8000/query_name_by_id") # option 1
        #Gene_id_map = Generate_Gene_id_map() # option 2

    dic_id_map = ID_convert_to_preferred_name_nodeNormalizer(names)
    new_colnames = []
    for item in names:
        if item in dic_id_map:
            new_colnames.append(dic_id_map[item])
        else:
            new_colnames.append(item)    

    #else:
    #    new_colnames = colnames
            
    primary_infore_by_nodes_df = pd.DataFrame(primary_infore_by_nodes)
    primary_infore_by_nodes_df.index = new_colnames
    primary_infore_by_nodes_df = primary_infore_by_nodes_df.T


    predicates_by_nodes_df = pd.DataFrame(predicates_by_nodes)
    predicates_by_nodes_df.index = new_colnames
    predicates_by_nodes_df = predicates_by_nodes_df.T

    plot_heatmap(primary_infore_by_nodes_df, num_of_nodes, fontsize, title_fontsize,output_png1)
    plot_heatmap(predicates_by_nodes_df, num_of_nodes, fontsize, title_fontsize,output_png2)

    return(predicates_by_nodes_df)

def plot_heatmap(predicates_by_nodes_df,num_of_nodes = 20, 
                                 fontsize = 6,
                                 title_fontsize = 10, 
                                 output_png="NE_heatmap.png"):
    #matplotlib.use('Agg')
    
    title = "Ranking of one-hop nodes by primary infores"
    ylab = "infores"
    df = predicates_by_nodes_df.iloc[:,0:num_of_nodes]
    colnames = list(df.columns)
    # create teh figure and subplot
    fig = plt.figure( figsize=(0.8+df.shape[1]*0.1,3.5),dpi = 300)
    ax = fig.add_subplot(111)

    # create the heatmap
    # heatmap with border
    p1 = sns.heatmap(df, cmap="Blues", cbar=False, ax=ax, linecolor='grey', linewidth=0.2)

    p1.set_title(title)
    p1.set_ylabel(ylab)
    print(p1.get_xticklabels())
    # set xticklabels with colnames

    #p1.set_xticklabels(colnames, rotation=90, fontsize = fontsize)
    plt.xticks(ticks=range(len(df.columns)), labels=df.columns)

        # set title font size
    p1.title.set_size(title_fontsize)
    plt.show()
    # save the figure
    #plt.savefig(output_png, bbox_inches='tight', dpi=300)



def plot_heatmap_ui(predicates_by_nodes_df,num_of_nodes = 20, 
                                 fontsize = 6,
                                 title_fontsize = 10, 
                                 output_png="NE_heatmap.png"):
   
    
    title = "Ranking of one-hop nodes by primary infores"
    ylab = "infores"
    df = predicates_by_nodes_df.iloc[:,0:num_of_nodes]
    colnames = list(df.columns)
    # create teh figure and subplot
    fig = plt.figure( figsize=(0.8+df.shape[1]*0.1,3.5),dpi = 100)
    ax = fig.add_subplot(111)

    # create the heatmap
    # heatmap with border
    p1 = sns.heatmap(df, cmap="Blues", cbar=False, ax=ax, linecolor='grey', linewidth=0.2)

    p1.set_title(title)
    p1.set_ylabel(ylab)
    print(p1.get_xticklabels())
    # set xticklabels with colnames

    #p1.set_xticklabels(colnames, rotation=90, fontsize = fontsize)
    plt.xticks(ticks=range(len(df.columns)), labels=df.columns)

        # set title font size
    p1.title.set_size(title_fontsize)
   # plt.show()
    # save the figure
    plt.savefig(output_png, bbox_inches='tight', dpi=300)


# used. Dec 5, 2023  (Example_query_one_hop_with_category.ipynb)
def Gene_id_converter(id_list, API_url):
    id_list_new = []
    for id in id_list:
        if id.startswith("NCBIGene:"):
            id = id.replace("NCBIGene:", "NCBIGene")
            id_list_new.append(id)
    query_json = {
                    "message": {
                        "query_graph": {
                        "nodes": {
                            "n0": {
                            "categories": ["Gene"],
                            "ids": id_list_new
                            },
                            "n1": {
                            "categories": [
                                "string"
                            ],
                            "ids": [
                                "string"
                            ]
                            }
                        },
                        "edges": {
                            "e1": {
                            "predicates": [
                                "string"
                            ]
                            }
                        }
                        }
                    }
                    }

    response = requests.post(API_url, json=query_json)
    result = {}

    if response.status_code == 200:
        result = response.json()

    return(result)


# used. Dec 5, 2023 (Example_query_one_hop_with_category.ipynb)
def format_query_json(subject_ids, object_ids, subject_categories, object_categories, predicates):
    '''
    Example input:
    subject_ids = ["NCBIGene:3845"]
    object_ids = []
    subject_categories = ["biolink:Gene"]
    object_categories = ["biolink:Gene"]
    predicates = ["biolink:positively_correlated_with", "biolink:physically_interacts_with"]

    '''
    #edited Dec 5, 2023
    query_json_temp = {
        "message": {
            "query_graph": {
                "nodes": {
                    "n0": {
                        "ids":[],
                        "categories":[]
                    },
                    "n1": {
                        #"ids":[],
                        "categories":[]
                }
                },
                "edges": {
                    "e1": {
                        "subject": "n0",
                        "object": "n1",
                        "predicates": predicates
                    }
                }
            }
        }
    }

    if len(subject_ids) > 0:
        query_json_temp["message"]["query_graph"]["nodes"]["n0"]["ids"] = subject_ids
    if len(object_ids) > 0:
        query_json_temp["message"]["query_graph"]["nodes"]["n1"]["ids"] = object_ids

    if len(subject_categories) > 0:
        query_json_temp["message"]["query_graph"]["nodes"]["n0"]["categories"] = subject_categories

    if len(object_categories) > 0:
        query_json_temp["message"]["query_graph"]["nodes"]["n1"]["categories"] = object_categories

    if len(predicates) > 0:
        query_json_temp["message"]["query_graph"]["edges"]["e1"]["predicates"] = predicates

    return(query_json_temp)

# used. Dec 5, 2023 (Example_query_one_hop_with_category.ipynb)
def query_KP(remoteURL, query_json):
    # Single query
    response = requests.post(remoteURL, json=query_json)
    #print(response.status_code)
    if response.status_code == 200:
        #print(response.json())[0]
        if "message" in response.json():
            result = response.json()["message"]
            #print(result) # revised Dec 1, 2023
            if "knowledge_graph" in result:
                #return(result['knowledge_graph'])
                print("Success!" + remoteURL)
                return(result)
                
            else:
                print("Warning:" + remoteURL + "no knowledge_graph in response.")
                return()
        else:
            print("Warning:" + remoteURL + "no message in response.")
            return()
    else:
        print("Warning Code:" + str(response.status_code) + ":" +remoteURL  )
        return()
    
# used. Dec 5, 2023 (Example_query_one_hop_with_category.ipynb)
def parallel_api_query(URLS, query_json, max_workers=1):
    # Parallel query
    result = []
    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(query_KP, url, query_json): url for url in URLS}

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                if 'knowledge_graph' in data:
                    result.append(data)
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
    
    included_KP_ID = []
    for i in range(0,len(result)):
        if result[i]['knowledge_graph'] is not None:
            if 'knowledge_graph' in result[i]:
                if 'edges' in result[i]['knowledge_graph']:
                    if len(result[i]['knowledge_graph']['edges']) > 0:
                        included_KP_ID.append(i)

    result_merged = {}
    for i in included_KP_ID:
        result_merged = {**result_merged, **result[i]['knowledge_graph']['edges']}

    len(result_merged)

    return(result_merged)

# used. Dec 5, 2023    (Example_query_one_hop_with_category.ipynb)
def parse_KG(result):
    '''
    subject_object
    subject
    object
    predicate
    primary_knowledge_sources
    aggregator_knowledge_sources
    subject_predicate_object_primary_knowledge_sources_aggregator_knowledge_sources
    
    '''
    # edited Dec 5, 2023

    result_parsed = {}
    for i in result:
        
        subject_object = result[i]['subject'] + "_" + result[i]['object']
        object_subject = result[i]['object'] + "_" + result[i]['subject']
        #result_parsed["predicate"].append(result[i]['predicate'])
        #result_parsed["sources"].append(result[i]['sources'])
        #result_parsed["subject"].append(result[i]['subject'])
        #result_parsed["object"].append(result[i]['object'])
        if subject_object not in result_parsed:
            result_parsed[subject_object] = {}
            result_parsed[subject_object]['predicate'] = [result[i]['predicate']]
            result_parsed[subject_object]['subject'] = result[i]['subject']
            result_parsed[subject_object]['object'] = result[i]['object']
            
            
            for j in result[i]['sources']:
                if j['resource_role'] == 'primary_knowledge_source':
                    result_parsed[subject_object]['primary_knowledge_source'] = [j['resource_id']]

                evidence =  result[i]['subject'] + "_" + result[i]['predicate'] + "_" + result[i]['object'] + "_" + j['resource_id']

                if j['resource_role'] == 'aggregator_knowledge_source':
                    result_parsed[subject_object]['aggregator_knowledge_source'] = [j['resource_id']]
                    evidence = evidence + "_" + j['resource_id']
            result_parsed[subject_object]['evidence'] = [evidence]

        else: # subject_object in result_parsed:
            result_parsed[subject_object]['predicate'].append(result[i]['predicate'])
            for j in result[i]['sources']:
                if j['resource_role'] == 'primary_knowledge_source':
                    result_parsed[subject_object]['primary_knowledge_source'].append(j['resource_id'])
                    evidence =  result[i]['subject'] + "_" + result[i]['predicate'] + "_" + result[i]['object'] + "_" + j['resource_id']
                if j['resource_role'] == 'aggregator_knowledge_source':
                    if 'aggregator_knowledge_source' not in result_parsed[subject_object]:
                        result_parsed[subject_object]['aggregator_knowledge_source'] = [j['resource_id']]
                    else:
                        result_parsed[subject_object]['aggregator_knowledge_source'].append(j['resource_id'])
                    evidence = evidence + "_" + j['resource_id']
            result_parsed[subject_object]['evidence'].append(evidence)

    return(result_parsed)


# parse network results. Dec 10, 2023
def parse_network_result(result, input_node1_list):
    dic_nodes = {}
    for i in result:
        subject = result[i]['subject']
        object = result[i]['object']
        predicate = result[i]['predicate']
        sources = result[i]['sources']

        if subject == object:
            continue
        
        if subject in dic_nodes:
            dic_nodes[subject].append(object)
        else:
            dic_nodes[subject] = [object]
        
        if object in dic_nodes:
            dic_nodes[object].append(subject)
        else:
            dic_nodes[object] = [subject]



    dic_remain_nodes = {}

    dic_with_input_nodes = {}

    for i in dic_nodes:
        if i in input_node1_list:
            dic_remain_nodes[i] = dic_nodes[i]
        else:
            continue

    for i in dic_remain_nodes:
        for j in dic_nodes[i]:
            if j in dic_with_input_nodes:
                dic_with_input_nodes[j].append(i)
            else:
                dic_with_input_nodes[j] = [i]

    for i in dic_with_input_nodes:
        dic_with_input_nodes[i] = list(set(dic_with_input_nodes[i]))
            



    for i in dic_with_input_nodes:
        if len(set(dic_with_input_nodes[i])) > 1: #
            #print(i, set(dic_with_input_nodes[i]))
            if i not in dic_remain_nodes:
                dic_remain_nodes[i] = dic_with_input_nodes[i]
        else:
            continue

    dic_remain_nodes_final = {}
    for i in dic_remain_nodes:
        dic_remain_nodes_final[i] = set(dic_remain_nodes[i]).intersection(set(dic_remain_nodes.keys()))


    subject_nodes = []
    object_nodes = []

    for i in dic_remain_nodes_final:
        for j in dic_remain_nodes_final[i]:
            subject_nodes.append(i)
            object_nodes.append(j)

    result_df = pd.DataFrame({'Subject':subject_nodes, 'Object':object_nodes})
    #result_df.to_csv('result_df.csv', index=False)
    return result_df

def rank_by_primary_infores_input_as_list(result_parsed, input_nodes):
    ''' Editd Dec 5, 2023'''
    rank_df = pd.DataFrame()
    output_nodes = []
    input_nodes_list = []
    Num_of_primary_infores = []
    type_of_nodes   = []
    unique_predicates = []
    for i in result_parsed:
        curr_predict = result_parsed[i]['predicate']
        subject = result_parsed[i]['subject']
        object = result_parsed[i]['object']

        if subject in input_nodes:
            input_nodes_list.append(subject)
            output_nodes.append(object)
            type_of_nodes.append('object')
            Num_of_primary_infores.append(len(set(result_parsed[i]['primary_knowledge_source'])))
            unique_predicates.append(curr_predict)
            

        elif object in input_nodes:
            input_nodes_list.append(object)
            output_nodes.append(subject)
            type_of_nodes.append('subject')
            unique_predicates.append(curr_predict)
        
            Num_of_primary_infores.append(len(set(result_parsed[i]['primary_knowledge_source'])))

    colnames = output_nodes
    names = colnames
    dic_id_map = ID_convert_to_preferred_name_nodeNormalizer(names)
    new_colnames = []
    for item in names:
        if item in dic_id_map:
            new_colnames.append(dic_id_map[item])
        else:
            new_colnames.append(item)   

    rank_df['output_node'] = output_nodes
    rank_df['Name'] = new_colnames
    rank_df['Num_of_primary_infores'] = Num_of_primary_infores
    rank_df['type_of_nodes'] = type_of_nodes
    rank_df['unique_predicates'] = unique_predicates
    
    rank_df['input_node'] = input_nodes_list
    
    rank_df_ranked = rank_df.sort_values(by=['Num_of_primary_infores'], ascending=False)
    return(rank_df_ranked)



# parse results to a dictionary. Dec 5, 2023
# used. Dec 5, 2023 (Example_query_one_hop_with_category.ipynb)
def rank_by_primary_infores(result_parsed, input_node):
    ''' Editd Dec 5, 2023'''
    rank_df = pd.DataFrame()
    output_nodes = []
    Num_of_primary_infores = []
    type_of_nodes   = []
    unique_predicates = []
    for i in result_parsed:
        curr_predict = result_parsed[i]['predicate']
        subject = result_parsed[i]['subject']
        object = result_parsed[i]['object']

        if subject == input_node:
            output_nodes.append(object)
            type_of_nodes.append('object')
            Num_of_primary_infores.append(len(set(result_parsed[i]['primary_knowledge_source'])))
            unique_predicates.append(curr_predict)
            

        elif object == input_node:
            output_nodes.append(subject)
            type_of_nodes.append('subject')
            unique_predicates.append(curr_predict)
        
            Num_of_primary_infores.append(len(set(result_parsed[i]['primary_knowledge_source'])))

    colnames = output_nodes
    names = colnames
    dic_id_map = ID_convert_to_preferred_name_nodeNormalizer(names)
    new_colnames = []
    for item in names:
        if item in dic_id_map:
            new_colnames.append(dic_id_map[item])
        else:
            new_colnames.append(item)   

    rank_df['output_node'] = output_nodes
    rank_df['Name'] = new_colnames
    rank_df['Num_of_primary_infores'] = Num_of_primary_infores
    rank_df['type_of_nodes'] = type_of_nodes
    rank_df['unique_predicates'] = unique_predicates
    
    
    
    rank_df_ranked = rank_df.sort_values(by=['Num_of_primary_infores'], ascending=False)
    return(rank_df_ranked)



# used. Dec 5, 2023 (Example_query_rank_the_path.ipynb)
def merge_by_ranking_index(result_ranked_by_primary_infores,
                           result_ranked_by_primary_infores2, 
                           top_n = 20,
                           title_fontsize = 12,
                           fontsize = 12,
                           ):

    
    dic_rank1 = {}
    for i in range(0, result_ranked_by_primary_infores.shape[0]):
        dic_rank1[result_ranked_by_primary_infores['output_node'][i]] = 1 - i / result_ranked_by_primary_infores.shape[0]

    dic_rank2 = {}
    for i in range(0, result_ranked_by_primary_infores2.shape[0]):
        dic_rank2[result_ranked_by_primary_infores2['output_node'][i]] = 1 - i / result_ranked_by_primary_infores2.shape[0]

    merged_nodes = set(dic_rank1.keys()).intersection(set(dic_rank2.keys()))
    dic_merged_rank = {}

    for node in merged_nodes:
        dic_merged_rank[node] = dic_rank1[node] * dic_rank2[node]

    result_ranked = pd.DataFrame.from_dict(dic_merged_rank, orient='index', columns=['score'])
    result_ranked = result_ranked.sort_values(by=['score'], ascending=False)
    result_ranked = result_ranked.reset_index()
    result_ranked.columns = ['output_node', 'score']
    result_xy_sorted = result_ranked
    result_xy_sorted.index = result_ranked['output_node']

    #convert = False
    colnames = result_xy_sorted.index.to_list()
    names = colnames
    dic_id_map = ID_convert_to_preferred_name_nodeNormalizer(names)
    new_colnames = []
    for item in names:
        if item in dic_id_map:
            new_colnames.append(dic_id_map[item])
        else:
            new_colnames.append(item)   

    result_xy_sorted.index = new_colnames
    result_xy_sorted = result_xy_sorted.sort_values(by=['score'], ascending=False)

    sns.set(style="whitegrid")
    plt.figure(figsize=(5,5), dpi = 300)
    ax = sns.barplot(x=result_xy_sorted.iloc[0:top_n].index, y=result_xy_sorted.iloc[0:top_n]['score'], color='grey')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha="center", fontsize=fontsize)
    ax.set_ylabel("Ranking score")
    ax.title.set_size(title_fontsize)
    plt.tight_layout()
    #plt.show()

    return result_xy_sorted



def merge_ranking_by_number_of_infores(result_ranked_by_primary_infores, 
                                       result_ranked_by_primary_infores1, 
                                       top_n = 30,
                                       fontsize = 12,
                                       title_fontsize = 12,
                                       output_png = "NE_heatmap.png"
                                       ):
    overlapped = (set(result_ranked_by_primary_infores1['output_node']).intersection(set(result_ranked_by_primary_infores['output_node'])))
    x = result_ranked_by_primary_infores.loc[result_ranked_by_primary_infores['output_node'].isin(overlapped)]
    y = result_ranked_by_primary_infores1.loc[result_ranked_by_primary_infores1['output_node'].isin(overlapped)]
    dic_x = {}
    for i in range(x.shape[0]):
        dic_x[x.iloc[i]['output_node']] = x.iloc[i]['Num_of_primary_infores']/np.max(x['Num_of_primary_infores'])

    dic_y = {}
    for i in range(y.shape[0]):
        dic_y[y.iloc[i]['output_node']] = y.iloc[i]['Num_of_primary_infores']/np.max(y['Num_of_primary_infores'])

    predicts_list1 = []
    predicts_list2 = []
    dic_xy = {}
    for i in overlapped:
        #print(result_ranked_by_primary_infores[result_ranked_by_primary_infores['output_node'] == i]['unique_predicates'])
        dic_xy[i] = dic_x[i] * dic_y[i]
        predicts_list1.append('\n'.join(list(set(result_ranked_by_primary_infores[result_ranked_by_primary_infores['output_node'] == i]['unique_predicates'].values[0]))))
        predicts_list2.append('\n'.join(list(result_ranked_by_primary_infores1[result_ranked_by_primary_infores1['output_node'] == i]['unique_predicates'].values[0])))

    result_xy = pd.DataFrame.from_dict(dic_xy, orient='index', columns=['score'])
    result_xy['output_node'] = result_xy.index
    # convert the output_node to preferred name

    
        
    #result_xy["output_node_name"] = new_colnames
    result_xy['predictes1'] = predicts_list1
    result_xy['predictes2'] = predicts_list2

    result_xy_sorted = result_xy.sort_values(by=['score'], ascending=False)

    convert = False
    colnames = result_xy_sorted.index.to_list()

    names = colnames
    dic_id_map = ID_convert_to_preferred_name_nodeNormalizer(names)
    new_colnames = []
    for item in names:
        if item in dic_id_map:
            new_colnames.append(dic_id_map[item])
        else:
            new_colnames.append(item)   


    result_xy_sorted.index = new_colnames
    result_xy_sorted['output_node_name'] = new_colnames
    x = result_xy_sorted.iloc[0:top_n].index
    y = result_xy_sorted.iloc[0:top_n]['score']

    plot_path_bar(x,y,fontsize, title_fontsize, output_png=output_png)

    return result_xy_sorted

def plot_path_bar(x,
                  y,
                    fontsize = 8,
                    title_fontsize = 10, 
                    output_png="NE_heatmap.png"):
    matplotlib.use('Agg')
    
    title = "Bridging nodes"
    fig = plt.figure(figsize=(5,5), dpi = 300)
    ax = fig.add_subplot(111)
    ax = sns.barplot(x=x, y=y, color='grey')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha="center", fontsize=fontsize)
    ax.set_ylabel("Ranking score")
    ax.title.set_size(title_fontsize)
    # save the figure
    plt.savefig(output_png, bbox_inches='tight', dpi=300)


# Sri-name-resolver  Used Dec 5, 2023 (Example_query_one_hop_with_category.ipynb)
def get_curie(name):
    response = requests.get("https://name-lookup.transltr.io/lookup", params={
        'string': name,
        'autocomplete': False
    })
    if response.status_code == 200:
        result = response.json()
        if len(result) != 0:
            return(result[0]['curie'])
        else:
            return(name)
    else:
        return(name)

# annotate gene pairs or a list of genes. Feb 25, 2024
def get_pair_annotation(result, input_node_list):
    pairs_found = {}
    for i in result.keys():
        
        if result[i]['subject'] in input_node_list and result[i]['object'] in input_node_list and result[i]['subject'] != result[i]['object']:
            pairs_found[i] = result[i]
    return pairs_found


def parse_pair_annotation(pairs_found, input_node_list):
    edge_list = []
    names = ID_convert_to_preferred_name_nodeNormalizer(input_node_list)
    dic_names = {}
    for i in input_node_list:
        dic_names[i] = names[i]

    for i in pairs_found.keys():
        primary_source = ''
        for source in pairs_found[i]['sources']:
            if source['resource_role'] == 'primary_knowledge_source':
                primary_source = source['resource_id']
                break
        edge_list.append([pairs_found[i]['subject'],dic_names[pairs_found[i]['subject']],  pairs_found[i]['predicate'], pairs_found[i]['object'], dic_names[pairs_found[i]['object']], primary_source ])
    return edge_list

#used

def query_chatGPT4(customized_input):
    message=[{"role": "user", 
            "content": customized_input}]

    response = openai.ChatCompletion.create(
    #model="gpt-3.5-turbo",
    model="gpt-4",
    max_tokens=1000,
    temperature=1.2,
    messages = message)

    #print(len(response.choices[0].message.content.split(" ")))

    return(response.choices[0].message.content)

def query_chatGPT(customized_input):
    message=[{"role": "user", 
            "content": customized_input}]

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    #model="gpt-4",
    max_tokens=1000,
    temperature=1.2,
    messages = message)

    #print(len(response.choices[0].message.content.split(" ")))

    return(response.choices[0].message.content)

# to be removed
def query_KP_all(subject_ids, object_ids, subject_categories, object_categories, predicates, API_list,metaKG, APInames):

    #APInames = API_list
    if len(API_list) == 0:
        API_list = select_API(subject_categories,object_categories,metaKG)
    else:
        API_list = list(APInames.keys())

    result_dict = {}
    result_concept = {}
    # Query individual KP
    
    # Needs parallel query
    

    for API_sele in API_list:
        print(API_sele)
        if len(predicates)==0:
            predicates_used = select_predicates_inKP(subject_categories,object_categories,API_sele,metaKG)
        else:
            predicates_used = predicates
        
        query_json = format_query_json(subject_ids, object_ids, subject_categories, object_categories, predicates_used)

        print(query_json)
        try:
            kg_output = query_KP(APInames[API_sele],query_json)
            
        except:
            print("Connection Error")
            kg_output = None
            
        if kg_output is not None:
            # if kg_output is  a dictionary

            if type(kg_output) == dict and 'nodes' in kg_output.keys():
                if len(kg_output['nodes']) >0:

                    print("Found: " + str(len(kg_output['edges'].keys())) + " nodes in " + API_sele) 
                    print(predicates_used)
                    result_concept[API_sele] = predicates_used
                    result_dict[API_sele] = kg_output
    return(result_dict, result_concept)

# to be removed
def format_query_json_old(subject_ids, object_ids, subject_categories, object_categories, predicates):
    '''
    Example input:
    subject_ids = ["NCBIGene:3845"]
    object_ids = []
    subject_categories = ["biolink:Gene"]
    object_categories = ["biolink:Gene"]
    predicates = ["biolink:positively_correlated_with", "biolink:physically_interacts_with"]

    '''
    query_json_temp = {
        "message": {
            "query_graph": {
                "nodes": {
                    "n0": {
                        "ids":[],
                        "categories":[]
                    },
                    "n1": {
                        "categories":[]
                }
                },
                "edges": {
                    "e1": {
                        "subject": "n0",
                        "object": "n1",
                        "predicates": predicates
                    }
                }
            }
        }
    }

    if len(subject_ids) > 0:
        query_json_temp["message"]["query_graph"]["nodes"]["n0"]["ids"] = subject_ids
    if len(object_ids) > 0:
        query_json_temp["message"]["query_graph"]["nodes"]["n1"]["ids"] = object_ids

    if len(subject_categories) > 0:
        query_json_temp["message"]["query_graph"]["nodes"]["n0"]["categories"] = subject_categories

    if len(object_categories) > 0:
        query_json_temp["message"]["query_graph"]["nodes"]["n1"]["categories"] = object_categories

    if len(predicates) > 0:
        query_json_temp["message"]["query_graph"]["edges"]["e1"]["predicates"] = predicates

    return(query_json_temp)

# to be removed
def parse_result_old( API_keys_sele, API_keys_Not_include, predicates_forAnalysis,result_dic):
    Temp_APIkey = []
    Temp_subject_key = []
    Temp_object_key = []
    Temp_predicate_key = []
    Temp_infores_key = []
    API_keys_forAnalysis = []

    ALL_APIs_in_result = list(result_dic.keys())
    print(ALL_APIs_in_result)

    if len(API_keys_sele) == 0:
        API_keys_forAnalysis = ALL_APIs_in_result
    else:
        API_keys_forAnalysis = list(set(ALL_APIs_in_result).intersection(set(API_keys_sele)))

    if len(API_keys_Not_include) != 0:
        API_keys_forAnalysis = list(set(API_keys_forAnalysis) - set(API_keys_Not_include))


    print(API_keys_forAnalysis)

    for API_key in API_keys_forAnalysis:
        cur_API_outputKeys = list(result_dic[API_key]['edges'].keys())
        for i in range(0, len(cur_API_outputKeys)):
            curr_key = i
            curr_graph = (result_dic[API_key]['edges'][cur_API_outputKeys[curr_key]])
            predicate = (curr_graph['predicate'])
            if predicate != "biolink:subclass_of":
                infores = (curr_graph['sources'][0]['resource_id'])
                subject = (curr_graph['subject'])

                if subject.startswith("CL:"):
                    subject = "CL" + subject.split(":")[1]

                object = (curr_graph['object'])
                if object.startswith("CL:"):
                    object = "CL" + object.split(":")[1]
                
                #exclude subclass_of
                
                Temp_APIkey.append(API_key)
                Temp_subject_key.append(subject)
                Temp_object_key.append(object)
                Temp_predicate_key.append(predicate)
                Temp_infores_key.append(infores)
            
            #Temp_APIkey.append(API_key)
            #Temp_subject_key.append(subject)
            #Temp_object_key.append(object)
            #Temp_predicate_key.append(predicate)
            #Temp_infores_key.append(infores)

    Temp_result_df = pd.DataFrame({'API': Temp_APIkey, 
                                   'Subject': Temp_subject_key,
                                   "Object":Temp_object_key, 
                                   "Predicate":Temp_predicate_key, 
                                   "Infores":Temp_infores_key})

    Temp_result_df.drop_duplicates(inplace=True)
    Temp_result_df = Temp_result_df.loc[Temp_result_df['API'].isin(API_keys_forAnalysis)]

    if len(predicates_forAnalysis) != 0:
        Temp_result_df = Temp_result_df.loc[Temp_result_df['Predicate'].isin(predicates_forAnalysis)]
    return(Temp_result_df)

# to be removed
def ranking_result_by_predicates_object(Temp_result_df):
    object_val_list = Temp_result_df['Object'].value_counts().index.tolist()
    object_val_value = Temp_result_df['Object'].value_counts().values.tolist()

    
    dic_rank = {}
    for i in range(0,len(object_val_list)):
        dic_rank[object_val_list[i]] = object_val_value[i]
  

    sorted_dic = sorted(dic_rank.items(), key=lambda x: x[1], reverse=True)
    return(sorted_dic)

# to be removed
def ranking_result_by_predicates_subject(Temp_result_df):
    subject_val_list = Temp_result_df['Subject'].value_counts().index.tolist()
    subject_val_list = Temp_result_df['Subject'].value_counts().values.tolist()

    dic_rank = {}
    for i in range(0,len(subject_val_list)):
        dic_rank[subject_val_list[i]] = subject_val_list[i]
  

    sorted_dic = sorted(dic_rank.items(), key=lambda x: x[1], reverse=True)
    return(sorted_dic)


# to be removed
def get_ranking_by_predicates(sorted_dic, Temp_result_df, Top):
    #item_ranking = []
    dic_ranking = {}

    if Top > len(sorted_dic):
        Top = len(sorted_dic)

    for i in range(1,Top):
        #item_ranking.append(sorted_dic[i][0])
        sele_result = sorted_dic[i][0]
        dic_ranking[sorted_dic[i][0]] = list(set(list(pd.concat([Temp_result_df.loc[Temp_result_df['Object'].isin([sele_result])], Temp_result_df.loc[Temp_result_df['Subject'].isin([sele_result])]], axis=0)['Predicate'])))
    
    return(dic_ranking)

# to be removed
def get_ranking_by_infores(sorted_dic, Temp_result_df, Top):
    #item_ranking = []
    dic_ranking = {}

    if Top > len(sorted_dic):
        Top = len(sorted_dic)

    for i in range(1,Top):
        #item_ranking.append(sorted_dic[i][0])
        sele_result = sorted_dic[i][0]
        dic_ranking[sorted_dic[i][0]] = list(set(list(pd.concat([Temp_result_df.loc[Temp_result_df['Object'].isin([sele_result])], Temp_result_df.loc[Temp_result_df['Subject'].isin([sele_result])]], axis=0)['Infores'])))
    
    return(dic_ranking)

# to be removed
def get_ranking_by_kp(sorted_dic, Temp_result_df, Top):
    #item_ranking = []
    dic_ranking = {}

    if Top > len(sorted_dic):
        Top = len(sorted_dic)

    for i in range(1,Top):
        #item_ranking.append(sorted_dic[i][0])
        sele_result = sorted_dic[i][0]
        dic_ranking[sorted_dic[i][0]] = list(set(list(pd.concat([Temp_result_df.loc[Temp_result_df['Object'].isin([sele_result])], Temp_result_df.loc[Temp_result_df['Subject'].isin([sele_result])]], axis=0)['API'])))
    
    return(dic_ranking)

# to be revised
def connecting_two_dots_two_hops(sorted_dic1, sorted_dic):
    intermediate = []
    normalized_rank = []

    rank1 = 0
    for i in sorted_dic1:
        gene1 = i[0]

        rank1 = rank1 + 1
        rank2 = 0
        for j in sorted_dic:
            gene2 = j[0]
            rank2 = rank2 + 1
            if gene1 == gene2:
                normlized_rank1 = rank1/(len(sorted_dic1) -1)
                normlized_rank2 = rank2/(len(sorted_dic) -1)
                new_order = normlized_rank1 * normlized_rank2
                intermediate.append(gene2)
                normalized_rank.append(new_order)

    res_df = pd.DataFrame({"node":intermediate, "normalized_rank":normalized_rank})
    res_df.sort_values(by=['normalized_rank'], inplace=True, ascending=True)
    res_df.reset_index(inplace=True, drop=True)

    return(res_df)

def select_result_to_analysis(sele_genes,Temp_result_df, Temp_result_df1 ):
    
    print(sele_genes)
    for_plot = pd.concat([Temp_result_df1.loc[Temp_result_df1['Object'].isin(sele_genes)],
            Temp_result_df.loc[Temp_result_df['Object'].isin(sele_genes)]], axis=0)

    return(for_plot)

# need revision
def find_path_by_two_ends(subject1_ids, 
                          subject1_categories, 
                          predicates1,
                          object_categories,
                          subject2_ids, 
                          subject2_categories,
                          predicates2,
                          API_list1,
                          API_list2,
                          API1_keys_forAnalysis,
                          API1_keys_NotforAnalysis,
                          API2_keys_forAnalysis,
                          API2_keys_NotforAnalysis,
                          metaKG,
                          APInames
                          ):
    
    result_dic_node1, result_concept_node1 = query_KP_all(subject1_ids, [], subject1_categories, object_categories, predicates1, API_list1, metaKG, APInames)
    result_dic_node2, result_concept_node2 = query_KP_all(subject2_ids, [], subject2_categories, object_categories, predicates2, API_list2, metaKG, APInames)

    
    Temp_result_df1 = parse_result(API1_keys_forAnalysis,API1_keys_NotforAnalysis, result_concept_node1, result_dic_node1)
    sorted_dic1 = ranking_result_by_predicates_object(Temp_result_df1)

    dic_ranking1 = get_ranking_by_infores(sorted_dic1, Temp_result_df1, 20)

    Temp_result_df2 = parse_result(API2_keys_forAnalysis,API2_keys_NotforAnalysis, result_concept_node2, result_dic_node2)
    sorted_dic2 = ranking_result_by_predicates_object(Temp_result_df2)

    dic_ranking2 = get_ranking_by_infores(sorted_dic2, Temp_result_df2, 20)
    
    connection_nodes_df = connecting_two_dots_two_hops(sorted_dic1, sorted_dic2)

    # bind all results in to a dictionary
    result = {"connection_nodes_df":connection_nodes_df,
              "dic_ranking1":dic_ranking1,
              "dic_ranking2":dic_ranking2,
              "Temp_result_df1":Temp_result_df1,
              "Temp_result_df2":Temp_result_df2,
              "result_dic_node1":result_dic_node1,
              "result_dic_node2":result_dic_node2,
              "result_concept_node1":result_concept_node1,
              "result_concept_node2":result_concept_node2}

    #return(connection_nodes_df, dic_ranking1, dic_ranking2, Temp_result_df1, Temp_result_df2,result_dic_node1, result_dic_node2, result_concept_node1, result_concept_node2)
    return(result)


def select_result_to_analysis(sele_genes,Temp_result_df1, Temp_result_df2 ):
    
    print("selected_path: "+ ';'.join(sele_genes))
    for_plot = pd.concat([  Temp_result_df1.loc[Temp_result_df1['Object'].isin(sele_genes)],
                            Temp_result_df2.loc[Temp_result_df2['Object'].isin(sele_genes)]], axis=0)

    return(for_plot)



def plot_graph_by_predicates(for_plot):
    graph = nx.from_pandas_edgelist(for_plot, 
                                source='Subject',
                                target='Object', 
                                edge_attr=["Predicate"], 
                                create_using=nx.MultiDiGraph)


    graph_style = [{'selector': 'node[id]',
                             'style': {
                                  'font-family': 'helvetica',
                                  'font-size': '14px',
                                 'text-valign': 'center',
                                 'label': 'data(id)',
                        }},
                        {'selector': 'node',
                         'style': {
                             'background-color': 'lightblue',
                             'shape': 'round-rectangle',
                             'width': '5em',
                         }},
                        {'selector': 'edge[Predicate]',
                         'style': {
                             'label': 'data(Predicate)',
                             'font-size': '12px',
                         }},
                        {"selector": "edge.directed",
                         "style": {
                            "curve-style": "bezier",
                            "target-arrow-shape": "triangle",
                        }},
                       {"selector": "edge",
                         "style": {
                            "curve-style": "bezier",
                        }},

                    ]

    undirected = ipycytoscape.CytoscapeWidget()
    undirected.graph.add_graph_from_networkx(graph)
    undirected.set_layout(title='Path', nodeSpacing=80, edgeLengthVal=50, )
    undirected.set_style(graph_style)

    display(undirected)
    return()


def plot_graph_by_infores(for_plot):
        
    graph = nx.from_pandas_edgelist(for_plot, 
                                    source='Subject',
                                    target='Object', 
                                    edge_attr=["Infores"], 
                                    create_using=nx.MultiDiGraph)


    graph_style = [{'selector': 'node[id]',
                                'style': {
                                    'font-family': 'helvetica',
                                    'font-size': '14px',
                                    'text-valign': 'center',
                                    'label': 'data(id)',
                            }},
                            {'selector': 'node',
                            'style': {
                                'background-color': 'lightblue',
                                'shape': 'round-rectangle',
                                'width': '5em',
                            }},
                            {'selector': 'edge[Infores]',
                            'style': {
                                'label': 'data(Infores)',
                                'font-size': '12px',
                            }},
                            {"selector": "edge.directed",
                            "style": {
                                "curve-style": "bezier",
                                "target-arrow-shape": "triangle",
                            }},
                        {"selector": "edge",
                            "style": {
                                "curve-style": "bezier",
                            }},

                        ]

    undirected = ipycytoscape.CytoscapeWidget()
    undirected.graph.add_graph_from_networkx(graph)
    undirected.set_layout(title='Path', nodeSpacing=80, edgeLengthVal=50, )
    undirected.set_style(graph_style)

    display(undirected)
    return(0)


def plot_graph_by_API(for_plot):
        
    graph = nx.from_pandas_edgelist(for_plot, 
                                    source='Subject',
                                    target='Object', 
                                    edge_attr=["API"], 
                                    create_using=nx.MultiDiGraph)


    graph_style = [{'selector': 'node[id]',
                                'style': {
                                    'font-family': 'helvetica',
                                    'font-size': '14px',
                                    'text-valign': 'center',
                                    'label': 'data(id)',
                            }},
                            {'selector': 'node',
                            'style': {
                                'background-color': 'lightblue',
                                'shape': 'round-rectangle',
                                'width': '5em',
                            }},
                            {'selector': 'edge[API]',
                            'style': {
                                'label': 'data(API)',
                                'font-size': '12px',
                            }},
                            {"selector": "edge.directed",
                            "style": {
                                "curve-style": "bezier",
                                "target-arrow-shape": "triangle",
                            }},
                        {"selector": "edge",
                            "style": {
                                "curve-style": "bezier",
                            }},

                        ]

    undirected = ipycytoscape.CytoscapeWidget()
    undirected.graph.add_graph_from_networkx(graph)
    undirected.set_layout(title='Path', nodeSpacing=80, edgeLengthVal=50, )
    undirected.set_style(graph_style)

    display(undirected)
    return(0)


def load_json_template():
    query_json_temp = {
        "message": {
            "query_graph": {
                "nodes": {
                    "n0": {
                        "ids":[],
                        "categories":["biolink:category"]
                    },
                    "n1": {
                        "categories":["biolink:category"]
                }
                },
                "edges": {
                    "e1": {
                        "subject": "n0",
                        "object": "n1",
                        "predicates": ["biolink:predicates"]
                    }
                }
            }
        }
    }
    return(query_json_temp)

def extract_json(txt):
    import json
    lft = txt.find('{')
    while lft != -1:
        rgt = txt.find('}', lft+1)
        while rgt != -1:
            substr = txt[lft:rgt+1]
            try:
                jsn = json.loads(substr)
                return jsn
            except Exception as e:
                rgt = txt.find('}', rgt+1)
        lft = txt.find('{', lft+1)
    return None


def TRAPI_json_validation(query_json_cur_clean, ALL_predicates, ALL_categories):
    if 'message' not in query_json_cur_clean.keys():
        print('message is missing')
    else:
        if 'query_graph' not in query_json_cur_clean['message'].keys():
            print('query_graph is missing')
        else:
            if 'edges' not in query_json_cur_clean['message']['query_graph'].keys():
                print('edges is missing')
            else:
                if 'e1' not in query_json_cur_clean['message']['query_graph']['edges'].keys():
                    print('e1 is missing')
                else:
                    if 'predicates' not in query_json_cur_clean['message']['query_graph']['edges']['e1'].keys():
                        print('predicates is missing')
                    
                    else:
                        if len(set(query_json_cur_clean['message']['query_graph']['edges']['e1']['predicates']).intersection(set(ALL_predicates))) == 0:
                            print('predicates is not in the KG')
                        else:
                            print("Predicates ok!")
                    
                if 'nodes' not in query_json_cur_clean['message']['query_graph'].keys():
                    print('nodes is missing')
                else:
                    if 'n0' not in query_json_cur_clean['message']['query_graph']['nodes'].keys():
                        print('n0 is missing')
                    else:
                        if 'categories' not in query_json_cur_clean['message']['query_graph']['nodes']['n0'].keys():
                            print('categories is missing')
                        else:
                            if len(set(query_json_cur_clean['message']['query_graph']['nodes']['n0']['categories']).intersection(set(ALL_categories))) == 0:
                                print('categories is not in the KG')
                            else:
                                print("node0 category OK!")
                    
                    if 'n1' not in query_json_cur_clean['message']['query_graph']['nodes'].keys():
                        print('n1 is missing')
                    else:
                        if 'categories' not in query_json_cur_clean['message']['query_graph']['nodes']['n1'].keys():
                            print('categories is missing')
                        else:
                            if len(set(query_json_cur_clean['message']['query_graph']['nodes']['n1']['categories']).intersection(set(ALL_categories))) == 0:
                                print('categories is not in the KG')
                            else:
                                print("node1 category OK!")

    return()

def format_id(query_json_cur_clean):
    input_nodes = query_json_cur_clean['message']['query_graph']['nodes']['n0']['ids']
    input_node1_id = []
    for i in input_nodes:
        input_node1_id.append(get_curie(i))
    print(input_node1_id)

    query_json_cur_clean['message']['query_graph']['nodes']['n0']['ids'] = input_node1_id
    return(query_json_cur_clean)

def query_chatGPT(customized_input, model="gpt-3.5-turbo"):
    message = [{"role": "user", "content": customized_input}]
    
    response = openai.chat.completions.create(
        model=model,
        max_tokens=1000,
        temperature=0.3,
        messages=message,
    )
    
    # print(len(response.choices[0].message.content.split(" ")))
    return response.choices[0].message.content

def query_chatGPT4(customized_input):
    return query_chatGPT(customized_input, "gpt-4")
    

def ask_chatGPT(prompt_text):
    response = query_chatGPT(prompt_text)
    return response
        

def ask_chatGPT4(prompt_text):
    response = query_chatGPT4(prompt_text)
    return response

def find_similar_predicates(query_json_cur_clean, ALL_predicates):
    current_predicates = query_json_cur_clean['message']['query_graph']['edges']['e1']['predicates']
    output = ask_chatGPT4("The predicates in the KG are: " + ','.join(ALL_predicates) + ". The predicates in the current query are: " + ','.join(current_predicates) + ". What predicates are similar to the predicates in the current query?")
    return(output)

def find_similar_category(query_json_cur_clean, ALL_categories):
    current_predicates1 = query_json_cur_clean['message']['query_graph']['nodes']['n0']['categories']
    current_predicates2 = query_json_cur_clean['message']['query_graph']['nodes']['n1']['categories']
    output = ask_chatGPT4("The categories in the KG are: " + ','.join(ALL_categories) + ". The category in the current query are: " + ','.join(current_predicates1 + current_predicates2) + ". What categories are similar to the categories in the current query?")
    return(output)


def visulize_path(input_node1_id, intermediate_node, input_node3_id, result, result2):
    forplot_subject = []
    forplot_object = []
    forplot_predicate = []
    forplot_Infores = []

    for k in result.keys():
        if (result[k]['object'] == intermediate_node and result[k]['subject'] == input_node1_id) or (result[k]['subject'] == intermediate_node and result[k]['object'] == input_node1_id)  :
            forplot_subject.append(result[k]['subject'])
            forplot_object.append(result[k]['object'])
            #forplot_predicate.append(result[k]['predicate'].split(':')[1])
            cur_sources_list = []
            sources = result[k]['sources']
            
            for s in sources:
                cur_source = s['resource_id']
                cur_sources_list.append(cur_source)
                
            forplot_Infores.append(cur_sources_list)

            forplot_predicate.append(result[k]['predicate'].split(':')[1] + "::" + cur_sources_list[0])

    for k in result2.keys():
        if (result2[k]['object'] == intermediate_node and result2[k]['subject'] ==input_node3_id ) or (result2[k]['subject'] == intermediate_node and result2[k]['object'] ==input_node3_id)  :
            forplot_subject.append(result2[k]['subject'])
            forplot_object.append(result2[k]['object'])
            #forplot_predicate.append(result2[k]['predicate'].split(':')[1])
            cur_sources_list = []
            sources = result2[k]['sources']
            
            for s in sources:
                cur_source = s['resource_id']
                cur_sources_list.append(cur_source)
                
            forplot_Infores.append(cur_sources_list)
            forplot_predicate.append(result2[k]['predicate'].split(':')[1] + "::" +  cur_sources_list[0])
            
    forplot =  pd.DataFrame({"Subject":forplot_subject, "Object":forplot_object, "Predicates":forplot_predicate})

    # get preferred name
    subject_name = list(forplot["Subject"] )
    object_name = list(forplot["Object"])
    dic_id_map = ID_convert_to_preferred_name_nodeNormalizer(subject_name+ object_name)
    new_subject_name = []
    for item in subject_name:
        if item in dic_id_map:
            new_subject_name.append(dic_id_map[item])
        else:
            new_subject_name.append(item)   

    new_object_name = []
    for item in object_name:
        if item in dic_id_map:
            new_object_name.append(dic_id_map[item])
        else:
            new_object_name.append(item)         
    forplot['Subject_name'] = new_subject_name
    forplot['Object_name'] = new_object_name

    forplot = forplot.drop_duplicates()

   

    graph = nx.from_pandas_edgelist(forplot, source='Subject_name', target='Object_name', edge_attr=[ 'Predicates'], create_using=nx.MultiGraph)
    graph_style = [{'selector': 'node[id]',
                             'style': {
                                  'font-family': 'Arial',
                                  'font-size': '12px',
                                 'text-valign': 'center',
                                 'label': 'data(id)',
                        }},
                        {'selector': 'node',
                         'style': {
                             'background-color': 'lightblue',
                             'shape': 'round-rectangle',
                             'width': '3em',
                         }},
                        {'selector': 'edge[Predicates]',
                         'style': {
                             'label': 'data(Predicates)',
                             'font-size': '8px',
                         }},
                        {"selector": "edge.directed",
                         "style": {
                            "curve-style": "bezier",
                            "target-arrow-shape": "triangle",
                        }},
                       {"selector": "edge",
                         "style": {
                            "curve-style": "bezier",
                        }},

                    ]
    pathgraph = ipycytoscape.CytoscapeWidget()
    pathgraph.graph.add_graph_from_networkx(graph)
    pathgraph.set_layout(title='Path', nodeSpacing=80, edgeLengthVal=50, )
    pathgraph.set_style(graph_style)

    display(pathgraph)
    return(forplot)


def get_similar_category(query_json_cur_clean, KG_category):
    similar_category_text = find_similar_category(query_json_cur_clean, KG_category)
    words = similar_category_text.split(' ')
    similar_category = []
    for word in words:
        if word.startswith('biolink:') :
            similar_category.append(word)

    for category in query_json_cur_clean['message']['query_graph']['nodes']['n0']['categories']:
        similar_category.append(category)

    for category in query_json_cur_clean['message']['query_graph']['nodes']['n1']['categories']:
        similar_category.append(category)

    similar_category = list(set(similar_category))

    similar_category
    return similar_category

def get_similar_predicate(query_json_cur_clean, All_predicates):
    similar_predicate_text = find_similar_predicates(query_json_cur_clean, All_predicates)
    similar_predicate_text
    lines = similar_predicate_text.split('\n')
    words = []
    for line in lines:
        cur_words = line.split(' ')
        words = words + cur_words
    similar_predicate = []
    for word in words:
        if word.startswith('biolink:') :
            similar_predicate.append(word)

    for predicate in query_json_cur_clean['message']['query_graph']['edges']['e1']['predicates']:
        similar_predicate.append(predicate)

    similar_predicate = list(set(similar_predicate))

    similar_predicate
    return similar_predicate


# I've added this code so I could test ID_convert_to_preferred_name_nodeNormalizer()
# without changing any of the rest of the code. Please delete it once you understand
# the other changes I've made!
if __name__ == "__main__":
    # Check function on some identifier lists.
    result1 = ID_convert_to_preferred_name_nodeNormalizer([])
    if result1 != {}:
        raise RuntimeError("ID_convert_to_preferred_name_nodeNormalizer([]) should equal []")

    result2 = ID_convert_to_preferred_name_nodeNormalizer(['UBERON:0000201'])
    if result2 != {'UBERON:0000201': 'endothelial blood brain barrier'}:
        raise RuntimeError(f"Incorrect result: {result2}")

    result3 = ID_convert_to_preferred_name_nodeNormalizer(['MESH:D005183', 'UBERON:0000201'])
    if result3 != {
        'UBERON:0000201': 'endothelial blood brain barrier',
        'MESH:D005183': 'Failure to Thrive'
    }:
        raise RuntimeError(f"Incorrect result: {result3}")

    result4 = ID_convert_to_preferred_name_nodeNormalizer(['CHEBI:45863', 'PUBCHEM.COMPOUND:31703'])
    if result4 != {
        'CHEBI:45863': 'Paclitaxel',
        'PUBCHEM.COMPOUND:31703': 'Doxorubicin'
    }:
        raise RuntimeError(f"Incorrect result: {result4}")

    result5 = ID_convert_to_preferred_name_nodeNormalizer([
        'RXCUI:258355',
        'PUBCHEM.COMPOUND:4261',
        'PUBCHEM.COMPOUND:49850262',
        'PUBCHEM.COMPOUND:50992434',
        'PUBCHEM.COMPOUND:135539077',
        'RXCUI:1430268',
        'CHEBI:90942',
        'CHEBI:110200',
        'CHEBI:63996',
        'CHEBI:6716',
        'CHEBI:14222',
        'PUBCHEM.COMPOUND:25141092',
        'PUBCHEM.COMPOUND:36314',
        'PUBCHEM.COMPOUND:31703',
        'PUBCHEM.COMPOUND:3385',
        'PUBCHEM.COMPOUND:126941',
        'PUBCHEM.COMPOUND:135410875',
        'PUBCHEM.COMPOUND:148124',
        'PUBCHEM.COMPOUND:5311497',
        'PUBCHEM.COMPOUND:107935',
        'PUBCHEM.COMPOUND:387447',
        'PUBCHEM.COMPOUND:518605',
        'PUBCHEM.COMPOUND:5282165',
        'PUBCHEM.COMPOUND:5591',
        'PUBCHEM.COMPOUND:1322',
        'PUBCHEM.COMPOUND:95170',
        'PUBCHEM.COMPOUND:2286',
        'PUBCHEM.COMPOUND:1242',
        'PUBCHEM.COMPOUND:8461',
        'PUBCHEM.COMPOUND:11813',
        'PUBCHEM.COMPOUND:1530',
        'PUBCHEM.COMPOUND:11831',
        'PUBCHEM.COMPOUND:7577',
        'PUBCHEM.COMPOUND:73864',
        'PUBCHEM.COMPOUND:4521392',
        'PUBCHEM.COMPOUND:47289',
        'PUBCHEM.COMPOUND:1983',
        'PUBCHEM.COMPOUND:12035',
        'PUBCHEM.COMPOUND:449459',
        'PUBCHEM.COMPOUND:186907',
        'PUBCHEM.COMPOUND:449171',
        'PUBCHEM.COMPOUND:7290',
        'PUBCHEM.COMPOUND:2236',
        'PUBCHEM.COMPOUND:5359596',
        'PUBCHEM.COMPOUND:6918483',
        'PUBCHEM.COMPOUND:23667548',
        'PUBCHEM.COMPOUND:2256',
        'PUBCHEM.COMPOUND:62306',
        'PUBCHEM.COMPOUND:2336',
        'PUBCHEM.COMPOUND:6623',
        'PUBCHEM.COMPOUND:66166',
        'PUBCHEM.COMPOUND:12111',
        'PUBCHEM.COMPOUND:6626',
        'PUBCHEM.COMPOUND:16682746',
        'PUBCHEM.COMPOUND:5360373',
        'PUBCHEM.COMPOUND:7961',
        'PUBCHEM.COMPOUND:2478',
        'PUBCHEM.COMPOUND:264',
        'PUBCHEM.COMPOUND:23973',
        'PUBCHEM.COMPOUND:2519',
        'PUBCHEM.COMPOUND:5280453',
        'PUBCHEM.COMPOUND:5943',
        'PUBCHEM.COMPOUND:1203',
        'PUBCHEM.COMPOUND:135411',
        'PUBCHEM.COMPOUND:154413',
        'PUBCHEM.COMPOUND:40470',
        'PUBCHEM.COMPOUND:2730',
        'PUBCHEM.COMPOUND:29131',
        'PUBCHEM.COMPOUND:9171',
        'PUBCHEM.COMPOUND:5702198',
        'PUBCHEM.COMPOUND:2797',
        'PUBCHEM.COMPOUND:24463',
        'PUBCHEM.COMPOUND:323',
        'PUBCHEM.COMPOUND:40585',
        'PUBCHEM.COMPOUND:451668',
        'PUBCHEM.COMPOUND:40024',
        'PUBCHEM.COMPOUND:3017',
        'PUBCHEM.COMPOUND:3026',
        'PUBCHEM.COMPOUND:5371560',
        'PUBCHEM.COMPOUND:969491',
        'PUBCHEM.COMPOUND:8343',
        'PUBCHEM.COMPOUND:5921',
        'PUBCHEM.COMPOUND:448537',
        'PUBCHEM.COMPOUND:6124',
        'PUBCHEM.COMPOUND:8346',
        'PUBCHEM.COMPOUND:5757',
        'PUBCHEM.COMPOUND:702',
        'PUBCHEM.COMPOUND:5991',
        'PUBCHEM.COMPOUND:11',
        'PUBCHEM.COMPOUND:3346',
        'PUBCHEM.COMPOUND:3397',
        'PUBCHEM.COMPOUND:135398658',
        'PUBCHEM.COMPOUND:14101198',
        'PUBCHEM.COMPOUND:104741',
        'PUBCHEM.COMPOUND:8029',
        'PUBCHEM.COMPOUND:60750',
        'PUBCHEM.COMPOUND:5280961',
        'PUBCHEM.COMPOUND:9898639',
        'PUBCHEM.COMPOUND:637566',
        'PUBCHEM.COMPOUND:3474',
        'PUBCHEM.COMPOUND:23985',
        'PUBCHEM.COMPOUND:3616',
        'PUBCHEM.COMPOUND:42890',
        'PUBCHEM.COMPOUND:3715',
        'PUBCHEM.COMPOUND:6912226',
        'PUBCHEM.COMPOUND:3779',
        'PUBCHEM.COMPOUND:9812710',
        'PUBCHEM.COMPOUND:46907787',
        'PUBCHEM.COMPOUND:25195294',
        'PUBCHEM.COMPOUND:896',
        'PUBCHEM.COMPOUND:10836',
        'PUBCHEM.COMPOUND:4098',
        'PUBCHEM.COMPOUND:13709',
        'PUBCHEM.COMPOUND:1349907',
        'PUBCHEM.COMPOUND:1674',
        'PUBCHEM.COMPOUND:4156',
        'PUBCHEM.COMPOUND:7456',
        'PUBCHEM.COMPOUND:6010',
        'PUBCHEM.COMPOUND:8575',
        'PUBCHEM.COMPOUND:4449',
        'PUBCHEM.COMPOUND:4122',
        'PUBCHEM.COMPOUND:442530',
        'PUBCHEM.COMPOUND:9887053',
        'PUBCHEM.COMPOUND:991',
        'PUBCHEM.COMPOUND:854',
        'PUBCHEM.COMPOUND:74483',
        'PUBCHEM.COMPOUND:9554',
        'PUBCHEM.COMPOUND:5794',
        'PUBCHEM.COMPOUND:5694',
        'PUBCHEM.COMPOUND:15032',
        'PUBCHEM.COMPOUND:657298',
        'PUBCHEM.COMPOUND:14942',
        'PUBCHEM.COMPOUND:5280343',
        'PUBCHEM.COMPOUND:5035',
        'PUBCHEM.COMPOUND:6758',
        'PUBCHEM.COMPOUND:5186',
        'PUBCHEM.COMPOUND:1091',
        'PUBCHEM.COMPOUND:133538',
        'PUBCHEM.COMPOUND:7305',
        'PUBCHEM.COMPOUND:5323',
        'PUBCHEM.COMPOUND:5329102',
        'PUBCHEM.COMPOUND:5284461',
        'PUBCHEM.COMPOUND:24857286',
        'PUBCHEM.COMPOUND:6410',
        'PUBCHEM.COMPOUND:5995',
        'PUBCHEM.COMPOUND:6618',
        'PUBCHEM.COMPOUND:15625',
        'PUBCHEM.COMPOUND:27924',
        'PUBCHEM.COMPOUND:2723949',
        'PUBCHEM.COMPOUND:26042',
        'PUBCHEM.COMPOUND:60700',
        'PUBCHEM.COMPOUND:444795',
        'PUBCHEM.COMPOUND:6575',
        'PUBCHEM.COMPOUND:5564',
        'PUBCHEM.COMPOUND:11089',
        'PUBCHEM.COMPOUND:65411',
        'PUBCHEM.COMPOUND:23964',
        'PUBCHEM.COMPOUND:3121',
        'PUBCHEM.COMPOUND:14969',
        'PUBCHEM.COMPOUND:39676',
        'PUBCHEM.COMPOUND:2116',
        'MESH:D014874',
        'PUBCHEM.COMPOUND:23994',
        'PUBCHEM.COMPOUND:11626560',
        'PUBCHEM.COMPOUND:57379345',
        'PUBCHEM.COMPOUND:5328940',
        'PUBCHEM.COMPOUND:49846579',
        'PUBCHEM.COMPOUND:25134326',
        'PUBCHEM.COMPOUND:9829523',
        'PUBCHEM.COMPOUND:25183872',
        'PUBCHEM.COMPOUND:49806720',
        'PUBCHEM.COMPOUND:71731823',
        'PUBCHEM.COMPOUND:5311',
        'PUBCHEM.COMPOUND:5281855',
        'PUBCHEM.COMPOUND:5291',
        'PUBCHEM.COMPOUND:135430309',
        'PUBCHEM.COMPOUND:447077',
        'PUBCHEM.COMPOUND:5284616',
        'PUBCHEM.COMPOUND:11707110',
        'PUBCHEM.COMPOUND:10184653',
        'TTD.DRUG:D0Z1OR',
        'UNII:334895S862',
        'PUBCHEM.COMPOUND:176870',
        'PUBCHEM.COMPOUND:6049',
        'PUBCHEM.COMPOUND:440473',
        'PUBCHEM.COMPOUND:175',
        'PUBCHEM.COMPOUND:457193',
        'PUBCHEM.COMPOUND:1548943',
        'PUBCHEM.COMPOUND:36462',
        'PUBCHEM.COMPOUND:5281672',
        'PUBCHEM.COMPOUND:6057',
        'PUBCHEM.COMPOUND:78165',
        'PUBCHEM.COMPOUND:6518',
        'PUBCHEM.COMPOUND:5360696',
        'PUBCHEM.COMPOUND:6253',
        'PUBCHEM.COMPOUND:30323',
        'PUBCHEM.COMPOUND:2733526',
        'PUBCHEM.COMPOUND:3108',
        'PUBCHEM.COMPOUND:10366136',
        'PUBCHEM.COMPOUND:3220',
        'PUBCHEM.COMPOUND:7405',
        'PUBCHEM.COMPOUND:656894',
        'PUBCHEM.COMPOUND:10607',
        'PUBCHEM.COMPOUND:135398748',
        'PUBCHEM.COMPOUND:8771',
        'PUBCHEM.COMPOUND:679',
        'PUBCHEM.COMPOUND:6918638',
        'PUBCHEM.COMPOUND:44259',
        'PUBCHEM.COMPOUND:444732',
        'PUBCHEM.COMPOUND:6029',
        'PUBCHEM.COMPOUND:34755',
        'PUBCHEM.COMPOUND:5284627',
        'PUBCHEM.COMPOUND:5957',
        'PUBCHEM.COMPOUND:2353',
        'PUBCHEM.COMPOUND:72277',
        'PUBCHEM.COMPOUND:46191454',
        'PUBCHEM.COMPOUND:8988',
        'PUBCHEM.COMPOUND:977',
        'DRUGBANK:DB12182',
        'PUBCHEM.COMPOUND:23725625',
        'PUBCHEM.COMPOUND:4212',
        'PUBCHEM.COMPOUND:91766',
        'PUBCHEM.COMPOUND:65359',
        'PUBCHEM.COMPOUND:441923',
        'PUBCHEM.COMPOUND:445154',
        'PUBCHEM.COMPOUND:65064',
        'PUBCHEM.COMPOUND:11338033',
        'PUBCHEM.COMPOUND:9444',
        'PUBCHEM.COMPOUND:30751'
    ])
    if result5 != {
        'RXCUI:258355': 'Rapamune', 'PUBCHEM.COMPOUND:4261': 'Entinostat', 'PUBCHEM.COMPOUND:49850262': 'Tubastatin A',
        'PUBCHEM.COMPOUND:50992434': 'Trametinib dimethyl sulfoxide', 'PUBCHEM.COMPOUND:135539077': 'Luminespib',
        'RXCUI:1430268': 'Gilotrif', 'CHEBI:90942': 'Ixazomib', 'CHEBI:110200': 'CHEBI:110200',
        'CHEBI:63996': 'SKF 83959 hydrobromide', 'CHEBI:6716': 'Medroxyprogesterone acetate',
        'CHEBI:14222': 'CHEBI:14222', 'PUBCHEM.COMPOUND:25141092': 'Entrectinib',
        'PUBCHEM.COMPOUND:36314': 'Paclitaxel', 'PUBCHEM.COMPOUND:31703': 'Doxorubicin',
        'PUBCHEM.COMPOUND:3385': 'Fluorouracil', 'PUBCHEM.COMPOUND:126941': 'Methotrexate',
        'PUBCHEM.COMPOUND:135410875': 'Pemetrexed', 'PUBCHEM.COMPOUND:148124': 'Docetaxel',
        'PUBCHEM.COMPOUND:5311497': 'Vinorelbine', 'PUBCHEM.COMPOUND:107935': 'Deguelin',
        'PUBCHEM.COMPOUND:387447': 'Bortezomib',
        'PUBCHEM.COMPOUND:518605': '2,4,6,8,9,10-Hexaoxa-1,3,5,7-tetraarsatricyclo[3.3.1.13,7]decane',
        'PUBCHEM.COMPOUND:5282165': 'Josamycin', 'PUBCHEM.COMPOUND:5591': 'Troglitazone',
        'PUBCHEM.COMPOUND:1322': '1,2-Dimethylhydrazine',
        'PUBCHEM.COMPOUND:95170': "2,2',4,4'-Tetrabromodiphenyl ether",
        'PUBCHEM.COMPOUND:2286': 'Bisphenol A diglycidyl ether',
        'PUBCHEM.COMPOUND:1242': '2,3,4,5-Tetrahydro-7,8-dihydroxy-1-phenyl-1H-3-benzazepine',
        'PUBCHEM.COMPOUND:8461': '2,4-Dinitrotoluene', 'PUBCHEM.COMPOUND:11813': '2,6-Dinitrotoluene',
        'PUBCHEM.COMPOUND:1530': '2-Amino-1-methyl-6-phenylimidazo(4,5-b)pyridine',
        'PUBCHEM.COMPOUND:11831': '2-Nitrofluorene', 'PUBCHEM.COMPOUND:7577': "4,4'-Methylenedianiline",
        'PUBCHEM.COMPOUND:73864': 'Bisphenol AF',
        'PUBCHEM.COMPOUND:4521392': '4-(4-(benzo[d][1,3]dioxol-5-yl)-5-(pyridin-2-yl)-1H-imidazol-2-yl)benzamide',
        'PUBCHEM.COMPOUND:47289': '4-(N-Nitrosomethylamino)-1-(3-pyridyl)-1-butanone',
        'PUBCHEM.COMPOUND:1983': 'Acetaminophen', 'PUBCHEM.COMPOUND:12035': 'Acetylcysteine',
        'PUBCHEM.COMPOUND:449459': 'Afimoxifene', 'PUBCHEM.COMPOUND:186907': 'Aflatoxin B1',
        'PUBCHEM.COMPOUND:449171': 'Alitretinoin', 'PUBCHEM.COMPOUND:7290': '3-Chloro-1,2-propanediol',
        'PUBCHEM.COMPOUND:2236': 'Aristolochic acid', 'PUBCHEM.COMPOUND:5359596': 'Arsenic',
        'PUBCHEM.COMPOUND:6918483': 'Artenimol', 'PUBCHEM.COMPOUND:23667548': 'Sodium Ascorbate',
        'PUBCHEM.COMPOUND:2256': 'Atrazine', 'PUBCHEM.COMPOUND:62306': 'Benoxacor',
        'PUBCHEM.COMPOUND:2336': 'Benzo[a]pyrene', 'PUBCHEM.COMPOUND:6623': 'Bisphenol A',
        'PUBCHEM.COMPOUND:66166': 'Bisphenol B', 'PUBCHEM.COMPOUND:12111': "4,4'-Methylenediphenol",
        'PUBCHEM.COMPOUND:6626': "4,4'-Sulfonyldiphenol", 'PUBCHEM.COMPOUND:16682746': 'Tributyltin oxide',
        'PUBCHEM.COMPOUND:5360373': 'Bleomycin', 'PUBCHEM.COMPOUND:7961': 'Bromobenzene',
        'PUBCHEM.COMPOUND:2478': 'Busulfan', 'PUBCHEM.COMPOUND:264': 'Butyric Acid',
        'PUBCHEM.COMPOUND:23973': 'Cadmium', 'PUBCHEM.COMPOUND:2519': 'Caffeine',
        'PUBCHEM.COMPOUND:5280453': 'Calcitriol', 'PUBCHEM.COMPOUND:5943': 'Carbon Tetrachloride',
        'PUBCHEM.COMPOUND:1203': '2-(3,4-Dihydroxyphenyl)chroman-3,5,7-triol',
        'PUBCHEM.COMPOUND:135411': '6-[3-(1-Adamantyl)-4-hydroxyphenyl]-2-naphthalenecarboxylic Acid',
        'PUBCHEM.COMPOUND:154413': 'Centchroman', 'PUBCHEM.COMPOUND:40470': "2,2',3,3',4-Pentachlorobiphenyl",
        'PUBCHEM.COMPOUND:2730': 'Chlorpyrifos', 'PUBCHEM.COMPOUND:29131': 'Chromium(6+)',
        'PUBCHEM.COMPOUND:9171': 'Chrysene', 'PUBCHEM.COMPOUND:5702198': 'azane;dichloroplatinum',
        'PUBCHEM.COMPOUND:2797': 'Clofibric acid', 'PUBCHEM.COMPOUND:24463': 'Copper sulfate pentahydrate',
        'PUBCHEM.COMPOUND:323': 'Coumarin', 'PUBCHEM.COMPOUND:40585': 'Deltamethrin',
        'PUBCHEM.COMPOUND:451668': 'Decitabine', 'PUBCHEM.COMPOUND:40024': 'Deoxynivalenol',
        'PUBCHEM.COMPOUND:3017': 'Diazinon', 'PUBCHEM.COMPOUND:3026': 'Dibutyl Phthalate',
        'PUBCHEM.COMPOUND:5371560': 'Dicrotophos', 'PUBCHEM.COMPOUND:969491': 'Dieldrin',
        'PUBCHEM.COMPOUND:8343': 'Bis(2-ethylhexyl) phthalate', 'PUBCHEM.COMPOUND:5921': 'N-Nitrosodiethylamine',
        'PUBCHEM.COMPOUND:448537': 'Diethylstilbestrol', 'PUBCHEM.COMPOUND:6124': 'N-Nitrosodimethylamine',
        'PUBCHEM.COMPOUND:8346': 'Dioctyl phthalate', 'PUBCHEM.COMPOUND:5757': 'Estradiol',
        'PUBCHEM.COMPOUND:702': 'Ethanol', 'PUBCHEM.COMPOUND:5991': 'Ethinyl estradiol',
        'PUBCHEM.COMPOUND:11': '1,2-Dichloroethane', 'PUBCHEM.COMPOUND:3346': 'Fenthion',
        'PUBCHEM.COMPOUND:3397': 'Flutamide', 'PUBCHEM.COMPOUND:135398658': 'Folic Acid',
        'PUBCHEM.COMPOUND:14101198': '[(1R)-1-[(3S,6S,9S,12S,18R,21S,22R)-21-acetamido-18-benzyl-3-[(1R)-1-methoxyethyl]-4,9,10,12,16-pentamethyl-15-methylidene-2,5,8,11,14,17,20-heptaoxo-22-propan-2-yl-1,19-dioxa-4,7,10,13,16-pentazacyclodocos-6-yl]-2-methylpropyl] (2S,3R)-3-hydroxy-4-methyl-2-(propanoylamino)pentanoate',
        'PUBCHEM.COMPOUND:104741': 'Fulvestrant', 'PUBCHEM.COMPOUND:8029': 'Furan',
        'PUBCHEM.COMPOUND:60750': 'Gemcitabine', 'PUBCHEM.COMPOUND:5280961': 'Genistein',
        'PUBCHEM.COMPOUND:9898639': 'Gentamicinsulfate salt', 'PUBCHEM.COMPOUND:637566': 'Geraniol',
        'PUBCHEM.COMPOUND:3474': 'Glafenine', 'PUBCHEM.COMPOUND:23985': 'Gold',
        'PUBCHEM.COMPOUND:3616': 'Hexamethylene bisacetamide', 'PUBCHEM.COMPOUND:42890': 'Idarubicin',
        'PUBCHEM.COMPOUND:3715': 'Indomethacin', 'PUBCHEM.COMPOUND:6912226': 'Ionomycin',
        'PUBCHEM.COMPOUND:3779': 'Isoproterenol',
        'PUBCHEM.COMPOUND:9812710': 'Ivermectine 100 microg/mL in Acetonitrile',
        'PUBCHEM.COMPOUND:46907787': '(S)-(+)-tert-Butyl 2-(4-(4-chlorophenyl)-2,3,9-trimethyl-6H-thieno(3,2-f)(1,2,4)triazolo(4,3-a)(1,4)diazepin-6-yl)acetate',
        'PUBCHEM.COMPOUND:25195294': '4-(6-(4-(Piperazin-1-yl)phenyl)pyrazolo[1,5-a]pyrimidin-3-yl)quinoline',
        'PUBCHEM.COMPOUND:896': 'Melatonin', 'PUBCHEM.COMPOUND:10836': 'Methamphetamine',
        'PUBCHEM.COMPOUND:4098': 'Methapyrilene', 'PUBCHEM.COMPOUND:13709': 'Methidathion',
        'PUBCHEM.COMPOUND:1349907': 'Methimazole', 'PUBCHEM.COMPOUND:1674': '3-Methylcholanthrene',
        'PUBCHEM.COMPOUND:4156': 'Methyl methanesulfonate', 'PUBCHEM.COMPOUND:7456': 'Methylparaben',
        'PUBCHEM.COMPOUND:6010': 'Methyltestosterone', 'PUBCHEM.COMPOUND:8575': 'Monobutyl phthalate',
        'PUBCHEM.COMPOUND:4449': 'Nefazodone', 'PUBCHEM.COMPOUND:4122': 'Nocodazole',
        'PUBCHEM.COMPOUND:442530': 'Ochratoxin A', 'PUBCHEM.COMPOUND:9887053': 'Oxaliplatin',
        'PUBCHEM.COMPOUND:991': 'Parathion', 'PUBCHEM.COMPOUND:854': 'DL-Arabinose',
        'PUBCHEM.COMPOUND:74483': 'Perfluorooctanesulfonic acid', 'PUBCHEM.COMPOUND:9554': 'Perfluorooctanoic acid',
        'PUBCHEM.COMPOUND:5794': 'Piperonyl butoxide', 'PUBCHEM.COMPOUND:5694': 'Pirinixic acid',
        'PUBCHEM.COMPOUND:15032': 'Pregnenolone carbonitrile', 'PUBCHEM.COMPOUND:657298': 'Propylthiouracil',
        'PUBCHEM.COMPOUND:14942': 'Orthosilicic acid', 'PUBCHEM.COMPOUND:5280343': 'Quercetin',
        'PUBCHEM.COMPOUND:5035': 'Raloxifene', 'PUBCHEM.COMPOUND:6758': 'Rotenone',
        'PUBCHEM.COMPOUND:5186': 'Scriptaid', 'PUBCHEM.COMPOUND:1091': 'Selenious acid',
        'PUBCHEM.COMPOUND:133538': '3-Methyl-6-chloro-2,3,4,5-tetrahydro-7,8-dihydroxy-1-(3-methylphenyl)-1H-3-benzazepine',
        'PUBCHEM.COMPOUND:7305': 'Soman', 'PUBCHEM.COMPOUND:5323': 'Sulfadimethoxine',
        'PUBCHEM.COMPOUND:5329102': 'Sunitinib', 'PUBCHEM.COMPOUND:5284461': 'T-2 Toxin',
        'PUBCHEM.COMPOUND:24857286': 'Fasiglifam', 'PUBCHEM.COMPOUND:6410': 'tert-Butyl Hydroperoxide',
        'PUBCHEM.COMPOUND:5995': 'Testosterone propionate', 'PUBCHEM.COMPOUND:6618': 'Tetrabromobisphenol A',
        'PUBCHEM.COMPOUND:15625': '2,3,7,8-Tetrachlorodibenzo-P-dioxin',
        'PUBCHEM.COMPOUND:27924': 'Phorbol 12-myristate 13-acetate', 'PUBCHEM.COMPOUND:2723949': 'Thioacetamide',
        'PUBCHEM.COMPOUND:26042': 'Titanium Dioxide', 'PUBCHEM.COMPOUND:60700': 'Topotecan',
        'PUBCHEM.COMPOUND:444795': 'Tretinoin', 'PUBCHEM.COMPOUND:6575': 'Trichloroethylene',
        'PUBCHEM.COMPOUND:5564': 'Triclosan', 'PUBCHEM.COMPOUND:11089': 'Trimellitic anhydride',
        'PUBCHEM.COMPOUND:65411': 'Triptonide', 'PUBCHEM.COMPOUND:23964': 'Tungsten',
        'PUBCHEM.COMPOUND:3121': 'Valproic Acid', 'PUBCHEM.COMPOUND:14969': 'Vancomycin',
        'PUBCHEM.COMPOUND:39676': 'Vinclozolin', 'PUBCHEM.COMPOUND:2116': 'DL-alpha-Tocopherol',
        'MESH:D014874': 'MESH:D014874', 'PUBCHEM.COMPOUND:23994': 'Zinc', 'PUBCHEM.COMPOUND:11626560': 'Crizotinib',
        'PUBCHEM.COMPOUND:57379345': 'Ceritinib', 'PUBCHEM.COMPOUND:5328940': 'Bosutinib',
        'PUBCHEM.COMPOUND:49846579': 'Venetoclax',
        'PUBCHEM.COMPOUND:25134326': 'N2-[2-Methoxy-4-[4-(4-methyl-1-piperazinyl)-1-piperidinyl]phenyl]-N4-[2-[(1-methylethyl)sulfonyl]phenyl]-1,3,5-triazine-2,4-diamine',
        'PUBCHEM.COMPOUND:9829523': 'Midostaurin', 'PUBCHEM.COMPOUND:25183872': 'Ixazomib',
        'PUBCHEM.COMPOUND:49806720': 'Alectinib', 'PUBCHEM.COMPOUND:71731823': 'Lorlatinib',
        'PUBCHEM.COMPOUND:5311': 'Vorinostat', 'PUBCHEM.COMPOUND:5281855': 'Ellagic Acid',
        'PUBCHEM.COMPOUND:5291': 'Imatinib', 'PUBCHEM.COMPOUND:135430309': '2-(4-methoxyphenyl)-1H-quinazolin-4-one',
        'PUBCHEM.COMPOUND:447077': '6-(2,6-dichlorophenyl)-8-methyl-2-((3-(methylthio)phenyl)amino)pyrido[2,3-d]pyrimidin-7(8H)-one',
        'PUBCHEM.COMPOUND:5284616': 'Sirolimus', 'PUBCHEM.COMPOUND:11707110': 'Trametinib',
        'PUBCHEM.COMPOUND:10184653': 'Afatinib', 'TTD.DRUG:D0Z1OR': 'TTD.DRUG:D0Z1OR',
        'UNII:334895S862': 'DOXYCYCLINE ANHYDROUS', 'PUBCHEM.COMPOUND:176870': 'Erlotinib',
        'PUBCHEM.COMPOUND:6049': 'Edetic Acid', 'PUBCHEM.COMPOUND:440473': 'L-mimosine',
        'PUBCHEM.COMPOUND:175': 'Acetate', 'PUBCHEM.COMPOUND:457193': 'Dactinomycin',
        'PUBCHEM.COMPOUND:1548943': 'Capsaicin', 'PUBCHEM.COMPOUND:36462': 'Etoposide',
        'PUBCHEM.COMPOUND:5281672': 'Myricetin', 'PUBCHEM.COMPOUND:6057': 'Tyrosine',
        'PUBCHEM.COMPOUND:78165': '2-(N-Morpholino)-ethanesulfonic acid',
        'PUBCHEM.COMPOUND:6518': 'Pentaerythritol tetranitrate', 'PUBCHEM.COMPOUND:5360696': 'Dextromethorphan',
        'PUBCHEM.COMPOUND:6253': 'Cytarabine', 'PUBCHEM.COMPOUND:30323': 'Daunorubicin',
        'PUBCHEM.COMPOUND:2733526': 'Tamoxifen', 'PUBCHEM.COMPOUND:3108': 'Dipyridamole',
        'PUBCHEM.COMPOUND:10366136': 'Crenolanib', 'PUBCHEM.COMPOUND:3220': 'Emodin',
        'PUBCHEM.COMPOUND:7405': 'L-Pyroglutamic acid',
        'PUBCHEM.COMPOUND:656894': 'Isopropyl-beta-D-thiogalactopyranoside', 'PUBCHEM.COMPOUND:10607': 'Podofilox',
        'PUBCHEM.COMPOUND:135398748': 'Penciclovir', 'PUBCHEM.COMPOUND:8771': 'Tetradecyl hydrogen sulfate (ester)',
        'PUBCHEM.COMPOUND:679': 'Dimethyl Sulfoxide', 'PUBCHEM.COMPOUND:6918638': 'Belinostat',
        'PUBCHEM.COMPOUND:44259': 'Staurosporine', 'PUBCHEM.COMPOUND:444732': 'trichostatin A',
        'PUBCHEM.COMPOUND:6029': 'Uridine', 'PUBCHEM.COMPOUND:34755': 'S-adenosylmethionine',
        'PUBCHEM.COMPOUND:5284627': 'Topiramate', 'PUBCHEM.COMPOUND:5957': "Adenosine-5'-triphosphate",
        'PUBCHEM.COMPOUND:2353': 'Berberine', 'PUBCHEM.COMPOUND:72277': 'Epigallocatechin',
        'PUBCHEM.COMPOUND:46191454': 'N-(6,6-dimethyl-5-(1-methylpiperidine-4-carbonyl)-1,4,5,6-tetrahydropyrrolo[3,4-c]pyrazol-3-yl)-3-methylbutanamide',
        'PUBCHEM.COMPOUND:8988': 'D-proline', 'PUBCHEM.COMPOUND:977': 'Oxygen', 'DRUGBANK:DB12182': 'DRUGBANK:DB12182',
        'PUBCHEM.COMPOUND:23725625': 'Olaparib', 'PUBCHEM.COMPOUND:4212': 'Mitoxantrone',
        'PUBCHEM.COMPOUND:91766': 'Flufenoxuron', 'PUBCHEM.COMPOUND:65359': 'Oxiglutatione',
        'PUBCHEM.COMPOUND:441923': 'Ginsenoside Rg1', 'PUBCHEM.COMPOUND:445154': 'Resveratrol',
        'PUBCHEM.COMPOUND:65064': 'Epigallocatechin Gallate',
        'PUBCHEM.COMPOUND:11338033': '4-(2,6-dichlorobenzamido)-N-(piperidin-4-yl)-1H-pyrazole-3-carboxamide',
        'PUBCHEM.COMPOUND:9444': 'Azacitidine', 'PUBCHEM.COMPOUND:30751': 'Fludarabine phosphate'
    }:
        raise RuntimeError(f"Incorrect result: {result5}")

    # Test get_curie() too while we're at it.
    result6 = get_curie('BRCA1')
    if result6 != 'NCBIGene:672':
        raise RuntimeError(f"Searching 'BRCA1' on NameLookup does not return NCBIGene:672 as expected but {result6}.")