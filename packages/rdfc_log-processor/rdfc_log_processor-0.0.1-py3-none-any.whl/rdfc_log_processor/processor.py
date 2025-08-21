from dataclasses import dataclass
from logging import getLogger, Logger, getLevelName

from rdfc_runner import Processor, ProcessorArgs, Reader, Writer


# --- Type Definitions ---
@dataclass
class LogArgs(ProcessorArgs):
    reader: Reader
    writer: Writer
    label: str = "log"
    level: str = "info"
    raw: bool = False


@dataclass
class SendArgs(ProcessorArgs):
    msgs: list[str]
    writer: Writer


# --- Processor Implementation ---
class Log(Processor[LogArgs]):
    logger: Logger = getLogger('rdfc.LogProcessor')

    def __init__(self, args: LogArgs):
        super().__init__(args)
        self.logger.debug(msg="Created Log processor with args: {}".format(args))
        self.msg_logger = self.logger.getChild(args.label if args.label else "log")

    async def init(self) -> None:
        """Initialize the processor."""
        self.logger.debug("Initializing Log processor with args: {}", self.args)

    async def transform(self) -> None:
        """Listen to the incoming stream, log them, and push them to the outgoing stream."""
        async for msg in self.args.reader.strings():
            # Log the incoming message
            if self.args.raw:
                print(msg)
            else:
                # Log the formatted message
                self.msg_logger.log(msg=msg, level=getLevelName(self.args.level.upper()))

            # Echo the message to the writer
            if self.args.writer:
                await self.args.writer.string(msg)

        # Close the writer after processing all messages
        if self.args.writer:
            await self.args.writer.close()
        self.logger.debug("done reading so closed writer.")

    async def produce(self) -> None:
        pass


class Send(Processor[SendArgs]):
    logger: Logger = getLogger('rdfc.SendProcessor')

    def __init__(self, args: SendArgs):
        super().__init__(args)
        self.logger.debug(msg="Created Send processor with args: {}".format(self.args))

    async def init(self) -> None:
        """Initialize the processor."""
        self.logger.debug(msg="Initializing Send processor with args: {}".format(self.args))
        pass

    async def transform(self) -> None:
        pass

    async def produce(self) -> None:
        """Send messages to the writer."""
        for msg in self.args.msgs:
            self.logger.debug(msg=f"Sending message: {msg}")
            await self.args.writer.string(msg)
        await self.args.writer.close()
        self.logger.debug("done sending messages so closed writer.")
