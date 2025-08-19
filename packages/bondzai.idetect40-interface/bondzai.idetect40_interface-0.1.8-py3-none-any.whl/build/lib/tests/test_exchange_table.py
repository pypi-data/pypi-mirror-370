from idetect40_interface.exchange_table import ExchangeTable, I40Table, PLCTable, bool_list_to_int, byte_to_word_length, int_to_bool_list, \
    encode_string, decode_string


def test_int_bool_list_conversion():
    int_val = 212
    bool_list = [False, False, True, False, True, False, True, True]
    assert int_to_bool_list(int_val) == bool_list
    assert bool_list_to_int(bool_list) == int_val

def test_byte_word_conversion():
    assert byte_to_word_length(2) == 1
    assert byte_to_word_length(1) == 1
    assert byte_to_word_length(3) == 2

TEST_DESCRIPTOR = {
    "agents": {
        "nb_sources": 4,
        "nb_agents": 4
    },
    "attributes": [
        {
            "name": "serial number",
            "type": "INT",
            "size": 16
        },
        {
            "name": "vehicule type",
            "type": "STRING",
            "size": 24
        },
        {
            "name": "temperature",
            "type": "FLOAT",
            "size": 32
        },
        {
            "name": "over pressure",
            "type": "BOOL",
            "size": 1
        }
    ]
}

def table_from_dict(descriptor: dict, d: dict) -> ExchangeTable:
    if "result" in d:
        table = I40Table(descriptor)
        table.set_exception_occured(d["system"]["exception_occured"])
        table.set_exception(d["system"]["exception"])
        table.set_result(d["result"]["agent_id"], d["result"]["source_id"], d["result"]["key_id"], 
                         d["result"]["value_id"], d["result"]["category_id"])
    else:
        table = PLCTable(descriptor)
        table.set_ack_result(d["system"]["ack_result"])
        table.set_ack_exception(d["system"]["ack_exception"])
    table.set_system_running(d["system"]["running"])
    table.set_process_ongoing(d["system"]["process_ongoing"])
    table.set_heart_beat(d["system"]["heart_beat"])
    for agent_id, agent_dict in d["agents"].items():
        table.set_agent_state(agent_id, agent_dict["active"])
        table.agents[agent_id].set_tool_id(agent_dict["tool_id"])
        table.agents[agent_id].set_cycle_iteration(agent_dict["cycle_iteration"])
        for source_id, scr_active in agent_dict["sources"].items():
            table.set_source_state(agent_id, source_id, scr_active)
    for attribute_name, value in d["attributes"].items():
        table.set_attribute_value(attribute_name, value)
    return table
    


