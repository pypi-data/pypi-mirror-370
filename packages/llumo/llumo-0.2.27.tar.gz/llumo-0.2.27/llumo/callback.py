from typing import Any, Dict, List
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult
from langchain_core.agents import AgentAction, AgentFinish
import json
from llumo.llumoLogger import LlumoLogger
from llumo.llumoSessionContext import LlumoSessionContext
import time
import re


class LlumoCallbackHandler(BaseCallbackHandler):
    def __init__(self, session: LlumoSessionContext = None):
        if session is None:
            raise ValueError("LlumoSessionContext is required")

        self.sessionLogger = session

        # Initialize timing and state variables
        self.llmStartTime = None
        self.agentStartTime = None
        self.toolStartTime = None
        self.chainStartTime = None
        self.stepTime = None

        # Initialize tracking variables
        self.prompt = ""
        self.currentToolName = None
        self.currentToolInput = None
        self.currentAgentName = None
        self.currentChainTime = "unknown"
        self.agentsSteps = 0
        self.toolsUsed = []
        self.llmProvider = "unknown"

        # Status tracking
        self.hasErrors = False
        self.lastError = None

        # ReAct specific tracking
        self.reactSteps = []
        self.currentThought = ""
        self.currentAction = ""
        self.currentObservation = ""
        self.isAgentExecution = False

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        """Called when a chain starts - this includes agent execution"""
        try:
            self.prompt = inputs.get("input", "")
            self.chainStartTime = time.time()

            # Reset all tracking variables for new query
            self.agentsSteps = 0
            self.toolsUsed = []
            self.reactSteps = []
            self.currentThought = ""
            self.currentAction = ""
            self.currentObservation = ""
            self.currentToolName = None
            self.currentToolInput = None
            self.hasErrors = False
            self.lastError = None

            # Dynamically detect agent name from serialized data
            if serialized is not None:
                # Check for 'name' parameter passed during initialization
                if "name" in serialized:
                    self.currentAgentName = serialized["name"]
                elif "_type" in serialized:
                    self.currentAgentName = serialized["_type"]
                elif "kwargs" in serialized and "name" in serialized["kwargs"]:
                    self.currentAgentName = serialized["kwargs"]["name"]
                elif "id" in serialized and isinstance(serialized["id"], list):
                    self.currentAgentName = serialized["id"][-1] if serialized["id"] else "unknown"
                else:
                    self.currentAgentName = "unknown"

            # Check if this is agent execution
            if ("agent" in str(self.currentAgentName).lower() or
                    (serialized and serialized.get("_type") == "agent_executor") or
                    any(key in str(serialized).lower() for key in ["agent", "react", "executor"])):

                self.agentStartTime = time.time()
                self.isAgentExecution = True
                print(f"[DEBUG] Agent execution started: {self.currentAgentName} - Reset counters for new query")
            else:
                self.isAgentExecution = False

        except Exception as e:
            print(f"[ERROR] in on_chain_start: {e}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Called when a chain ends"""
        try:
            if self.isAgentExecution and isinstance(outputs, dict) and "output" in outputs:
                # Use logAgentStep for final completion
                self.sessionLogger.logAgentStep(
                    stepName="Agent Execution Completed",
                    agentType="react_agent",
                    agentName=self.currentAgentName or "unknown",
                    numStepsTaken=self.agentsSteps,
                    tools=self.toolsUsed,
                    query=self.prompt,
                    status="SUCCESS",
                    message=f"Final output: {outputs['output']}. ReAct steps: {json.dumps(self.reactSteps)}",
                )

            # Reset execution state after chain ends
            self.isAgentExecution = False

        except Exception as e:
            print(f"[ERROR] Failed to log chain output: {e}")

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[Any], **kwargs: Any) -> None:
        """Called when LLM starts"""
        self.llmStartTime = time.time()
        self.stepTime = time.time()

        # Dynamically get model info
        model = "unknown"
        if serialized and "kwargs" in serialized:
            model = serialized["kwargs"].get("model_name",serialized["kwargs"].get("model", "unknown"))

        provider = "unknown"
        if isinstance(serialized.get("id", []), list) and len(serialized["id"]) > 2:
            provider = serialized["id"][2]
        self.llmProvider = provider

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """Called when LLM completes"""
        duration_ms = int((time.time() - self.llmStartTime) * 1000) if self.llmStartTime else 0

        # Initialize default values
        output = ""
        model_name = "unknown"
        input_tokens = 0
        output_tokens = 0
        status = "SUCCESS"
        error_message = ""

        try:
            # Case 1: LLMResult object
            if hasattr(response, 'generations'):
                if response.generations and len(response.generations) > 0:
                    generation = response.generations[0][0] if len(response.generations[0]) > 0 else None
                    if generation:
                        # Handle message content
                        if hasattr(generation, 'message'):
                            message = generation.message
                            if hasattr(message, 'content'):
                                output = message.content
                            # Handle function calls
                            if hasattr(message, 'additional_kwargs'):
                                func_call = message.additional_kwargs.get('function_call')
                                if func_call:
                                    output = (f"Function call: {func_call.get('name', 'unknown')} "
                                            f"with arguments {func_call.get('arguments', '{}')}")
                            if not output:
                                output = str(message)
                        else:
                            output = getattr(generation, 'text', str(generation))

                # Get token usage and model name
                if hasattr(response, 'llm_output'):
                    model_name = response.llm_output.get("model_name", "unknown")
                    usage = response.llm_output.get("token_usage", {})
                    input_tokens = usage.get("prompt_tokens", usage.get("input_tokens", 0))
                    output_tokens = usage.get("completion_tokens", usage.get("output_tokens", 0))

            # Case 2: Direct AIMessage
            elif hasattr(response, 'content'):
                output = response.content
                # Handle function calls
                if hasattr(response, 'additional_kwargs'):
                    func_call = response.additional_kwargs.get('function_call')
                    if func_call:
                        output = (f"Function call: {func_call.get('name', 'unknown')} "
                                    f"with arguments {func_call.get('arguments', '{}')}")

                # Get metadata
                if hasattr(response, 'response_metadata'):
                    model_name = getattr(response.response_metadata, "model_name", "unknown")
                    token_usage = getattr(response.response_metadata, "token_usage", {})
                    if isinstance(token_usage, dict):
                        input_tokens = token_usage.get("prompt_tokens", token_usage.get("input_tokens", 0))
                        output_tokens = token_usage.get("completion_tokens", token_usage.get("output_tokens", 0))

            # Case 3: Other types
            else:
                output = str(response)
                if hasattr(response, 'model'):
                    model_name = response.model

        except Exception as e:
            error_message = f"Response processing error: {str(e)}"
            status = "ERROR"

        # Ensure we have string values
        output = str(output) if output is not None else ""
        model_name = str(model_name) if model_name is not None else "unknown"

        # Parse ReAct reasoning from LLM output if we're in agent execution
        if self.isAgentExecution and output:
            self._parse_react_reasoning(output)

        try:
            self.sessionLogger.logLlmStep(
                stepName="LLM Call Completed",
                model=model_name,
                provider=self.llmProvider,
                inputTokens=int(input_tokens),
                outputTokens=int(output_tokens),
                temperature=float(kwargs.get("temperature", 0.7)),
                promptTruncated=False,
                latencyMs=duration_ms,
                query=str(self.prompt),
                output=output,
                status=status,
                message=error_message if status == "ERROR" else "",
            )
        except Exception as e:
            print(f"[ERROR] Failed to log LLM end: {e}")

    def _parse_react_reasoning(self, llm_output: str):
        """Parse ReAct reasoning pattern from LLM output"""
        try:
            # Extract thought patterns
            thought_match = re.search(r'Thought:\s*(.+?)(?=Action:|$)', llm_output, re.DOTALL)
            if thought_match:
                self.currentThought = thought_match.group(1).strip()

            # Extract action patterns
            action_match = re.search(r'Action:\s*(.+?)(?=Action Input:|Thought:|$)', llm_output, re.DOTALL)
            if action_match:
                self.currentAction = action_match.group(1).strip()

            # Extract action input patterns
            action_input_match = re.search(r'Action Input:\s*(.+?)(?=Observation:|Thought:|$)', llm_output, re.DOTALL)
            action_input = ""
            if action_input_match:
                action_input = action_input_match.group(1).strip()

            # Store the reasoning step for ReAct trace
            if self.currentThought or self.currentAction:
                reasoning_step = {
                    "step_number": self.agentsSteps + 1,
                    "thought": self.currentThought,
                    "planned_action": self.currentAction,
                    "action_input": action_input,
                    "full_llm_output": llm_output,
                    "timestamp": time.time()
                }

                # Add to react steps for complete trace
                if not self.reactSteps or self.reactSteps[-1].get("step_number") != reasoning_step["step_number"]:
                    self.reactSteps.append(reasoning_step)
                else:
                    # Update existing step
                    self.reactSteps[-1].update(reasoning_step)

        except Exception as e:
            print(f"[ERROR] Failed to parse ReAct reasoning: {e}")

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Called when a tool starts executing"""
        self.toolStartTime = time.time()
        self.stepTime = time.time()

        # Dynamically get tool name
        self.currentToolName = (serialized.get("name") or
                                serialized.get("_type") or
                                "unknown")

        # Handle the case where input_str is "None" or None
        if input_str == "None" or input_str is None:
            self.currentToolInput = {"input": ""}
        else:
            try:
                # Try to parse as JSON if it looks like JSON
                if input_str.startswith("{") and input_str.endswith("}"):
                    self.currentToolInput = json.loads(input_str)
                else:
                    self.currentToolInput = {"input": input_str}
            except:
                self.currentToolInput = {"input": input_str}

        # Track tools used
        if self.currentToolName not in self.toolsUsed:
            self.toolsUsed.append(self.currentToolName)

        print(f"[DEBUG] Tool started: {self.currentToolName} with input: {input_str}")

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        """Called when a tool completes execution"""
        duration_ms = int((time.time() - self.toolStartTime) * 1000) if self.toolStartTime else 0

        try:
            # Ensure output is stringified safely
            if output is None:
                output_str = ""
            elif isinstance(output, (dict, list)):
                output_str = json.dumps(output)
            else:
                output_str = str(output)

            # Store as observation for ReAct step
            self.currentObservation = output_str

            # Update the current ReAct step with observation
            if self.reactSteps and self.isAgentExecution:
                self.reactSteps[-1]["observation"] = output_str
                self.reactSteps[-1]["tool_execution_ms"] = duration_ms

            self.sessionLogger.logToolStep(
                stepName="Tool Execution Completed",
                toolName=self.currentToolName or "unknown",
                input=self.currentToolInput or {"input": ""},
                output=output_str,
                latencyMs=duration_ms,
                status="SUCCESS",
                message="",
            )

            print(f"[DEBUG] Tool completed: {self.currentToolName} -> {output_str}")

        except Exception as e:
            print(f"[ERROR] Failed to log tool end: {e}")

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        """Called when an agent takes an action"""
        self.agentsSteps += 1
        print("ON AGENT ACTION: ", action)

        try:
            # Dynamically extract information from action
            tool_name = getattr(action, "tool", "unknown")
            tool_input = getattr(action, "tool_input", "")
            log_message = getattr(action, "log", "")

            # Track tools if not already tracked
            if tool_name not in self.toolsUsed:
                self.toolsUsed.append(tool_name)

            # Update our ReAct steps tracking with executed action
            if self.reactSteps:
                self.reactSteps[-1].update({
                    "executed_action": tool_name,
                    "executed_input": tool_input,
                    "action_log": log_message
                })

            # Log the agent action step using logAgentStep
            current_status = "ERROR" if self.hasErrors else "SUCCESS"
            reasoning_text = self.currentThought if self.currentThought else "No reasoning captured"

            self.sessionLogger.logAgentStep(
                stepName=f"Agent Action Step {self.agentsSteps}",
                agentType="react_agent",
                agentName=self.currentAgentName or "unknown",
                numStepsTaken=self.agentsSteps,
                tools=[tool_name],
                query=self.prompt,
                status=current_status,
                message=f"Executing {tool_name} with input: {tool_input}. Reasoning: {reasoning_text}",
            )

        except Exception as e:
            print(f"[ERROR] Failed to log agent action: {e}")

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Called when an agent completes execution"""
        print("ON AGENT FINISH:", finish)
        # We don't need to log anything here since the final result is already logged in on_chain_end
        pass

    def on_agent_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when an agent encounters an error"""
        print("ITS A AGENT ERROR:", error)
        self.hasErrors = True
        self.lastError = str(error)

        try:
            self.sessionLogger.logAgentStep(
                stepName="Agent Execution Error",
                agentType="react_agent",
                agentName=self.currentAgentName or "unknown",
                numStepsTaken=self.agentsSteps,
                tools=self.toolsUsed,
                query=self.prompt,
                status="ERROR",
                message=str(error),
            )
        except Exception as e:
            print(f"[ERROR] Failed to log agent error: {e}")

    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when a tool encounters an error"""
        print("ITS A TOOL ERROR:", error)
        self.hasErrors = True
        self.lastError = str(error)

        try:
            # Update ReAct step with error observation
            if self.reactSteps:
                self.reactSteps[-1]["observation"] = f"ERROR: {str(error)}"
                self.reactSteps[-1]["error"] = True

            self.sessionLogger.logToolStep(
                stepName="Tool Execution Failed",
                toolName=self.currentToolName or "unknown",
                input=self.currentToolInput or {"input": ""},
                output="",
                latencyMs=0,
                status="ERROR",
                message=str(error),
            )
        except Exception as e:
            print(f"[ERROR] Failed to log tool error: {e}")

    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when a chain encounters an error"""
        print("ITS A CHAIN ERROR:", error)
        self.hasErrors = True
        self.lastError = str(error)

        try:
            if self.isAgentExecution:
                # Use logAgentStep for agent-related chain errors
                self.sessionLogger.logAgentStep(
                    stepName="Agent Chain Error",
                    agentType="react_agent",
                    agentName=self.currentAgentName or "unknown",
                    numStepsTaken=self.agentsSteps,
                    tools=self.toolsUsed,
                    query=self.prompt,
                    status="ERROR",
                    message=str(error),
                )
            else:
                # Use logLlmStep for general chain errors
                self.sessionLogger.logLlmStep(
                    stepName="Chain Execution Error",
                    model="unknown",
                    provider=self.llmProvider,
                    inputTokens=0,
                    outputTokens=0,
                    temperature=0.0,
                    promptTruncated=False,
                    latencyMs=0,
                    query=self.prompt,
                    output="",
                    status="ERROR",
                    message=str(error),
                )
        except Exception as e:
            print(f"[ERROR] Failed to log chain error: {e}")

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Called when LLM generates a new token (for streaming)"""
        pass

    def on_text(self, text: str, **kwargs: Any) -> None:
        """Called when arbitrary text is logged"""
        # Only log significant text events during agent execution
        if self.isAgentExecution and text.strip():
            print(f"[DEBUG] Additional text: {text}")

            # Check if this text contains important ReAct information like "Observation:"
            if any(keyword in text.lower() for keyword in ['observation:']):
                try:
                    # Update the current ReAct step with additional observation info
                    if self.reactSteps:
                        existing_obs = self.reactSteps[-1].get("observation", "")
                        self.reactSteps[-1][
                            "observation"] = f"{existing_obs}\n{text.strip()}" if existing_obs else text.strip()

                except Exception as e:
                    print(f"[ERROR] Failed to process text event: {e}")
