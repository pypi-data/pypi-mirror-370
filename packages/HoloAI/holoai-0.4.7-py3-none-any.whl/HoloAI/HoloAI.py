
# Pip Package: HoloAI
import asyncio
import inspect
import logging
import os
import re
import threading
from importlib import import_module
from datetime import datetime
from dotenv import load_dotenv
from typing import Iterable, Union, List, Dict, Any
import tempfile, mimetypes, urllib.request

from .HAIUtils.HAIUtils import (
    getFrameworkInfo,
    formatJsonInput,
    formatJsonExtended,
    parseJsonInput,
    formatTypedInput,
    formatTypedExtended,
    parseTypedInput,
    parseInstructions,
    parseModels,
    isStructured,
    safetySettings,
    getFrames
)

load_dotenv()
logger = logging.getLogger(__name__)

def setProvider(apiInput=None):
    """
    Sets provider API keys from string, tuple, or list, or env.
    Passes API key directly to config if possible.
    Returns a providerMap of all found providers.
    """

    PROVIDERS = {
        "OPENAI_API_KEY":    ("HoloAI.HAIConfigs.OpenAIConfig",   "OpenAIConfig",   "openai"),
        "ANTHROPIC_API_KEY": ("HoloAI.HAIConfigs.AnthropicConfig","AnthropicConfig","anthropic"),
        "GOOGLE_API_KEY":    ("HoloAI.HAIConfigs.GoogleConfig",   "GoogleConfig",   "google"),
        "GROQ_API_KEY":      ("HoloAI.HAIConfigs.GroqConfig",     "GroqConfig",     "groq"),
        "XAI_API_KEY":       ("HoloAI.HAIConfigs.xAIConfig",      "xAIConfig",      "xai"),
    }


    # Step 1: Parse keys from apiInput (if given) and always set env too (for backward compat)
    keyMap = {}
    if apiInput is None:
        inputList = []
    elif isinstance(apiInput, str):
        inputList = [apiInput.strip()]
    elif isinstance(apiInput, (list, tuple)):
        inputList = [s.strip() for s in apiInput if isinstance(s, str) and s.strip()]
    else:
        raise ValueError("setProvider input must be a string, list, tuple, or None")

    for assignment in inputList:
        try:
            envKey, apiKey = assignment.split('=', 1)
            envKey = envKey.strip()
            apiKey = apiKey.strip()
            os.environ[envKey] = apiKey  # set for backward compat
            keyMap[envKey] = apiKey      # track for direct pass
        except Exception:
            raise ValueError(f"Each assignment must be 'PROVIDER_KEY=key', got: {assignment}")

    providerMap = {}
    for envKey, (module, clsName, mapKey) in PROVIDERS.items():
        apiKey = keyMap.get(envKey) or os.getenv(envKey)
        if apiKey:
            try:
                mod = import_module(module)
                # Pass apiKey directly if config supports it, else fallback to no-arg
                try:
                    providerMap[mapKey] = getattr(mod, clsName)(apiKey)
                except TypeError:
                    providerMap[mapKey] = getattr(mod, clsName)()
            except ImportError:
                continue

    return providerMap

MODELS = {
    ("gpt", "o", "dall-e-3"): "openai",
    ("claude",): "anthropic",
    ("llama", "meta-llama", "gemma2", "qwen", "deepseek",): "groq",
    ("gemini", "gemma",): "google",
    ("grok"): "xai",
}


