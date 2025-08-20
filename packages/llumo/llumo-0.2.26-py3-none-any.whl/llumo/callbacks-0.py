from langchain_core.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List, Optional, Union
import time
import json
from llumo.llumoSessionContext import  getSessionID, getLlumoRun
from llumo.llumoSessionContext import LlumoSessionContext


class LlumoCallbackHandler(BaseCallbackHandler):
    """
    LangChain callback handler that integrates with Llumo logging system.
    Tracks LLM calls, tool usage, agent actions, and chains.
    """

    def __init__(self, logger):
        self.logger = logger
        self.start_times = {}  # Track start times for latency calculation
        self.step_counters = {}  # Track step counts for agents

    def _get_session_context(self) -> Optional[LlumoSessionContext]:
        """Get the current Llumo session context from context variables."""
        try:
            session_id = getSessionID()
            run = getLlumoRun()
            if session_id and run:
                # Create a temporary context object to access logging methods
                ctx = LlumoSessionContext(self.logger, session_id)
                return ctx
        except Exception:
            pass
        return None

    def _safe_serialize(self, obj: Any) -> str:
        """Safely serialize objects to JSON string."""
        try:
            return json.dumps(obj, default=str, ensure_ascii=False)
        except Exception:
            return str(obj)

    # LLM Callbacks
    def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Called when LLM starts generating."""
        run_id = kwargs.get('run_id')
        if run_id:
            self.start_times[run_id] = time.time()

        print("LLM started - prompts:", len(prompts))

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Called when LLM generates a new token."""
        # Optional: Could be used for streaming token tracking
        pass

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """Called when LLM finishes generating."""
        ctx = self._get_session_context()
        if not ctx:
            print("No Llumo session context available")
            return

        run_id = kwargs.get('run_id')
        start_time = self.start_times.pop(run_id, time.time())
        latency_ms = int((time.time() - start_time) * 1000)

        # Extract LLM response details
        model = getattr(response, 'model_name', 'unknown')

        # Get token usage if available
        token_usage = getattr(response, 'llm_output', {}).get('token_usage', {})
        input_tokens = token_usage.get('prompt_tokens', 0)
        output_tokens = token_usage.get('completion_tokens', 0)

        # Get the generated text
        if hasattr(response, 'generations') and response.generations:
            output_text = response.generations[0][0].text if response.generations[0] else ""
        else:
            output_text = str(response)

        # Get the original prompt
        prompts = kwargs.get('prompts', [''])
        query = prompts[0] if prompts else ""

        try:
            ctx.logLlmStep(
                stepName=f"LLM Call - {model}",
                model=model,
                provider="langchain",
                inputTokens=input_tokens,
                outputTokens=output_tokens,
                temperature=kwargs.get('temperature', 0.7),
                promptTruncated=False,
                latencyMs=latency_ms,
                query=query,
                output=output_text,
                status="SUCCESS",
                message=""
            )
            print(f"Logged LLM step: {model} ({latency_ms}ms)")
        except Exception as e:
            print(f"Failed to log LLM step: {e}")

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when LLM encounters an error."""
        ctx = self._get_session_context()
        if not ctx:
            return

        run_id = kwargs.get('run_id')
        start_time = self.start_times.pop(run_id, time.time())
        latency_ms = int((time.time() - start_time) * 1000)

        prompts = kwargs.get('prompts', [''])
        query = prompts[0] if prompts else ""

        try:
            ctx.logLlmStep(
                stepName="LLM Call - Error",
                model="unknown",
                provider="langchain",
                inputTokens=0,
                outputTokens=0,
                temperature=0.7,
                promptTruncated=False,
                latencyMs=latency_ms,
                query=query,
                output="",
                status="FAILURE",
                message=str(error)
            )
            print(f"Logged LLM error: {error}")
        except Exception as e:
            print(f"Failed to log LLM error: {e}")

    # Chain Callbacks
    def on_chain_start(
            self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        pass

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Called when a chain ends."""
        print("Chain execution completed")

    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when a chain encounters an error."""
        print(f"Chain error: {error}")

    # Tool Callbacks
    def on_tool_start(
            self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Called when a tool starts."""
        run_id = kwargs.get('run_id')
        if run_id:
            self.start_times[run_id] = time.time()

        tool_name = serialized.get('name', 'Unknown Tool')
        print(f"Tool started: {tool_name}")

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Called when a tool ends."""
        ctx = self._get_session_context()
        if not ctx:
            return

        run_id = kwargs.get('run_id')
        start_time = self.start_times.pop(run_id, time.time())
        latency_ms = int((time.time() - start_time) * 1000)

        # Extract tool info from kwargs
        serialized = kwargs.get('serialized', {})
        tool_name = serialized.get('name', 'Unknown Tool')
        input_str = kwargs.get('input_str', '')

        try:
            ctx.logToolStep(
                stepName=f"Tool - {tool_name}",
                toolName=tool_name,
                input={"input": input_str},
                output=output,
                latencyMs=latency_ms,
                status="SUCCESS",
                message=""
            )
            print(f"Logged tool step: {tool_name} ({latency_ms}ms)")
        except Exception as e:
            print(f"Failed to log tool step: {e}")

    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when a tool encounters an error."""
        ctx = self._get_session_context()
        if not ctx:
            return

        run_id = kwargs.get('run_id')
        start_time = self.start_times.pop(run_id, time.time())
        latency_ms = int((time.time() - start_time) * 1000)

        serialized = kwargs.get('serialized', {})
        tool_name = serialized.get('name', 'Unknown Tool')
        input_str = kwargs.get('input_str', '')

        try:
            ctx.logToolStep(
                stepName=f"Tool - {tool_name} - Error",
                toolName=tool_name,
                input={"input": input_str},
                output="",
                latencyMs=latency_ms,
                status="FAILURE",
                message=str(error)
            )
            print(f"Logged tool error: {tool_name} - {error}")
        except Exception as e:
            print(f"Failed to log tool error: {e}")

    # Agent Callbacks
    def on_agent_action(self, action: Any, **kwargs: Any) -> None:
        """Called when an agent takes an action."""
        run_id = kwargs.get('run_id')

        # Track agent step count
        if run_id not in self.step_counters:
            self.step_counters[run_id] = 0
        self.step_counters[run_id] += 1

        print(f"Agent action: {getattr(action, 'tool', 'unknown')}")

    def on_agent_finish(self, finish: Any, **kwargs: Any) -> None:
        """Called when an agent finishes."""
        ctx = self._get_session_context()
        if not ctx:
            return

        run_id = kwargs.get('run_id')
        num_steps = self.step_counters.pop(run_id, 0)

        try:
            ctx.logAgentStep(
                stepName="Agent Execution",
                agentType="langchain_agent",
                agentName="LangChain Agent",
                numStepsTaken=num_steps,
                tools=[],  # Could be populated if tool info is available
                query=getattr(finish, 'log', ''),
                status="SUCCESS",
                message=""
            )
            print(f"Logged agent finish: {num_steps} steps")
        except Exception as e:
            print(f"Failed to log agent step: {e}")





