
import os
import inspect
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ArgumentParser:
    def __init__(self):
        pass

    def printArgs(self, caller: str, localVars: dict) -> None:
        showOutput = os.getenv("SHOW_CALLED_ACTIONS", 'False') == 'True'
        if not showOutput:
            return

        frame      = inspect.currentframe().f_back
        className  = caller.__class__.__name__ if hasattr(caller, '__class__') else caller.__name__
        actionName = frame.f_code.co_name

        # Filter out 'self' and any dunder vars
        args = {k: v for k, v in localVars.items() if k != 'self' and not k.startswith('__')}
        if args:
            print(f"Called {actionName} with arguments:")
            for k, v in args.items():
                print(f"  {k}: {v}\n")
        else:
            print(f"Called {actionName}:")

    def getListSig(self, obj, func_name):
        for attr in ("listSig", "list_sig", "LIST_SIG"):
            value = getattr(obj, attr, None)
            if isinstance(value, dict) and func_name in value:
                return value[func_name]
        return None

    def getDictSig(self, obj, func_name):
        for attr in ("dictSig", "dict_sig", "DICT_SIG"):
            value = getattr(obj, attr, None)
            if isinstance(value, dict) and func_name in value:
                return value[func_name]
        return None


# import os
# import inspect
# import logging
# from dotenv import load_dotenv

# load_dotenv()
# logger = logging.getLogger(__name__)

# class ArgumentParser:
#     def __init__(self):
#         pass

#     # def printArgs(self, caller: str, localVars: dict) -> None:
#     #     """
#     #     Print the arguments passed to the caller function for debugging purposes.
#     #     The caller can be a function or a class method. The
#     #     localVars dictionary should contain the local variables of the caller function.
#     #     This function will only print the arguments if the environment variable SHOW_CALLED_ACTIONS is set to 'True'.
#     #     """
#     #     showOutput = showOutput = os.getenv("SHOW_CALLED_ACTIONS", 'False') == 'True'
#     #     if showOutput:
#     #         frame     = inspect.currentframe().f_back
#     #         className = caller.__class__.__name__ if hasattr(caller, '__class__') else caller.__name__
#     #         actionName = frame.f_code.co_name
#     #         print(f"{actionName} called with arguments:")
#     #         for k, v in localVars.items():
#     #             if k != 'self':
#     #                 print(f"  {k}: {v}\n")
#     def printArgs(self, caller: str, localVars: dict) -> None:
#         showOutput = os.getenv("SHOW_CALLED_ACTIONS", 'False') == 'True'
#         if not showOutput:
#             return

#         frame      = inspect.currentframe().f_back
#         className  = caller.__class__.__name__ if hasattr(caller, '__class__') else caller.__name__
#         actionName = frame.f_code.co_name

#         # Filter out 'self' and any dunder vars
#         args = {k: v for k, v in localVars.items() if k != 'self' and not k.startswith('__')}
#         if args:
#             print(f"Called {actionName} with arguments:")
#             for k, v in args.items():
#                 print(f"  {k}: {v}\n")
#         else:
#             print(f"Called {actionName}:")