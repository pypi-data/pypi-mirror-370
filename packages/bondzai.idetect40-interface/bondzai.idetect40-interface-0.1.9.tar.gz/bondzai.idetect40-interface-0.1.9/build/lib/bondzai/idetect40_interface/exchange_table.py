
from enum import Enum
import struct
from typing import Any

import numpy as np

class ComProtocolType(Enum):
    DIRECT = "direct"
    MODBUS = "modbus"
    S7_NET = "s7_net"
    
def int_to_bool_list(n: int) -> list[bool]:
    """Convert a int to a bool list

    Args:
        n (int): int coded in a byte (0 to 255)

    Returns:
        list[bool]: list of bool representing bits
    """
    return [bool(n & (1 << i)) for i in range(0, 8)]

def bool_list_to_int(bool_list: list[bool]) -> int:
    """_summary_

    Args:
        bool_list (list[bool]): list of bool representing bits (len of 8)

    Returns:
        int: int coded in a byte (0 to 255)
    """
    byte_value = 0
    for i, bit in enumerate(bool_list):
        if bit:
            byte_value |= 1 << i
    return byte_value

def byte_to_word_length(byte_len: int) -> int:
    """Convert a size in bytes to a size in words

    Args:
        byte_len (int): size in bytes

    Returns:
        int: size in words (minimal to handle the number of bytes into words)
    """
    return (byte_len + (byte_len % 2)) // 2

class AttributeDataType(Enum):
    BOOL = "BOOL"
    INT = "INT"
    STRING = "STRING"
    FLOAT = "FLOAT" # TODO : check if necessary

    def to_type(self) -> type:
        """Get associated python type

        Returns:
            type: python type
        """
        if self == AttributeDataType.BOOL:
            data_type = bool
        elif self == AttributeDataType.INT:
            data_type = int
        elif self == AttributeDataType.STRING:
            data_type = str
        elif self == AttributeDataType.FLOAT:
            data_type = float
        return data_type
    
    def get_null(self) -> Any:
        """Get associated null value

        Returns:
            Any: null value of correct type
        """
        if self == AttributeDataType.BOOL:
            null_value = False
        elif self == AttributeDataType.INT:
            null_value = 0
        elif self == AttributeDataType.STRING:
            null_value = "\0"
        elif self == AttributeDataType.FLOAT:
            null_value = 0.0
        return null_value
    
    def __str__(self) -> str:
        return self.value

class Attribute():
    """Attribute element stored in  the exchange table
    """
    def __init__(self, name: str, attr_type: AttributeDataType, size: int) -> None:
        self.name = name
        self.type = attr_type
        self.value = attr_type.get_null()
        self.size = size
    
    def __eq__(self, other) -> bool:
        eq = self.name == other.name and self.type == other.type and self.value == other.value and self.size == other.size
        return eq
    
    def __len__(self) -> int:
        """Get len in bytes

        Returns:
            int: length of attribute in bytes
        """
        return int(np.ceil(self.size / 8))
        
    
class Agent():
    """Agent element
    """
    def __init__(self, agent_id: int, source_nb: int):
        self.active = False
        self.agent_id = agent_id
        self.source_dict = {src_id: False for src_id in range(1, source_nb + 1)}
        self.tool_id = 0
        self.cycle_iteration = 0

    def set_tool_id(self, tool_id: int):
        self.tool_id = tool_id

    def set_cycle_iteration(self, iteration: int):
        self.cycle_iteration = iteration
    
    def set_state(self, active: bool):
        """Set agent state

        Args:
            active (bool): If True, the agent is agent else not
        """
        self.active = active
    
    def get_state(self) -> bool:
        """Get agent state

        Returns:
            bool: If True, the agent is agent else not
        """
        return self.active
    
    def set_source_state(self, source_id: int, active: bool):
        """Set source state

        Args:
            source_id (int): ID of the source
            active (bool): If True, the source is agent else not
        """
        self.source_dict[source_id] = active
    
    def get_source_state(self, source_id: int) -> bool:
        """Get source state

        Args:
            source_id (int): ID of the source

        Returns:
            bool: If True, the source is agent else not
        """
        return self.source_dict[source_id]
    
    def get_source_nb(self) -> int:
        """Get number of sources

        Returns:
            int: number of sources
        """
        return len(self.source_dict)
    
    def to_dict(self) -> dict:
        """Convert agent to dict

        Returns:
            dict: dict representation of agent
        """
        return {
            "active": self.active, 
            "sources": self.source_dict,
            "tool_id": self.tool_id, 
            "cycle_iteration": self.cycle_iteration
        }
    
    def __eq__(self, other) -> bool:
        eq = self.active == other.active and self.agent_id == other.agent_id \
            and self.tool_id == other.tool_id and self.cycle_iteration == other.cycle_iteration
        
        for source_id, active in self.source_dict.items():
            eq = eq and other.source_dict[source_id] == active
        
        return eq


