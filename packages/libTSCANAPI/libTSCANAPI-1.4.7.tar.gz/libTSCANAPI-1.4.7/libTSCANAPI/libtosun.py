'''
Author: seven 865762826@qq.com
Date: 2023-06-11 14:14:06
LastEditors: seven 865762826@qq.com
LastEditTime: 2023-06-11 15:36:01
'''
import typing

from can.message import Message
from libTSCANAPI.TSMasterDevice import *
import can
from typing import List, Optional, Tuple, Union, Deque, Any
from can.bus import LOG

class libtosunBus(can.BusABC):
    def __init__(self, channel: int = 0, *,
                is_include_tx=False,
                can_filters: Optional[can.typechecking.CanFilters] = None,
                hwserial: bytes = b"",
                dbc:str = '',
                filters = [],
                 **kwargs: object):
        super().__init__(channel, can_filters, **kwargs)
        self.ChannelIdx = channel
        configs=[]
        businfo = {}
        businfo['FChannel'] = channel
        businfo['rate_baudrate'] = kwargs.get('rate_baudrate',500)
        businfo['data_baudrate'] = kwargs.get('data_baudrate',500)
        businfo['enable_120hm'] = kwargs.get('enable_120hm',True)
        businfo['is_fd'] = kwargs.get('is_fd',True)
        configs.append(businfo)
        self.device = TSMasterDevice(configs=configs, hwserial=hwserial,is_include_tx=is_include_tx,
        dbc=dbc,filters = filters)
        self.channel_info = channel
    def send(self, msg: can.Message, timeout: Optional[float] = 0.1, sync: bool = False,
            is_cyclic: bool = False) -> None:
        if isinstance(msg, TLIBCAN):
            msg.FIdxChn = self.channel_info
        elif isinstance(msg, TLIBCANFD):
            msg.FIdxChn = self.channel_info
        else:
            msg.channel = self.channel_info
        self.device.send_msg(msg, timeout, sync, is_cyclic)

    def recv(self, timeout: Optional[float] = 0.1) -> Message or None:
        return self._recv_internal(timeout=timeout)[0]

    def _recv_internal(self, timeout: Optional[float] = 0.1) -> Tuple[Optional[can.Message], bool] or Tuple[None,bool]:
        return self.device.recv(channel = self.channel_info,timeout = timeout), False

    def shutdown(self) -> None:
        LOG.debug('TSMaster - shutdown.')
        self.device.shut_down()
        super().shutdown()