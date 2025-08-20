Translator Components
=====================

## Introduction

Translator is a National Center for Advancing Translational Sciences (NCATS) program that aims to accelerate the process of translating basic scientific discoveries into new therapies.
TCT is a Python package that provides a set of tools for building and managing Translator components.
TCT is designed to be used by developers who want to build components that can be used in the Translator ecosystem.
If you would like to direct interact with the Translator UI, please visit https://ui.transltr.io/

## Key components

In the translator ecosystem, there are several groups of components that can be used for standaradization, Translator standard API development, reasoning, and visualization.

### Translator Component Toolkit (TCT)

A python library and related jupyter notebooks for users to explore the APIs in Translator with functionalities for pathfinder etc. It would be useful for developers or computational biologists who would like to build their own use cases using the resources in the Translator ecosystem. Key functions currently available include 1) Neighborhood finding: to explore anything that is connected to an entity of interest;  2) PathFinder: to find the intermediate nodes between two entities; 3) Network annotation: to find the interactions among the entities of interest. 

TCT link: https://github.com/NCATSTranslator/Translator_component_toolkit. 

### Biolink

- Tree-viz-biolink: https://biolink.github.io/biolink-model/categories.html
- Biolink repo: https://biolink.github.io/biolink-model/
- Biolink Model Toolkit (BMT): A python library for working with the biolink-model.
- BMT codebase: https://github.com/biolink/biolink-model-toolkit 
- Latest release: https://pypi.org/project/bmt/ 

--------------------------------------------------------------------------------------------------

###  Knowledge source related:

**KGX_format:** KGX is a format for distributing Biolink-compliant knowledge graphs. 

**KGXTool:** The translator team also developed a KGX tool that allows transforming KGs from one graph formalism to another, creating KGs or subgraphs, merging two or more KGs, validating KG against the Biolink Model etc. 

**KGXTool link:** https://github.com/biolink/kgx/blob/master/README.md

**KGhub:** KGhub is a resource that hosts a number of KGX formatted biomedical knowledge graphs. 

**KGhub link:** https://kghub.org/kg-registry/

----------------------------------------------------------------------------------------------------

### Translator API standard (TRAPI)

**TRAPI standard:** A data model and API definition that enables query by graph template and responses by graph and ranked results. It will be useful for anyone who 1) wants to write code that queries existing Translator components; 2) build a KP/tool that integrates into the Translator ecosystem; 3) reuse a carefully thought out schema for other projects that aim to pose/answer biomedical questions via graph template. 

**TRAPI standard repo:** https://github.com/NCATSTranslator/ReasonerAPI. 

----------------------------------------------------------------------------------------------------

#### TRAPI validator:

A python library of methods to validate TRAPI and Biolink Model compliance of biomedical data processing software. It would be useful for developers of Biolink Model components accessed using TRAPI web services. Key functions include: given a TRAPI response (or comparable knowledge query inputs), validates compliance to TRAPI and Biolink Model standards (current release or user specified releases of the standards). 

**TRAPI validator link:** https://github.com/NCATSTranslator/reasoner-validator

----------------------------------------------------------------------------------------------------

#### Translator APIs:
Translator KG APIs are a set of APIs that follows the TRAPI standard and biolink standard to explore underline biomedical knowledge graphs. 

Link: https://smart-api.info/registry/translator?tags=translator&tags.name=TRAPI

----------------------------------------------------------------------------------------------------
#### Translator API deployment tool:

**Plover description:** an in-memory knowledge graph database server system, built for Translator. Potential users include knowledge providers (who might use PloverDB to host a KP); ARAs (who can programmatically access KPs hosted in PloverDB); other application developers. Key functions: /query, /meta_knowledge_graph, /sri_test_triples, /code_version, /logs. 

**Plover link:** https://github.com/RTXteam/PloverDB

#### knowledge graph node normalization:

**NodeNorm description:** An API based tool to normalize identifiers (such as genes, diseases, drugs). The potential users include anybody who wants to translate different identifier systems into a single consistent set of identifiers, such as bioinformaticians.  

**NodeNorm Links:** https://nodenorm.transltr.io/docs (Translator Prod); https://nodenormalization-sri.renci.org/docs (RENCI Dev).

----------------------------------------------------------------------------------------------------
**Name Resolver:** An API for named entity linker for Translator. It allows a user to look up possible CURIEs for biomedical terms. It will be useful for anybody who would like to look up a CURIE for biomedical concepts. 

**NameRes Link:** https://name-lookup.transltr.io/ (Translator Prod); https://name-resolution-sri.renci.org/docs (RENCI Dev). 

----------------------------------------------------------------------------------------------------

##### To be continued
