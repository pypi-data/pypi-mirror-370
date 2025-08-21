import json
from typing import Any, List, Tuple

import requests

from .config import VER, BASE_URL_API


def Description():
    print(f"Tikos Platform {VER}")


def Version():
    print(VER)


def CreateExtractionRequest(url: str = "", orgId: str = "", orgToken: str = "", userId: str = "0",
                            numOfFiles: str = "1"):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/client/extractionrequest',
                           json={'orgId': orgId, 'token': orgToken, 'userId': userId, 'numOfFiles': numOfFiles})
    return result.status_code, result.reason, result.text


# Add Text
def AddExtractionText(url: str = "", requestId: str = "", authToken: str = "", text: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/client/storeprocesstext',
                           json={'requestId': requestId, 'authToken': authToken, 'chunk': text})
    return result.status_code, result.reason, result.text


# Add Files
def AddExtractionFile(url: str = "", requestId: str = "", authToken: str = "", fileObj: (str, str) = None):
    if url == "":
        url = BASE_URL_API

    payload = {'requestId': requestId, 'authToken': authToken}

    files = [
        ('json', ('payload.json', json.dumps(payload), 'application/json')),
        ('file', (fileObj[0], open(fileObj[1], 'rb')))
    ]

    result = requests.post(url + '/client/addprocessfile', files=files)
    return result.status_code, result.reason, result.text


def AddExtractionFiles(url: str = "", requestId: str = "", authToken: str = "", fileObjs: [(str, str)] = None):
    rtnResponses = []
    for fileObj in fileObjs:
        rtnVal = AddExtractionFile(url=url, requestId=requestId, authToken=authToken, fileObj=fileObj)
        rtnResponses.extend(rtnVal)

    return rtnResponses


def AddExtractionFileStream(url: str = "", requestId: str = "", authToken: str = "", fileObj: (str, Any) = None):
    if url == "":
        url = BASE_URL_API

    payload = {'requestId': requestId, 'authToken': authToken}

    files = [
        ('json', ('payload.json', json.dumps(payload), 'application/json')),
        ('file', (fileObj[0], fileObj[1]))
    ]

    result = requests.post(url + '/client/addprocessfile', files=files)
    return result.status_code, result.reason, result.text


def AddExtractionFileStreams(url: str = "", requestId: str = "", authToken: str = "", fileObjs: [(str, Any)] = None):
    rtnResponses = []
    for fileObj in fileObjs:
        rtnVal = AddExtractionFileStream(url=url, requestId=requestId, authToken=authToken, fileObj=fileObj)
        rtnResponses.extend(rtnVal)

    return rtnResponses


# EXTRACT
def ProcessExtract(url: str = "", requestId: str = "", authToken: str = "", jq: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/processextract',
                           json={'requestId': requestId, 'authToken': authToken, 'jq': jq})
    return result.status_code, result.reason, result.text


def ProcessExtractFile(url: str = "", requestId: str = "", authToken: str = "", fileName: str = "", jq: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/processextractfile',
                           json={'requestId': requestId, 'authToken': authToken, 'source': fileName, 'jq': jq})
    return result.status_code, result.reason, result.text


def GetExtract(url: str = "", requestId: str = "", authToken: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/getextract',
                           json={'requestId': requestId, 'authToken': authToken})
    return result.status_code, result.reason, result.text


def GetExtractDocs(url: str = "", requestId: str = "", authToken: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/getextractdocs',
                           json={'requestId': requestId, 'authToken': authToken})
    return result.status_code, result.reason, result.text


def GetGraphStructure(url: str = "", requestId: str = "", authToken: str = "", orgId: str = "", modelid: int = 1):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/getextractkg',
                           json={'requestId': requestId, 'authToken': authToken, 'orgId': orgId, 'X-TIKOS-MODEL': modelid})
    return result.status_code, result.reason, result.text

