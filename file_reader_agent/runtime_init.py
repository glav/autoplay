# Create the runtime and register the agent.
from dataclasses import dataclass
from agent_common import LocalDirMessage, GithubMessage, CustomSerializer
from agent_init import register_agents
import grpc

from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentId, TopicId
from autogen_core.application import SingleThreadedAgentRuntime, WorkerAgentRuntime, WorkerAgentRuntimeHost
from autogen_core.base import AgentId, BaseAgent, MessageContext
from autogen_core.base import try_get_known_serializers_for_type

import asyncio
from autogen_ext.models import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
import logging

from autogen_core.application.logging import TRACE_LOGGER_NAME
import platform


class SingleRuntimeFacade():
  def __init__(self) -> None:
    self._runtime = SingleThreadedAgentRuntime()

  async def start(self) -> None:
    self._runtime.start()

  async def stop(self) -> None:
    await self._runtime.stop()

  async def register_agents(self):
    await register_agents(self._runtime,self._runtime,self._runtime)

  async def get_runtime(self) -> list[SingleThreadedAgentRuntime]:
    return [self._runtime]

  async def stop_when_idle(self):
    await self._runtime.stop_when_idle()

  async def publish_message(self, **kwargs) -> None:
    await self._runtime.publish_message(**kwargs)



class DistributedRuntimeFacade():
  def __init__(self) -> None:
    self._worker1runtime = None
    self._worker2runtime = None
    self._worker3runtime = None
    self._host = None

  async def start(self) -> None:
    self._host = WorkerAgentRuntimeHost(address="localhost:50052")
    self._host.start()

    await asyncio.sleep(1)

    self._worker1runtime = WorkerAgentRuntime(host_address="localhost:50052")
    #self._worker1runtime.add_message_serializer(CustomSerializer())  # this does nothing
    self._worker2runtime = WorkerAgentRuntime(host_address="localhost:50052")
    #self._worker2runtime.add_message_serializer(CustomSerializer())
    self._worker3runtime = WorkerAgentRuntime(host_address="localhost:50052")
    self._worker3runtime.add_message_serializer(CustomSerializer())

    #channel = grpc.secure_channel("localhost:50052", grpc.ssl_channel_credentials())

    self._worker1runtime.start()
    self._worker2runtime.start()
    self._worker3runtime.start()

  async def stop(self) -> None:
    await self._worker1runtime.stop()
    await self._worker2runtime.stop()
    await self._worker3runtime.stop()
    await self._host.stop()

  async def register_agents(self):
    await register_agents(self._worker1runtime, self._worker2runtime, self._worker3runtime)
    #await register_agents(self._worker2runtime)

  async def get_runtime(self) -> list[WorkerAgentRuntime]:
    return [self._worker1runtime, self._worker2runtime, self._worker3runtime]

  async def stop_when_idle(self):
    await asyncio.sleep(1)
    # await self._worker1runtime.stop_when_signal()
    # await self._worker2runtime.stop_when_signal()
    # await self._worker3runtime.stop_when_signal()

  async def publish_message(self, **kwargs) -> None:
    await self._worker3runtime.publish_message(**kwargs)  # Use the router agent runtime to publish a message
    #await self._worker2runtime.publish_message(**kwargs)
