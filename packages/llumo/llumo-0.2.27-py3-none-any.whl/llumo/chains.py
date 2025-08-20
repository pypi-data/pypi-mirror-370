import pandas as pd
from .helpingFuntions import *

class LlumoDataFrameResults(pd.DataFrame):
    _metadata=["evals","evalData","definationMapping"]

    def __init__(self, *args,evals=None,evalData=None,definationMapping=None,**kwargs):
        self.evals = evals or []
        self.evalData= evalData or []
        self.definationMapping= definationMapping or {}
        super().__init__(*args, **kwargs)

    @property
    def _constructor(self):
        # Needed so slicing operations return the same type
        return LlumoDataFrameResults

    def insights(self):
        
        if not self.evalData:
            print("No raw data available. Please run evaluateMultiple() first.")
            return None
        try:
            insights=[]
            reasonData,uniqueEdgecase=groupLogsByClass(self.evalData) # print(rawResults)
            
            for evalname in self.evals:
                uniqueclassesstring = ",".join(uniqueEdgecase.get(evalname, []))
                allReasons = []
                for edgeCase in reasonData[evalname]:
                    allReasons.extend(reasonData[evalname][edgeCase])
                
                evalDefinition = self.definationMapping.get(evalname, {}).get("definition", "")

                insights.append(getPlaygroundInsights(evalDefinition,uniqueclassesstring,allReasons))
            return insights
        except Exception as e:

            print("Can not genrate insights for this eval, please try again later.")


class LlumoDictResults(list):
    _metadata=["evals","evalData","definationMapping"]

    def __init__(self, *args,evals=None,evalData=None,definationMapping=None,**kwargs):
        self.evals = evals or []
        self.evalData= evalData or []
        self.definationMapping= definationMapping or {}
        super().__init__(*args, **kwargs) # This will handle list[dict]

    def insights(self):
        
        if not self.evalData:
            print("No raw data available. Please run evaluateMultiple() first.")
            return None
        try:
            insights=[]
            reasonData,uniqueEdgecase=groupLogsByClass(self.evalData) # print(rawResults)
            for evalname in self.evals:
                uniqueclassesstring = ",".join(uniqueEdgecase.get(evalname, []))
                allReasons = []
                for edgeCase in reasonData[evalname]:
                    allReasons.extend(reasonData[evalname][edgeCase])
                evalDefinition = self.definationMapping.get(evalname, {}).get("definition", "")
                insights.append(getPlaygroundInsights(evalDefinition,uniqueclassesstring,allReasons))
            return insights
        except Exception as e:
            print("Can not genrate insights for this eval, please try again later.")
    
    
for _cls in (LlumoDataFrameResults, LlumoDictResults):
    _cls.__name__ = "LlumoResults"
    _cls.__qualname__ = "LlumoResults"