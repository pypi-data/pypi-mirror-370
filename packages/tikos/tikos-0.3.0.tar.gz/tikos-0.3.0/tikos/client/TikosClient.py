import json
from typing import Any, List, Tuple
import concurrent.futures
import requests

from tikos.config import VER, BASE_URL_API
from tikos.tikos import (
    AddExtractionFileStream,
    ProcessExtractFile,
    GetGraphStructurePerDoc,
    GenerateGraphPerDoc,
    GetGraph,
    GetGraphRetrievalWithDS,
    BuildSC,
    GetReasoning,
    UploadModel,
    UploadModelConfig,
    UploadModelCaseData,
    ProcessModel)

class TikosClient(object):

    def __init__(self, url: str = "", requestId: str = "", authToken: str = ""):
        if url == "":
            self.url = BASE_URL_API
        else:
            self.url = url
        self.requestId = requestId
        self.authToken = authToken

    def __AddFileBase(self, fn, fs):
        try:
            rtnValAdd = AddExtractionFileStream(url=self.url, requestId=self.requestId, authToken=self.authToken,
                                                fileObj=(fn, fs))
            return fn, rtnValAdd
        except Exception as e:
            return False, False

    def __ProcessFileBase(self, fn, fs):
        try:
            jq_schema = ".[]"

            rtnValAdd = AddExtractionFileStream(url=self.url, requestId=self.requestId, authToken=self.authToken,
                                                fileObj=(fn, fs))

            rtnvalProcess = ProcessExtractFile(
                url=self.url,
                requestId=self.requestId,
                authToken=self.authToken,
                fileName=fn,
                jq=jq_schema,
            )

            return fn, rtnValAdd, rtnvalProcess
        except Exception as e:
            return False, False, False

    '''
        Multithreading supported file processing function
        Accepts: List of filenames and file paths as a tuple
    '''
    def addProcessFiles(self, fileObjs: [(str, str)] = None):
        return_dict = []
        futures = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for fileObj in fileObjs:
                fn, fl = fileObj
                fs = open(fl, "rb")

                futures.append(executor.submit(self.__ProcessFileBase, fn=fn, fs=fs))

            for future in concurrent.futures.as_completed(futures):
                return_dict.append(future)

        return return_dict

    '''
        Multithreading supported file addition function
        Accepts: List of filenames and file stream as a tuple
    '''
    def addFileStreams(self, fileObjs: [(str, Any)] = None):

        return_dict = []
        futures = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for fileObj in fileObjs:
                fn, fs = fileObj

                futures.append(executor.submit(self.__AddFileBase, fn=fn, fs=fs))

            for future in concurrent.futures.as_completed(futures):
                return_dict.append(future)

        return return_dict

    '''
        Multithreading supported combined file addition and processing function
        Accepts: List of filenames and file stream as a tuple
    '''
    def addProcessFileStreams(self, fileObjs: [(str, Any)] = None):
        return_dict = []
        futures = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for fileObj in fileObjs:
                fn, fs = fileObj

                futures.append(executor.submit(self.__ProcessFileBase, fn=fn, fs=fs))

            for future in concurrent.futures.as_completed(futures):
                return_dict.append(future)

        return return_dict

    def __ProcessGetGraphStructureBase(self, fn):
        try:
            rtnValG = GetGraphStructurePerDoc(
                url=self.url,
                requestId=self.requestId,
                authToken=self.authToken,
                refDoc=fn,
                modelid=6,
            )

            return fn, rtnValG
        except Exception as e:
            return False, False

    '''
        Multithreading supported graph structure generation function
        Accepts: List of filenames as contexes
    '''
    def generateGraphStructures(self, contexts: [str] = None):

        return_dict = []
        futures = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for context in contexts:
                futures.append(executor.submit(self.__ProcessGetGraphStructureBase, fn=context))

            for future in concurrent.futures.as_completed(futures):
                return_dict.append(future)

        return return_dict

    def __ProcessGenerateGraphBase(self, fn):
        try:
            rtnValGS = GetGraphStructurePerDoc(
                url=self.url,
                requestId=self.requestId,
                authToken=self.authToken,
                refDoc=fn,
                modelid=6,
            )

            status_code, reason, text = rtnValGS

            rtnValG = None
            if (status_code == 200) or (status_code == 201):
                jsonResponse = json.loads(text)
                jsonLLMResponse = str(jsonResponse.get("llmExtraction"))

                rtnValG = GenerateGraphPerDoc(
                    url=self.url,
                    requestId=self.requestId,
                    authToken=self.authToken,
                    fileObj=jsonLLMResponse,
                    refDoc=fn,
                    modelid=6,
                )

            return fn, rtnValGS, rtnValG
        except Exception as e:
            return False, False, False

    '''
        Multithreading supported graph creation function
        Accepts: List of filenames as contexes
    '''
    def createGraph(self, contexts: [str] = None):
        return_dict = []
        futures = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for context in contexts:
                futures.append(executor.submit(self.__ProcessGenerateGraphBase, fn=context))

            for future in concurrent.futures.as_completed(futures):
                return_dict.append(future)

        return return_dict

    '''
        Graph structure extraction function
    '''
    def getGraph(self):
        rtnVal = GetGraph(
            url=self.url,
            requestId=self.requestId,
            authToken=self.authToken
        )

        return rtnVal

    '''
        Graph retrieval function
        Accepts: Filenames as context and query
    '''
    def getGraphRetrieval(self, context: str = "", retrieveQuery: str = ""):
        rtnVal = GetGraphRetrievalWithDS(
            url=self.url,
            requestId=self.requestId,
            authToken=self.authToken,
            retrieveQuery=retrieveQuery,
            refdoc=context
        )
        return rtnVal

    '''
        Sequential Collection creation function
        Accepts: Case-Type, Data File name as context, Weight Type and Sequential Collection Config
    '''
    def createSequentialCollection(self, caseType: str = "", context: str = "", wType: str = "BIN", scConfig: str = ""):
        rtnVal = BuildSC(
            url=self.url,
            requestId=self.requestId,
            authToken=self.authToken,
            source=context,
            refCaseType=caseType,
            WType=wType,
            scConfig = scConfig
        )

        return rtnVal

    '''
        Sequential Collection reasoning function 
        Accepts: Case-Type, Data File name as context, problem space case as 
        a JSON object string, Weight Type and Reasoning Type
    '''
    def generateReasoning(self, caseType: str = "", context: str = "", problemSpaceCase: str = "", wType: str = "BIN",
                          rType: str = "CAUSAL", nType:int = 0):

        rtnVal = GetReasoning(
            url=self.url,
            requestId=self.requestId,
            authToken=self.authToken,
            WType=wType,
            refCaseType=caseType,
            psCase=problemSpaceCase,
            refDoc=context,
            RType=rType,
            nType=nType,
        )

        return rtnVal

    '''
        Embedded model Upload function
        Accepts: filenames and file stream as a tuple on model
    '''
    def uploadEmbeddingModel(self, modelObj: (str, Any) = None, modelType: str = "DNN"):
        rtnValAdd = UploadModel(url=self.url, requestId=self.requestId, authToken=self.authToken,
                                modelObj=modelObj, modelType=modelType)
        return rtnValAdd

    '''
        Embedded model Upload function
        Accepts: filenames and file stream as a tuple on model config and model schema
    '''
    def uploadEmbeddingConfig(self, modelConfig: (str, Any) = None, modelSchema: (str, Any) = None, modelType: str = "DNN"):
        rtnValAdd = UploadModelConfig(url=self.url, requestId=self.requestId, authToken=self.authToken,
                                      modelConfig=modelConfig, modelSchema=modelSchema, modelType=modelType)
        return rtnValAdd

    '''
        Upload selected Knowledge Cases (feature sets), that will build the initial Sequential Collection case base
    '''
    def uploadModelCaseData(self, caseDataSet: (str, Any) = None):
        rtnVal = UploadModelCaseData(
            url=self.url,
            requestId=self.requestId,
            authToken=self.authToken,
            caseDataSet = caseDataSet
        )

        return rtnVal

    '''
        Process the upload DNN model with Synapses Logger embedding and dynamically creating the Sequential Collection case base
    '''

    def processEmbeddedModel(self, caseType: str = ""):
        rtnVal = ProcessModel(
            url=self.url,
            requestId=self.requestId,
            authToken=self.authToken,
            refCaseType=caseType
        )

        return rtnVal

    '''
        Foundational Model Profiling function
        Accepts: Case-Type, Network Type, Model Name, Prompt List, Keyword List and the Token Length
    '''
    # Reasoning:Base
    def __GetFMProfilingBase(self, url: str = "", requestId: str = "", authToken: str = "", refCaseType: str = "", nType: int = 0,
                           modelName: str = "", promptTextList: List[str] = [], keyList:List[str] = [],
                           tokenLen:int = 100):
        if url == "":
            url = BASE_URL_API

        result = requests.post(url + '/internal/profiling',
                               json={'requestId': requestId, 'authToken': authToken,
                                     'refCaseType': refCaseType,
                                     'nType': nType, 'modelName': modelName, 'promptTextList': promptTextList,
                                     'keyList': keyList, 'tokenLen': tokenLen})
        return result.status_code, result.reason, result.text

    def generateFMProfiling(self, refCaseType: str = "", nType: int = 2, modelName: str = "meta-llama/Llama-3.2-1B", promptTextList: List[str] = [], keyList:List[str] = [], tokenLen:int = 100):

        rtnVal = self.__GetFMProfilingBase(
            url=self.url,
            requestId=self.requestId,
            authToken=self.authToken,
            refCaseType=refCaseType,
            nType=nType,
            modelName=modelName,
            promptTextList=promptTextList,
            keyList=keyList,
            tokenLen=tokenLen,
        )

        return rtnVal