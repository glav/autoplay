from dataclasses import dataclass
from autogen_core import MessageSerializer
import json

AGENT_GITHUB = 'agent_github'
AGENT_LOCAL_FILE = 'agent_local_file'
AGENT_ROUTER = 'agent_router'

AGENT_TOPIC_USER_REQUEST='userrequest'
AGENT_TOPIC_LOCALDIR='localdir'
AGENT_TOPIC_GITHUB='github'

ARTIFACT_SOURCE_GITHUB = 'github'
ARTIFACT_SOURCE_LOCAL_FILE = 'local_file'

@dataclass
class AgentMessage:
  def __init__(self, content: str, message_type: str = "AgentMessage"):
    self.content = content
    self.message_type = message_type

  message_type: str
  content: str

@dataclass
class UserRequestMessage:
  content: str

@dataclass
class LocalDirMessage:
  content: str

@dataclass
class GithubMessage:
  content: str


class CustomSerializer(MessageSerializer):
    def serialize(self, obj):
        if isinstance(obj, (LocalDirMessage, GithubMessage, UserRequestMessage)):
            return json.dumps({
                "type": obj.__class__.__name__,
                "data": obj.__dict__
            })
        return super().serialize(obj)

    def deserialize(self, data):
        try:
            parsed = json.loads(data)
            if isinstance(parsed, dict) and "type" in parsed and "data" in parsed:
                if parsed["type"] == "LocalDirMessage":
                    return LocalDirMessage(**parsed["data"])
                elif parsed['type'] == 'GithubMessage':
                    return GithubMessage(**parsed["data"])
                elif parsed["type"] == "UserRequestMessage":
                    return UserRequestMessage(**parsed["data"])
        except json.JSONDecodeError:
            pass
        return super().deserialize(data)
