import time
import uuid
import numpy as np
from datetime import datetime
from dateutil import parser
import requests
import json
import base64
import os
import re
import openai
import google.generativeai as genai
from collections import defaultdict


from .models import  _MODEL_METADATA,  AVAILABLEMODELS
subscriptionUrl = "https://app.llumo.ai/api/workspace/record-extra-usage"
getStreamdataUrl = "https://app.llumo.ai/api/data-stream/all"
createPlayUrl = "https://app.llumo.ai/api/New-Eval-API/create-new-eval-playground"
deletePlayUrl = "https://app.llumo.ai/api/New-Eval-API/new-upload-flow/delete-columnlist-in-playground"
uploadColList = (
    "https://app.llumo.ai/api/New-Eval-API/new-upload-flow/uploadColumnListInPlayground"
)
uploadRowList = (
    "https://app.llumo.ai/api/New-Eval-API/new-upload-flow/uploadRowsInDBPlayground"
)
createInsightUrl="https://app.llumo.ai/api/external/generate-insight-from-eval-for-sdk"

getCustomAnalyticsUrl="https://app.llumo.ai/api/workspace/get-all-analytics"

def getProcessID():
    return f"{int(time.time() * 1000)}{uuid.uuid4()}"


def getInputPopulatedPrompt(promptTemplate, tempObj):
    for key, value in tempObj.items():
        promptTemplate = promptTemplate.replace(f"{{{{{key}}}}}", value)
    return promptTemplate


def costColumnMapping(costResults, allProcess):
    # this dict will store cost column data for each row
    cost_cols = {}

    compressed_prompt = []
    compressed_prompt_output = []
    cost = []
    cost_saving = []

    for record in allProcess:
        cost_cols[record] = []
        for item in costResults:
            if list(item.keys())[0].split("-")[0] == record.split("-")[0]:
                cost_cols[record].append(list(item.values())[0])

    for ky, val in cost_cols.items():
        try:
            compressed_prompt.append(val[0])
        except IndexError:
            compressed_prompt.append("error occured")

        try:
            compressed_prompt_output.append(val[1])
        except IndexError:
            compressed_prompt_output.append("error occured")

        try:
            cost.append(val[2])
        except IndexError:
            cost.append("error occured")

        try:
            cost_saving.append(val[3])
        except IndexError:
            cost_saving.append("error occured")

    return compressed_prompt, compressed_prompt_output, cost, cost_saving


def checkUserHits(
    workspaceID,
    hasSubscribed,
    trialEndDate,
    subscriptionEndDate,
    remainingHits,
    datasetLength,
):
    # Get the current date (only the date part)
    current_date = datetime.now().date()

    # Parse trialEndDate if provided
    if trialEndDate is not None:
        try:
            trialEndDate = parser.parse(trialEndDate).date()
        except Exception:
            return {"success": False, "message": "Invalid trialEndDate format"}

    # Parse subscriptionEndDate if provided
    if subscriptionEndDate is not None:
        try:
            subscriptionEndDate = parser.parse(subscriptionEndDate).date()
        except Exception:
            return {"success": False, "message": "Invalid subscriptionEndDate format"}

    # If user is on a free trial
    if not hasSubscribed and trialEndDate is not None:
        if current_date > trialEndDate:
            return {"success": False, "message": "Trial expired. Access denied"}

        if remainingHits < datasetLength or remainingHits <= 0:
            return {"success": False, "message": "Trial Hits Exhausted"}

    else:
        if subscriptionEndDate and current_date > subscriptionEndDate:
            return {"success": False, "message": "Subscription expired. Access denied."}


        
        if remainingHits <= 0 or remainingHits < datasetLength:
            if workspaceID:
                workspaceID=str(workspaceID)
                headers = {
                    "Authorization": f"Bearer {base64.b64encode(workspaceID.encode()).decode()}",
                    "Content-Type": "application/json",
                }
                reqBody = {"unitsToSet": 1}
                responseBody = requests.post(
                    url=subscriptionUrl, json=reqBody, headers=headers
                )
                response = json.loads(responseBody.text)

                proceed = response.get("execution", "")
                print(proceed)

                if proceed:
                    return {"success": True, "message": "Hits added and access granted."}
            else:
                return {"success": False, "message": "Workspace ID is required for subscription."}
    return {"success": True, "message": "Access granted."}


