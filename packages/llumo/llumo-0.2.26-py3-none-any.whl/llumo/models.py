from enum import Enum

class Provider(str, Enum):
    OPENAI = "OPENAI"
    GOOGLE = "GOOGLE"

# Maps model aliases → (provider, actual model name for API)
_MODEL_METADATA = {
    "GPT_4O": (Provider.OPENAI, "GPT_4O"),
    "GPT_4_5": (Provider.OPENAI, "GPT_4_5"),
    "GPT_4": (Provider.OPENAI, "GPT_4"),
    "GPT_4_32K": (Provider.OPENAI, "GPT_4_32K"),
    "GPT_3_5_Turbo": (Provider.OPENAI, "GPT_35T"),
    "GPT_3_5_Turbo_Instruct": (Provider.OPENAI, "GPT_35T_INS"),
    "GPT_3_5_Turbo_16K": (Provider.OPENAI, "GPT_35T_16K"),
    "GPT_4_o_Mini": (Provider.OPENAI, "GPT_4O_MINI"),
    "o4_MINI": (Provider.OPENAI, "O4_MINI"),
    "o4_MINI_HIGH": (Provider.OPENAI, "O4_MINI_HIGH"),
    "GPT_4_1": (Provider.OPENAI, "GPT_4_1"),
    "GPT_4_1_Mini": (Provider.OPENAI, "GPT_4_1_MINI"),
    "GPT_4_1_nano": (Provider.OPENAI, "GPT_4_1_NANO"),
    "o3": (Provider.OPENAI, "O3"),
    "o3_MINI": (Provider.OPENAI, "O3_MINI"),
    "o1": (Provider.OPENAI, "O1"),
    "o1_MINI": (Provider.OPENAI, "O1_MINI"),
    
    
    "Gemini_2_5_Pro": (Provider.GOOGLE, "GEMINI_2_5_PRO"),
    "Gemini_2_5_Flash": (Provider.GOOGLE, "GEMINI_2_5_FLASH"),
    "Gemini_2_0": (Provider.GOOGLE, "GEMINI_2_0"),
    "Gemini_2_0_Flash": (Provider.GOOGLE, "GEMINI_2_0_FLASH"),
    "Gemini_Pro": (Provider.GOOGLE, "GEMINI_PRO"),
    "Text_Bison": (Provider.GOOGLE, "TEXT_BISON"),
    "Chat_Bison": (Provider.GOOGLE, "CHAT_BISON"),
    "Text_Bison_32k": (Provider.GOOGLE, "TEXT_BISON_32K"),
    "Text_Unicorn": (Provider.GOOGLE, "TEXT_UNICORN"),
    "Google_1_5_Flash": (Provider.GOOGLE, "GOOGLE_15_FLASH"),
    "Gemma_3_9B": (Provider.GOOGLE, "GEMMA_3_9B"),
    "Gemma_3_27B": (Provider.GOOGLE, "GEMMA_3_27B"),
}

class AVAILABLEMODELS(str, Enum):
    GPT_4o= "GPT_4O",
    GPT_4o_Mini= "GPT_4O_MINI",
    GPT_4_5= "GPT_4_5",
    GPT_4= "GPT_4",
    GPT_4_32K= "GPT_4_32K",
    GPT_3_5_Turbo= "GPT_35T",
    GPT_3_5_Turbo_Instruct= "GPT_35T_INS",
    GPT_3_5_Turbo_16K= "GPT_35T_16K",
    GPT_4_o_Mini= "GPT_4O_MINI",
    o4_MINI = "O4_MINI",
    o4_MINI_HIGH = "O4_MINI_HIGH",
    GPT_4_1 = "GPT_4_1",
    GPT_4_1_Mini = "GPT_4_1_MINI",
    GPT_4_1_nano = "GPT_4_1_NANO",
    o3 = "O3",
    o3_MINI = "O3_MINI",
    o1 = "O1",
    o1_MINI = "O1_MINI",
    
    Gemini_2_5_Pro = "GEMINI_2_5_PRO",
    Gemini_2_5_Flash = "GEMINI_2_5_FLASH",
    Gemini_2_0 = "GEMINI_2_0",
    Gemini_2_0_Flash = "GEMINI_2_0_FLASH",
    Gemini_Pro = "GEMINI_PRO",
    Text_Bison = "TEXT_BISON",
    Chat_Bison = "CHAT_BISON",
    Text_Bison_32k = "TEXT_BISON_32K",
    Text_Unicorn = "TEXT_UNICORN",
    Google_1_5_Flash = "GOOGLE_15_FLASH",
    Gemma_3_9B = "GEMMA_3_9B",
    Gemma_3_27B = "GEMMA_3_27B",
    

def getProviderFromModel(model: AVAILABLEMODELS) -> Provider:
    for alias, (provider, apiName) in _MODEL_METADATA.items():
        if model.value == apiName:
            return provider
    raise ValueError(f"Provider not found for model: {model}")