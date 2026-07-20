# -*- coding: utf-8 -*-
# 异常体系


class HelloAgentsException(Exception):
    """基础异常类"""
    pass

class LLMException(HelloAgentsException):
    """LLM异常类"""
    pass

class ToolException(HelloAgentsException):
    """工具异常类"""
    pass

class AgentException(HelloAgentsException):
    """智能体异常类"""
    pass

class ConfigException(HelloAgentsException):
    """配置异常类"""
    pass