def getStreamId(workspaceID: str, token, dataStreamName):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    reqBody = {"workspaceID": workspaceID}
    response = requests.post(url=getStreamdataUrl, json=reqBody, headers=headers)

    if response.status_code == 200:
        responseJson = response.json()
        data = responseJson.get("data", [])

        # Find stream by name
        matchedStream = next(
            (stream for stream in data if stream.get("name") == dataStreamName), None
        )

        if matchedStream:

            return matchedStream.get("dataStreamID")

        else:
            print(f"No stream found with name: {dataStreamName}")
            return None
    else:
        print("Error:", response.status_code, response.text)
        return None


def createEvalPlayground(email: str, workspaceID: str):
    url = createPlayUrl
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "workspaceID": workspaceID,
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        try:
            responseJson = response.json()
            # print(responseJson)
            return responseJson.get("data", {}).get("playgroundID", None)

        except Exception as e:
            print("Failed to parse JSON:", e)
            return None
    else:
        print("Error:", response.status_code, response.text)
        return None


def deleteColumnListInPlayground(workspaceID: str, playgroundID: str):
    url = deletePlayUrl
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "workspaceID": workspaceID,
        "playgroundID": playgroundID,
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        try:

            return response.json()
        except Exception as e:
            print("⚠️ Failed to parse JSON:", e)
            return None
    else:
        print("❌ Error:", response.status_code, response.text)
        return None

