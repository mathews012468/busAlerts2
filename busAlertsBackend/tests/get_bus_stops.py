import requests
from bs4 import BeautifulSoup
from constants import *

ERROR_MESSAGE = "Not a common name we recognize for a bus route"

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
    if not test_status_code(GET_BUS_STOPS_URL, data=data, desired_status_code=400):
        return False
    
    if not test_alert_element_exists(GET_BUS_STOPS_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_correct_alert_message(GET_BUS_STOPS_URL, data=data, desired_alert_message=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed no data test\n")
    return True

def test_invalid_bus_name():
    print("Start invalid bus name test")

    data = {BUS_NAME_KEY: INVALID_BUS_NAME}
    if not test_status_code(GET_BUS_STOPS_URL, data=data, desired_status_code=400):
        return False
    
    if not test_alert_element_exists(GET_BUS_STOPS_URL, data=data):
        return False
    
    error_message = ERROR_MESSAGE
    if not test_correct_alert_message(GET_BUS_STOPS_URL, data=data, desired_alert_message=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed invalid bus name test\n")
    return True

def test_valid_data():
    #should add more tests than just verifying the status code.
    #How do we know that the page served is the correct one?
    print("Start valid data test")

    data = {BUS_NAME_KEY: VALID_BUS_NAME}
    if not test_status_code(GET_BUS_STOPS_URL, data=data, desired_status_code=200):
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