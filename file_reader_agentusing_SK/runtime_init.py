# Create the runtime and register the agent.
from dataclasses import dataclass
from agent_common import LocalDirMessage, GithubMessage, CustomSerializer
from agent_init import register_agents
import grpc

from autogen_core import AgentId, TopicId
from autogen_core import SingleThreadedAgentRuntime
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntime, GrpcWorkerAgentRuntimeHost
from autogen_core import AgentId, BaseAgent, MessageContext
from autogen_core import try_get_known_serializers_for_type

import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
import logging

from autogen_core import TRACE_LOGGER_NAME
import platform
import config


class SingleRuntimeFacade():
  def __init__(self) -> None:
    self._runtime = SingleThreadedAgentRuntime()
    #self._runtime = SingleThreadedAgentRuntime(tracer_provider=tracer_provider)

  async def start(self) -> None:
    self._runtime.start()

  async def stop(self) -> None:
    await self._runtime.stop()

  async def register_agents(self, logger):
    await register_agents(self._runtime,self._runtime,self._runtime, logger)

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
    self._host = GrpcWorkerAgentRuntimeHost(address=config.HOST_ADDRESS)
    self._host.start()

    await asyncio.sleep(1)

    self._worker1runtime = GrpcWorkerAgentRuntime(host_address=config.HOST_ADDRESS)
    self._worker2runtime = GrpcWorkerAgentRuntime(host_address=config.HOST_ADDRESS)
    self._worker3runtime = GrpcWorkerAgentRuntime(host_address=config.HOST_ADDRESS)

    #channel = grpc.secure_channel("localhost:50052", grpc.ssl_channel_credentials())

    self._worker1runtime.start()
    self._worker2runtime.start()
    self._worker3runtime.start()

  async def stop(self) -> None:
    await self._worker1runtime.stop()
    await self._worker2runtime.stop()
    await self._worker3runtime.stop()
    await self._host.stop()

  async def register_agents(self, logger):
    await register_agents(self._worker1runtime, self._worker2runtime, self._worker3runtime, logger)
    #await register_agents(self._worker2runtime)

  async def get_runtime(self) -> list[GrpcWorkerAgentRuntime]:
    return [self._worker1runtime, self._worker2runtime, self._worker3runtime]

  async def stop_when_idle(self):
    await asyncio.sleep(1)
    # await self._worker1runtime.stop_when_signal()
    # await self._worker2runtime.stop_when_signal()
    # await self._worker3runtime.stop_when_signal()

  async def publish_message(self, **kwargs) -> None:
    await self._worker3runtime.publish_message(**kwargs)  # Use the router agent runtime to publish a message
    #await self._worker2runtime.publish_message(**kwargs)