def createColumn(workspaceID, dataframe, playgroundID, promptText=None,queryColName=None,
                 outputColName= "output",dataStreamName=None,definationMapping=None,evalOutputMap = None,customAnalytics=[]):
    if len(dataframe) > 100:
        dataframe = dataframe.head(100)
        print("⚠️ Dataframe truncated to 100 rows for upload.")

    coltemplate = {
        "workspaceID": workspaceID,
        "playgroundID": playgroundID,
        "columnListToUpload": [],
    }
    allEvals = ['Response Completeness', 'Response Bias', 'Response Harmfulness', 'Input Toxicity', 'Input Harmfulness', 'Context Utilization', 'Relevance Retention', 'Semantic Cohesion', 'Final Task Alignment', 'Tool Reliability', 'Response Correctness', 'Response Toxicity', 'Input Bias', 'Input Relevancy', 'Redundancy Reduction', 'Response Sentiment', 'Tool Selection Accuracy', 'Stepwise Progression', 'Hallucination', 'Faithfulness', 'Answer Relevancy', 'Context Precision', 'Answer Similarity', 'Harmfulness', 'Maliciousness', 'Coherence', 'Answer Correctness', 'Context Recall', 'Context Entity Recall', 'Conciseness', 'customEvalColumn', 'Groundedness', 'Memory Utilization', 'Input Relevancy (Multi-turn)','PII Check','Prompt Injection']
    try:
        allEvals.extend(list(customAnalytics.keys()))
    except Exception as e:
        pass
    evalDependencies =  checkDependency(_returnDepMapping=True,customevals=customAnalytics)
    print(allEvals)
    # Create a mapping of column names to unique column IDs
    columnIDMapping = {}

    # Iterate over each column in the dataframe
    for indx, col in enumerate(dataframe.columns):
        # Generate a unique column ID using uuid
        columnID = str(uuid.uuid4().hex[:8])

        columnIDMapping[col] = columnID


        # if col.startswith('output') and promptText!=None:
        #     # For output columns, create the prompt template with promptText
        #     if promptText:
        #         # Extract variables from promptText and set them as dependencies
        #         dependencies = []
        #
        #         # Find variables inside {{variable}}
        #         variables = re.findall(r'{{(.*?)}}', promptText)
        #
        #         # Loop through each variable and check if it exists as a column name
        #         for var in variables:
        #             varName = var.strip()
        #             if varName in columnIDMapping:  # Check if the variable is a column name
        #                 dependencies.append(columnIDMapping[varName])  # Add its columnID
        #
        #         # Now update the template for the output column
        #
        #         template={
        #             "provider": "OPENAI",
        #             "model": "GPT_4o",
        #             "promptText": promptText,
        #             "modelOptions": {
        #                 "temperature": 0,
        #                 "frequencyPenalty": 0,
        #                 "presencePenalty": 0,
        #                 "maxToken": 8192
        #             },
        #             "toolConfig": "none",
        #             "concurrency": "",
        #             "outputType": "STRING",
        #             "isPromptSelected": True,
        #             "isSmartPromptSelected": False,
        #             "dependency": dependencies,  # Use the dependencies extracted from promptText
        #             "columnID": columnID,  # Use the generated column ID
        #             "label": col,
        #             "type": "PROMPT",
        #             "order": indx,
        #         }

        if col.startswith('context') and dataStreamName != None :
            if queryColName and dataStreamName:
                dependencies = []
                dependencies.append(columnIDMapping[queryColName])
                template = {
                    "variableType": "STRING",
                    "dependency": dependencies,
                    "dataStreamName": dataStreamName,
                    "query": columnIDMapping[queryColName],
                    "columnID": columnID,  # Use the generated column ID
                    "label": "context",
                    "type": "DATA_STREAM",
                    "order": indx}


        elif any(col.startswith(eval + "_") or col == eval for eval in allEvals) and not " Reason" in col and promptText is not None :
            if evalOutputMap != None:
                outputColName = evalOutputMap[col]
            else:
                outputColName = outputColName
            dependencies = []
            variables = re.findall(r'{{(.*?)}}', promptText)

                # Loop through each variable and check if it exists as a column name
            for var in variables:
                varName = var.strip()
                if varName in columnIDMapping:  # Check if the variable is a column name
                    dependencies.append(columnIDMapping[varName])

            dependencies.append(columnIDMapping[outputColName])  # Add the output column ID

            longDef = definationMapping.get(col.rsplit("_",1)[0], {}).get('definition', "")
            shortDef =definationMapping.get(col.rsplit("_",1)[0], {}).get('briefDefinition', "")
            enum = col.rsplit("_",1)[0].upper().replace(" ","_")

            template = {
      "analytics": [
        col.lower().replace(" ","_")
      ],
      "evaluationMetric": "ALL",
      "evaluationModel": "LLUMO_EVALLM",
      "selectPrompt": None if "output" not in columnIDMapping.keys() else columnIDMapping["output"],
      "scoreCondition": "GREATER_THAN",
      "scoreValue": "50",
      "scoreResult": "PASS",
      "llmKpi": col.rsplit("_",1)[0],
      "setRules": True,
      "type": "EVAL",
      "evalType": "LLM",
      "similarityMetric": None,
      "embeddingModel": None,
      "groundTruth": None if "groundTruth" not in columnIDMapping.keys() else columnIDMapping["groundTruth"],
      "dataStream": None,
      "context":None if "context" not in columnIDMapping.keys() else columnIDMapping["context"],
      "dependency":[columnIDMapping[col] if dep == "output" else columnIDMapping[dep] for dep in evalDependencies[col.rsplit("_", 1)[0]]],
      "query": None if "query" not in columnIDMapping.keys() else columnIDMapping["query"],
    "tools":None if "tools" not in columnIDMapping.keys() else columnIDMapping["tools"],
    "messageHistory":None if "messageHistory" not in columnIDMapping.keys() else columnIDMapping["messageHistory"],
      "hallucinationFields": {
        "query": None,
        "context": None,
        "output": None
      },
      "definition": longDef,
      "analyticsENUM": enum,
      "prompt": shortDef,
      "analyticsName": col.rsplit("_",1)[0],
      "columnID": columnID,
      "label": col,
      "order": indx
    }

        elif col.endswith(' Reason') and promptText!=None:
            continue


        else:

            template = {
                "label": col,  # Label is the column name
                "type": "VARIABLE",  # Default type for non-output columns
                "variableType": "STRING",
                "order": indx,
                "columnID": columnID,  # Use the generated column ID
            }

        # Append the template to the column list
        coltemplate["columnListToUpload"].append(template)

    # Prepare the row template structure
    rowTemplate = {
        "workspaceID": workspaceID,
        "playgroundID": playgroundID,
        "dataToUploadList": [],
        "columnList": coltemplate["columnListToUpload"],
    }

    # Populate dataToUploadList with rows from the dataframe
    for indx, row in dataframe.iterrows():
        row_dict = {}

        # For each column, we need to map the column ID to the corresponding value in the row
        
        for col in dataframe.columns:
            columnID = columnIDMapping[col]

            if any(col.startswith(eval + "_") or col == eval for eval in allEvals) and not " Reason"  in col and promptText!=None:
                
                row_dict[columnID] = {

                    "value": row[col],
                    "type": "EVAL",
                    "isValid": True,
                    "reasoning": row[col+" Reason"],
                    "edgeCase": "minorHallucinationDetailNotInContext",
                    "kpi": col

                }
            elif col.endswith(' Reason') and promptText!=None:
                continue
            else:# Get the columnID from the mapping
                row_dict[columnID] = row[col]

            # row_dict[columnID] = row[col]  # Directly map the column ID to the row value
        # Add the row index (if necessary)
        row_dict["pIndex"] = indx
        rowTemplate["dataToUploadList"].append(row_dict)

    # Return the column template, row template, and the column ID mapping
    return coltemplate, rowTemplate