### Accept a file names and generate NER JSON of the (submitted) file
def GetGraphStructurePerDoc(url: str = "", requestId: str = "", authToken: str = "", orgId: str = "", refDoc: str = "", modelid: int = 1):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/getextractkgdoc',
                           json={'requestId': requestId, 'authToken': authToken, 'orgId': orgId, 'refdoc': refDoc, 'X-TIKOS-MODEL': modelid})
    return result.status_code, result.reason, result.text


def GenerateGraph(url: str = "", requestId: str = "", authToken: str = "", fileObj: str = "", payloadConfig: str = "", modelid: int = 1):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/generategraph',
                           json={'requestId': requestId, 'authToken': authToken, 'payload': fileObj, 'payloadconfig': payloadConfig, 'X-TIKOS-MODEL': modelid})
    return result.status_code, result.reason, result.text


### Accept a NER JSON object and create a graph of the (submitted) file
def GenerateGraphPerDoc(url: str = "", requestId: str = "", authToken: str = "", fileObj: str = "", refDoc: str = "", payloadConfig: str = "", modelid: int = 1):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/generategraphdoc',
                           json={'requestId': requestId, 'authToken': authToken, 'payload': fileObj, 'refdoc': refDoc, 'payloadconfig': payloadConfig, 'X-TIKOS-MODEL': modelid})
    return result.status_code, result.reason, result.text


### Accept a list of file names, that will be used to generate the NER generation automatically and create a full graph
def GenerateAutoGraph(url: str = "", requestId: str = "", authToken: str = "", orgId: str = "", refFiles: [str] = None, payloadConfig: str = "", modelid: int = 1):
    rtnResponses = []

    for fileObj in refFiles:
        responseCodeNER = ""
        responseReasonNER = ""
        responseTextNER = ""

        responseCodeGraph = ""
        responseReasonGraph = ""
        responseTextGraph = ""

        responseCodeNER, responseReasonNER, responseTextNER = GetGraphStructurePerDoc(url, requestId, authToken, orgId,
                                                                                      fileObj, modelid)

        if (responseCodeNER == 200) or (responseCodeNER == 201):
            jsonResponse = json.loads(responseTextNER)
            jsonLLMResponse = str(jsonResponse.get("llmExtraction"))

            responseCodeGraph, responseReasonGraph, responseTextGraph = GenerateGraphPerDoc(url, requestId, authToken,
                                                                                            jsonLLMResponse, fileObj, payloadConfig, modelid)

        rtnResponses.append((fileObj, (responseCodeNER, responseReasonNER, responseTextNER), (responseCodeGraph, responseReasonGraph, responseTextGraph)))

    return rtnResponses


def GetGraph(url: str = "", requestId: str = "", authToken: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/extractgraph',
                           json={'requestId': requestId, 'authToken': authToken})
    return result.status_code, result.reason, result.text


def GetGraphRelationships(url: str = "", requestId: str = "", authToken: str = "", fromNode: str = "",
                          toNode: str = ""):
    if url == "":
        url = BASE_URL_API

    payloadJson = '{"fromEntity": "' + fromNode + '", "toEntity": "' + toNode + '"}'

    result = requests.post(url + '/internals/extractgraph',
                           json={'requestId': requestId, 'authToken': authToken, 'payload': payloadJson})
    return result.status_code, result.reason, result.text


def GenerateSC(url: str = "", requestId: str = "", authToken: str = ""):
    pass


def GetGraphRetrieval(url: str = "", requestId: str = "", authToken: str = "", retrieveQuery: str = "", refdoc: str = "", modelid: int = 1):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/retrievalexplainer',
                           json={'requestId': requestId, 'authToken': authToken, 'retrieveq': retrieveQuery, 'refdoc': refdoc, 'X-TIKOS-MODEL': modelid})
    return result.status_code, result.reason, result.text


def GetGraphRetrievalWithDS(url: str = "", requestId: str = "", authToken: str = "", retrieveQuery: str = "", refdoc: str = "", modelid: int = 1):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/retrievalexplainerds',
                           json={'requestId': requestId, 'authToken': authToken, 'retrieveq': retrieveQuery, 'refdoc': refdoc, 'X-TIKOS-MODEL': modelid})
    return result.status_code, result.reason, result.text

