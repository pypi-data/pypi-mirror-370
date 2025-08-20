import os
import threading
import base64
from tkinter import SE
from dotenv import load_dotenv
from google import genai
from google.genai import types

from HoloAI.HAIUtils.HAIUtils import (
    isStructured,
    formatTypedInput,
    formatTypedExtended,
    parseTypedInput,
    getFrames,
    supportsReasoning,
    extractFileInfo,
    extractText
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()


class GoogleConfig(BaseConfig):
    def __init__(self, apiKey=None):
        super().__init__()
        self._setClient(apiKey)
        self._setModels()

    def _setClient(self, apiKey=None):
        if not apiKey:
            apiKey = os.getenv("GOOGLE_API_KEY")
        if not apiKey:
            raise KeyError("Google API key not found. Please set GOOGLE_API_KEY in your environment variables.")
        self.client = genai.Client(api_key=apiKey)

    def _setModels(self):
        self.RModel = os.getenv("GOOGLE_RESPONSE_MODEL", "gemini-2.5-flash")
        self.VModel = os.getenv("GOOGLE_VISION_MODEL", "gemini-2.5-flash")

    # ---------------------------------------------------------
    # Response
    # --------------------------------------------------------- 
    def Response(self, **kwargs) -> str:
        keys = self.getKeys("response")
        params = self.extractKwargs(kwargs, keys)
        messages = parseTypedInput(params["user"])

        if params.get("skills"):
            additionalInfo = self.executeSkills(
                params["skills"], params["user"], params["tokens"], params["verbose"]
            )
            if additionalInfo:
                messages.append(formatTypedInput("user", additionalInfo))

        messages += self._docFiles(params)
        
        reasoning = supportsReasoning(params["model"])
        generateConfig = self._configArgs(params, reasoning=reasoning)
        args = self._getArgs(params["model"], messages, generateConfig)

        response = self._endPoint(**args)
        return response if params["verbose"] else response.text

    # -----------------------------------------------------------------
    # Vision
    # -----------------------------------------------------------------
    def Vision(self, **kwargs):
        keys = self.getKeys("vision")
        params = self.extractKwargs(kwargs, keys)

        images = self._mediaFiles(params["files"], params["collect"])

        textPart = types.Part(text=params["user"])
        messages = [types.Content(role="user", parts=images + [textPart])]

        generateConfig = self._configArgs(params, reasoning=False)
        args = self._getArgs(params["model"], messages, generateConfig)

        response = self._endPoint(**args)
        return response if params["verbose"] else response.text

    # ---------------------------------------------------------
    # Generation
    # ---------------------------------------------------------
    def Generation(self, **kwargs):
        keys = self.getKeys("generation")
        params = self.extractKwargs(kwargs, keys)

        model = params.get("model")
        user = params["user"]

        return "Google image generation not support yet."
    
    # ---------------------------------------------------------
    # Skills
    # ---------------------------------------------------------
    def processSkills(self, instructions, user, tokens) -> str:
        intent = self.extractIntent(user)
        messages = [formatTypedInput("user", intent)]
        params = {
            "system": instructions,
            "tokens": tokens,
        }
        generateConfig = self._configArgs(params, reasoning=False)
        args = self._getArgs(self.RModel, messages, generateConfig)
        response = self._endPoint(**args)
        return response.text

    def _endPoint(self, **args) -> str:
        return self.client.models.generate_content(**args)

    def _configArgs(self, params, reasoning=False):
        args = {
            "response_mime_type": "text/plain",
            "system_instruction": [params["system"]],
            "max_output_tokens": params["tokens"],
        }
        if params.get("creativity"):
            args["temperature"] = params["creativity"]

        if params.get("tools"):
            args["tools"] = params["tools"]
            args["function_calling_config"] = types.FunctionCallingConfig(
                mode=self._mapChoice(params.get("choice"))
            )

        if reasoning and supportsReasoning(params["model"]):
            if params["effort"] == "auto":
                params["budget"] = -1
            args["thinking_config"] = types.ThinkingConfig(thinking_budget=params["budget"])
        return types.GenerateContentConfig(**args)

    def _mapChoice(self, choice):
        mapping = {
            "auto": "AUTO",
            "required": "ANY",
            "none": "NONE"
        }
        return mapping.get((choice or "auto").lower(), "AUTO")

    def _getArgs(self, model, messages, config):
        args = {
            "model": model,
            "contents": messages,
            "config": config
        }
        return args

    def _mediaFiles(self, files, collect):
        images = []
        for path in files:
            frames = getFrames(path, collect)
            b64, mimeType, _ = frames[0]
            images.append(
                types.Part(
                    inline_data=types.Blob(
                        mime_type=f"image/{mimeType}",
                        data=base64.b64decode(b64)
                    )
                )
            )
        return images

    def _docFiles(self, params):
        messages = []
        # intent = self.extractIntent(params["user"])
        # fileInfo = extractFileInfo(intent)
        # if fileInfo:
        #     messages.append(formatTypedInput("user", fileInfo))
        files = params["files"]
        if files:
            fileInfo = str(extractText(files))
            if fileInfo:
                messages.append(formatTypedInput("user", fileInfo))
        return messages