def uploadColumnListInPlayground(payload):
    url = uploadColList
    headers = {
        "Content-Type": "application/json",
    }
    payload = payload

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        try:

            return response.json()
        except Exception as e:
            print("⚠️ Failed to parse JSON:", e)
            return None
    else:
        print("❌ Error:", response.status_code, response.text)
        return None


def uploadRowsInDBPlayground(payload):
    url = uploadRowList
    headers = {
        "Content-Type": "application/json",
    }

    payload = payload

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        try:

            return response.json()
        except Exception as e:
            print("⚠️ Failed to parse JSON:", e)
            return None
    else:
        print("❌ Error:", response.status_code, response.text)
        return None


def createPlayground(email, workspaceID, df, promptText=None,queryColName=None,dataStreamName=None,definationMapping=None,outputColName="output",evalOutputMap = None,activePlayground=None,customAnalytics=[]):
    
    if activePlayground != None:
        playgroundId=activePlayground
    else:
        playgroundId = str(createEvalPlayground(email=email, workspaceID=workspaceID))
    payload1, payload2 = createColumn(
        workspaceID=workspaceID, dataframe=df, playgroundID=playgroundId, promptText=promptText,queryColName=queryColName,dataStreamName=dataStreamName,definationMapping=definationMapping,outputColName=outputColName,evalOutputMap=evalOutputMap,customAnalytics=customAnalytics
    )
    
 # Debugging line to check the payload2 structure
    deleteExistingRows = deleteColumnListInPlayground(
        workspaceID=workspaceID, playgroundID=playgroundId
    )
    colListUpload = uploadColumnListInPlayground(payload=payload1)
    rowListUpload = uploadRowsInDBPlayground(payload=payload2)

    if rowListUpload:
        return True




