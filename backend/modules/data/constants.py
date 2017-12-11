
class Constants:
    """
    Global constants
    """
    hil_object_data_model = {
        "ip": None,
        "port": 9001,
        "index": None,
        "info": None,
        "data": None,
        "in": "",
        "rx_counter": 0
    }
    LOOP_DELAY = 0.001
    NODE_PUMP = 101
    NODE_FLOW_SENSOR = 1

    RESULT_OK = 0
    RESULT_FAIL = 1

    CLUSTER_MODEL = {
        "id": 0,
        "priority": 0,
        "centroid": [],
        "demand": None
    }
    NODE_MODEL = {
        "id": 0,
        "class": None,
        "demand": None,
        "priority": None
    }

    # NETWORK_FILE = "data/network_simple.json"
    NETWORK_FILE = "data/network.json"



