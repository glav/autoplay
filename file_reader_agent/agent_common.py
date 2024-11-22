from dataclasses import dataclass

AGENT_GITHIB = 'agent_github'
AGENT_LOCAL_FILE = 'agent_local_file'
AGENT_ROUTER = 'agent_router'

AGENT_TOPIC_USER_REQUEST='userrequest'
AGENT_TOPIC_LOCALDIR='localdir'
AGENT_TOPIC_GITHUB='github'

ARTIFACT_SOURCE_GITHUB = 'github'
ARTIFACT_SOURCE_LOCAL_FILE = 'local_file'

@dataclass
class UserRequestMessage:
  content: str

@dataclass
class LocalDirMessage:
  content: str

@dataclass
class GithubMessage:
  content: str