def getPlaygroundInsights(defination:str,uniqueClassesString: str, reasonList: list):
    headers = {
        
        "Content-Type": "application/json",
    }

    # Initial request to generate playground insights
    payload = {
        "uniqueClassesString": uniqueClassesString,
        "reasonList": reasonList,
        "definition": defination,
    }

    urlGenerate = createInsightUrl
    try:
        responseGenerate = requests.post(urlGenerate, json=payload, headers=headers)

        if responseGenerate.status_code == 200:
            responseJson = responseGenerate.json()
            # print(responseJson)

            # ✅ NEW: unwrap "data" if it exists, otherwise fall back to the old shape
            payloadData = responseJson.get("data", responseJson)

            # keep only the fields you care about
            filteredResponse = {
                key: payloadData[key] for key in ("analysis", "nextStep") if key in payloadData
            }

            return filteredResponse
    except Exception as e:
        print(f"Exception occurred while generating insight: {e}")
        return None
        
    else:
        print(f"Error generating insight: {responseGenerate.status_code} - {responseGenerate.text}")
        return None
def checkDependency(selectedEval:list = [], columns:list = [],tocheck=True,_returnDepMapping = False,customevals={}):
    """
    Checks if all the required input columns for the selected evaluation metric are present.

    Parameters:
    - selectedEval (str): The name of the selected evaluation metric.
    - columns (list): List of column names present in the dataset.

    Raises:
    - LlumoAIError.dependencyError: If any required column is missing.
    """
    # Define required dependencies for each evaluation metric

    metricDependencies = {
        'Response Completeness': ['context', 'query', 'output'],
        'Response Bias': ['output'],
        'Response Harmfulness': ['output'],
        'Input Toxicity': ['query'],
        'Input Harmfulness': ['query'],
        'Context Utilization': ['output', 'context'],
        'Relevance Retention': ['context', 'query'],
        'Semantic Cohesion': ['context'],
        'Final Task Alignment': ['query','output'],
        'Tool Reliability': ['intermediateSteps'],
        'Response Correctness': ['output', 'query', 'context'],
        'Response Toxicity': ['output'],
        'Input Bias': ['query'],
        'Input Relevancy': ['context', 'query'],
        'Redundancy Reduction': ['context'],
        'Response Sentiment': ['output'],
        'Tool Selection Accuracy': ['tools', 'intermediateSteps'],
        'Stepwise Progression': ['tools', 'intermediateSteps'],
        'Hallucination': ['query', 'context', 'output'],
        'Groundedness': ['groundTruth', 'output'],
        'Memory Utilization': ['context', 'messageHistory'],
        'Input Relevancy (Multi-turn)': ['context', 'query'],
        'PII Check':["query","output"],
        'Prompt Injection':["query"]
    }
    
    metricDependencies.update(customevals)
    if _returnDepMapping == True:
        return metricDependencies

    if tocheck == True:
        # Check if the selected evaluation metric is known
        if selectedEval not in metricDependencies:
            return {"status": False,"message":f"Unknown evaluation metric: {selectedEval}"}

        # Get the required columns for the selected evaluation
        columnsRequired = metricDependencies[selectedEval]

        # Check if each required column is present in the provided columns
        for requirement in columnsRequired:
            if requirement not in columns:
                return {"status":False,
                    "message":f"'{selectedEval}' requires columns: {columnsRequired}. "
                    f"Missing: '{requirement}'. Please ensure your data includes all required columns."
                    }
        return {"status":True,"message":"success"}
    else:
        return {"status":True,"message":"success"}
    

def fetchData(workspaceID, playgroundID, missingList: list):
    # Define the URL and prepare the payload
    socket_data_url = "https://app.llumo.ai/api/eval/get-awaited"
    payload = {
        "workspaceID": workspaceID,
        "playgroundID": playgroundID,
        "missingList": missingList
    }
    
    try:
        # Send a POST request to the API
        response = requests.post(socket_data_url, json=payload)
        
        # Check if the response is successful
        if response.status_code == 200:
            # Parse the JSON data from the response
            data = response.json().get("data", {})
            
            
            # Prepare the list of all data values in the desired format
            result_list = []
            for key, value in data.items():
                # Create a dictionary for each item in the response data
                result_list.append({
                    key: {
                        "value": value.get("value"),
                        "reasoning": value.get("reasoning"),
                        "edgeCase": value.get("edgeCase"),
                        "kpi": value.get("kpi")
                    }
                })
            
            return result_list
        else:
            print(f"Failed to fetch data. Status Code: {response.status_code}")
            return []

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def validateModels(model_aliases):

    selectedProviders = []
    for name in model_aliases:
        for alias ,(provider , modelName ) in _MODEL_METADATA.items():
            if modelName == name:
                selectedProviders.append(provider)

    if len(set(selectedProviders)) > 1:
        return {"status": False,"message":"All selected models should be of same provider."}
    else:
        return {"status": True,"message":"All selected models are of same provider."}



