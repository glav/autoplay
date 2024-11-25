import os
import logging

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_ORG = os.getenv('GITHUB_ORG') or ""
GITHUB_REPONAME = os.getenv('GITHUB_REPONAME')

ENABLE_TRACE_LOGGING = os.getenv('ENABLE_TRACE_LOGGING', 'true').lower() == 'true'
LOG_LEVEL = logging.INFO
