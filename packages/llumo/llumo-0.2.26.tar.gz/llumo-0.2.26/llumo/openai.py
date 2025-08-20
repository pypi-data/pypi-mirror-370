import time
from openai import OpenAI as OpenAIClient
from .client import LlumoClient
from .llumoSessionContext import LlumoSessionContext
from .llumoLogger import LLUMOLogger


# evaluation function that uses LlumoClient
def performEvaluation(data, api_key=None, evals=["Response Correctness"], **kwargs):
    try:
        client = LlumoClient(api_key=api_key)
        results = client.evaluateMultiple(
            data,
            evals=evals,
            createExperiment=kwargs.get("createExperiment", False),
            playgroundID=kwargs.get("playgroundID"),
            prompt_template="Give answer to the query: {{query}}, using context: {{context}}",
            getDataFrame=False,
        )
        return results
    except Exception as e:
        print(f"Error in perform_evaluation: {e}")
        raise


# Wrapper around ChatCompletion to allow custom fields like `.evaluation`
class ChatCompletionWithEval:
    def __init__(self, response, evaluation):
        self._response = response
        self.evaluation = evaluation

    def __getattr__(self, name):
        return getattr(self._response, name)

    def __getitem__(self, key):
        return self._response[key]

    def __repr__(self):
        return repr(self._response)


class OpenAI(OpenAIClient):
    def __init__(self, api_key: str, session):
        super().__init__(api_key=api_key)
        self.session = session
        self.llumo_key = session.apiKey

        original_create = self.chat.completions.create

        def create_wrapper(*args, **kwargs):
            context = kwargs.pop("context", None)
            model = kwargs["model"]
            create_experiment = kwargs.pop("createExperiment", False)

            messages = kwargs.get("messages", [])
            user_message = next(
                (
                    m.get("content")
                    for m in reversed(messages)
                    if m.get("role") == "user"
                ),
                "",
            )

            if not context or context.strip() == "":
                context = user_message

            # Get IDs from the session logger
            playground_id = self.session.logger.getPlaygroundID()
            workspace_id = self.session.logger.getWorkspaceID()

            # Input Bias Evaluation
            eval_input_bias = [
                {
                    "query": user_message,
                    "context": context,
                    "output": "",  # No output yet
                }
            ]
            try:
                start_time = time.time()
                bias_evaluation_result = performEvaluation(
                    eval_input_bias,
                    api_key=self.llumo_key,
                    evals=["Input Bias"],
                    playgroundID=playground_id,
                    workspaceID=workspace_id,
                    createExperiment=create_experiment,
                )
                latency = int((time.time() - start_time) * 1000)
                # Access the first result object
                bias_evaluation = bias_evaluation_result[0]
                # message = "-".join(
                #     getattr(bias_evaluation, "edgeCases", {}).get("value", [])
                # )
                # self.session.logEvalStep(
                #     stepName=f"EVAL-Input Bias",
                #     output="",
                #     context=context,
                #     query=user_message,
                #     messageHistory="",
                #     tools="",
                #     intermediateSteps="",
                #     groundTruth="",
                #     analyticsScore=getattr(bias_evaluation, "analyticsScore", {}),
                #     reasoning=getattr(bias_evaluation, "reasoning", {}),
                #     classification=getattr(bias_evaluation, "classification", {}),
                #     evalLabel=getattr(bias_evaluation, "evalLabel", {}),
                #     latencyMs=latency,
                #     status="SUCCESS",
                #     message=message,
                # )
            except Exception as e:
                print(f"Input Bias evaluation failed: {e}")
                self.session.logEvalStep(
                    stepName=f"EVAL-FAILURE",
                    output="",
                    context=context,
                    query=user_message,
                    messageHistory="",
                    tools="",
                    intermediateSteps="",
                    groundTruth="",
                    analyticsScore={},
                    reasoning={},
                    classification={},
                    evalLabel={},
                    latencyMs=0,
                    status="FAILURE",
                    message="EVAL_ERROR",
                )

            start_time = time.time()
            response = original_create(*args, **kwargs)
            latency = int((time.time() - start_time) * 1000)
            output_text = response.choices[0].message.content

            self.session.logLlmStep(
                stepName=f"LLM-{user_message[:30]}",
                model=model,
                provider="openai",
                inputTokens=response.usage.prompt_tokens,
                outputTokens=response.usage.completion_tokens,
                temperature=kwargs.get("temperature", 0.0),
                promptTruncated=False,
                latencyMs=latency,
                query=user_message,
                output=output_text,
                status="SUCCESS",
                message="",
            )

            # Response Correctness Evaluation
            eval_input_correctness = [
                {
                    "query": user_message,
                    "context": context,
                    "output": output_text,
                }
            ]
            try:
                start_time = time.time()
                correctness_evaluation_result = performEvaluation(
                    eval_input_correctness,
                    api_key=self.llumo_key,
                    evals=["Response Correctness"],
                    playgroundID=playground_id,
                    workspaceID=workspace_id,
                    createExperiment=create_experiment,
                )
                latency = int((time.time() - start_time) * 1000)
                # Access the first result object
                correctness_evaluation = correctness_evaluation_result[0]
                # message = "-".join(
                #     getattr(correctness_evaluation, "edgeCases", {}).get("value", [])
                # )
                # self.session.logEvalStep(
                #     stepName=f"EVAL-Response Correctness",
                #     output=output_text,
                #     context=context,
                #     query=user_message,
                #     messageHistory="",
                #     tools="",
                #     intermediateSteps="",
                #     groundTruth="",
                #     analyticsScore=getattr(
                #         correctness_evaluation, "analyticsScore", {}
                #     ),
                #     reasoning=getattr(correctness_evaluation, "reasoning", {}),
                #     classification=getattr(
                #         correctness_evaluation, "classification", {}
                #     ),
                #     evalLabel=getattr(correctness_evaluation, "evalLabel", {}),
                #     latencyMs=latency,
                #     status="SUCCESS",
                #     message=message,
                # )
            except Exception as e:
                print(f"Response Correctness evaluation failed: {e}")
                correctness_evaluation = None
                self.session.logEvalStep(
                    stepName=f"EVAL-FAILURE",
                    output=output_text,
                    context=context,
                    query=user_message,
                    messageHistory="",
                    tools="",
                    intermediateSteps="",
                    groundTruth="",
                    analyticsScore={},
                    reasoning={},
                    classification={},
                    evalLabel={},
                    latencyMs=0,
                    status="FAILURE",
                    message="EVAL_ERROR",
                )

            if correctness_evaluation is None:
                return response

            return ChatCompletionWithEval(response, correctness_evaluation)

        self.chat.completions.create = create_wrapper
