import requests
import json

# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):

    print("GET from {} ".format(url))
    try:
        if "api_key" in kwargs:
            # With Authentication
            print("API_KEEEEEEY")
            params = dict()
            params["text"] = kwargs.get("text")
            params["version"] = kwargs.get("version")
            params["features"] = kwargs.get("features")
            params["return_analyzed_text"] = kwargs.get("return_analyzed_text")
            print(params)
            print(kwargs.get("api_key"))
            response = requests.get(
                url,
                headers={"Content-Type": "application/json", "X-Debug-Mode": "true"},
                params=params,
                auth=HTTPBasicAuth("apikey", str(kwargs.get("api_key"))),
            )
            print("RESPONSEEEEEEE")
            print(response)
        else:
            # Without Authentication
            print("NOOOOOO API_KEEEEEEY")
            response = requests.get(
                url,
                headers={"Content-Type": "application/json", "X-Debug-Mode": "true"},
                params=kwargs,
            )
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data

    except:
        # If any error occurs
        print("Network exception occurred")
        return {"error": "Network Error"}


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(json_payload, url, **kwargs):
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            params=kwargs,
            json=json_payload,
        )
        print("RESPONSEEEEEEE")
        print(response)

        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data

    except:
        # If any error occurs
        print("Network exception occurred")
        return {"error": "Network Error"}


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        if "docs" in json_result:
            # Get the row list in JSON as dealers
            dealers = json_result["docs"]
            # For each dealer object
            for dealer in dealers:
                # Create a CarDealer object with values in `doc` object
                dealer_obj = CarDealer(
                    address=dealer["address"],
                    city=dealer["city"],
                    full_name=dealer["full_name"],
                    id=dealer["id"],
                    lat=dealer["lat"],
                    long=dealer["long"],
                    short_name=dealer["short_name"],
                    st=dealer["st"],
                    zip=dealer["zip"],
                )
                results.append(dealer_obj)
        else:
            return {"error": "No dealers exists in the database"}

    return results


def get_dealers_by_state(url, st):
    results = []
    # Call get_request with a URL parameter and state
    json_result = get_request(url, state=st)
    if json_result:
        if "docs" in json_result:
            # Get the row list in JSON as dealers
            dealers = json_result["docs"]
            # For each dealer object
            for dealer in dealers:
                # Create a CarDealer object with values in `doc` object
                dealer_obj = CarDealer(
                    address=dealer["address"],
                    city=dealer["city"],
                    full_name=dealer["full_name"],
                    id=dealer["id"],
                    lat=dealer["lat"],
                    long=dealer["long"],
                    short_name=dealer["short_name"],
                    st=dealer["st"],
                    zip=dealer["zip"],
                )
                results.append(dealer_obj)
        else:
            return {"error": "This state doesn't have any dealers"}
    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    # Call get_request with a URL parameter and dealerId
    json_result = get_request(url, dealerId=dealer_id)
    if json_result:
        # Get the row list in JSON as dealers
        if "docs" in json_result:
            reviews = json_result["docs"]
            # For each dealer object
            for review in reviews:
                # Create a CarDealer object with values in `doc` object
                if review["purchase"] == True:
                    review_obj = DealerReview(
                        dealership=review["dealership"],
                        name=review["name"],
                        purchase=review["purchase"],
                        id=review["id"],
                        review=review["review"],
                        purchase_date=review["purchase_date"],
                        purchase_year=review["purchase_year"],
                        car_make=review["car_make"],
                        car_model=review["car_model"],
                        car_year=review["car_year"],
                        sentiment=analyze_review_sentiments(review["review"]),
                    )
                elif review["purchase"] == False:
                    review_obj = DealerReview(
                        dealership=review["dealership"],
                        name=review["name"],
                        purchase=review["purchase"],
                        id=review["id"],
                        review=review["review"],
                        purchase_date=None,
                        purchase_year=None,
                        car_make=None,
                        car_model=None,
                        car_year=None,
                        sentiment=analyze_review_sentiments(review["review"]),
                    )
                results.append(review_obj)
        else:
            return {"error": "The dealership doesn't have any reviews"}
    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealer_review):
    api_url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/61ea925f-b9e8-41c3-9e9a-b0b7eb150720/v1/analyze?version=2021-05-24"

    # Call get_request with a URL parameter and Watson NLU parameters
    json_result = get_request(
        api_url,
        api_key="RtXdBaaJb_yaBAqBSSgx45DfTx9i_SueMCdVTvpRELsw",
        version="2021-05-24",
        text=dealer_review,
        features="sentiment",
        return_analyzed_text=True,
    )
    if "sentiment" in json_result:
        print(json_result)
        # Get sentiment Object from the result
        sentiment_obj = json_result["sentiment"]
        sentiment = sentiment_obj["document"]["label"]
        return sentiment
    else:
        return None


def get_reviews_max_id(url, **kwargs):
    maxId = 0
    # Call get_request with a URL parameter
    json_result = get_request(url)

    if "maxId" in json_result:
        # Get the max id in reviews database
        maxId = json_result["maxId"]

    return maxId
