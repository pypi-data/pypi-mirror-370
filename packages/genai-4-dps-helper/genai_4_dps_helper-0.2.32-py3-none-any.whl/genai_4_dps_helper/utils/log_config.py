"""
This code is the intellectual property of IBM and is not to be used by non-IBM practitioners
nor distributed outside of IBM internal without having the proper clearance.
For full usage guidelines refer to Guidelines for Code Accelerator Consumption.
https://w3.ibm.com/services/lighthouse/help-and-support/terms#asset-consumption

@author Benjamin A. Janes (benjamin.janes@se.ibm.com)
"""

import logging
import os


def get_logger(name):
    # Create a custom logger
    logger = logging.getLogger(name)
    log_level: int = int(os.getenv("APP_LOG_LEVEL", logging.INFO))
    # Set the log level
    logger.setLevel(log_level)

    # Create a console handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # Create a formatter that includes the class name and line number
    formatter = logging.Formatter(
        "%(levelname)s:    app:orchestration-layer - %(asctime)s - %(name)s [%(lineno)d]: %(message)s"
    )
    ch.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)

    return logger