class Test_ExchangeTable():
    is_connected = False
    error_code = 125
    plc_table_dict = {
        "system": {
            "running": True, "process_ongoing": False, "heart_beat": False, 
            "ack_result": True, "ack_exception": True
        },
        "agents": {
            1: {"active": True, "sources": {1: True, 2: False, 3: True, 4: False}, "tool_id": 0, "cycle_iteration": 0},
            2: {"active": True, "sources": {1: False, 2: False, 3: True, 4: False}, "tool_id": 0, "cycle_iteration": 0},
            3: {"active": False, "sources": {1: True, 2: True, 3: True, 4: False}, "tool_id": 1, "cycle_iteration": 88},
            4: {"active": False, "sources": {1: True, 2: False, 3: True, 4: True}, "tool_id": 2, "cycle_iteration": 5}
        },
        "attributes": {
            "serial number": 12, "vehicule type": "abc", "temperature": 48.70000076293945, 
            "over pressure": False
        }
    }
    plc_table = table_from_dict(TEST_DESCRIPTOR, plc_table_dict)
    plc_table_msg = bytearray([
        25, 0, 
        11, 0, 
        9, 0, 
        14, 0, 
        26, 0, 
        0, 0, 
        0, 0, 
        0, 0, 
        0, 0, 
        1, 0, 
        88, 0, 
        2, 0, 
        5, 0, 
        12, 0, 
        97, 98, 
        99, 0, 
        205, 204, 
        66, 66, 
        0, 0
    ])
    i40_table_dict = {
        "system": {
            "running": True, "process_ongoing": False, "heart_beat": False, "exception_occured": True, 
            "exception": error_code
        },
        "agents": {
            1: {"active": True, "sources": {1: True, 2: False, 3: True, 4: False}, "tool_id": 0, "cycle_iteration": 0},
            2: {"active": True, "sources": {1: False, 2: False, 3: True, 4: False}, "tool_id": 0, "cycle_iteration": 0},
            3: {"active": False, "sources": {1: True, 2: True, 3: True, 4: False}, "tool_id": 1, "cycle_iteration": 88},
            4: {"active": False, "sources": {1: True, 2: False, 3: True, 4: True}, "tool_id": 2, "cycle_iteration": 5}
        },
        "result": {"agent_id": 1, "source_id": 3, "key_id": 1, "value_id": 6, "category_id": 4},
        "attributes": {
            "serial number": 12, "vehicule type": "ab", "temperature": 48.70000076293945, 
            "over pressure": False
        }
    } 
    i40_table = table_from_dict(TEST_DESCRIPTOR, i40_table_dict)
    i40_table_msg = bytearray([
        9, error_code, 
        11, 0, 
        9, 0, 
        14, 0, 
        26, 0,
        0, 0, 
        0, 0, 
        0, 0, 
        0, 0, 
        1, 0, 
        88, 0, 
        2, 0, 
        5, 0, 
        1, 3,
        1, 6,
        4, 0, 
        12, 0, 
        97, 98,
        0, 0, 
        205, 204, 
        66, 66, 
        0, 0
    ])
           
    def test_msg_to_table(self):
        table_from_msg = PLCTable(TEST_DESCRIPTOR, self.plc_table_msg)
        assert self.plc_table == table_from_msg
        table_from_msg = I40Table(TEST_DESCRIPTOR, self.i40_table_msg)
        assert self.i40_table == table_from_msg

    def test_table_to_msg(self):
        result = self.plc_table.to_msg()
        assert result == self.plc_table_msg
        result = self.i40_table.to_msg()
        assert result == self.i40_table_msg
    
    def test_get_plc_table_size(self):
        input_size = len(self.plc_table)
        assert input_size == len(self.plc_table_msg)
    
    def test_get_output_table_size(self):
        output_size = len(self.i40_table)
        assert output_size == len(self.i40_table_msg)
    
    def test_plc_table_dict(self):
        d = self.plc_table.to_dict()
        assert d == self.plc_table_dict

    def test_i40_table_dict(self):
        d = self.i40_table.to_dict()
        assert d == self.i40_table_dict
    
    def test_init_from_msg(self):
        self.i40_table.init_from_msg(self.i40_table_msg)
        result = self.i40_table.to_msg()
        assert result == self.i40_table_msg
        self.plc_table.init_from_msg(self.plc_table_msg)
        result = self.plc_table.to_msg()
        assert result == self.plc_table_msg

    def test_get_set_exception(self):
        error_code = 7
        self.i40_table.set_exception(error_code)
        assert self.i40_table.get_exception() == error_code

def test_encode_string():
    # standard encoding
    data_str = "abc"
    encoded_bytes = encode_string(data_str, encoding='utf-8')
    assert encoded_bytes == b'\x61\x62\x63\x00'  # 'abc' in little-endian, with padding with null byte

    data_str = "abcd"
    encoded_bytes = encode_string(data_str, encoding='utf-8')
    assert encoded_bytes == b'\x61\x62\x63\x64'  # 'abcd' in little-endian

    # s7-like big-endian 16-bit encoding
    data_str = "abc"
    encoded_bytes = encode_string(data_str, encoding='utf-8', big_endian16=True)
    assert encoded_bytes == b'\x62\x61\x00\x63'  # 'ba\0c' in big-endian 16-bit encoding

    data_str = "abcd"
    encoded_bytes = encode_string(data_str, encoding='utf-8', big_endian16=True)
    assert encoded_bytes == b'\x62\x61\x64\x63'  # 'badc' in big-endian 16-bit encoding


def decode_string():

    # standard encoding
    encoded_bytes = b'\x61\x62\x63' # 'abc' in little-endian
    data_str = decode_string(encoded_bytes, encoding='utf-8')
    assert data_str ==  'abc' 

    encoded_bytes = b'\x61\x62\x63\x64'# 'abcd' in little-endian
    data_str = decode_string(encoded_bytes, encoding='utf-8')
    assert data_str ==  'abcd' 

    # with padding
    encoded_bytes = b'\x61\x62\x63\x00' # 'abc' in little-endian, pith padding with null byte
    data_str = decode_string(encoded_bytes, encoding='utf-8')
    assert data_str ==  'abc'

    # s7-like big-endian 16-bit encoding
    encoded_bytes = b'\x62\x61\x00\x63' # 'abc' in big-endian, with padding
    data_str = decode_string(encoded_bytes, encoding='utf-8', big_endian16=True)
    assert data_str ==  'abc'
    
    encoded_bytes = b'\x62\x61\x64\x63'# 'abcd' in big-endian, without padding
    data_str = decode_string(encoded_bytes, encoding='utf-8', big_endian16=True)
    assert data_str ==  'abcd'

    encoded_bytes = b'\x62\x61\x64\x63\x00'# 'abcd' in big-endian, with padding, impaired (should not happen)
    data_str = decode_string(encoded_bytes, encoding='utf-8', big_endian16=True)
    assert data_str ==  'abcd'