class ExchangeTable:
    """Generic exchange table
    """
    def __init__(self, descriptor: dict, msg: bytearray = None):
        self.system_running = False
        self.process_ongoing = False
        self.heartbeat = False
        self.nb_sources = descriptor["agents"]["nb_sources"]
        self.agents = {
            agent_id: Agent(agent_id, self.nb_sources) 
            for agent_id in range(1, descriptor["agents"]["nb_agents"] + 1)
        }
        self.attributes = [
            Attribute(attr["name"], AttributeDataType(attr["type"]), attr["size"]) 
            for attr in descriptor["attributes"]
        ]
        if msg is not None:
            self.init_from_msg(msg)
    
    def init_from_msg(self, msg: bytearray):
        """Set bytes message info into table

        Args:
            binary (bytearray): message as array of bytes
        """
        byte_offset = 0
        msg_int_list = [int(byte) for byte in msg]
        self._set_system_word(int_to_bool_list(msg_int_list[0]) + int_to_bool_list(msg_int_list[1]))
        byte_offset += 2

        agent_bin_table = msg_int_list[byte_offset:byte_offset + 2 * len(self.agents)]
        for index in range(0, len(agent_bin_table), 2):
            agent_bin_data = int_to_bool_list(agent_bin_table[index]) + int_to_bool_list(agent_bin_table[index + 1])
            agent_id = index // 2 + 1
            self.set_agent_state(agent_id, agent_bin_data[0])
            for source_id in range(1, self.nb_sources + 1):
                self.set_source_state(agent_id, source_id, agent_bin_data[source_id])
            byte_offset += 2

        pm_data_table = msg_int_list[byte_offset:byte_offset + 4 * len(self.agents)]
        agent_idx = 1
        for idx in range(0, len(pm_data_table), 4):
            self.agents[agent_idx].set_tool_id(int.from_bytes(pm_data_table[idx:idx + 2], byteorder="little"))
            self.agents[agent_idx].set_cycle_iteration(int.from_bytes(pm_data_table[idx + 2:idx + 4], byteorder="little"))
            byte_offset += 4
            agent_idx += 1

        byte_offset += self._set_result_word(msg_int_list[byte_offset: byte_offset + 6])
        attr_bin_table = msg[byte_offset:]
        idx = 0

        for attribute in self.attributes:
            byte_len = len(attribute)
            value_array = attr_bin_table[idx: idx + byte_len]
            idx += byte_to_word_length(byte_len) * 2
            if attribute.type == AttributeDataType.STRING:
                value = str(value_array.decode("utf8")).rstrip("\x00")
            elif attribute.type == AttributeDataType.INT:
                value = int.from_bytes(value_array, byteorder="little")
            elif attribute.type == AttributeDataType.FLOAT:
                value = struct.unpack('f',value_array)[0]
            elif attribute.type == AttributeDataType.BOOL:
                value = struct.unpack("?", value_array)[0] # TODO : Check if other value next to it
            attribute.value = value
    
    def __len__(self) -> int:
        """Get size of the table

        Returns:
            int: size of the table in bytes
        """
        nb_agent = len(self.agents)
        system_size = 2
        agent_size = nb_agent * 6
        attribute_size = sum([byte_to_word_length(len(attr)) * 2 for attr in self.attributes])
        output_size = system_size + agent_size + attribute_size
        return output_size
    
    def set_system_running(self, running: bool):
        """Set system running

        Args:
            running (bool): If True current system is running
        """
        self.system_running = running
    
    def get_system_running(self) -> bool:
        """Get system running

        Returns:
            bool: If True current system is running
        """
        return self.system_running
    
    def set_process_ongoing(self, ongoing: bool):
        """Set process ongoing

        Args:
            ongoing (bool): If True, one process is ongoing
        """
        self.process_ongoing = ongoing
    
    def get_process_ongoing(self) -> bool:
        """Get process ongoing

        Args:
            ongoing (bool): If True, one process is ongoing
        """
        return self.process_ongoing
    
    def set_heart_beat(self, heartbeat: bool):
        """Set heart beat

        Args:
            heartbeat (bool): Heart beat of the system
        """
        self.heartbeat = heartbeat
    
    def get_heart_beat(self) -> bool:
        """Get heart beat

        Returns:
            bool: Heart beat of the system
        """
        return self.heartbeat
    
    def _get_system_word(self) -> list[bool]:
        """Internal method to get the system word as an array of bits (bool)

        Returns:
            list[bool]: array of bits of the system word
        """
        return [self.get_system_running(), self.get_process_ongoing(), self.get_heart_beat()] + [False] * 13
    
    def _set_system_word(self, word: list[bool]):
        """Internal method to set the system word from an array of bits (bool)

        Args:
            word (list[bool]): array of bits of the system word
        """
        self.set_system_running(word[0])
        self.set_process_ongoing(word[1])
        self.set_heart_beat(word[2])
        
    def _get_result_word(self) -> list[int]:
        """Internal method to get the result word as an array of bytes (int)

        Args:
            list[int]: array of bytes of the result word
        """
        return []
    
    def _set_result_word(self, word: list[int]) -> int:
        """Internal method to set the result word as an array of bytes (int)

        Args:
            word (list[int]): array of bytes of the result word
        Returns:
            int: size of the result word (in bytes)
        """
        return 0
    
    def set_agent_state(self, agent_id: int, active: bool):
        """Set agent state

        Args:
            agent_id (int): ID of the agent
            active (bool): It True, agent is active, else not
        """
        self.agents[agent_id].set_state(active)
    
    def get_agent_state(self, agent_id: int) -> bool:
        """Get agent state

        Args:
            agent_id (int): ID of the agent
        Returns:
            bool: It True, agent is active, else not
        """
        return self.agents[agent_id].get_state()
    
    def set_source_state(self, agent_id: int, source_id: int, active: bool):
        """Set source state

        Args:
            agent_id (int): ID of the agent
            source_id (int): ID of the source
            active (bool): It True, agent is active, else not
        """
        self.agents[agent_id].set_source_state(source_id, active)

    def get_source_state(self, agent_id: int, source_id: int) -> bool:
        """Get source state

        Args:
            agent_id (int): ID of the agent
            source_id (int): ID of the source
        Returns:
            bool: It True, agent is active, else not
        """
        return self.agents[agent_id].get_source_state(source_id)
    
    def _get_attribute_by_name(self, attribute_name: str) -> Attribute:
        """Internal function to get the attribute by its name

        Args:
            attribute_name (str): name of the attribute

        Returns:
            Attribute: attribute object with the corresponding name
        """
        attribute = None
        for _attribute in self.attributes:
            if _attribute.name == attribute_name:
                attribute = _attribute
                break
        return attribute
    
    def get_attribute_value(self, attribute_name: str) -> Any:
        """Get the value of the attribute from its name

        Args:
            attribute_name (str): name of the attribute

        Returns:
            Any: attribute value
        """
        return self._get_attribute_by_name(attribute_name).value
    
    def set_attribute_value(self, attribute_name: str, value: Any):
        """Set the value of the attribute from its name

        Args:
            attribute_name (str): name of the attribute
            value (Any): attribute value
        """
        self._get_attribute_by_name(attribute_name).value = value
    
    def to_msg(self) -> bytearray:
        """Convert table to a bytearray
        Returns:
            bytearray: message as array of bytes
        """
        byte_array = bytearray()
        pm_byte_array = bytearray()

        system_word = self._get_system_word()
        byte_array.extend([bool_list_to_int(system_word[:8]), bool_list_to_int(system_word[8:])])

        for agent_id in range(1, len(self.agents) + 1):
            agent_integer = int(self.get_agent_state(agent_id))
            for source_id in range(1, self.nb_sources + 1):
                agent_integer += int(self.get_source_state(agent_id, source_id)) * 2 ** (source_id)
            byte_array += agent_integer.to_bytes(2, "little")

            tool_id = int(self.agents[agent_id].tool_id)
            cycle_iteration = int(self.agents[agent_id].cycle_iteration)
            pm_byte_array += tool_id.to_bytes(2, "little") + cycle_iteration.to_bytes(2, "little")

        byte_array.extend(pm_byte_array)
        byte_array.extend(self._get_result_word())

        for attribute in self.attributes:
            byte_nb = int(np.ceil(attribute.size / 16)) * 2
            value = attribute.value
            if attribute.type == AttributeDataType.STRING:
                value_array = attribute.value.encode("utf8")
            elif attribute.type ==  AttributeDataType.INT:
                value_array = attribute.value.to_bytes(int(attribute.size / 8), byteorder="little")
            elif attribute.type ==  AttributeDataType.FLOAT:
                value_array = struct.pack('f',value)
            elif attribute.type ==  AttributeDataType.BOOL:
                value_array = struct.pack("?", value)
            byte_array += bytearray(value_array) + int(0).to_bytes(byte_nb - len(value_array), byteorder="little")

        return byte_array
    
    def __eq__(self, other):
        eq = self.system_running == other.system_running
        eq = eq and self.process_ongoing == other.process_ongoing
        eq = eq and self.heartbeat == other.heartbeat
        for agent_id, agent in self.agents.items():
            eq = eq and other.agents[agent_id] == agent
        for idx, attribute in enumerate(self.attributes):
            eq = eq and other.attributes[idx] == attribute
        return eq
    
    def to_dict(self) -> dict:
        """Convert exchange table to dict

        Returns:
            dict: dict representation of v
        """
        return {
            "system": {
                "running": self.system_running, 
                "process_ongoing": self.process_ongoing, 
                "heart_beat": self.heartbeat
            },
            "agents": {
                agent_id: agent.to_dict() for agent_id, agent in self.agents.items()
            },
            "attributes": {
                attribute.name: attribute.value for attribute in self.attributes
            }
        }


