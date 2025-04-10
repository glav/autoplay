from dataclasses import dataclass

from dotenv import load_dotenv
env_loaded = load_dotenv(dotenv_path="../.env", override=True)
print(f"Env variables loaded: {env_loaded}")

import asyncio
from autogen_core import MessageContext
from autogen_core import DefaultTopicId, RoutedAgent, default_subscription, message_handler
from autogen_core import TypeSubscription
from autogen_core import TopicId
from autogen_core import MessageContext
import logging
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntimeHost, GrpcWorkerAgentRuntime

from autogen_core import TRACE_LOGGER_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(TRACE_LOGGER_NAME)
#logger.setLevel(logging.DEBUG)



@dataclass
class MyMessage:
    content: str


@default_subscription
class MyAgent(RoutedAgent):
    def __init__(self, name: str) -> None:
        super().__init__("My agent")
        self._name = name
        self._counter = 0

    @message_handler
    async def my_message_handler(self, message: MyMessage, ctx: MessageContext) -> None:
        self._counter += 1
        if self._counter > 5:
            return
        content = f"{self._name}: Hello x {self._counter}"
        print(content)
        await self.publish_message(MyMessage(content=content), DefaultTopicId())


async def main() -> None:
    host = GrpcWorkerAgentRuntimeHost(address="localhost:50051")
    host.start()  # Await the start operation to ensure host is ready

    worker1 = GrpcWorkerAgentRuntime(host_address="localhost:50051")
    await worker1.start()  # Await to ensure connection is established
    await MyAgent.register(worker1, "worker1", lambda: MyAgent("worker1"))

    worker2 = GrpcWorkerAgentRuntime(host_address="localhost:50051")
    await worker2.start()  # Await to ensure connection is established
    await MyAgent.register(worker2, "worker2", lambda: MyAgent("worker2"))

    await worker2.publish_message(MyMessage(content="Hello!"), DefaultTopicId())

    # Let the agents run for a while.
    await asyncio.sleep(5)

    await worker1.stop()
    await worker2.stop()
    await host.stop()

asyncio.run(main())
