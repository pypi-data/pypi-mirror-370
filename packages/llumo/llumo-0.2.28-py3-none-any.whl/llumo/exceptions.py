class LlumoAIError(Exception):
    """Base class for all Llumo SDK-related errors."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    @staticmethod
    def InvalidApiKey():
        return LlumoAIError("The provided API key is invalid or unauthorized")

    @staticmethod
    def InvalidApiResponse():
        return LlumoAIError("Invalid or UnexpectedError response from the API")

    @staticmethod
    def RequestFailed(detail="The request to the API failed"):
        return LlumoAIError(f"Request to the API failed: {detail}")

    @staticmethod
    def InvalidJsonResponse():
        return LlumoAIError("The API response is not in valid JSON format")

    @staticmethod
    def UnexpectedError(detail="Metric"):
        return LlumoAIError(f"Can you please check if {detail} is written correctly. If you want to run {detail} please create a custom eval with same name of app.llumo.ai/evallm ")

    @staticmethod
    def EvalError(detail="Some error occured while processing"):
        return LlumoAIError(f"error: {detail}")

    @staticmethod
    def InsufficientCredits(details):
        return LlumoAIError(details)

        # return LlumoAIError("LLumo hits exhausted")

    @staticmethod
    def InvalidPromptTemplate():
        return LlumoAIError('''Make sure the prompt template fulfills the following criteria:
        1. All the variables should be inside double curly braces. Example: Give answer for the {{query}}, based on given {{context}}.
        2. The variables used in the prompt template must be present in the dataframe columns with the same name..
        ''')

    @staticmethod
    def modelHitsExhausted(details = "Your credits for the selected model exhausted."):
        return LlumoAIError(details)

    @staticmethod
    def dependencyError(details):
        return LlumoAIError(details)

    @staticmethod
    def providerError(details):
        return LlumoAIError(details)

    # @staticmethod
    # def dateNotFound():
    #     return LlumoAIError("Trial end date or subscription end date not found for the given user.")
