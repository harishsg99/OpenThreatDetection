import datetime
import math
from gingerit.gingerit import GingerIt
from autoscraper import AutoScraper
import phonenumbers
from phonenumbers import geocoder, carrier
from phonenumbers import timezone
import is_disposable_email
import holidays
from verify_email import verify_email
from validate_email import validate_email
from links_verification import verify
from permutations import email_permuter
from linkpreview import Link, LinkPreview, LinkGrabber
from linkpreview import link_preview
from ip2geotools.databases.noncommercial import DbIpCity
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from .image_detection import detect_faces
from .models import TrackedRequest, Payment
from .permissions import IsMember
from .serializers import (
    ChangeEmailSerializer,
    ChangePasswordSerializer,
    FileSerializer,
    TokenSerializer,
    SubscribeSerializer
)

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

User = get_user_model()


def get_user_from_token(request):
    print(request)
    print(request.META)
    key = request.META.get("HTTP_AUTHORIZATION").split(' ')[1]
    token = Token.objects.get(key=key)
    user = User.objects.get(id=token.user_id)
    return user


def get_user_from_tokenize(request):
    print(request.META)
    key = request.META.get("HTTP_API_KEY")
    print(key)
    token = Token.objects.get(key=key)
    user = User.objects.get(id=token.user_id)
    return user

slack_bot_token = ""
slack_signing_secret = ""

class EmailView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        text = request.data.get('email')
        result = is_disposable_email.check(text)
        print(result)
        is_valid = validate_email(email_address=text, check_format=True, check_blacklist=True, check_dns=True, dns_timeout=10,
                                  check_smtp=True, smtp_timeout=10, smtp_helo_host=None, smtp_from_address=None, smtp_debug=False)

        print(is_valid)
        z = {
            "isdisposable": result,
            "isvalid": is_valid
        }

        return Response(z, status=HTTP_200_OK)
        return Response({"Received incorrect data"}, status=HTTP_400_BAD_REQUEST)
      
 class PhoneView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        text = request.data.get('phonenumber')
        phoneNumber = phonenumbers.parse(text)
        timeZone = timezone.time_zones_for_number(phoneNumber)
        Carrier = carrier.name_for_number(phoneNumber, 'en')
        Region = geocoder.description_for_number(phoneNumber, 'en')
        valid = phonenumbers.is_valid_number(phoneNumber)
        possible = phonenumbers.is_possible_number(phoneNumber)
        z = {
            "timezone": timeZone,
            "Carrier": Carrier,
            "Region": Region,
            "isvalid": valid,
            "isdeliverable": possible
        }
        return Response(z, status=HTTP_200_OK)
        return Response({"Received incorrect data"}, status=HTTP_400_BAD_REQUEST)
    
 class SpamView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        text = request.data.get('spam')
        result = spamcheck.check(text, report=True)
        score = result['score']
        report = result['report']
        if(score > 5):
            z = {
            "isSpam": "True",
            "spam_score": score
            } 
        elif(score < 5):
            z = {
            "isSpam": "False",
            "spam_score": score
            } 

        return Response(z, status=HTTP_200_OK)
        return Response({"Received incorrect data"}, status=HTTP_400_BAD_REQUEST)
    
 class PhishingView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        text = request.data.get('url')
        sb = SafeBrowsing(conf['SafeBrowsing']['key'])
        res = sb.lookup_url("text")
        z = {
            "ismalicious": res["malicious"],
            } 
        if(res["malicious"] == True):
            slack_client.chat_postMessage(response_type="in_channel",channel="",text="Alert! Phishing link detected!")

        return Response(z, status=HTTP_200_OK)
        return Response({"Received incorrect data"}, status=HTTP_400_BAD_REQUEST)
