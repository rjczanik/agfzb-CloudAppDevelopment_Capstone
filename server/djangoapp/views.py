from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import (
    get_dealers_from_cf,
    get_dealers_by_state,
    get_dealer_reviews_from_cf,
    post_request,
    get_reviews_max_id,
)
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from django.template import RequestContext


# Get an instance of a logger
logger = logging.getLogger(__name__)
base_url = "https://b32a16a9.eu-gb.apigw.appdomain.cloud/api"

# Endpoints paths
dealershipsPath = "/dealership"
dealerReviewsPath = "/review"
maxIdPath = "/maxid"

# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, "djangoapp/about.html")


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "POST":
        context["message"] = "Your message has been sent."
    return render(request, "djangoapp/contact.html", context)


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST["username"]
        password = request.POST["pwd"]
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect("djangoapp:index")
        else:
            # If not, return to login page again
            return render(request, "djangoapp/login.html", context)
    else:
        return render(request, "djangoapp/login.html", context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect("djangoapp:index")


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == "GET":
        return render(request, "djangoapp/registration.html", context)
    # If it is a POST request
    elif request.method == "POST":
        # Get user information from request.POST
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        password = request.POST["pwd"]
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
            # Login the user and redirect to index page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, "djangoapp/registration.html", context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(base_url + dealershipsPath)
        print(dealerships)
        context["dealers"] = dealerships
        # Return list of dealerships
        return render(request, "djangoapp/index.html", context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        dealers = get_dealers_from_cf(base_url + dealershipsPath)
        chosen_dealer = [dealer for dealer in dealers if dealer.id == dealer_id][0]
        # Get dealer's reviews from the URL
        dealerReviews = get_dealer_reviews_from_cf(
            base_url + dealerReviewsPath, dealer_id
        )
        # Return a list of dealer's reviews
        print(dealerReviews)
        if "error" not in dealerReviews:
            context["reviews"] = dealerReviews
        context["dealer_id"] = dealer_id
        context["dealer_name"] = chosen_dealer.full_name
        return render(request, "djangoapp/dealer_details.html", context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    if request.method == "GET":
        cars = CarModel.objects.filter(dealerId=dealer_id)
        context["cars"] = cars
        context["dealer_id"] = dealer_id
        return render(request, "djangoapp/add_review.html", context)
    elif request.method == "POST":
        review = dict()
        review["id"] = get_reviews_max_id(base_url + maxIdPath) + 1
        review["purchase"] = True if "purchasecheck" in request.POST else False
        review["review"] = request.POST["message"]
        review["dealership"] = dealer_id
        review["name"] = request.user.first_name + " " + request.user.last_name
        if review["purchase"] == True:
            date_obj = datetime.strptime(request.POST["purchasedate"], "%Y-%m-%d")
            formatedDate = date_obj.strftime("%m/%d/%Y")
            review["purchase_date"] = str(formatedDate)
            purchasedCar = get_object_or_404(CarModel, pk=request.POST["car"])
            review["car_make"] = purchasedCar.make.name
            review["car_model"] = purchasedCar.name
            review["car_year"] = int(purchasedCar.year.strftime("%Y"))
        json_payload = dict()
        json_payload["review"] = review
        print(json_payload)
        url = base_url + dealerReviewsPath
        response = post_request(json_payload, url, dealerId=dealer_id)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
