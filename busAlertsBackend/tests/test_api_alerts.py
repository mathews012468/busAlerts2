import requests
import json
from test_constants import *
from test_alerts import test_status_code


def test_response_is_json(url, data):
    response = requests.post(url, data=data)
    try:
        json.loads(response.content)
    except json.JSONDecodeError:
        print(f"{TEST_NOT_PASSED_MESSAGE}: response not valid JSON")
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: response is valid JSON")
    return True

def test_success_and_error_keys(url, data, success, error):
    response = requests.post(url, data=data)
    response_dict = json.loads(response.content)
    
    try:
        response_success = response_dict["success"]
    except KeyError:
        print(f"{TEST_NOT_PASSED_MESSAGE}: success key not present")
        return False
    
    if response_success != success:
        print(f"{TEST_NOT_PASSED_MESSAGE}: success key different from what we expect.\n Actual success key: {response_success}.\n Should be: {success}.")
        return False
    
    try:
        response_error = response_dict["error"]
    except KeyError:
        print(f"{TEST_NOT_PASSED_MESSAGE}: error key not present")
        return False

    if response_error != error:
        print(f"{TEST_NOT_PASSED_MESSAGE}: error key different from what we expect.\n Actual error key: {response_error}.\n Should be: {error}.")
        return False

    print(f"{TEST_PASSED_MESSAGE}: success and error key test passed")
    return True


def test_no_data():
    print("Start no data test")

    data = {}
    if not test_status_code(API_ALERT_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_URL, data=data):
        return False
    
    if not test_success_and_error_keys(API_ALERT_URL, data=data, success=False, error=MISSING_ROUTE_OR_STOP_MESSAGE):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed no data test\n")
    return True

def test_missing_route_id():
    print("Start missing route id test")

    data = {
        BUS_STOP_KEY: VALID_STOP_ID
    }
    if not test_status_code(API_ALERT_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_URL, data=data):
        return False
    
    if not test_success_and_error_keys(API_ALERT_URL, data=data, success=False, error=MISSING_ROUTE_OR_STOP_MESSAGE):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed missing route id test\n")
    return True

def test_missing_stop_id():
    print("Start missing stop id test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID
    }
    if not test_status_code(API_ALERT_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_URL, data=data):
        return False
    
    if not test_success_and_error_keys(API_ALERT_URL, data=data, success=False, error=MISSING_ROUTE_OR_STOP_MESSAGE):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed missing stop id test\n")
    return True

def test_invalid_route_id():
    print("Start invalid route id test")

    data = {
        BUS_ROUTE_KEY: INVALID_ROUTE_ID,
        BUS_STOP_KEY: VALID_STOP_ID
    }
    if not test_status_code(API_ALERT_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_URL, data=data):
        return False
    
    if not test_success_and_error_keys(API_ALERT_URL, data=data, success=False, error=INVALID_ROUTE_MESSAGE):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed invalid route id test\n")
    return True

def test_invalid_stop_id():
    print("Start invalid stop id test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: INVALID_STOP_ID
    }
    if not test_status_code(API_ALERT_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_URL, data=data):
        return False
    
    if not test_success_and_error_keys(API_ALERT_URL, data=data, success=False, error=INVALID_STOP_MESSAGE):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed invalid stop id test\n")
    return True

def test_stop_not_in_route():
    print("Start stop not in route test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: WRONG_ROUTE_STOP_ID
    }
    if not test_status_code(API_ALERT_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_URL, data=data):
        return False
    
    if not test_success_and_error_keys(API_ALERT_URL, data=data, success=False, error=INVALID_STOP_MESSAGE):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed stop not in route test\n")
    return True

def test_no_phone_and_email():
    print("Start no phone and email test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: VALID_STOP_ID
    }
    if not test_status_code(API_ALERT_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_URL, data=data):
        return False
    
    if not test_success_and_error_keys(API_ALERT_URL, data=data, success=False, error=EMAIL_AND_PHONE_MISSING_MESSAGE):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed no phone and email test\n")
    return True

def test_invalid_email():
    print("Start invalid email test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: VALID_STOP_ID,
        EMAIL_KEY: INVALID_EMAIL
    }
    if not test_status_code(API_ALERT_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_URL, data=data):
        return False
    
    if not test_success_and_error_keys(API_ALERT_URL, data=data, success=False, error=INVALID_EMAIL_MESSAGE):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed invalid email test\n")
    return True

def test_invalid_phone():
    print("Start invalid phone test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: VALID_STOP_ID,
        PHONE_KEY: INVALID_PHONE
    }
    if not test_status_code(API_ALERT_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_URL, data=data):
        return False
    
    if not test_success_and_error_keys(API_ALERT_URL, data=data, success=False, error=INVALID_PHONE_MESSAGE):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed invalid phone test\n")
    return True

def test_invalid_number():
    print("Start invalid number test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: VALID_STOP_ID,
        EMAIL_KEY: VALID_EMAIL,
        NUMBER_KEY: INVALID_NUMBER
    }
    if not test_status_code(API_ALERT_URL, data=data, desired_status_code=400):
        return False
    
    if not test_response_is_json(API_ALERT_URL, data=data):
        return False
    
    if not test_success_and_error_keys(API_ALERT_URL, data=data, success=False, error=INVALID_NUMBER_MESSAGE):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed invalid number test\n")
    return True

def test_valid_data():
    print("Start valid data test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: VALID_STOP_ID,
        EMAIL_KEY: VALID_EMAIL,
        NUMBER_KEY: VALID_NUMBER
    }
    if not test_status_code(API_ALERT_URL, data=data, desired_status_code=200):
        return False
    
    if not test_response_is_json(API_ALERT_URL, data=data):
        return False
    
    if not test_success_and_error_keys(API_ALERT_URL, data=data, success=True, error=None):
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
        test_no_phone_and_email(),
        test_invalid_email(),
        test_invalid_phone(),
        test_invalid_number(),
        test_valid_data()
    ]
    print(f"{sum(test_results)} of {len(test_results)} tests passed.")

if __name__ == "__main__":
    all_tests()