
import os
import threading
import logging

from HoloLink import HoloLink
from SkillLink import SkillLink

from HoloAI.HAIUtils.HAIUtils import (
    parseInstructions,
    validateResponseArgs,
    validateVisionArgs,
    validateGenerationArgs,
    safeStrip,
)

logger = logging.getLogger(__name__)


class BaseConfig:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(BaseConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return

        self.holoLink  = HoloLink()  # Initialize the HoloLink instance
        self.skillLink = SkillLink()  # Initialize the SkillLink instance
        self.skills  = None
        self.actions = None 
        self.tools   = None
        self.show    = 'hidden'
        self.effort  = 'auto'
        self.budget  = 1369
        self.tokens  = 3369
        self.files   = []      # Default paths for images
        self.path    = "image.png"
        self.collect = 10      # Default number of frames to collect
        self.verbose = False
        self.choice  = 'auto'  # Default choice for tool choice
        self.creativity = 0.5

        self.initialized = True

    # ---------------------------------------------------------
    # Public methods
    # ---------------------------------------------------------
    def getResponse(self, **kwargs):
        """
        Get a Response from the configured model.
        """
        kwargs = self.getKwargs(**kwargs)

        keys = self.getKeys("response")
        params = self.extractKwargs(kwargs, keys)

        if ('skills' in kwargs) or ('actions' in kwargs):
            params['skills'] = self.parseSkillsAndActions(kwargs.get('skills'), kwargs.get('actions'))
        else:
            params.pop('skills', None)
        params.pop('actions', None)
        validateResponseArgs(params["model"], params["user"])
        return self.Response(**params)

    def getVision(self, **kwargs):
        """
        Get a Vision response from the configured model.
        """
        kwargs = self.getKwargs(**kwargs)

        keys = self.getKeys("vision")
        params = self.extractKwargs(kwargs, keys)

        if ('skills' in kwargs) or ('actions' in kwargs):
            params['skills'] = self.parseSkillsAndActions(kwargs.get('skills'), kwargs.get('actions'))
        else:
            params.pop('skills', None)
        params.pop('actions', None)
        validateVisionArgs(params["model"], params["user"], params["files"])
        return self.Vision(**params)

    def getGeneration(self, **kwargs):
        """
        Get a Generation response from the configured model.
        """
        kwargs = self.getKwargs(**kwargs)

        keys = self.getKeys("generation")
        params = self.extractKwargs(kwargs, keys)

        if ('skills' in kwargs) or ('actions' in kwargs):
            params['skills'] = self.parseSkillsAndActions(kwargs.get('skills'), kwargs.get('actions'))
        else:
            params.pop('skills', None)
        params.pop('actions', None)
        validateGenerationArgs(params["model"], params["user"])
        return self.Generation(**params)

    def getKeys(self, key):
        baseKeys = [
            "model", "system", "user", "tokens", "creativity", "verbose"
        ]
        extras = {
            "response":   ["skills", "actions", "tools", "choice", "show", "effort", "budget", "files"],
            "vision":     ["files", "collect"],
            "generation": []
        }
        try:
            return baseKeys + extras[key.lower()]
        except KeyError:
            raise ValueError(f"Unknown key set: {key}")

    def getKwargs(self, **kwargs):
        """
        Normalizes incoming kwargs into canonical names.
        """
        k = dict(kwargs)  # shallow copy to avoid side effects

        # derive 'system' from current kwargs first
        system = parseInstructions(k)
        if system is not None:
            k['system'] = system

        # prefer explicit 'user', else fall back to 'input'
        if 'user' not in k and k.get('input') is not None:
            k['user'] = k['input']

        # alias map: only fill target if not already set
        aliasMap = {
            'max_tokens': 'tokens',
            'max_budget': 'budget',
            'tool_choice':'choice',
            'temperature':'creativity',
        }
        for src, dst in aliasMap.items():
            if dst not in k and k.get(src) is not None:
                k[dst] = k[src]

        return k

    def extractKwargs(self, kwargs, keys, defaults=None):
        """
        Extracts specified keys from kwargs, using defaults or class attributes if needed.
        Treats explicit None as "not provided" so defaults still apply.
        """
        result = {}
        defaults = defaults or {}

        for k in keys:
            if k in kwargs and kwargs[k] is not None:
                result[k] = kwargs[k]
            else:
                result[k] = defaults.get(k, getattr(self, k, None))

        return result

    def parseSkillsAndActions(self, skills, actions):
        if actions and not skills:
            raise ValueError("You cannot use 'actions' without also providing 'skills'.")
        if skills and actions:
            return [skills, actions]
        # if skills is already a list, return it as is if not make sure it's a list
        if isinstance(skills, list):
            return skills
        else:
            return [skills]

    def extractIntent(self, user):
        """
        Extract the last user text from a string, a list of message dicts, or a mixed list.
        Returns a string suitable for use in skills or message formatting.
        """
        if isinstance(user, list) and user:
            lastMsg = user[-1]
            if isinstance(lastMsg, dict):
                content = lastMsg.get("content", "")
                if isinstance(content, list):
                    return " ".join(
                        safeStrip(part.get("text", "")) for part in content if part.get("type") == "text"
                    )
                if isinstance(content, str):
                    return safeStrip(content)
                return safeStrip(content)
            if isinstance(lastMsg, str):
                return safeStrip(lastMsg)
            return safeStrip(lastMsg)
        elif isinstance(user, str):
            return safeStrip(user)
        return ""

    def skillInstructions(self, capabilities):
        """
        Get skill instructions for the ava based on its capabilities.
        NOTE: the skillInstructions in the skillLink method will automatically use your naming conventions you can also,
        - pass limit=(int e.g 10) to limit the number of examples included in the instructions, or
        - pass verbose=True to view the instructions in detail as it will print the instructions to the console.
        """
        try:
            return self.holoLink.skillInstructions(capabilities)
        except Exception as e:
            try:
                return self.skillLink.skillInstructions(capabilities)
            except Exception as e:
                logger.error(f"Failed to get Skill Instructions", exc_info=True)
                return ""

    def getActions(self, action: str) -> list:
        """
        Get a list of actions based on the given action string.
        This method uses the skills manager's action parser to retrieve actions that match the given string.
        If the action is not found, it returns an empty list.
        """
        try:
            return self.holoLink.actionParser.getActions(action)
        except Exception as e:
            try:
                return self.skillLink.actionParser.getActions(action)
            except Exception as e:
                logger.error(f"Failed to get Actions for action: {action}", exc_info=True)
                return []

    def executeActions(self, actions, action):
        """
        Execute a list of actions using the skillLink's executeActions method.
        This method will return the results of the executed actions.
        If the actions are not found, it will return an empty list.
        """
        try:
            return self.holoLink.executeActions(actions, action)
        except Exception as e:
            try:
                return self.skillLink.executeActions(actions, action)
            except Exception as e:
                logger.error(f"Failed to execute Actions for action: {action}", exc_info=True)
                return []

    def executeSkills(self, skills, user, tokens, verbose=False) -> str:
        """
        Execute skills based on the provided skills, user input, and tokens.
        This method processes the skills, retrieves the actions, and executes them.
        :param skills: List of skills to execute.
        :param user: User input to provide context for the skills.
        :param tokens: Number of tokens to use for the skills execution.
        :param verbose: If True, prints detailed information about the execution.
        :return: A string containing the results of the executed skills.
        """
        try:
            if skills:
                agentSkills, actions = (skills or [None, None])[:2]
                instructions  = self.skillInstructions(agentSkills)
                calledActions = self.processSkills(instructions, user, tokens)
                getActions    = self.getActions(calledActions)
                if getActions:
                    results         = self.executeActions(actions, getActions)
                    filteredResults = [str(result) for result in results if result]
                    if filteredResults:
                        combined = "\n".join(filteredResults)
                        if verbose:
                            print(f"Combined Results:\n{combined}\n")
                        return f"Use these results from the actions called when responding:\n{combined}"
            return 'None'
        except Exception as e:
            logger.error(f"Failed to execute skills: {skills} with user: {user}", exc_info=True)
            return ""























# class BaseConfig:
#     _instance = None
#     _lock = threading.Lock()

#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             with cls._lock:
#                 if not cls._instance:
#                     cls._instance = super(BaseConfig, cls).__new__(cls)
#         return cls._instance

#     def __init__(self):
#         if getattr(self, 'initialized', False):
#             return

#         self.holoLink  = HoloLink()  # Initialize the HoloLink instance
#         self.skillLink = SkillLink()  # Initialize the SkillLink instance
#         self.skills  = None
#         self.actions = None 
#         self.tools   = None
#         self.show    = 'hidden'
#         self.effort  = 'auto'
#         self.budget  = 1369
#         self.tokens  = 3369
#         self.files   = []      # Default paths for images
#         self.collect = 10      # Default number of frames to collect
#         self.verbose = False
#         self.choice  = 'auto'  # Default choice for tool choice
#         self.creativity = 0.5

#         self.initialized = True

#     # ---------------------------------------------------------
#     # Public methods
#     # ---------------------------------------------------------
#     def getResponse(self, **kwargs):
#         """
#         Get a Response from the configured model.
#         """
#         user = kwargs.get('user') or kwargs.get('input')
#         if user is not None:
#             kwargs['user'] = user
#         system = parseInstructions(kwargs)
#         if system is not None:
#             kwargs['system'] = system
#         if 'tokens' not in kwargs and 'max_tokens' in kwargs:
#             kwargs['tokens'] = kwargs['max_tokens']
#         if 'budget' not in kwargs and 'max_budget' in kwargs:
#             kwargs['budget'] = kwargs['max_budget']
#         if 'files' not in kwargs and 'paths' in kwargs:
#             kwargs['files'] = kwargs['paths']
#         if 'choice' not in kwargs and 'tool_choice' in kwargs:
#             kwargs['choice'] = kwargs['tool_choice']
#         if 'creativity' not in kwargs and 'temperature' in kwargs:
#             kwargs['creativity'] = kwargs['temperature']
        
#         # keys = [
#         #     "model", "system", "user", "skills", "tools", "choice",
#         #     "show", "effort", "budget", "tokens", "files", "collect", "verbose"
#         # ]
#         keys = self.getKeys("response")
#         params = self.extractKwargs(kwargs, keys)
#         # params['skills'] = self.parseSkillsAndActions(params.get('skills'), params.get('actions'))
#         # params.pop('actions', None)
#         if ('skills' in kwargs) or ('actions' in kwargs):
#             params['skills'] = self.parseSkillsAndActions(kwargs.get('skills'), kwargs.get('actions'))
#         else:
#             params.pop('skills', None)
#         params.pop('actions', None)
#         validateResponseArgs(params["model"], params["user"])
#         return self.Response(**params)

#     def getVision(self, **kwargs):
#         """
#         Get a Vision response from the configured model.
#         """
#         user = kwargs.get('user') or kwargs.get('input')
#         if user is not None:
#             kwargs['user'] = user
#         system = parseInstructions(kwargs)
#         if system is not None:
#             kwargs['system'] = system
#         if 'tokens' not in kwargs and 'max_tokens' in kwargs:
#             kwargs['tokens'] = kwargs['max_tokens']
#         if 'budget' not in kwargs and 'max_budget' in kwargs:
#             kwargs['budget'] = kwargs['max_budget']
#         if 'files' not in kwargs and 'paths' in kwargs:
#             kwargs['files'] = kwargs['paths']
#         if 'choice' not in kwargs and 'tool_choice' in kwargs:
#             kwargs['choice'] = kwargs['tool_choice']
#         if 'creativity' not in kwargs and 'temperature' in kwargs:
#             kwargs['creativity'] = kwargs['temperature']
#         # keys = [
#         #     "model", "system", "user", "skills", "tools", "choice",
#         #     "show", "effort", "budget", "tokens", "files", "collect", "verbose"
#         # ]
#         keys = self.getKeys("vision")
#         params = self.extractKwargs(kwargs, keys)
#         # params['skills'] = self.parseSkillsAndActions(params.get('skills'), params.get('actions'))
#         # params.pop('actions', None)
#         if ('skills' in kwargs) or ('actions' in kwargs):
#             params['skills'] = self.parseSkillsAndActions(kwargs.get('skills'), kwargs.get('actions'))
#         else:
#             params.pop('skills', None)
#         params.pop('actions', None)
#         validateVisionArgs(params["model"], params["user"], params["files"])
#         return self.Vision(**params)

#     def getKeys(self, key):
#         keyMap = {
#             "response": [
#                 "model", "system", "user", "skills", "actions", "tools", "choice",
#                 "show", "effort", "budget", "tokens", "creativity", "files", "verbose"
#             ],
#             "vision": [
#                 "model", "system", "user", "skills", "actions", "tools", "choice",
#                 "show", "effort", "budget", "tokens", "creativity", "files", "collect", "verbose"
#             ]
#         }
#         try:
#             return keyMap[key.lower()]
#         except KeyError:
#             raise ValueError(f"Unknown key set: {key}")

#     def parseSkillsAndActions(self, skills, actions):
#         if actions and not skills:
#             raise ValueError("You cannot use 'actions' without also providing 'skills'.")
#         if skills and actions:
#             return [skills, actions]
#         # if skills is already a list, return it as is if not make sure it's a list
#         if isinstance(skills, list):
#             return skills
#         else:
#             return [skills]

#     def extractKwargs(self, kwargs, keys, defaults=None):
#         """
#         Extracts specified keys from kwargs, using defaults or class attributes if needed.

#         Args:
#             kwargs (dict): Incoming keyword arguments.
#             keys (list[str]): Keys to extract.
#             defaults (dict, optional): Default values for keys.

#         Returns:
#             dict: Extracted key-value pairs.
#         """
#         result = {}
#         defaults = defaults or {}
#         for k in keys:
#             # Priority: kwargs > defaults > class attribute > None
#             result[k] = kwargs.get(k,
#                            defaults.get(k, getattr(self, k, None)))
#         return result

#     def extractIntent(self, user):
#         """
#         Extract the last user text from a string, a list of message dicts, or a mixed list.
#         Returns a string suitable for use in skills or message formatting.
#         """
#         # if isinstance(user, list) and user:
#         #     lastMsg = user[-1]
#         #     if isinstance(lastMsg, dict):
#         #         content = lastMsg.get("content", "")
#         #         # If content is a list of type-objects (OpenAI v1)
#         #         if isinstance(content, list):
#         #             return " ".join(
#         #                 str(part.get("text", "")) for part in content if part.get("type") == "text"
#         #             ).strip()
#         #         # If content is a string (Anthropic etc.)
#         #         if isinstance(content, str):
#         #             return content.strip() if content else ""
#         #         # Fallback: convert to string if not None, else empty
#         #         return str(content).strip() if content is not None else ""
#         #     if isinstance(lastMsg, str):
#         #         return lastMsg.strip() if lastMsg else ""
#         #     return str(lastMsg).strip() if lastMsg is not None else ""
#         # elif isinstance(user, str):
#         #     return user.strip() if user else ""
#         # return ""
#         if isinstance(user, list) and user:
#             lastMsg = user[-1]
#             if isinstance(lastMsg, dict):
#                 content = lastMsg.get("content", "")
#                 if isinstance(content, list):
#                     return " ".join(
#                         safeStrip(part.get("text", "")) for part in content if part.get("type") == "text"
#                     )
#                 if isinstance(content, str):
#                     return safeStrip(content)
#                 return safeStrip(content)
#             if isinstance(lastMsg, str):
#                 return safeStrip(lastMsg)
#             return safeStrip(lastMsg)
#         elif isinstance(user, str):
#             return safeStrip(user)
#         return ""

#     def skillInstructions(self, capabilities):
#         """
#         Get skill instructions for the ava based on its capabilities.
#         NOTE: the skillInstructions in the skillLink method will automatically use your naming conventions you can also,
#         - pass limit=(int e.g 10) to limit the number of examples included in the instructions, or
#         - pass verbose=True to view the instructions in detail as it will print the instructions to the console.
#         """
#         try:
#             return self.holoLink.skillInstructions(capabilities)
#         except Exception as e:
#             try:
#                 return self.skillLink.skillInstructions(capabilities)
#             except Exception as e:
#                 logger.error(f"Failed to get Skill Instructions", exc_info=True)
#                 return ""

#     def getActions(self, action: str) -> list:
#         """
#         Get a list of actions based on the given action string.
#         This method uses the skills manager's action parser to retrieve actions that match the given string.
#         If the action is not found, it returns an empty list.
#         """
#         try:
#             return self.holoLink.actionParser.getActions(action)
#         except Exception as e:
#             try:
#                 return self.skillLink.actionParser.getActions(action)
#             except Exception as e:
#                 logger.error(f"Failed to get Actions for action: {action}", exc_info=True)
#                 return []

#     def executeActions(self, actions, action):
#         """
#         Execute a list of actions using the skillLink's executeActions method.
#         This method will return the results of the executed actions.
#         If the actions are not found, it will return an empty list.
#         """
#         try:
#             return self.holoLink.executeActions(actions, action)
#         except Exception as e:
#             try:
#                 return self.skillLink.executeActions(actions, action)
#             except Exception as e:
#                 logger.error(f"Failed to execute Actions for action: {action}", exc_info=True)
#                 return []

#     def executeSkills(self, skills, user, tokens, verbose=False) -> str:
#         """
#         Execute skills based on the provided skills, user input, and tokens.
#         This method processes the skills, retrieves the actions, and executes them.
#         :param skills: List of skills to execute.
#         :param user: User input to provide context for the skills.
#         :param tokens: Number of tokens to use for the skills execution.
#         :param verbose: If True, prints detailed information about the execution.
#         :return: A string containing the results of the executed skills.
#         """
#         try:
#             if skills:
#                 agentSkills, actions = (skills or [None, None])[:2]
#                 instructions  = self.skillInstructions(agentSkills)
#                 calledActions = self.processSkills(instructions, user, tokens)
#                 getActions    = self.getActions(calledActions)
#                 if getActions:
#                     results         = self.executeActions(actions, getActions)
#                     filteredResults = [str(result) for result in results if result]
#                     if filteredResults:
#                         combined = "\n".join(filteredResults)
#                         if verbose:
#                             print(f"Combined Results:\n{combined}\n")
#                         return f"Use these results from the actions called when responding:\n{combined}"
#             return 'None'
#         except Exception as e:
#             logger.error(f"Failed to execute skills: {skills} with user: {user}", exc_info=True)
#             return ""
