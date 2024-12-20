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

from autogen_core.application.logging import TRACE_LOGGER_NAME
import platform
import config
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
# Import the `configure_azure_monitor()` function from the
# `azure.monitor.opentelemetry` package.
from azure.monitor.opentelemetry import configure_azure_monitor
import os
# Import the tracing api from the `opentelemetry` package.
from opentelemetry import trace
from opentelemetry.instrumentation.openai import OpenAIInstrumentor




def configure_oltp_tracing(endpoint: str = None) -> trace.TracerProvider:
    # Configure OpenTelemetry to use Azure Monitor with the
    # APPLICATIONINSIGHTS_CONNECTION_STRING environment variable.
    #configure_azure_monitor(connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"))
    #configure_azure_monitor()

    # !!!Not using the commented out bits below seems to work best!
    # otherwise generates errors in the trace logs

    # Configure Tracing
    tracer_provider = TracerProvider(resource=Resource({"service.name": "my-service"}))
    processor = BatchSpanProcessor(OTLPSpanExporter())
    tracer_provider.add_span_processor(processor)
    trace.set_tracer_provider(tracer_provider)

    OpenAIInstrumentor().instrument()
    #return trace.get_tracer_provider()

    return tracer_provider

class SingleRuntimeFacade():
  def __init__(self) -> None:
    tracer_provider = configure_oltp_tracing()
    self._runtime = SingleThreadedAgentRuntime(tracer_provider=tracer_provider)

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
    self._host = GrpcWorkerAgentRuntimeHost(address=config.HOST_ADDRESS)
    self._host.start()

    await asyncio.sleep(1)

    tracer_provider = configure_oltp_tracing()

    self._worker1runtime = GrpcWorkerAgentRuntime(host_address=config.HOST_ADDRESS, tracer_provider=tracer_provider)
    #self._worker1runtime.add_message_serializer(CustomSerializer())  # this does nothing
    self._worker2runtime = GrpcWorkerAgentRuntime(host_address=config.HOST_ADDRESS, tracer_provider=tracer_provider)
    #self._worker2runtime.add_message_serializer(CustomSerializer())
    self._worker3runtime = GrpcWorkerAgentRuntime(host_address=config.HOST_ADDRESS, tracer_provider=tracer_provider)
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
