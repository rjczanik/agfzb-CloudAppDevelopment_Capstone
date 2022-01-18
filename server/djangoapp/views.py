from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect

# from .models import related models
from .models import CarMake, CarModel, CarDealer

# from .restapis import related methods
from .restapis import (
    get_dealers_from_cf,
    get_request,
    get_dealer_reviews_id_from_cf,
    post_request,
)
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
# ...
def about(request):
    return render(request, "djangoapp/about.html")


# Create a `contact` view to return a static contact page
# def contact(request):


def contact(request):
    return render(request, "djangoapp/contact_us.html")


# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST["username"]
        password = request.POST["psw"]
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect("djangoapp:index")  # home page redirect
        else:
            # If not, return to login page again
            messages.error(request, "Invalid User Name or Password")
            return render(request, "djangoapp/index.html", context)
    else:
        return render(request, "djangoapp/index.html", context)


# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect("djangoapp:index")


# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...


def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == "GET":
        return render(request, "djangoapp/registration.html", context)
    # If it is a POST request
    elif request.method == "POST":
        # Get user information from request.POST
        username = request.POST["username"]
        password = request.POST["psw"]
        first_name = request.POST["firstname"]
        last_name = request.POST["lastname"]
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, "djangoapp/registration.html", context)


# Update the `get_dealerships` view to render the index page with a list of dealerships


def get_dealerships(request):
    context = {}
    if request.method == "GET":
        # url = "your-cloud-function-domain/dealerships/dealer-get"
        url = "https://d34eafb5.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # save to list to render in template
        dealer_list = []
        for dealer in dealerships:
            dealership = {}
            dealership["id"] = dealer.id
            dealership["full_name"] = dealer.full_name
            dealership["city"] = dealer.city
            dealership["state"] = dealer.state
            dealership["zip"] = dealer.zip
            dealership["address"] = dealer.address
            print(dealership)
            dealer_list.append(dealership)
        print("dealer_list: ", dealer_list)
        context = {"dealer_list": dealer_list}
        print(context)
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        # return HttpResponse(dealer_names)
        return render(request, "djangoapp/index.html", context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...


def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        parameters = {"dealership": dealer_id}
        url = "https://d34eafb5.us-south.apigw.appdomain.cloud/api/review"
        reviews = get_dealer_reviews_id_from_cf(url, kwargs=parameters)
        print("get_dealer_details() --> (reviews):", reviews)
        # review_cat=' '.join([review.review for review in reviews])
        # review_cat2=' '.join([review.sentiment for review in reviews])
        # return HttpResponse(review_cat)
        analyzed_reviews = []
        for review in reviews:
            individual_review = {}
            individual_review["dealership"] = review.dealership
            individual_review["car_make"] = review.car_make
            individual_review["car_model"] = review.car_model
            individual_review["car_year"] = review.car_year
            individual_review["review"] = review.review
            individual_review["sentiment"] = review.sentiment
            analyzed_reviews.append(individual_review)
        context = {"analyzed_reviews": analyzed_reviews}
        print("context: ", context)
        return render(request, "djangoapp/dealer_details.html", context)
        # for review in reviews:
        # message1=review.review
        # message2=review.sentiment
        # message=message1 + " (" + message2 + ") "
        # temp.append(message)
        # reviews_analyzed=" ".join(temp)
        # return HttpResponse(reviews_analyzed)


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...


def add_review(request, dealer_id):
    if request.user.is_authenticated:
        new_review = dict()
        new_review["car_make"] = "Ford"
        new_review["car_model"] = "MustangGT"
        new_review["car_year"] = 2021
        new_review["dealership"] = dealer_id
        new_review["id"] = 11
        new_review["name"] = "Neddy Speddy"
        new_review["purchase"] = True
        new_review["purchase_date"] = "12/14/21"
        new_review["review"] = "Dreaming of Speed in my Wake."

        review_payload = {}
        review_payload["review"] = new_review
        # review_payload=new_review
        # convert python dictionary to json object
        # review_payload_json=json.dumps(review_payload)
        # print("review_payload_json: ",review_payload_json)

        review_post_url = "https://d34eafb5.us-south.apigw.appdomain.cloud/api/review"
        parameters = {"dealership": dealer_id}
        print("parameters: ", parameters)
        post_response = post_request(review_post_url, review_payload, **parameters)
        print(post_response)
        return JsonResponse(post_response)
    else:
        print("Unauthenticated User Please Log in to Submit Review")
