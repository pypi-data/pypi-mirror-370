import os
import json
import pandas as pd
from typing import Callable, List, Dict
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from openai import OpenAI
from .exceptions import *

# openai_api = os.getenv("OPENAI_API_KEY")
# google_api_key = os.getenv("GOOGLE_API_KEY")


class LlumoAgent:
    def __init__(
        self, name: str, description: str, parameters: Dict, function: Callable
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.function = function

    def run(self, **kwargs):
        return self.function(**kwargs)

    def createGoogleTool(self):
        return FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters={
                "type": "object",
                "properties": self.parameters,
                "required": list(self.parameters.keys()),
            },
        )

    def createOpenaiTool(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": list(self.parameters.keys()),
                },
            },
        }


class LlumoAgentExecutor:

    @staticmethod
    def run(df: pd.DataFrame, agents: List[LlumoAgent], model: str, model_api_key=None):
        if model.lower() == "google":
            return LlumoAgentExecutor.runWithGoogle(
                df, agents, model_api_key=model_api_key
            )
        elif model.lower() == "openai":
            return LlumoAgentExecutor.runWithOpenAI(
                df, agents, model_api_key=model_api_key
            )
        else:
            raise ValueError(f"Unsupported model: {model}. Use 'google' or 'openai'.")

    @staticmethod
    def runWithGoogle(df: pd.DataFrame, agents: List[LlumoAgent], model_api_key=None):
        try:
            genai.configure(api_key=model_api_key)
            tool_defs = []
            func_lookup = {}
            for agent in agents:
                tool_defs.append(agent.createGoogleTool())
                func_lookup[agent.name] = agent

            tool_wrapper = Tool(function_declarations=tool_defs)
            model = genai.GenerativeModel("gemini-1.5-pro", tools=[tool_wrapper])

            results = []
            histories = []

            for _, row in df.iterrows():
                try:
                    query = row["query"]
                    chat = model.start_chat()
                    response = chat.send_message(query)
                    parts = response.candidates[0].content.parts
                    final_output = ""

                    for part in parts:
                        if hasattr(part, "function_call") and part.function_call:
                            func_call = part.function_call
                            agent = func_lookup.get(func_call.name)
                            result = agent.run(**(func_call.args or {}))

                            follow_up_msg = {
                                "function_response": {
                                    "name": func_call.name,
                                    "response": result,
                                }
                            }

                            follow_up_response = chat.send_message(follow_up_msg)
                            final_output = follow_up_response.text
                        else:
                            final_output = part.text

                    results.append(final_output)
                    histories.append(str(chat.history))
                except Exception as e:
                    raise LlumoAIError.modelHitsExhausted()
                    # results.append(f"Error during processing: {e}")
                    # histories.append("Error in conversation")

            df["output"] = results
            df["messageHistory"] = histories
            df["tools"] = str({a.name: a.description for a in agents})
            return df

        except Exception as e:
            raise RuntimeError(f"Error in runWithGoogle: {e}")

    @staticmethod
    def runWithOpenAI(df: pd.DataFrame, agents: List[LlumoAgent], model_api_key=None):
        try:
            client = OpenAI(api_key=model_api_key)
            all_tools = [agent.createOpenaiTool() for agent in agents]
            agent_lookup = {agent.name: agent for agent in agents}

            results = []
            messageHistories = []

            for _, row in df.iterrows():
                try:
                    query = row["query"]
                    messages = [{"role": "user", "content": query}]

                    initial_response = client.chat.completions.create(
                        model="gpt-4",
                        messages=messages,
                        tools=all_tools,
                        tool_choice="auto",
                    )

                    first_message = initial_response.choices[0].message
                    assistant_msg = {"role": "assistant"}

                    if first_message.content:
                        assistant_msg["content"] = first_message.content
                    if first_message.tool_calls:
                        assistant_msg["tool_calls"] = first_message.tool_calls

                    messages.append(assistant_msg)

                    if first_message.tool_calls:
                        for call in first_message.tool_calls:
                            tool_name = call.function.name
                            args = json.loads(call.function.arguments)
                            agent = agent_lookup[tool_name]
                            tool_result = agent.run(**args)

                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": call.id,
                                    "content": str(tool_result),
                                }
                            )

                        final_response = client.chat.completions.create(
                            model="gpt-4", messages=messages
                        )
                        final_output = final_response.choices[0].message.content
                        messages.append({"role": "assistant", "content": final_output})
                    else:
                        final_output = first_message.content

                    results.append(final_output)
                    messageHistories.append(str(messages))

                except Exception as e:
                    # results.append(f"Error during processing: {e}")
                    # messageHistories.append("Error in conversation")
                    raise LlumoAIError.modelHitsExhausted()

            df["output"] = results
            df["messageHistory"] = messageHistories
            df["tools"] = str({a.name: a.description for a in agents})
            return df

        except Exception as e:
            raise RuntimeError(f"Error in runWithOpenAI: {e}")
