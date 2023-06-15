import requests
import json
from constants import *
from get_bus_stops import test_status_code, ERROR_MESSAGE


def test_response_is_json(url, data):
    response = requests.get(url, params=data)
    try:
        json.loads(response.content)
    except json.JSONDecodeError:
        print(f"{TEST_NOT_PASSED_MESSAGE}: response not valid JSON")
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: response is valid JSON")
    return True

def test_keys(url, data, error):
    response = requests.get(url, params=data)
    response_dict = json.loads(response.content)
    
    keys = ["routeName", "routeID", "destinations", "stops", "error"]
    for key in keys:
        try:
            response_dict[key]
        except KeyError:
            print(f"{TEST_NOT_PASSED_MESSAGE}: {key} key not present")
            return False

    response_error = response_dict["error"]
    if response_error != error:
        print(f"{TEST_NOT_PASSED_MESSAGE}: error key different from what we expect.\n Actual error key: {response_error}.\n Should be: {error}.")
        return False

    print(f"{TEST_PASSED_MESSAGE}: keys test passed")
    return True


def test_no_data():
    print("Start no data test")

    data = {}
    if not test_status_code(API_GET_BUS_STOPS_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_GET_BUS_STOPS_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_keys(API_GET_BUS_STOPS_URL, data=data, error=ERROR_MESSAGE):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed no data test\n")
    return True

def test_invalid_bus_name():
    print("Start invalid bus name test")

    data = {BUS_NAME_KEY: INVALID_BUS_NAME}
    if not test_status_code(API_GET_BUS_STOPS_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_GET_BUS_STOPS_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_keys(API_GET_BUS_STOPS_URL, data=data, error=ERROR_MESSAGE):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed invalid bus name test\n")
    return True

def test_valid_data():
    print("Start valid data test")

    data = {BUS_NAME_KEY: VALID_BUS_NAME}
    if not test_status_code(API_GET_BUS_STOPS_URL, data=data, desired_status_code=200):
        return False
    
    if not test_response_is_json(API_GET_BUS_STOPS_URL, data=data):
        return False
    
    error_message = None
    if not test_keys(API_GET_BUS_STOPS_URL, data=data, error=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed valid data test\n")
    return True

def all_tests():
    test_results = [
        test_no_data(),
        test_invalid_bus_name(),
        test_valid_data()
    ]
    print(f"{sum(test_results)} of {len(test_results)} tests passed.")

if __name__ == "__main__":
    all_tests()
