import enum
import io
from typing import List
from aardwolf.protocol.T128.share import TS_SHARECONTROLHEADER
from aardwolf.protocol.pdu.capabilities import TS_CAPS_SET

class TS_CONFIRM_ACTIVE_PDU:
	def __init__(self):
		self.shareControlHeader:TS_SHARECONTROLHEADER = None
		self.shareID:int = None
		self.originatorID:int = None
		self.lengthSourceDescriptor:int = None
		self.lengthCombinedCapabilities:int = None 
		self.sourceDescriptor:bytes = b'MSTSC\x00' #cli: MTSC\0x00 srv: RDP\x00
		self.numberCapabilities:int = None
		self.pad2Octets:int = 0
		self.capabilitySets:List[TS_CAPS_SET] = []

	def to_bytes(self):
		capdata = b''
		for cap in self.capabilitySets:
			capdata += cap.to_bytes()
		
		t = self.shareID.to_bytes(4, byteorder='little', signed = False)
		t += self.originatorID.to_bytes(2, byteorder='little', signed = False)
		t += len(self.sourceDescriptor).to_bytes(2, byteorder='little', signed = False)
		t += (len(capdata) + 2 + 2).to_bytes(2, byteorder='little', signed = False)
		t += self.sourceDescriptor
		t += len(self.capabilitySets).to_bytes(2, byteorder='little', signed = False)
		t += self.pad2Octets.to_bytes(2, byteorder='little', signed = False)
		t += capdata
		#self.shareControlHeader.totalLength = 6 + len(t)
		#t = self.shareControlHeader.to_bytes() + t
		return t

	@staticmethod
	def from_bytes(bbuff: bytes):
		return TS_CONFIRM_ACTIVE_PDU.from_buffer(io.BytesIO(bbuff))

	@staticmethod
	def from_buffer(buff: io.BytesIO):
		msg = TS_CONFIRM_ACTIVE_PDU()
		msg.shareControlHeader = TS_SHARECONTROLHEADER.from_buffer(buff)
		msg.shareID = int.from_bytes(buff.read(4), byteorder='little', signed = False)
		msg.originatorID = int.from_bytes(buff.read(2), byteorder='little', signed = False)
		msg.lengthSourceDescriptor = int.from_bytes(buff.read(2), byteorder='little', signed = False)
		msg.lengthCombinedCapabilities = int.from_bytes(buff.read(2), byteorder='little', signed = False)
		msg.sourceDescriptor = buff.read(msg.lengthSourceDescriptor)
		msg.numberCapabilities = int.from_bytes(buff.read(2), byteorder='little', signed = False)
		msg.pad2Octets = int.from_bytes(buff.read(2), byteorder='little', signed = False)
		for _ in range(msg.numberCapabilities):
			msg.capabilitySets.append(TS_CAPS_SET.from_buffer(buff))
		
		return msg

	def __repr__(self):
		t = '==== TS_CONFIRM_ACTIVE_PDU ====\r\n'
		for k in self.__dict__:
			if isinstance(self.__dict__[k], enum.IntFlag):
				value = self.__dict__[k]
			elif isinstance(self.__dict__[k], enum.Enum):
				value = self.__dict__[k].name
			else:
				value = self.__dict__[k]
			t += '%s: %s\r\n' % (k, value)
		return t