from autogen_core import TypeSubscription
from autogen_core import TopicId
import asyncio
from dataclasses import dataclass
from autogen_core import RoutedAgent, message_handler, type_subscription
from autogen_core import SingleThreadedAgentRuntime
from autogen_core import MessageContext
import logging

from autogen_core import TRACE_LOGGER_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(TRACE_LOGGER_NAME)
#logger.setLevel(logging.DEBUG)

@dataclass
class Message:
    content: str

@type_subscription(topic_type="default")
class ReceivingAgent(RoutedAgent):
    @message_handler
    async def on_my_message(self, message: Message, ctx: MessageContext) -> None:
        logger.debug(f"Received a message: {message.content}")

class BroadcastingAgent(RoutedAgent):
    @message_handler
    async def on_my_message(self, message: Message, ctx: MessageContext) -> None:
        await self.publish_message(
            Message("Publishing a message from broadcasting agent!"),
            topic_id=TopicId(type="default", source=self.id.key),
        )
runtime = SingleThreadedAgentRuntime()

async def main() -> None:

  # Option 1: with type_subscription decorator
  # The type_subscription class decorator automatically adds a TypeSubscription to
  # the runtime when the agent is registered.
  await ReceivingAgent.register(runtime, "receiving_agent", lambda: ReceivingAgent("Receiving Agent"))

  # Option 2: with TypeSubscription
  await BroadcastingAgent.register(runtime, "broadcasting_agent", lambda: BroadcastingAgent("Broadcasting Agent"))
  await runtime.add_subscription(TypeSubscription(topic_type="default", agent_type="broadcasting_agent"))

  # Start the runtime and publish a message.
  runtime.start()
  await runtime.publish_message(
      Message("Hello, World! From the runtime!"), topic_id=TopicId(type="default", source="default")
  )
  await runtime.stop_when_idle()

asyncio.run(main())
