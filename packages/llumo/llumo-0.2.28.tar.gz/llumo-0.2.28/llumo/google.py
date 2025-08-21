from google import generativeai as _genai
from .client import LlumoClient


def evaluate_multiple(data, api_key=None, evals=["Response Correctness"]):
    client = LlumoClient(api_key=api_key)
    results = client.evaluateMultiple(
        data,
        evals=evals,
        createExperiment=False,
        prompt_template="Give answer to the query: {{query}}, using context: {{context}}",
        getDataFrame=False
    )
    return results


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


class genai:
    class GenerativeModel:
        def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
            _genai.configure(api_key=api_key)
            self._api_key = api_key
            self._model_name = model
            self._model_instance = _genai.GenerativeModel(model_name=model)

        def generate_content(self, contents: str | list[str], **kwargs):
            context = kwargs.pop("context", None)
            evals = kwargs.pop("evals", [])
            llumo_key = kwargs.pop("llumo_key", None)

            # Run Gemini generation
            response = self._model_instance.generate_content(contents=contents, **kwargs)
            output = response.text

            eval_input = [{
                "query": contents,
                "context": context or contents,
                "output": output,
            }]

            evaluation = None
            try:
                evaluation = evaluate_multiple(data=eval_input, evals=evals, api_key=llumo_key)
            except Exception as e:
                evaluation = None
            
            if evaluation is None:
                    print("Cannot process your request for evaluation, please check your api and try again later.")
                    return response
            

            return ChatCompletionWithEval(response, evaluation)
