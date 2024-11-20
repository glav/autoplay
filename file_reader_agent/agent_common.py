from dataclasses import dataclass

AGENT_GITHIB = 'agent_github'
AGENT_LOCAL_FILE = 'agent_local_file'

ARTIFACT_SOURCE_GITHUB = 'github'
ARTIFACT_SOURCE_LOCAL_FILE = 'local_file'

@dataclass
class Message:
  content: str

@dataclass
class FileMessage:
  source: str
  path: str
