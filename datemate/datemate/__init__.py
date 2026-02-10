# -*- coding: utf-8 -*-
"""
DateMate AI package entrypoint for Google ADK.

This module must export `root_agent` for `adk run datemate` to work.
"""

from datemate.agent import root_agent

__all__ = ["root_agent"]

