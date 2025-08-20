from dataclasses import KW_ONLY, dataclass, field

from websockets.asyncio.client import ClientConnection
from websockets.asyncio.client import connect as ws_connect

from palabra_ai.audio import AudioFrame
from palabra_ai.enum import Channel, Direction
from palabra_ai.message import Dbg
from palabra_ai.task.io.base import Io
from palabra_ai.util.logger import debug, trace


@dataclass
class WsIo(Io):
    _: KW_ONLY
    ws: ClientConnection | None = field(default=None, init=False)
    _ws_cm: object | None = field(default=None, init=False)
    dbg_in: list = field(default_factory=list, init=False)

    @property
    def dsn(self) -> str:
        return f"{self.credentials.ws_url}?token={self.credentials.jwt_token}"

    @property
    def channel(self) -> Channel:
        return Channel.WS

    async def send_message(self, msg_data: bytes) -> None:
        await self.ws.send(msg_data)

    async def send_frame(self, frame: AudioFrame) -> None:
        raw = frame.to_ws()
        debug(f"<- {frame}")
        await self.ws.send(raw)
        self.dbg_in.append((frame, raw))

    def new_frame(self) -> AudioFrame:
        return AudioFrame.create(*self.cfg.mode.for_audio_frame)

    async def ws_receiver(self):
        from palabra_ai.message import EosMessage, Message

        try:
            async for raw_msg in self.ws:
                if self.stopper or raw_msg is None:
                    debug("Stopping ws_receiver due to stopper or None message")
                    raise EOFError("WebSocket connection closed or stopper triggered")
                trace(f"-> {raw_msg[:30]}")
                audio_frame = AudioFrame.from_ws(
                    raw_msg,
                    sample_rate=self.cfg.mode.sample_rate,
                    num_channels=self.cfg.mode.num_channels,
                    samples_per_channel=self.cfg.mode.samples_per_channel,
                )
                if audio_frame:
                    debug(f"-> {audio_frame!r}")
                    self.writer.q.put_nowait(audio_frame)
                else:
                    msg = Message.decode(raw_msg)
                    msg._dbg = Dbg(Channel.WS, Direction.OUT)
                    self.out_msg_foq.publish(msg)
                    debug(f"-> {msg!r}")
                    if isinstance(msg, EosMessage):
                        raise EOFError(f"End of stream received: {msg}")

        except EOFError as e:
            +self.eof  # noqa
            debug(f"EOF!!! {e}")
        finally:
            self.writer.q.put_nowait(None)
            self.out_msg_foq.publish(None)

    async def boot(self):
        """Start WebSocket connection"""
        # Create context manager and enter it
        self._ws_cm = ws_connect(self.dsn)
        self.ws = await self._ws_cm.__aenter__()

        # Verify connection is ready
        await self.ws.ping()
        self.sub_tg.create_task(self.ws_receiver(), name="WsIo:receiver")
        self.sub_tg.create_task(self.in_msg_sender(), name="WsIo:in_msg_sender")
        await self.set_task()

    async def exit(self):
        """Clean up WebSocket connection"""
        if self._ws_cm and self.ws:
            await self._ws_cm.__aexit__(None, None, None)
        self.ws = None
