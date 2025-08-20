
import os
import sys
import json
import inspect
import re
import logging
from google import genai
from google.genai import types
from typing import get_type_hints, get_origin, get_args
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ToolParser:

    @staticmethod
    def parseToolDocstring(docstring):
        result = {"description": "", "additional_information": None}
        if not docstring:
            return result
        lines = [l.strip() for l in docstring.splitlines() if l.strip()]
        for line in lines:
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            key = key.lower().replace(" ", "_")
            val = val.strip().strip('"').strip("'")
            if key in result:
                result[key] = val
        if not result["description"] and lines:
            result["description"] = lines[0]
        return result

    @staticmethod
    def getListSig(obj, func_name):
        """
        Look for LIST_SIG (or listSig/list_sig) on the module or instance.
        Returns a list of field-names if present, else None.
        """
        for attr in ("LIST_SIG", "listSig", "list_sig"):
            val = getattr(obj, attr, None)
            if isinstance(val, dict):
                # 1) exact match
                if func_name in val:
                    return val[func_name]
                # 2) fallback: strip trailing digits (e.g. updateId1 → updateId)
                base = re.sub(r"\d+$", "", func_name)
                if base in val:
                    return val[base]
        return None

    @staticmethod
    def getDictSig(obj, func_name):
        """
        Look for DICT_SIG (or dictSig/dict_sig) on the module or instance.
        Returns a dict-of-descriptions if present, else None.
        """
        for attr in ("DICT_SIG", "dictSig", "dict_sig"):
            val = getattr(obj, attr, None)
            if isinstance(val, dict):
                # 1) exact match
                if func_name in val:
                    return val[func_name]
                # 2) fallback: strip trailing digits (e.g. updateId2 → updateId)
                base = re.sub(r"\d+$", "", func_name)
                if base in val:
                    return val[base]
        return None


    @staticmethod
    def getTools(toolLists):
        """
        Extract all public callables from modules, classes or instances,
        and register class-methods under their plain method names.
        """
        tools = {}

        def addModuleFunctions(mod):
            for name, fn in inspect.getmembers(mod, inspect.isfunction):
                if not name.startswith("_"):
                    tools[name] = fn

        def addModuleClassMethods(mod):
            for cls_name, cls in inspect.getmembers(mod, inspect.isclass):
                if cls.__module__ != mod.__name__:
                    continue
                try:
                    inst = cls()
                except:
                    inst = None
                for name, fn in inspect.getmembers(cls, inspect.isfunction):
                    if not name.startswith("_"):
                        tools[name] = getattr(inst, name) if inst else fn

        for item in toolLists:
            if inspect.ismodule(item):
                addModuleFunctions(item)
                addModuleClassMethods(item)

            elif inspect.isclass(item):
                # When they pass a class itself
                try:
                    inst = item()
                except:
                    inst = None
                for name, fn in inspect.getmembers(item, inspect.isfunction):
                    if not name.startswith("_"):
                        tools[name] = getattr(inst, name) if inst else fn

            elif inspect.isfunction(item):
                if not item.__name__.startswith("_"):
                    tools[item.__name__] = item

            else:
                # bound instance or arbitrary object
                cls = item.__class__
                for name, fn in inspect.getmembers(cls, inspect.isfunction):
                    if not name.startswith("_"):
                        tools[name] = getattr(item, name)

        return tools


    @staticmethod
    def extractJson(text):
        match = re.search(r"(\[.*?\]|\{.*?\})", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return json.loads(text)

    @staticmethod
    def parseJsonSchema(func, schemaType):
        """
        Build a JSON schema for a function.  If a LIST_SIG or DICT_SIG exists,
        emit a single array or object parameter but set `required` to the
        fields declared in your LIST_SIG/DICT_SIG.
        """
        schemaType = schemaType.lower()
        if schemaType == "chat_completions":
            schemaType = "completions"

        sig   = inspect.signature(func)
        hints = get_type_hints(func)
        props = {}
        required = []
        TYPE_MAP = {int: "integer", float: "number", str: "string", bool: "boolean"}

        # first look on module, then on bound instance
        module    = sys.modules.get(func.__module__)
        list_info = ToolParser.getListSig(module, func.__name__) or []
        dict_info = ToolParser.getDictSig(module, func.__name__) or []
        inst = getattr(func, "__self__", None)
        if inst:
            list_info = list_info or ToolParser.getListSig(inst, func.__name__) or []
            dict_info = dict_info or ToolParser.getDictSig(inst, func.__name__) or []

        # if a LIST_SIG is declared, emit one array param but mark required=its fields
        if list_info:
            # assume single arg (e.g. infoList)
            param = next(p for p in sig.parameters.values() if p.name != "self")
            name = param.name
            # figure out item type from annotation if present
            pType = hints.get(name, list)
            origin, args = get_origin(pType), get_args(pType)
            itemType = args[0] if origin is list and args else str
            props[name] = {
                "type":  "array",
                "items": { "type": TYPE_MAP.get(itemType, "string") }
            }
            # required should be the fields the user declared:
            required = list_info

        # if a DICT_SIG is declared, emit one object param but required=its keys
        elif dict_info:
            param = next(p for p in sig.parameters.values() if p.name != "self")
            name = param.name
            props[name] = {
                "type":  "object",
                "items": { "type": "string" }
            }
            # dict_info may be list-of-keys or dict-of-descriptions
            keys = dict_info if isinstance(dict_info, list) else list(dict_info.keys())
            required = keys

        # otherwise generic: each parameter becomes its own prop
        else:
            for param in sig.parameters.values():
                name = param.name
                pType = hints.get(name, str)
                origin, args = get_origin(pType), get_args(pType)

                if origin is list or pType is list:
                    item = args[0] if args else str
                    props[name] = {
                        "type":  "array",
                        "items": { "type": TYPE_MAP.get(item, "string") }
                    }
                elif origin is dict or pType is dict:
                    val = args[1] if len(args) > 1 else str
                    props[name] = {
                        "type":  "object",
                        "items": { "type": TYPE_MAP.get(val, "string") }
                    }
                else:
                    props[name] = { "type": TYPE_MAP.get(pType, "string") }

                if param.default is param.empty:
                    required.append(name)

        # pull description from docstring
        meta = ToolParser.parseToolDocstring(inspect.getdoc(func))
        desc = meta["description"] or ""
        if meta.get("additional_information"):
            desc += f"\nAdditional Information: {meta['additional_information']}"

        func_schema = {
            "name":        func.__name__,
            "description": desc,
            "parameters": {
                "type":       "object",
                "properties": props,
                "required":   required
            }
        }

        if schemaType == "completions":
            return { "type": "function", "function": func_schema }
        return { "type": "function", **func_schema }


    @staticmethod
    def parseTypedSchema(func):
        """
        Build a Google GenAI FunctionDeclaration, flattening LIST_SIG/DICT_SIG metadata
        into a single list or dict parameter when present, otherwise
        emitting individual parameters.
        """
        sig   = inspect.signature(func)
        hints = get_type_hints(func)
        props = {}
        TYPE_MAP = {
            int:   types.Type.INTEGER,
            float: types.Type.NUMBER,
            str:   types.Type.STRING,
            bool:  types.Type.BOOLEAN,
        }

        # 1) grab module-level metadata
        module    = sys.modules.get(func.__module__)
        list_info = ToolParser.getListSig(module, func.__name__) or []
        dict_info = ToolParser.getDictSig(module, func.__name__) or []

        # 2) override with bound-method metadata if present
        inst = getattr(func, "__self__", None)
        if inst:
            list_info = list_info or ToolParser.getListSig(inst, func.__name__) or []
            dict_info = dict_info or ToolParser.getDictSig(inst, func.__name__) or []

        # 3) if LIST_SIG exists → one array param
        if list_info:
            # assume single signature parameter (e.g. infoList)
            param = next(p for p in sig.parameters.values() if p.name != "self")
            name  = param.name
            # derive item type from annotation if available
            pType  = hints.get(name, list)
            origin, args = get_origin(pType), get_args(pType)
            itemType = args[0] if origin is list and args else str
            itemSchema = types.Schema(type=TYPE_MAP.get(itemType, types.Type.STRING))

            props[name] = types.Schema(
                type=types.Type.ARRAY,
                items=itemSchema
            )
            required = [name]

        # 4) if DICT_SIG exists → one object param with nested props
        elif dict_info:
            param = next(p for p in sig.parameters.values() if p.name != "self")
            name  = param.name
            # dict_info may be list-of-keys or dict-of-descriptions
            keys = dict_info if isinstance(dict_info, list) else list(dict_info.keys())

            # build nested properties for the dict
            nested = {
                key: types.Schema(type=TYPE_MAP[str])
                for key in keys
            }
            props[name] = types.Schema(
                type=types.Type.OBJECT,
                properties=nested,
                required=keys
            )
            required = [name]

        # 5) otherwise generic: one prop per parameter
        else:
            required = []
            for param in sig.parameters.values():
                name   = param.name
                pType  = hints.get(name, str)
                origin = get_origin(pType)
                args   = get_args(pType)

                if origin is list or pType is list:
                    item       = args[0] if args else str
                    itemSchema = types.Schema(type=TYPE_MAP.get(item, types.Type.STRING))
                    props[name] = types.Schema(
                        type=types.Type.ARRAY,
                        items=itemSchema
                    )
                elif origin is dict or pType is dict:
                    props[name] = types.Schema(type=types.Type.OBJECT)
                else:
                    props[name] = types.Schema(
                        type=TYPE_MAP.get(pType, types.Type.STRING)
                    )

                if param.default is param.empty:
                    required.append(name)

        # build the description
        meta = ToolParser.parseToolDocstring(inspect.getdoc(func))
        desc = meta["description"] or ""
        if meta.get("additional_information"):
            desc += f"\nAdditional Information: {meta['additional_information']}"
        desc = desc.strip()

        # — build the Schema in proto‐field order: type → properties → required
        params_schema = types.Schema(
            type=types.Type.OBJECT,
            properties=props,
            required=required
        )

        return types.FunctionDeclaration(
            name=func.__name__,
            description=desc,
            parameters=params_schema
        )





# import os
# import importlib.util
# import sys
# import json
# import inspect
# import re
# import logging
# from google import genai
# from google.genai import types
# from typing import get_type_hints
# from dotenv import load_dotenv

# load_dotenv()
# logger = logging.getLogger(__name__)


# class ToolParser:

#     @staticmethod
#     def parseToolDocstring(docstring):
#         """
#         Parse the docstring of a function to extract metadata like description and additional information.
#         Returns a dictionary with keys 'description' and 'additional_information'.
#         """
#         result = {
#             "description": "",
#             "additional_information": None,
#         }
#         if not docstring:
#             return result
#         lines = [line.strip() for line in docstring.strip().splitlines() if line.strip()]
#         for line in lines:
#             if ":" not in line:
#                 continue
#             key, value = line.split(":", 1)
#             key = key.lower().replace(" ", "_")
#             value = value.strip().strip('"').strip("'")
#             if key in result:
#                 result[key] = value
#         if not result["description"] and lines:
#             result["description"] = lines[0]
#         return result

#     @staticmethod
#     def getTools(toolLists):
#         """
#         Parses a list of tools (modules, functions, or classes/instances) to extract all public callable tools.
#         Returns a dictionary of tool names to their callable objects.
#         """
#         tools = {}

#         def addModuleFunctions(module):
#             publicFunctions = {
#                 name: fn
#                 for name, fn in inspect.getmembers(module, inspect.isfunction)
#                 if not name.startswith("_")
#             }
#             tools.update(publicFunctions)

#         def addClassMethods(module):
#             for className, cls in inspect.getmembers(module, inspect.isclass):
#                 if cls.__module__ != module.__name__:
#                     continue
#                 try:
#                     instance = cls()
#                 except Exception:
#                     instance = None
#                 for name, fn in inspect.getmembers(cls, inspect.isfunction):
#                     if not name.startswith("_"):
#                         funcKey = f"{className}.{name}"
#                         tools[funcKey] = getattr(instance, name) if instance else fn

#         for tool in toolLists:
#             if inspect.ismodule(tool):
#                 addModuleFunctions(tool)
#                 addClassMethods(tool)
#             elif inspect.isfunction(tool):
#                 if not tool.__name__.startswith("_"):
#                     tools[tool.__name__] = tool
#             elif inspect.isclass(tool):
#                 try:
#                     instance = tool()
#                 except Exception:
#                     instance = None
#                 className = tool.__name__
#                 for name, fn in inspect.getmembers(tool, inspect.isfunction):
#                     if not name.startswith("_"):
#                         funcKey = f"{className}.{name}"
#                         tools[funcKey] = getattr(instance, name) if instance else fn
#             elif hasattr(tool, "__class__"):
#                 # For instances passed directly
#                 className = tool.__class__.__name__
#                 for name, fn in inspect.getmembers(tool.__class__, inspect.isfunction):
#                     if not name.startswith("_"):
#                         funcKey = f"{className}.{name}"
#                         tools[funcKey] = getattr(tool, name)

#         return tools

#     @staticmethod
#     def extractJson(text):
#         """
#         Extract the first JSON array or object from a string, even if wrapped in markdown or extra commentary.
#         """
#         match = re.search(r"(\[.*?\]|\{.*?\})", text, re.DOTALL)
#         if match:
#             json_str = match.group(1)
#             return json.loads(json_str)
#         return json.loads(text)

#     @staticmethod
#     def parseJsonSchema(func, schemaType):
#         """
#         Build a JSON schema for a function based on its signature and docstring metadata.
#         schemaType can be 'completions', 'chat_completions', or 'responses'.
#         Returns a dictionary representing the schema.
#         """
#         schemaType = schemaType.lower()
#         if schemaType == "chat_completions":
#             schemaType = "completions"
#         sig = inspect.signature(func)
#         typeHints = get_type_hints(func)
#         properties = {}
#         required = []
#         TYPE_MAP = {int: "integer", float: "number", str: "string", bool: "boolean", dict: "object", list: "array"}

#         for param in sig.parameters.values():
#             paramType = typeHints.get(param.name, str)
#             jsonType = TYPE_MAP.get(paramType, "string")
#             properties[param.name] = {"type": jsonType}
#             if param.default is param.empty:
#                 required.append(param.name)

#         meta = ToolParser.parseToolDocstring(inspect.getdoc(func))
#         descriptionLines = [meta["description"]]
#         if meta.get("additional_information"):
#             descriptionLines.append(f"Additional Information: {meta['additional_information']}")
#         description = "\n".join(descriptionLines)

#         schemaMap = {
#             "completions": lambda: {
#                 "type": "function",
#                 "function": {
#                     "name": func.__name__,
#                     "description": description,
#                     "parameters": {
#                         "type": "object",
#                         "properties": properties,
#                         "required": required,
#                     },
#                 }
#             },
#             "responses": lambda: {
#                 "type": "function",
#                 "name": func.__name__,
#                 "description": description,
#                 "parameters": {
#                     "type": "object",
#                     "properties": properties,
#                     "required": required,
#                 },
#             }
#         }

#         return schemaMap[schemaType]()

#     @staticmethod
#     def parseTypedSchema(func):
#         """
#         Build a Google GenAI function declaration for a given function based on its signature and docstring metadata.
#         Returns a FunctionDeclaration object.
#         """
#         sig = inspect.signature(func)
#         type_hints = get_type_hints(func)
#         properties = {}
#         type_map = {
#             int: genai.types.Type.INTEGER,
#             float: genai.types.Type.NUMBER,
#             str: genai.types.Type.STRING,
#             bool: genai.types.Type.BOOLEAN,
#             dict: genai.types.Type.OBJECT,
#             list: genai.types.Type.ARRAY,
#         }
#         for param in sig.parameters.values():
#             param_type = type_hints.get(param.name, str)
#             schema_type = type_map.get(param_type, genai.types.Type.STRING)
#             properties[param.name] = genai.types.Schema(type=schema_type)

#         meta = ToolParser.parseToolDocstring(inspect.getdoc(func))
#         description_lines = [meta["description"]]
#         if meta.get("additional_information"):
#             description_lines.append(meta["additional_information"])
#         # This is what will show up when you print it out
#         description = "\n    ".join(description_lines)

#         return types.FunctionDeclaration(
#             name=func.__name__,
#             description=description,
#             parameters=genai.types.Schema(
#                 type=genai.types.Type.OBJECT,
#                 properties=properties,
#             ),
#         )

#     @staticmethod
#     def addModuleFunctions(module, toolFunctions):
#         """
#         Adds all public standalone functions from a module to the toolFunctions dictionary.
#         """
#         publicFunctions = {
#             name: fn
#             for name, fn in inspect.getmembers(module, inspect.isfunction)
#             if not name.startswith("_")
#         }
#         toolFunctions.update(publicFunctions)

#     @staticmethod
#     def addClassMethods(module, toolFunctions):
#         """
#         Adds all public methods from classes in a module to the toolFunctions dictionary.

#         Each method is bound to an instance of the class to hide 'self' in the signature.
#         """
#         for className, cls in inspect.getmembers(module, inspect.isclass):
#             if cls.__module__ != module.__name__:
#                 continue
#             try:
#                 instance = cls()
#             except Exception:
#                 instance = None
#             for name, fn in inspect.getmembers(cls, inspect.isfunction):
#                 if not name.startswith("_"):
#                     funcKey = f"{className}.{name}"
#                     toolFunctions[funcKey] = getattr(instance, name) if instance else fn