def validateOpenaiKey(api_key):
    try:
        client = openai.OpenAI(api_key=api_key)
        _ = client.models.list()  # Light call to list models
    except openai.AuthenticationError:
        raise ValueError("❌ Invalid OpenAI API key.")
    except Exception as e:
        raise RuntimeError(f"⚠️ Error validating OpenAI key: {e}")

def validateGoogleKey(api_key):
    try:
        genai.configure(api_key=api_key)
        _ = genai.GenerativeModel("gemini-2.0-flash-lite").generate_content("test")
    except Exception as e:
        if "PERMISSION_DENIED" in str(e) or "API key not valid" in str(e):
            raise ValueError("❌ Invalid Google API key.")
        raise RuntimeError(f"⚠️ Error validating Gemini key: {e}")

def groupLogsByClass(logs, max_logs=2):
    # Initialize the final result structures (no defaultdict)
    
    groupedLogs = {}
    uniqueEdgeCases = {}  # This will store unique edge cases for each eval_name

    # Iterate through the logs
    for log in logs:
        log_details = list(log.values())[0]  # Get the details dictionary
        eval_name = log_details.get("kpi", "unmarked")
        edge_case = log_details.get("edgeCase", "unmarked")
        reasoning = log_details.get("reasoning", "")

        if eval_name != "unmarked" and edge_case != "unmarked":
            # Ensure that the eval_name and edge_case exist in the dictionary
            if eval_name not in groupedLogs:
                groupedLogs[eval_name] = {}
                uniqueEdgeCases[eval_name] = set()  # Initialize the set for unique edge cases

            if edge_case not in groupedLogs[eval_name]:
                groupedLogs[eval_name][edge_case] = []

            # Append the reasoning to the correct place
            groupedLogs[eval_name][edge_case].append(reasoning)
            uniqueEdgeCases[eval_name].add(edge_case)  # Add the edge case to the set

    # Limit the number of reasons to max_logs
    for eval_name in groupedLogs:
        for edge_case in groupedLogs[eval_name]:
            groupedLogs[eval_name][edge_case] = groupedLogs[eval_name][edge_case][:max_logs]

    # Convert the set of unique edge cases to a list for easier reading
    for eval_name in uniqueEdgeCases:
        uniqueEdgeCases[eval_name] = list(uniqueEdgeCases[eval_name])

    return groupedLogs, uniqueEdgeCases


def getCustomAnalytics(workspaceID):
    try:
        url = getCustomAnalyticsUrl
        payload = {
            "workspaceID": workspaceID
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        data=response.json()
        customData=data.get("data","").get("analyticsCustom","")
        customMapping = {
            "QUERY": "query",
            "CONTEXT": "context",
            "OUTPUT": "output",
            "MESSAGEHISTORY": "messageHistory",
            "TOOLS": "tools",
            "INTERMEDIATESTEPS": "intermediateSteps",
            "GROUNDTRUTH": "groundTruth",
        }

        metricDependencies = {}
        
        

        for eval in customData:
            evalName = eval.get("analyticsName")
            evalDependencyRaw = list(eval.get("variableMappings").values())
            
            # Replace each value using the custom mapping
            evalDependency = [customMapping.get(val.upper(), val.lower()) for val in evalDependencyRaw]
            
            # Build the dict
            metricDependencies[evalName] = evalDependency
        return metricDependencies
    
    except Exception as e:
        return {}