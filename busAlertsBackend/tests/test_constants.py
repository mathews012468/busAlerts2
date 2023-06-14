REGULAR_URL = "http://127.0.0.1/alert"
API_URL = "http://127.0.0.1/api/alert"

BUS_ROUTE_KEY = "busRouteID"
BUS_STOP_KEY = "busStopID"
PHONE_KEY = "phone"
EMAIL_KEY = "email"
NUMBER_KEY = "number"

TEST_NOT_PASSED_MESSAGE = "Test not passed"
TEST_PASSED_MESSAGE = "Test passed"

MISSING_ROUTE_OR_STOP_MESSAGE = "One of the following necessary pieces of information is missing: the bus route (busRouteID) or the bus stop (busStopID)"
INVALID_ROUTE_MESSAGE = "Not a valid route."
INVALID_STOP_MESSAGE = "Either invalid stop or stop doesn't belong to given route."
EMAIL_AND_PHONE_MISSING_MESSAGE = "Email and phone number are missing: at least one must be provided"
INVALID_EMAIL_MESSAGE = "Invalid email format."
INVALID_PHONE_MESSAGE = "Phone number not in valid format"
INVALID_NUMBER_MESSAGE = "The number of minutes/bus stops must be positive."
SUCCESS_MESSAGE = "Alert set up successfully!"

#could test any route and stop, this is arbitrary
VALID_ROUTE_ID = "MTA NYCT_B3"
INVALID_ROUTE_ID = "MTAB_Q40"
VALID_STOP_ID = "300240"
INVALID_STOP_ID = "5325232"
WRONG_ROUTE_STOP_ID = "550093"
VALID_EMAIL = "busalertsrecipient@gmail.com"
INVALID_EMAIL = "ABACUS"
VALID_PHONE = "+13474221229"
INVALID_PHONE = "123456789"
VALID_NUMBER = 6
INVALID_NUMBER = -1