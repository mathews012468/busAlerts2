#test every path through alerts route
import requests
from bs4 import BeautifulSoup
from test_constants import *

def test_status_code(url, data, desired_status_code):
    response = requests.post(url, data=data)

    try:
        assert response.status_code == desired_status_code
    except AssertionError:
        print(f"{TEST_NOT_PASSED_MESSAGE}: status code not {desired_status_code}")
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: status code {desired_status_code}")
    return True

def test_alert_element_exists(url, data):
    response = requests.post(url, data=data)
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
    response = requests.post(url, data=data)
    soup = BeautifulSoup(response.content, "html.parser")
    alert_element = soup.find(id="alert")
    try:
        assert alert_element.text == desired_alert_message
    except AssertionError:
        print(f"{TEST_NOT_PASSED_MESSAGE}: alert message different from what we expect.\n Actual alert message: {alert_element.text}.\n Should be: {desired_alert_message}")
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: alert message is what we expect: {desired_alert_message}")
    return True


def core_test_for_errors(url, data, desired_alert_message):
    if not test_status_code(url, data=data, desired_status_code=400):
        return False

    if not test_alert_element_exists(url, data=data):
        return False
    
    if not test_correct_alert_message(url, data=data, desired_alert_message=desired_alert_message):
        return False
    
    print(f"Core tests passed")
    return True

def test_no_data():
    print("Start no data test")

    data = {}
    error_message = MISSING_ROUTE_OR_STOP_MESSAGE
    if not core_test_for_errors(REGULAR_URL, data=data, desired_alert_message=error_message):
        return False

    print(f"{TEST_PASSED_MESSAGE}: completed no data test\n")
    return True

def test_missing_route_id():
    print("Start missing route id test")

    #send stop but not route
    data = {BUS_STOP_KEY: VALID_STOP_ID}
    error_message = MISSING_ROUTE_OR_STOP_MESSAGE
    if not core_test_for_errors(REGULAR_URL, data=data, desired_alert_message=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed missing route id test\n")
    return True

def test_missing_stop_id():
    print("Start missing stop id test")

    #send route but not stop
    data = {BUS_ROUTE_KEY: VALID_ROUTE_ID}    
    error_message = MISSING_ROUTE_OR_STOP_MESSAGE
    if not core_test_for_errors(REGULAR_URL, data=data, desired_alert_message=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed missing stop id test\n")
    return True

def test_invalid_route_id():
    print("Start invalid route id test")

    data = {
        BUS_ROUTE_KEY: INVALID_ROUTE_ID,
        BUS_STOP_KEY: VALID_STOP_ID
    }
    error_message = INVALID_ROUTE_MESSAGE
    if not core_test_for_errors(REGULAR_URL, data=data, desired_alert_message=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed invalid route id test\n")
    return True

def test_invalid_stop_id():
    print("Start invalid stop id test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: INVALID_STOP_ID
    }
    error_message = INVALID_STOP_MESSAGE
    if not core_test_for_errors(REGULAR_URL, data=data, desired_alert_message=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed invalid stop id test\n")
    return True

def test_stop_not_in_route():
    print("Start stop not in route test")

    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: WRONG_ROUTE_STOP_ID
    }
    error_message = INVALID_STOP_MESSAGE
    if not core_test_for_errors(REGULAR_URL, data=data, desired_alert_message=error_message):
        return False
    
    print(f"{TEST_PASSED_MESSAGE}: completed stop not in route test\n")
    return True

def test_no_phone_and_email():
    print("Start no phone and email test")
    
    data = {
        BUS_ROUTE_KEY: VALID_ROUTE_ID,
        BUS_STOP_KEY: VALID_STOP_ID
    }
    error_message = EMAIL_AND_PHONE_MISSING_MESSAGE
    if not core_test_for_errors(REGULAR_URL, data=data, desired_alert_message=error_message):
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
    error_message = INVALID_EMAIL_MESSAGE
    if not core_test_for_errors(REGULAR_URL, data=data, desired_alert_message=error_message):
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
    error_message = INVALID_PHONE_MESSAGE
    if not core_test_for_errors(REGULAR_URL, data=data, desired_alert_message=error_message):
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
    error_message = INVALID_NUMBER_MESSAGE
    if not core_test_for_errors(REGULAR_URL, data=data, desired_alert_message=error_message):
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
    #status code
    if not test_status_code(REGULAR_URL, data=data, desired_status_code=200):
        return False
    #alert element
    if not test_alert_element_exists(REGULAR_URL, data=data):
        return False
    #alert message
    alert_message = SUCCESS_MESSAGE
    if not test_correct_alert_message(REGULAR_URL, data=data, desired_alert_message=alert_message):
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
        test_no_phone_and_email(),
        test_invalid_email(),
        test_invalid_phone(),
        test_invalid_number(),
        test_valid_data()
    ]
    print(f"{sum(test_results)} of {len(test_results)} tests passed.")

if __name__ == "__main__":
    all_tests()