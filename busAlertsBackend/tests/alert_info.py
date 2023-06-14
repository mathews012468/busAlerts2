import requests
from bs4 import BeautifulSoup
from constants import *

ERROR_MESSAGE = "Either invalid stop, invalid route, or stop doesn't belong to route."
#overwrite the version of these variables from test_constants
#unfortunately I use a different key name for the same concept in different routes
BUS_ROUTE_KEY = "routeID"
BUS_STOP_KEY = "stopID"

def test_status_code(url, data, desired_status_code):
    response = requests.get(url, params=data)

    try:
        assert response.status_code == desired_status_code
    except AssertionError:
        print(f"{TEST_NOT_PASSED_MESSAGE}: status code not {desired_status_code}")
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: status code {desired_status_code}")
    return True

def test_alert_element_exists(url, data):
    response = requests.get(url, params=data)
    soup = BeautifulSoup(response.content, "html.parser")
    alert_element = soup.find(id="alert")
    try:
        assert alert_element is not None
    except AssertionError:
        print(f"{TEST_NOT_PASSED_MESSAGE}: alert element does not exist")
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: alert message exists")
    return True

def test_correct_alert_message(url, data, desired_alert_message):
    response = requests.get(url, params=data)
    soup = BeautifulSoup(response.content, "html.parser")
    alert_element = soup.find(id="alert")
    try:
        assert alert_element.text == desired_alert_message
    except AssertionError:
        print(f"{TEST_NOT_PASSED_MESSAGE}: alert message different from what we expect.\n Actual alert message: {alert_element.text}.\n Should be: {desired_alert_message}")
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: alert message is what we expect: {desired_alert_message}")
    return True

def test_no_data():
    print("Start no data test")

    data = {}
    if not test_status_code(ALERT_INFO_URL, data=data, desired_status_code=400):
        return False
    
    if not test_alert_element_exists(ALERT_INFO_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_correct_alert_message(ALERT_INFO_URL, data=data, desired_alert_message=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed no data test\n")
    return True

def test_missing_route_id():
    print("Start missing route id test")

    data = {
        BUS_STOP_KEY: VALID_STOP_ID
    }
    if not test_status_code(ALERT_INFO_URL, data=data, desired_status_code=400):
        return False
    
    if not test_alert_element_exists(ALERT_INFO_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_correct_alert_message(ALERT_INFO_URL, data=data, desired_alert_message=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed missing route id test\n")
    return True

def test_missing_stop_id():
    print("Start missing stop id test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID
    }
    if not test_status_code(ALERT_INFO_URL, data=data, desired_status_code=400):
        return False
    
    if not test_alert_element_exists(ALERT_INFO_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_correct_alert_message(ALERT_INFO_URL, data=data, desired_alert_message=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed missing stop id test\n")
    return True

def test_invalid_route_id():
    print("Start invalid route id test")

    data = {
        BUS_ROUTE_KEY: INVALID_ROUTE_ID,
        BUS_STOP_KEY: VALID_STOP_ID
    }
    if not test_status_code(ALERT_INFO_URL, data=data, desired_status_code=400):
        return False
    
    if not test_alert_element_exists(ALERT_INFO_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_correct_alert_message(ALERT_INFO_URL, data=data, desired_alert_message=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed invalid route id test\n")
    return True

def test_invalid_stop_id():
    print("Start invalid stop id test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: INVALID_STOP_ID
    }
    if not test_status_code(ALERT_INFO_URL, data=data, desired_status_code=400):
        return False
    
    if not test_alert_element_exists(ALERT_INFO_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_correct_alert_message(ALERT_INFO_URL, data=data, desired_alert_message=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed invalid stop id test\n")
    return True

def test_stop_not_in_route():
    print("Start stop not in route test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: WRONG_ROUTE_STOP_ID
    }
    if not test_status_code(ALERT_INFO_URL, data=data, desired_status_code=400):
        return False
    
    if not test_alert_element_exists(ALERT_INFO_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_correct_alert_message(ALERT_INFO_URL, data=data, desired_alert_message=error_message):
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
    if not test_status_code(ALERT_INFO_URL, data=data, desired_status_code=200):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed valid data test")
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