class PLCTable(ExchangeTable):
    """Exchange table used on PLC side
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ack_result = False
        self.ack_exception = False
    
    def set_ack_result(self, ack: bool):
        self.ack_result = ack
    
    def get_ack_result(self):
        return self.ack_result
    
    def set_ack_exception(self, ack: bool):
        self.ack_exception = ack
    
    def get_ack_exception(self):
        return self.ack_exception
    
    def _get_system_word(self):
        system_word = super()._get_system_word()
        system_word[3]= self.get_ack_result()
        system_word[4] = self.get_ack_exception()
        return system_word
    
    def _set_system_word(self, word: list[bool]):
        super()._set_system_word(word)
        self.set_ack_result(word[3])
        self.set_ack_exception(word[4])
    
    def to_dict(self) -> dict:
        d = super().to_dict()
        d["system"]["ack_result"] = self.ack_result
        d["system"]["ack_exception"] = self.ack_exception
        return d

class I40Table(ExchangeTable):
    """Exchange table used on Industry4.0 side
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception_occured = False
        self.exception_code = 0
        self.result = {"agent_id": 0, "source_id": 0, "key_id": 0, "value_id": 0, "category_id": 0}
    
    def __len__(self) -> int:
        result_size = 6
        return super().__len__() + result_size

    def set_exception_occured(self, is_exception: bool):
        self.exception_occured = is_exception
    
    def get_exception_occured(self):
        return self.exception_occured
    
    def set_exception(self, exception_code: int):
        self.exception_code = exception_code
    
    def get_exception(self) -> int:
        return self.exception_code
    
    def _get_system_word(self):
        system_word = super()._get_system_word()
        system_word[3]= self.get_exception_occured()
        system_word[8:] = int_to_bool_list(self.get_exception())
        return system_word
    
    def _set_system_word(self, word: list[bool]):
        super()._set_system_word(word)
        self.set_exception_occured(word[3])
        self.set_exception(bool_list_to_int(word[8:]))
    
    def _get_result_word(self):
        return [self.result["agent_id"], self.result["source_id"], 
                self.result["key_id"], self.result["value_id"], self.result["category_id"], 0]
    
    def _set_result_word(self, word: list[int]):
        self.set_result(word[0], word[1], word[2], word[3], word[4])
        return 6
    
    def set_result(self, agent_id: int, source_id: int, key_id: int, value_id: int, category_id: int):
        """Set the result of the inference

        Args:
            agent_id (int): ID of the agent
            source_id (int): ID of the source
            key_id (int): ID of the label key
            value_id (int): ID of the label value
            category_id (int): ID of the category
        """
        self.result = {"agent_id": agent_id, "source_id": source_id, "key_id": key_id, 
                       "value_id": value_id, "category_id": category_id}
    
    def get_result(self) -> dict:
        """Get the result of the inference

        Returns:
            dict: dict with the following keys : agent_id, source_id, key_id, value_id, category_id
        """
        return self.result  
    
    def to_dict(self) -> dict:
        d = super().to_dict()
        d["system"]["exception_occured"] = self.exception_occured
        d["system"]["exception"] = self.exception_code
        d["result"] = self.result
        return d