def GetCustomerGraphRetrievalWithDS(url: str = "", requestId: str = "", authToken: str = "", clientid: str = "", clientauth: str = "", companyname: str = "", refdoc: str = "", modelid: int = 1):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/client/retrievalexplainerds',
                           json={'requestId': requestId, 'authToken': authToken, 'clientid': clientid, 'clientauth': clientauth, 'companyname': companyname, 'refdoc': refdoc, 'X-TIKOS-MODEL': modelid})
    return result.status_code, result.reason, result.text


# SC

def BuildSC(url: str = "", requestId: str = "", authToken: str = "", WType: str = "BIN", source: str = "",
            refCaseType: str = "", scConfig: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/buildsc',
                           json={'requestId': requestId, 'authToken': authToken, 'source': source,
                                 'refCaseType': refCaseType, 'scConfig': scConfig})
    return result.status_code, result.reason, result.text


def GetSimilarCase(url: str = "", requestId: str = "", authToken: str = "", WType: str = "BIN", refCaseType: str = "",
                   psCase: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/similaritysc',
                           json={'requestId': requestId, 'authToken': authToken, 'WType': WType,
                                 'refCaseType': refCaseType, 'psCase': psCase})
    return result.status_code, result.reason, result.text

# Reasoning:Base
def GetReasoning(url: str = "", requestId: str = "", authToken: str = "", payloadId: str = "", WType: str = "BIN", refCaseType: str = "",
                   psCase: str = "", refDoc: str = "", payloadConfig: str = "", RType: str = "CAUSAL", nType:int = 0):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/reasoningsc',
                           json={'payloadId': payloadId, 'requestId': requestId, 'authToken': authToken, 'WType': WType,
                                 'refCaseType': refCaseType, 'psCase': psCase, 'refdoc': refDoc,
                                 'payloadconfig': payloadConfig, 'RType': RType, 'nType': nType})
    return result.status_code, result.reason, result.text

# Model Embedding
def UploadModel(url: str = "", requestId: str = "", authToken: str = "", modelObj: (str, Any) = None, modelType: str = "DNN"):
    if url == "":
        url = BASE_URL_API

    payload = {'requestId': requestId, 'authToken': authToken, 'modelType': modelType}

    files = [
        ('json', ('payload.json', json.dumps(payload), 'application/json')),
        ('file', (modelObj[0], modelObj[1]))
    ]

    result = requests.post(url + '/internals/embeddingmodelupload', files=files)
    return result.status_code, result.reason, result.text

def UploadModelConfig(url: str = "", requestId: str = "", authToken: str = "", modelConfig: (str, Any) = None, modelSchema: (str, Any) = None, modelType: str = "DNN"):
    if url == "":
        url = BASE_URL_API

    payload = {'requestId': requestId, 'authToken': authToken, 'modelType': modelType}

    files = [
        ('json', ('payload.json', json.dumps(payload), 'application/json')),
        ('filemodelparamconfig', (modelConfig[0], modelConfig[1])),
        ('filemodelconfig', (modelSchema[0], modelSchema[1]))
    ]

    result = requests.post(url + '/internals/embeddingconfigupload', files=files)
    return result.status_code, result.reason, result.text

def UploadModelCaseData(url: str = "", requestId: str = "", authToken: str = "", caseDataSet: (str, Any) = None):
    if url == "":
        url = BASE_URL_API

    payload = {'requestId': requestId, 'authToken': authToken}

    files = [
        ('json', ('payload.json', json.dumps(payload), 'application/json')),
        ('filetd', (caseDataSet[0], caseDataSet[1]))
    ]

    result = requests.post(url + '/internals/embeddingdataupload', files=files)
    return result.status_code, result.reason, result.text

def ProcessModel(url: str = "", requestId: str = "", authToken: str = "", refCaseType: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/embeddingcreatesc',
                           json={'requestId': requestId, 'authToken': authToken, 'refCaseType': refCaseType})
    return result.status_code, result.reason, result.text
