"""
This code is the intellectual property of IBM and is not to be used by non-IBM practitioners
nor distributed outside of IBM internal without having the proper clearance.
For full usage guidelines refer to Guidelines for Code Accelerator Consumption.
https://w3.ibm.com/services/lighthouse/help-and-support/terms#asset-consumption

@author Benjamin A. Janes (benjamin.janes@se.ibm.com)
"""

import linecache

from genai_4_dps_helper.models.generic_base_models import ExceptionResponse
from genai_4_dps_helper.utils.log_config import get_logger


class BaseObj(object):
    def __init__(self):
        self._logger = get_logger(f"{self.__module__}.{self.__class__.__name__}")

    def _generate_exception_obj(self, exc: Exception) -> ExceptionResponse:
        f = exc.__traceback__.tb_frame
        lineno = exc.__traceback__.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)

        err_str = "EXCEPTION IN ({}, LINE {} '{}'): {}".format(
            filename, lineno, line.strip(), exc
        )
        err_str = err_str.replace("\\", "/")
        err_str = err_str.replace("\r", "")
        err_str = err_str.replace("\n", " ")
        err_str = err_str.replace('"', "'")
        return ExceptionResponse(
            filename=filename,
            message=str(type(exc)) + ": " + str(exc),
            lineno=lineno,
            codeLine=line.strip()
            .replace("\\", "/")
            .replace("\r", "")
            .replace("\n", " ")
            .replace('"', "'"),
            exceptionClass=str(type(exc)),
            errStr=err_str,
        )
