import json
from typing import Any, List, Tuple
import concurrent.futures
import requests

from tikos.config import VER, BASE_URL_API

class Tooling(object):

    def __init__(self, url: str = "", requestId: str = "", authToken: str = ""):
        if url == "":
            self.url = BASE_URL_API
        else:
            self.url = url
        self.requestId = requestId
        self.authToken = authToken

    '''
        Foundational Model Profiling Matching tool
        Accepts: PayloadId, Reference Docs, Case-Type, Network Type, Reasoning Type, Similarity Type, NMP model Type, Payload Config, Network Type, Model Name, Prompt List and the Token Length
    '''
    # Reasoning:Base
    def __GetProfileMatchingBase(self, url: str = "", requestId: str = "", authToken: str = "", payloadId: str = "", refdoc: str = "", refCaseType: str = "", RType: str = "", WType: str = "", llmmodel: int = 2, payloadconfig: str = "", nType: int = 0,
                           modelName: str = "", promptTextList: List[str] = [], tokenLen:int = 100):
        if url == "":
            url = BASE_URL_API

        result = requests.post(url + '/tooling/profiling',
                               json={'requestId': requestId, 'authToken': authToken, 'payloadId': payloadId, 'refdoc': refdoc,
                                     'refCaseType': refCaseType, 'RType': RType, 'WType': WType, 'X-TIKOS-MODEL': llmmodel, 'payloadconfig': payloadconfig,
                                     'nType': nType, 'modelName': modelName, 'promptTextList': promptTextList, 'tokenLen': tokenLen})
        return result.status_code, result.reason, result.text

    def generateFMProfileMatching(self, payloadId: str = "", refdoc: str = "", refCaseType: str = "", RType: str = "DEEPCAUSAL_PROFILE_PATTERN_ADV", WType: str = "PROFILING", llmmodel: int = 2, payloadconfig: str = "", nType: int = 2,
                           modelName: str = "meta-llama/Llama-3.2-1B", promptTextList: List[str] = [], tokenLen:int = 100):

        rtnVal = self.__GetProfileMatchingBase(
            url=self.url,
            requestId=self.requestId,
            authToken=self.authToken,
            payloadId=payloadId,
            refdoc=refdoc,
            refCaseType=refCaseType,
            RType=RType,
            WType=WType,
            llmmodel=llmmodel,
            payloadconfig=payloadconfig,
            nType=nType,
            modelName=modelName,
            promptTextList=promptTextList,
            tokenLen=tokenLen,
        )

        return rtnVal

    '''
        Foundational Model Profiling Guard Railing tool
        Accepts: PayloadId, Reference Docs, Case-Type, Network Type, Reasoning Type, Similarity Type, NMP model Type, Payload Config, Network Type, Model Name, Prompt List and the Token Length
    '''
    # Reasoning:Base
    def __GetProfileGuardRailingBase(self, url: str = "", requestId: str = "", authToken: str = "", payloadId: str = "",
                                 refdoc: str = "", refCaseType: str = "", RType: str = "", WType: str = "",
                                 llmmodel: int = 2, payloadconfig: str = "", nType: int = 0,
                                 modelName: str = "", promptTextList: List[str] = [], tokenLen: int = 100):
        if url == "":
            url = BASE_URL_API

        result = requests.post(url + '/tooling/profiling/guardrailing',
                               json={'requestId': requestId, 'authToken': authToken, 'payloadId': payloadId,
                                     'refdoc': refdoc,
                                     'refCaseType': refCaseType, 'RType': RType, 'WType': WType,
                                     'X-TIKOS-MODEL': llmmodel, 'payloadconfig': payloadconfig,
                                     'nType': nType, 'modelName': modelName, 'promptTextList': promptTextList,
                                     'tokenLen': tokenLen})
        return result.status_code, result.reason, result.text

    def generateFMProfileGuardRailing(self, payloadId: str = "", refdoc: str = "", refCaseType: str = "", RType: str = "DEEPCAUSAL_PROFILE_PATTERN_ADV", WType: str = "PROFILING", llmmodel: int = 2, payloadconfig: str = "", nType: int = 2,
                           modelName: str = "meta-llama/Llama-3.2-1B", promptTextList: List[str] = [], tokenLen:int = 100):

        rtnVal = self.__GetProfileGuardRailingBase(
            url=self.url,
            requestId=self.requestId,
            authToken=self.authToken,
            payloadId=payloadId,
            refdoc=refdoc,
            refCaseType=refCaseType,
            RType=RType,
            WType=WType,
            llmmodel=llmmodel,
            payloadconfig=payloadconfig,
            nType=nType,
            modelName=modelName,
            promptTextList=promptTextList,
            tokenLen=tokenLen,
        )

        return rtnVal