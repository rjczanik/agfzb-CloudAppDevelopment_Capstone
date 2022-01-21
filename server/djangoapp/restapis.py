import requests
import json

# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url):
    kwargs = {
        "account_name": "77409d8b-7b29-4012-9f11-7397fa8471d0-bluemix",
        "api_key": "SYuLBU0NbYpfkunSquDMS_QE3iiD-afQLBifKCreb42o",
    }
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        if "api_key" in kwargs:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]

            print("params: ", params)

            response = requests.get(
                url,
                params=params,
                headers={"Content-Type": "application/json"},
                auth=HTTPBasicAuth("apikey", kwargs["api_key"]),
            )

            print("Response_apikey_Provided: ", response)

        else:
            print("No api_key passed to get request.")
            # Call get method of requests library with URL and parameters
            response = requests.get(
                url, headers={"Content-Type": "application/json"}, params=kwargs
            )
    except:
        # If any error occurs
        response = requests.get(
            url, headers={"Content-Type": "application/json"}, params=kwargs
        )
        print("Network exception occurred")

    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


def post_request(url, payload, **kwargs):
    print("Payload: ", payload)
    print("Kwargs: ", kwargs)
    print("POST to {}".format(url))
    try:
        response = requests.post(url, params=kwargs, json=payload)
        print(response)
    except:
        print("Post Network Exception Occured")

    status_code = response.status_code
    print("With status {}".format(status_code))
    json_data = json.loads(response.text)
    print("json_data: ", json_data)

    return json_data


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list


def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["body"]["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(
                address=dealer_doc["address"],
                city=dealer_doc["city"],
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"],
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                state=dealer_doc["state"],
                zip=dealer_doc["zip"],
            )
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list


def get_dealer_reviews_id_from_cf(url, **kwargs):
    results = []
    parameters = kwargs["kwargs"]

    json_result = get_request(url, **parameters)

    if json_result:
        reviews = json_result["body"]["data"]["docs"]
        for review in reviews:
            review_obj = DealerReview(
                # car_make=review["car_make"],
                # car_model=review["car_model"],
                # car_year=review["car_year"],
                dealership=review["dealership"],
                # id=review["id"],
                name=review["name"],
                purchase=review["purchase"],
                # purchase_date=review["purchase_date"],
                review=review["review"],
                # sentiment="default"
            )

            if "id" in review:
                review_obj.id = review["id"]
            if "purchase_date" in review:
                review_obj.purchase_date = review["purchase_date"]
            if "car_make" in review:
                review_obj.car_make = review["car_make"]
            if "car_model" in review:
                review_obj.car_model = review["car_model"]
            if "car_year" in review:
                review_obj.car_year = review["car_year"]

            # sentiment="default"
            print("Sentiment: ", review_obj.sentiment)
            # review_obj.sentiment=analyze_review_sentiments(review_obj.review)
            sentiment_response = analyze_review_sentiments(review_obj.review)
            print("Sentiment_(NLU_RAW): ", sentiment_response)
            if "sentiment" in sentiment_response:
                # Extrat Sentiment Label
                review_obj.sentiment = sentiment_response["sentiment"]["document"][
                    "label"
                ]
            else:
                review_obj.sentiment = sentiment_response["error"]
            print("Sentiment_(NLU_label_extract): ", review_obj.sentiment)
            results.append(review_obj)
            # print(results)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealer_review):
    api_url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/d1d2f758-3a11-4eac-a334-094ea9dd9c51/v1/analyze"

    parameters = {
        "api_key": "VvIMhCl_nW1AH_tOUo77nQLPJbEFriLitpyjJqUQlFzd",
        "text": dealer_review,
        "version": "2021-08-01",
        "features": "sentiment",
        "return_analyzed_text": True,
    }

    json_result = get_request(api_url, **parameters)

    return json_result
