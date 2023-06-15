import requests
import json
from constants import *
from alert_info import \
    test_status_code, \
    ERROR_MESSAGE, \
    BUS_ROUTE_KEY, \
    BUS_STOP_KEY

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
    
    keys = ["routeName", "stopName", "routeID", "stopID", "error"]
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
    if not test_status_code(API_ALERT_INFO_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_INFO_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_keys(API_ALERT_INFO_URL, data=data, error=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed no data test\n")
    return True

def test_missing_route_id():
    print("Start missing route id test")

    data = {
        BUS_STOP_KEY: VALID_STOP_ID
    }
    if not test_status_code(API_ALERT_INFO_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_INFO_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_keys(API_ALERT_INFO_URL, data=data, error=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed missing route id test\n")
    return True

def test_missing_stop_id():
    print("Start missing stop id test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID
    }
    if not test_status_code(API_ALERT_INFO_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_INFO_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_keys(API_ALERT_INFO_URL, data=data, error=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed missing stop id test\n")
    return True

def test_invalid_route_id():
    print("Start invalid route id test")

    data = {
        BUS_ROUTE_KEY: INVALID_ROUTE_ID,
        BUS_STOP_KEY: VALID_STOP_ID
    }
    if not test_status_code(API_ALERT_INFO_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_INFO_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_keys(API_ALERT_INFO_URL, data=data, error=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed invalid route id test\n")
    return True

def test_invalid_stop_id():
    print("Start invalid stop id test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: INVALID_STOP_ID
    }
    if not test_status_code(API_ALERT_INFO_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_INFO_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_keys(API_ALERT_INFO_URL, data=data, error=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed invalid stop id test\n")
    return True

def test_stop_not_in_route():
    print("Start stop not in route test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: WRONG_ROUTE_STOP_ID
    }
    if not test_status_code(API_ALERT_INFO_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_INFO_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_keys(API_ALERT_INFO_URL, data=data, error=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed stop not in route test\n")
    return True

def test_valid_data():
    #I should probably throw in more tests than just the status code.
    #How can we verify that received the correct page?
    print("Start valid data test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: VALID_STOP_ID
    }
    if not test_status_code(API_ALERT_INFO_URL, data=data, desired_status_code=200):
        return False
    
    if not test_response_is_json(API_ALERT_INFO_URL, data=data):
        return False
    
    error_message = None
    if not test_keys(API_ALERT_INFO_URL, data=data, error=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed valid data test\n")
    return True

def all_tests():
    test_results = [
        test_no_data(),
        test_missing_route_id(),
        test_missing_stop_id(),
        test_invalid_route_id(),
        test_invalid_stop_id(),
        test_stop_not_in_route(),
        test_valid_data()
    ]
    print(f"{sum(test_results)} of {len(test_results)} tests passed.")

if __name__ == "__main__":
    all_tests()