class HoloAI:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(HoloAI, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return

        self.providerMap = setProvider()
        self.initialized = True

    def getFrameworkInfo(self):
        return getFrameworkInfo()

    def listProviders(self):
        return list(self.providerMap.keys())

    def _inferModelProvider(self, model: str):
        return next(
            (provider for prefixes, provider in MODELS.items()
             if any(model.startswith(prefix) for prefix in prefixes)),
            None
        )

    def setProvider(self, apiInput=None):
        """
        Sets provider API keys from:
        - a single string:      'PROVIDER_KEY=api_key'
        - a tuple of strings:   ('PROVIDER_KEY=api_key', ...)
        - a list of strings:    ['PROVIDER_KEY=api_key', ...]
        - or uses environment if nothing passed.

        Returns a providerMap of all found providers.
        """
        self.providerMap = setProvider(apiInput)

    def _getProviderConfig(self, model: str):
        """
        Returns the provider configuration for a given model.
        :param model: (str) The model name to infer the provider from.
        :return: The provider configuration object.
        :raises ValueError: If the provider cannot be inferred from the model.
        """
        provider = self._inferModelProvider(model)
        if provider and provider in self.providerMap:
            return self.providerMap[provider]
        raise ValueError(f"Cannot infer provider from model '{model}'. Valid providers: {list(self.providerMap.keys())}")

    def HoloCompletion(self, **kwargs):
        """
        HoloAI completion requests.
        Handles both text and vision requests.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use for both response and vision (Not Required if 'models' is set).
            - models: (str, list, or dict) Per-task models (Optional):
                - str: Used for both response and vision.
                - list/tuple: [response_model, vision_model].
                - dict: {'response': ..., 'vision': ...}.
            - system/instructions: (str) System prompt or additional instructions (Optional).
                system = "You are a helpful assistant."
                instructions = "You can answer questions and provide information."
            - user/input: (str or list) The main user input (Required).
                Accepts a single prompt string or a message history (list of messages).
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: Skills and Actions to use (Optional).
                Skills and actions will be executed if the model chooses to call them.
                Valid options:
                    - skills=[skills, actions]
                    - skills=skills, 
                      actions=actions
                If only actions is provided (without skills), this is not allowed and will result in an error.
            - tools: (list) Tools to use (Optional) [tools].
            - choice/tool_choice: (str) Controls model tool-calling behavior.
                Valid values:
                    - 'auto': Model decides when to call tools (default)
                    - 'required': Model must call a tool (forces function/tool call)
                    - 'none': Tool/function calling is disabled
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - creativity/temperature: (float) Creativity level (0.0 to 1.0, default: 0.5).
            - effort: (str) Effort level ('auto', 'low', 'medium', 'high') (Optional (default: 'auto')).
            - budget/max_budget: (int) Budget for the response (Optional (default: 1369)).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object, or a Vision object if image paths are found.
        """
        return self._routeCompletion(**kwargs)

    def HoloAgent(self, **kwargs):
        """
        HoloAI agent requests.
        Handles both text and vision requests.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use for both response and vision (Not Required if 'models' is set).
            - models: (str, list, or dict) Per-task models (Optional):
                - str: Used for both response and vision.
                - list/tuple: [response_model, vision_model].
                - dict: {'response': ..., 'vision': ...}.
            - system/instructions: (str) System prompt or additional instructions (Optional).
                system = "You are a helpful assistant."
                instructions = "You can answer questions and provide information."
            - user/input: (str or list) The main user input (Required).
                Accepts a single prompt string or a message history (list of messages).
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: Skills and Actions to use (Optional).
                Skills and actions will be executed if the model chooses to call them.
                Valid options:
                    - skills=[skills, actions]
                    - skills=skills, 
                      actions=actions
                If only actions is provided (without skills), this is not allowed and will result in an error.
            - tools: (list) Tools to use (Optional) [tools].
            - choice/tool_choice: (str) Controls model tool-calling behavior.
                Valid values:
                    - 'auto': Model decides when to call tools (default)
                    - 'required': Model must call a tool (forces function/tool call)
                    - 'none': Tool/function calling is disabled
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - creativity/temperature: (float) Creativity level (0.0 to 1.0, default: 0.5).
            - effort: (str) Effort level ('auto', 'low', 'medium', 'high') (Optional (default: 'auto')).
            - budget/max_budget: (int) Budget for the response (Optional (default: 1369)).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object, or a Vision object if image paths are found.
        """
        return self._routeCompletion(**kwargs)

    def Reasoning(self, **kwargs):
        """
        Get a Response from the Response model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
                system = "You are a helpful assistant."
                instructions = "You can answer questions and provide information."
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - tools: (list) Tools to use (Optional) [tools].
            - choice/tool_choice: (str) Controls model tool-calling behavior.
                Valid values:
                    - 'auto': Model decides when to call tools (default)
                    - 'required': Model must call a tool (forces function/tool call)
                    - 'none': Tool/function calling is disabled
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - creativity/temperature: (float) Creativity level (0.0 to 1.0, default: 0.5).
            - effort: (str) Effort level ('auto', 'low', 'medium', 'high') (Optional (default: 'auto')).
            - budget/max_budget: (int) Budget for the response (Optional (default: 1369)).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object.
        """
        return self._routeResponse(**kwargs)

    def Response(self, **kwargs):
        """
        Get a Response from the Response model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
                system = "You are a helpful assistant."
                instructions = "You can answer questions and provide information."
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - tools: (list) Tools to use (Optional) [tools].
            - choice/tool_choice: (str) Controls model tool-calling behavior.
                Valid values:
                    - 'auto': Model decides when to call tools (default)
                    - 'required': Model must call a tool (forces function/tool call)
                    - 'none': Tool/function calling is disabled
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - creativity/temperature: (float) Creativity level (0.0 to 1.0, default: 0.5).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object.
        """
        return self._routeResponse(**kwargs)

    def Vision(self, **kwargs):
        """
        Get a Vision response from the Vision model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
                system = "You are a helpful assistant."
                instructions = "You can answer questions and provide information."
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - creativity/temperature: (float) Creativity level (0.0 to 1.0, default: 0.5).
            - files: (list) List of image file paths (default: empty list).
            - collect: (int) Number of frames to collect (default: 10).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Vision response object.
        """
        return self._routeVision(**kwargs)

    def Generation(self, **kwargs):
        # """
        # Get a Generation response from the Generation model.
        # :param kwargs: Keyword arguments to customize the request.
        #     - model: (str) The model to use (Required).
        #     - system/instructions: (str) System prompt or additional instructions (Optional).
        #         system = "You are a helpful assistant."
        #         instructions = "You can answer questions and provide information."
        #     - user/input: (str or list) The main user input (Required). 
        #         Accepts a single prompt string or a message history (list of messages). 
        #         Both 'user' and 'input' are interchangeable; use either (Preferred: input).
        # :return: A Generation response object.
        # """
        return self._routeGeneration(**kwargs)

    def Agent(self, **kwargs):
        """
        Get a Response from the Agent model.
        :param kwargs: Keyword arguments to customize the request.
            - task: (str) Task type ('response', 'reasoning', 'vision') (Optional (default: 'response')).
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
                system = "You are a helpful assistant."
                instructions = "You can answer questions and provide information."
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - tools: (list) Tools to use (Optional) [tools].
            - choice/tool_choice: (str) Controls model tool-calling behavior.
                Valid values:
                    - 'auto': Model decides when to call tools (default)
                    - 'required': Model must call a tool (forces function/tool call)
                    - 'none': Tool/function calling is disabled
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - creativity/temperature: (float) Creativity level (0.0 to 1.0, default: 0.5).
            - effort: (str) Effort level ('auto', 'low', 'medium', 'high') (Optional (default: 'auto')).
            - budget/max_budget: (int) Budget for the response (Optional (default: 1369)).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - collect: (int) Number of frames to collect (default: 10).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Reasoning, Response, or Vision object.
        """
        task = kwargs.get('task', 'response').lower()
        taskMap = {
            'reasoning': self._routeResponse,
            'response': self._routeResponse,
            'vision': self._routeVision,
        }
        if task not in taskMap:
            raise ValueError(f"Unknown task: '{task}'. Supported tasks: {list(taskMap.keys())}")
        return taskMap[task](**kwargs)

    #------------- Utility Methods -------------#
    def _routeCompletion(self, **kwargs):
        kwargs  = {k.lower(): v for k, v in kwargs.items()}
        models  = kwargs.pop("model", None) or kwargs.pop("models", None)
        system  = parseInstructions(kwargs)  # popped in parseInstructions
        raw     = kwargs.pop("input", None) or kwargs.pop("user", None)
        files   = kwargs.pop("files", None)

        models = parseModels(models)

        if isinstance(raw, list):
            last = raw[-1]
            if isinstance(last, dict) and "content" in last:
                text = str(last["content"])
            else:
                text = str(last)
        else:
            text = str(raw)

        # Detect
        passedImages = self._extractMediaInfo(files)
        inlineImages = self._extractMediaInfo(text)
        passedFiles  = self._extractFileInfo(files)
        inlineFiles  = self._extractFileInfo(text)

        # Normalize paths
        passedImages = self._normalizePaths(passedImages)
        inlineImages = self._normalizePaths(inlineImages)
        passedFiles  = self._normalizePaths(passedFiles)
        inlineFiles  = self._normalizePaths(inlineFiles)
        
        allImages = list(dict.fromkeys([*passedImages, *inlineImages]))
        allFiles  = list(dict.fromkeys([*passedFiles, *inlineFiles]))

        # Build prompt without any paths
        cleanedInput = self._cleanInput(text)
        #print(f"\nCleaned input: {cleanedInput}\n")

        def holoMode():
            model  = models['response']
            config = self._getProviderConfig(model)
            return config.getResponse(
                model  = model,
                system = system,
                input  = raw,
                **kwargs,
            )

        def responseMode():
            model  = models['response']
            config = self._getProviderConfig(model)
            # skills  = kwargs.pop('skills', None)
            # actions = kwargs.pop('actions', None)
            skills, actions = self._popSkillsActions(kwargs)
            localFiles = [self._downloadUrlToTemp(p) if p.startswith(("http://", "https://")) else p for p in allFiles]
            # Decide singular vs plural replacement
            if len(localFiles) == 1:
                responseInput = re.sub(r"\bthese files\b", "this file", cleanedInput, flags=re.IGNORECASE)
            else:
                responseInput = cleanedInput
            #print(f"Response input: {responseInput}\n")
            return config.getResponse(
                model  = model,
                system = system,
                input  = responseInput,
                files  = localFiles, # allFiles,
                **kwargs,
            )

        def visionMode():
            model  = models['vision']
            config = self._getProviderConfig(model)
            # skills  = kwargs.pop('skills', None)
            # actions = kwargs.pop('actions', None)
            skills, actions = self._popSkillsActions(kwargs)
            localFiles = [self._downloadUrlToTemp(p) if p.startswith(("http://", "https://")) else p for p in allImages]
            # Decide singular vs plural replacement
            if len(localFiles) == 1:
                visionInput = re.sub(r"\bthese files\b", "this image", cleanedInput, flags=re.IGNORECASE)
            else:
                visionInput = re.sub(r"\bfiles\b", "images", cleanedInput)
            #print(f"Vision input: {visionInput}\n")
            return config.getVision(
                model   = model,
                system  = system,
                input   = visionInput,
                files   = localFiles, # allImages,
                **kwargs,
            )

        # FUTURE: Uncomment when generation mode is supported DO NOT DELETE
        # def generationMode():
        #     # skills  = kwargs.pop('skills', None)
        #     # actions = kwargs.pop('actions', None)
        #     kwargs.pop('model', None)  # remove model from kwargs
        #     kwargs.pop('user', None) or kwargs.pop('input', None)   # remove models from kwargs
        #     skills, actions = self._popSkillsActions(kwargs)
        #     model  = models['generation']
        #     config = self._getProviderConfig(model)
        #     user = cleanedInput
        #     return config.getGeneration(model=model, user=user, **kwargs)

        async def hybridMode():
            # skills  = kwargs.pop('skills', None)
            # actions = kwargs.pop('actions', None)
            model  = models['response']
            config = self._getProviderConfig(model)
            skills, actions = self._popSkillsActions(kwargs)
            # Run vision and response concurrently in threads
            visionTask   = asyncio.to_thread(visionMode)
            responseTask = asyncio.to_thread(responseMode)
            vision, response = await asyncio.gather(visionTask, responseTask)

            additional = f"[Media Files]:\n{vision}\n[Doc Files]:\n{response}"

            #print(f"Hybrid text: {text}\n")
            msgs       = f"{cleanedInput}[Media Files]:\n[Doc Files]:\n"

            return config.getResponse(
                model        = model,
                system       = system,
                instructions = additional,
                input        = msgs,
                **kwargs,
            )

        # FUTURE: Uncomment when generation mode is supported DO NOT DELETE
        # intent = self._routeIntent(models['response'], cleanedInput)
        # if intent == "generation":
        #     return generationMode()

        modeMap = {
            "holo": holoMode,
            "vision": visionMode,
            "response": responseMode,
            "hybrid": hybridMode,
        }

        mode = (
            "hybrid"   if (allImages and allFiles) else
            "vision"   if allImages                else
            "response" if allFiles                 else
            "holo"
        )
        #print(f"Using mode: {mode}\n")

        modeFunc = modeMap[mode]

        # Handle both sync and async seamlessly
        if inspect.iscoroutinefunction(modeFunc):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # Already in an event loop -> return coroutine for caller to await
                #print("[Notice] Running in an existing event loop, returning coroutine.")
                return modeFunc()
            else:
                # No event loop running -> safe to use asyncio.run
                #print("[Notice] No event loop running, using asyncio.run.")
                return asyncio.run(modeFunc())

        return modeFunc()

    def _popSkillsActions(self, kwargs):
        return kwargs.pop("skills", None), kwargs.pop("actions", None)

    def _normalizePaths(self, paths):
        out = []
        for p in paths:
            if isinstance(p, str) and p.startswith(("http://", "https://")):
                out.append(p)  # leave URL untouched
            else:
                out.append(os.path.normpath(p))
        return out

    def _extractPaths(self, text: Union[str, Iterable[str]], includePatterns: dict, excludePatterns: dict):
        texts = text if isinstance(text, (list, tuple, set)) else [text]

        # Join all include/exclude patterns into one regex each
        includeRegex = re.compile("|".join(includePatterns.values()), re.IGNORECASE)
        excludeRegex = re.compile("|".join(fr"^{p}$" for p in excludePatterns.values()), re.IGNORECASE)

        results = []
        for t in texts:
            if not t:
                continue
            matches = includeRegex.findall(t)
            # findall with capturing groups returns tuples; flatten and filter
            results.extend(
                p for pair in matches for p in (pair if isinstance(pair, tuple) else (pair,))
                if p and not excludeRegex.fullmatch(p)
            )
        return results

    def _extractMediaInfo(self, text: Union[str, Iterable[str]]):
        return self._extractPaths(text, self._mediaPatterns(), self._filePatterns())

    def _extractFileInfo(self, text: Union[str, Iterable[str]]):
        return self._extractPaths(text, self._filePatterns(), self._mediaPatterns())

    def _downloadUrlToTemp(self, url: str) -> str:
        try:
            # Guess extension from URL or MIME
            _, ext = os.path.splitext(url)
            if not ext:
                mime, _ = mimetypes.guess_type(url)
                ext = mimetypes.guess_extension(mime) or ".bin"

            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                urllib.request.urlretrieve(url, tmp.name)
                return tmp.name
        except Exception as e:
            print(f"[Warning] Failed to fetch {url}: {e}")
            return None

    def _mediaPatterns(self):
        EXT = r'(?:png|jpe?g|gif|webp|bmp|tiff?)'
        return {
            "win":  fr'([A-Za-z]:(?:\\|/)[^,\n]*?\.{EXT})',
            "unix": fr'(/[^ ,\n]*?/[^,\n]*?\.{EXT})',
            "url":  fr'(https?://[^\s,;()]+?\.{EXT}(?:\?[^\s,;()]*)?)',
        }

    def _filePatterns(self):
        EXT = r'(?:docx?|pdf|txt|odt|rtf|xlsx?|pptx?)'
        return {
            "win":  fr'([A-Za-z]:(?:\\|/)[^,\n]*?\.{EXT})',
            "unix": fr'(/[^ ,\n]*?/[^,\n]*?\.{EXT})',
            "url":  fr'(https?://[^\s,;()]+?\.{EXT}(?:\?[^\s,;()]*)?)',
        }

    def _cleanInput(self, text: str) -> str:
        allExts = r'(?:png|jpe?g|gif|webp|bmp|tiff?|docx?|pdf|txt|odt|rtf|xlsx?|pptx?)'

        # Local paths (allow spaces until extension)
        win  = rf'[A-Za-z]:(?:\\|/)[^,\n]*?\.{allExts}'
        unix = rf'/[^ ,\n]*?/[^,\n]*?\.{allExts}'

        # URLs ending with target extensions (optional querystring)
        url  = rf'https?://[^\s,;()]+?\.{allExts}(?:\?[^\s,;()]*)?'

        pathOrUrl = rf'(?:{win}|{unix}|{url})'

        # Remove matches with optional nearby separators
        text = re.sub(rf'(?:\s*[,;]?\s*){pathOrUrl}(?=(\s|[,;.)]|$))',
                      '', text, flags=re.IGNORECASE)

        # Collapse leftover punctuation/whitespace artifacts
        text = re.sub(r'\s*[,;]\s*', ' ', text)
        return ' '.join(text.split())

    def _routeResponse(self, **kwargs):
        kwargs = {k.lower(): v for k, v in kwargs.items()}
        model  = kwargs.get('model')
        config = self._getProviderConfig(model)
        return config.getResponse(**kwargs)

    def _routeVision(self, **kwargs):
        kwargs = {k.lower(): v for k, v in kwargs.items()}
        model  = kwargs.get('model')
        config = self._getProviderConfig(model)
        return config.getVision(**kwargs)

    def _routeGeneration(self, **kwargs):
        kwargs = {k.lower(): v for k, v in kwargs.items()}
        model  = kwargs.get('model')
        config = self._getProviderConfig(model)
        return config.getGeneration(**kwargs)

    def _routeIntent(self, model, user):
        system = (
            "Your task is to determine the user's intent and respond ONLY with one of the following:"
            "\n- 'response' for text generation"
            "\n- 'vision' for vision tasks"
            "\n- 'generation' for image generation tasks"
        )

        return self.Response(model=model,system=system,input=user)

    def isStructured(self, obj):
        """
        Check if the input is a structured list of message dicts.
        A structured list is defined as a list of dictionaries where each dictionary
        contains both "role" and "content" keys.
        Returns True if the input is a structured list, False otherwise.
        """
        return isStructured(obj)

    def formatInput(self, value):
        """
        Formats the input value into a list.
        - If `value` is a string, returns a list containing that string.
        - If `value` is already a list, returns it as is.
        - If `value` is None, returns an empty list.
        """
        return [value] if isinstance(value, str) else value

    def formatConversation(self, convo, user):
        """
        Returns a flat list representing the full conversation:
        - If `convo` is a list, appends the user input (str or list) to it.
        - If `convo` is a string, creates a new list with convo and user input.
        """
        if isinstance(convo, str):
            convo = [convo]
        if isinstance(user, str):
            return convo + [user]
        elif isinstance(user, list):
            return convo + user
        else:
            raise TypeError("User input must be a string or list of strings.")


    def formatJsonInput(self, role: str, content: str) -> dict:
        """
        Format content for JSON-based APIs like OpenAI, Groq, etc.
        Converts role to lowercase and ensures it is one of the allowed roles.
        """
        return formatJsonInput(role=role, content=content)

    def formatJsonExtended(self, role: str, content: str) -> dict:
        """
        Extended JSON format for APIs like OpenAI, Groq, etc.
        Maps 'assistant', 'developer', 'model' and 'system' to 'assistant'.
        All other roles (including 'user') map to 'user'.
        """
        return formatJsonExtended(role=role, content=content)

    def parseJsonInput(self, data):
        """
        Accepts a string, a list of strings, or a list of message dicts/typed objects.
        Parses a single raw string with optional role prefix (user:, system:, developer:, assistant:)
        Returns a list of normalized message objects using formatJsonExtended.
        """
        return parseJsonInput(data)

    def formatTypedInput(self, role: str, content: str) -> dict:
        """
        Format content for typed APIs like Google GenAI.
        Converts role to lowercase and ensures it is one of the allowed roles.
        """
        return formatTypedInput(role=role, content=content)

    def formatTypedExtended(self, role: str, content: str) -> dict:
        """
        Extended typed format for Google GenAI APIs.
        Maps 'assistant', 'developer', 'system' and 'model' to 'model'.
        All other roles (including 'user') map to 'user'.
        """
        return formatTypedExtended(role=role, content=content)

    def parseTypedInput(self, data):
        """
        Accepts a string, a list of strings, or a list of message dicts/typed objects.
        Parses a single raw string with optional role prefix (user:, system:, developer:, assistant:)
        Returns a list of normalized Google GenAI message objects using formatTypedExtended.
        """
        return parseTypedInput(data)

    def safetySettings(self, **kwargs):
        """
        Construct a list of Google GenAI SafetySetting objects.

        Accepts thresholds as keyword arguments:
            harassment, hateSpeech, sexuallyExplicit, dangerousContent

        Example:
            safetySettings(harassment="block_high", hateSpeech="block_low")
        """
        return safetySettings(**kwargs)

