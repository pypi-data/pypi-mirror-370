from typing import Optional

import threading
import select
from google.protobuf.message import DecodeError
from pubsub import pub

from meshtastic import protocols
from meshtastic.protobuf import portnums_pb2, mesh_pb2
from mudp.singleton import conn
from mudp.encryption import decrypt_packet


def _decode_and_optionally_parse(
    raw: bytes, key: Optional[bytes] = None, *, parse_payload: bool = True
) -> Optional[mesh_pb2.MeshPacket]:
    try:
        mp = mesh_pb2.MeshPacket()
        mp.ParseFromString(raw)

        if mp.HasField("encrypted") and not mp.HasField("decoded"):
            decoded = decrypt_packet(mp, key)
            if decoded is not None:
                mp.decoded.CopyFrom(decoded)
            # else: keep the encrypted packet as-is

        if parse_payload and mp.HasField("decoded"):
            portnum = mp.decoded.portnum
            handler = protocols.get(portnum) if portnum is not None else None
            if handler is not None and handler.protobufFactory is not None:
                pb = handler.protobufFactory()
                try:
                    pb.ParseFromString(mp.decoded.payload)
                    pb_str = str(pb).replace("\n", " ").replace("\r", " ").strip()
                    mp.decoded.payload = pb_str.encode("utf-8")
                except DecodeError:
                    pass

        return mp
    except DecodeError:
        return None


class UDPPacketStream:
    """
    Background listener that publishes:
      - 'mesh.rx.raw'(data)
      - 'mesh.rx.decode_error'(addr)
      - 'mesh.rx.packet'(packet, addr)
      - 'mesh.rx.decoded'(packet, portnum, addr)
      - 'mesh.rx.port.<portnum>'(packet, addr)  # per-port topic for easy filtering
    """

    def __init__(
        self,
        mcast_grp: str,
        mcast_port: int,
        key: Optional[bytes] = None,
        recv_buf: int = 65535,
        parse_payload: bool = True,
        select_timeout: float = 0.2,
    ) -> None:
        self.mcast_grp = mcast_grp
        self.mcast_port = mcast_port
        self.key = key
        self.recv_buf = recv_buf
        self.parse_payload = parse_payload
        self.select_timeout = select_timeout

        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._sock = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        conn.setup_multicast(self.mcast_grp, self.mcast_port)

        # Try to grab underlying socket and make it non-blocking
        self._sock = getattr(conn, "sock", None)
        if self._sock is not None:
            try:
                self._sock.setblocking(False)
            except Exception:
                try:
                    self._sock.settimeout(0.0)
                except Exception:
                    pass

        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="UDPPacketStream", daemon=True)
        self._thread.start()

    def stop(self, join: bool = True) -> None:
        self._stop.set()
        if join and self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                if self._sock is not None:
                    r, _, _ = select.select([self._sock], [], [], self.select_timeout)
                    if not r:
                        continue
                    raw, _addr = self._sock.recvfrom(self.recv_buf)
                else:
                    raw, _addr = conn.recvfrom(self.recv_buf)

                pub.sendMessage("mesh.rx.raw", data=raw, addr=_addr)

                mp = _decode_and_optionally_parse(raw, self.key, parse_payload=self.parse_payload)
                if mp is None:
                    pub.sendMessage("mesh.rx.decode_error", addr=_addr)
                    continue

                pub.sendMessage("mesh.rx.packet", packet=mp, addr=_addr)

                if mp.HasField("decoded"):
                    portnum = mp.decoded.portnum
                    pub.sendMessage("mesh.rx.decoded", packet=mp, portnum=portnum, addr=_addr)
                    pub.sendMessage(f"mesh.rx.port.{portnum}", packet=mp, addr=_addr)
                    if portnum == portnums_pb2.PortNum.TEXT_MESSAGE_APP:
                        pub.sendMessage("mesh.rx.text", packet=mp, addr=_addr)

            except Exception as e:
                pub.sendMessage("mesh.rx.listener_error", error=e)
