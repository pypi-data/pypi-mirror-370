# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Trick Python into loading the agent.

"""

from __future__ import unicode_literals
import os
import sys

from appdynamics import basic_json_logger

# patching getargspec for inspect since it got deprecaited from python 3.11
try:
    import inspect
    if sys.version_info[0] == 3 and sys.version_info[1] == 11:
        if not hasattr(inspect, 'getargspec'):
            inspect.getargspec = inspect.getfullargspec
except AttributeError:
    pass

try:
    sys.path.remove(os.path.dirname(__file__))
except ValueError:  # directory not in sys.path
    pass

try:
    import appdynamics.agent
    if appdynamics.agent.configure():
        appdynamics.agent.bootstrap()
except:
    logger = basic_json_logger('appdynamics.agent')
    logger.exception('Exception in agent startup.')
finally:
    appdynamics.agent.load_sitecustomize()
