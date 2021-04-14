# Document-level Grammatical Error Correction

This repository contains the scripts used to generate the document-level evaluation data in:  

> Zheng Yuan and Christopher Bryant. 2021. **Document-level grammatical error correction**. In Proceedings of the Sixteenth Workshop on Innovative Use of NLP for Building Educational Applications. Kyiv, Ukraine.

## Overview

We evaluate on the [FCE](https://www.aclweb.org/anthology/P11-1019/), [CoNLL-2014](https://www.aclweb.org/anthology/W14-1701/) and [BEA-2019](https://www.aclweb.org/anthology/W19-4406/) shared task datasets.  

The FCE and BEA-2019 datasets are available from the [BEA-2019 shared task website](https://www.cl.cam.ac.uk/research/nl/bea2019st/#data), while the CoNLL-2014 data is available from the [CoNLL-2014 shared task website](https://www.comp.nus.edu.sg/~nlp/conll14st.html).  

#### Direct download links:

FCE: [download](https://www.cl.cam.ac.uk/research/nl/bea2019st/data/fce_v2.1.bea19.tar.gz)  
CoNLL-2014: [download](https://www.comp.nus.edu.sg/~nlp/conll14st/conll14st-test-data.tar.gz)  
BEA-2019: [download](https://www.cl.cam.ac.uk/research/nl/bea2019st/data/wi+locness_v2.1.bea19.tar.gz)  

## Preprocessing

The specific files we use are located in:  
FCE: `fce/json/fce.test.json`  
CoNLL-2014: `conll14st-test-data/noalt/official-2014.[01].sgml`  
BEA-2019: `wi+locness/json/[ABCN].dev.json`  

Since the main `json_to_doc_m2.py` script takes a json file as input, the first step is to convert the CoNLL-2014 sgml to json format. This can be achieved using the following command:

`python3 sgml_to_json.py <sgml_dir> -out conll2014.test.json`

Where `<sgml_dir>` is the path to a directory that contains both `official-2014.0.sgml` and `official-2014.1.sgml` files. Note that this script also filters a small number of rare edits (e.g. edits longer than 40 characters).  

For BEA-2019, the only preprocessing is to combine the different level json files into a single file:  

`cat [ABCN].dev.json > ABCN.dev.json`  

There is no preprocesing for the FCE.  

## Usage

The main `json_to_doc_m2.py` script takes a BEA-2019 style json file as input and produces an M2 file as output. It is a variant of the `json_to_m2.py` script released in the BEA-2019 shared task. The only prerequisite is [ERRANT](https://github.com/chrisjbryant/errant). We used ERRANT v2.1 in our paper. The command is run as follows:

`python3 json_to_doc_m2.py <json_file> -out <output_m2> -gold -docs`  

Where `<json_file>` is the input json file outlined in the Preprocessing step, and `<output_m2>` is the name of the output M2 file. The `-gold` flag ensures the output file uses human annotated edits (rather than `-auto` edits extracted by ERRANT), while the `-docs` flag generates the document-level M2 file. If the `-docs` flag is not specified, the command will produce a sentence-level M2 file. 

