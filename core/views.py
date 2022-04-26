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


class FileUploadView(APIView):
    permission_classes = (AllowAny, )
    throttle_scope = 'demo'

    def post(self, request, *args, **kwargs):
        print("key")
        content_length = request.META.get('CONTENT_LENGTH')  # bytes
        if int(content_length) > 5000000:
            return Response({"message": "Image size is greater than 5MB"}, status=HTTP_400_BAD_REQUEST)

        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            image_path = file_serializer.data.get('file')
            recognition = detect_faces(image_path)
        return Response(recognition, status=HTTP_200_OK)


class UserEmailView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        user = get_user_from_token(request)
        obj = {'email': user.email}
        return Response(obj)


class ChangeEmailView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = get_user_from_token(request)
        email_serializer = ChangeEmailSerializer(data=request.data)
        if email_serializer.is_valid():
            print(email_serializer.data)
            email = email_serializer.data.get('email')
            confirm_email = email_serializer.data.get('confirm_email')
            if email == confirm_email:
                user.email = email
                user.save()
                return Response({"email": email}, status=HTTP_200_OK)
            return Response({"message": "The emails did not match"}, status=HTTP_400_BAD_REQUEST)
        return Response({"message": "Did not receive the correct data"}, status=HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = get_user_from_token(request)
        password_serializer = ChangePasswordSerializer(data=request.data)
        if password_serializer.is_valid():
            password = password_serializer.data.get('password')
            confirm_password = password_serializer.data.get('confirm_password')
            current_password = password_serializer.data.get('current_password')
            auth_user = authenticate(
                username=user.username,
                password=current_password
            )
            if auth_user is not None:
                if password == confirm_password:
                    auth_user.set_password(password)
                    auth_user.save()
                    return Response(status=HTTP_200_OK)
                else:
                    return Response({"message": "The passwords did not match"}, status=HTTP_400_BAD_REQUEST)
            return Response({"message": "Incorrect user details"}, status=HTTP_400_BAD_REQUEST)
        return Response({"message": "Did not receive the correct data"}, status=HTTP_400_BAD_REQUEST)


class UserDetailsView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        user = get_user_from_token(request)
        membership = user.membership
        today = datetime.datetime.now()
        month_start = datetime.date(today.year, today.month, 1)
        tracked_request_count = TrackedRequest.objects \
            .filter(user=user, timestamp__gte=month_start) \
            .count()
        amount_due = 0
        if user.is_member:
            amount_due = stripe.Invoice.upcoming(
                customer=user.stripe_customer_id)['amount_due'] / 100
            print(amount_due)
        obj = {
            'membershipType': membership.get_type_display(),
            'free_trial_end_date': membership.end_date,
            'next_billing_date': membership.end_date,
            'api_request_count': tracked_request_count,
            'amount_due': amount_due
        }
        return Response(obj)


class SubscribeView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = get_user_from_token(request)
        # get the user membership
        membership = user.membership

        try:

            # get the stripe customer
            customer = stripe.Customer.retrieve(user.stripe_customer_id)
            serializer = SubscribeSerializer(data=request.data)

            # serialize post data (stripeToken)
            if serializer.is_valid():

                # get stripeToken from serializer data
                stripe_token = serializer.data.get('stripeToken')

                # create the stripe subscription
                subscription = stripe.Subscription.create(
                    customer=customer.id,
                    items=[{"plan": settings.STRIPE_PLAN_ID}]
                )

                # update the membership
                membership.stripe_subscription_id = subscription.id
                membership.stripe_subscription_item_id = subscription['items']['data'][0]['id']
                membership.type = 'M'
                membership.start_date = datetime.datetime.now()
                membership.end_date = datetime.datetime.fromtimestamp(
                    subscription.current_period_end
                )
                membership.save()

                # update the user
                user.is_member = True
                user.on_free_trial = False
                user.save()

                # create the payment
                payment = Payment()
                payment.amount = subscription.plan.amount / 100
                payment.user = user
                payment.save()

                return Response({'message': "success"}, status=HTTP_200_OK)

            else:
                return Response({'message': "Incorrect data was received"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.CardError as e:
            return Response({'message': "Your card has been declined"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            return Response({'message': "There was an error. You have not been billed. If this persists please contact support"}, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": "We apologize for the error. We have been informed and are working on the problem."}, status=HTTP_400_BAD_REQUEST)


class CancelSubscription(APIView):
    permission_classes = (IsMember, )

    def post(self, request, *args, **kwargs):
        user = get_user_from_token(request)
        membership = user.membership

        # update the stripe subscription
        try:
            sub = stripe.Subscription.retrieve(
                membership.stripe_subscription_id)
            sub.delete()
        except Exception as e:
            return Response({"message": "We apologize for the error. We have been informed and are working on the problem."}, status=HTTP_400_BAD_REQUEST)

        # update the user
        user.is_member = False
        user.save()

        # update the membership
        membership.type = "N"
        membership.save()

        return Response({'message': "Your subscription has been cancelled."}, status=HTTP_200_OK)


class ImageRecognitionView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        user = get_user_from_tokenize(request)
        print(user)
        membership = user.membership
        file_serializer = FileSerializer(data=request.data)

        usage_record_id = None
        if user.is_member and not user.on_free_trial:
            usage_record = stripe.UsageRecord.create(
                quantity=1,
                timestamp=math.floor(datetime.datetime.now().timestamp()),
                subscription_item=membership.stripe_subscription_item_id
            )
            usage_record_id = usage_record.id

        tracked_request = TrackedRequest()
        tracked_request.user = user
        tracked_request.usage_record_id = usage_record_id
        tracked_request.endpoint = '/api/image-recognition/'
        tracked_request.save()

        content_length = request.META.get('CONTENT_LENGTH')  # bytes
        if int(content_length) > 5000000:
            return Response({"message": "Image size is greater than 5MB"}, status=HTTP_400_BAD_REQUEST)

        if file_serializer.is_valid():
            file_serializer.save()
            image_path = file_serializer.data.get('file')
            recognition = detect_faces(image_path)
            return Response(recognition, status=HTTP_200_OK)
        return Response({"Received incorrect data"}, status=HTTP_400_BAD_REQUEST)


class ScraperView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        user = get_user_from_tokenize(request)
        membership = user.membership
        usage_record_id = None
        if user.is_member and not user.on_free_trial:
            usage_record = stripe.UsageRecord.create(
                quantity=1,
                timestamp=math.floor(datetime.datetime.now().timestamp()),
                subscription_item=membership.stripe_subscription_item_id
            )
            usage_record_id = usage_record.id

        tracked_request = TrackedRequest()
        tracked_request.user = user
        tracked_request.usage_record_id = usage_record_id
        tracked_request.endpoint = '/api/image-recognition/'
        tracked_request.save()
        sent = request.data.get('scrapinfo')
        wanted_list = sent.split('@@')
        scraper = AutoScraper()
        result = scraper.build(wanted_list[0], wanted_list)
        return Response(result, status=HTTP_200_OK)
        return Response({"Received incorrect data"}, status=HTTP_400_BAD_REQUEST)


class EmailView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        user = get_user_from_tokenize(request)
        print(user)
        membership = user.membership

        usage_record_id = None
        if user.is_member and not user.on_free_trial:
            usage_record = stripe.UsageRecord.create(
                quantity=1,
                timestamp=math.floor(datetime.datetime.now().timestamp()),
                subscription_item=membership.stripe_subscription_item_id
            )
            usage_record_id = usage_record.id

        tracked_request = TrackedRequest()
        tracked_request.user = user
        tracked_request.usage_record_id = usage_record_id
        tracked_request.endpoint = '/api/image-recognition/'
        tracked_request.save()

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
        user = get_user_from_tokenize(request)
        membership = user.membership

        usage_record_id = None
        if user.is_member and not user.on_free_trial:
            usage_record = stripe.UsageRecord.create(
                quantity=1,
                timestamp=math.floor(datetime.datetime.now().timestamp()),
                subscription_item=membership.stripe_subscription_item_id
            )
            usage_record_id = usage_record.id

        tracked_request = TrackedRequest()
        tracked_request.user = user
        tracked_request.usage_record_id = usage_record_id
        tracked_request.endpoint = '/api/image-recognition/'
        tracked_request.save()
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


class LinkView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        user = get_user_from_tokenize(request)
        membership = user.membership
        file_serializer = FileSerializer(data=request.data)

        usage_record_id = None
        if user.is_member and not user.on_free_trial:
            usage_record = stripe.UsageRecord.create(
                quantity=1,
                timestamp=math.floor(datetime.datetime.now().timestamp()),
                subscription_item=membership.stripe_subscription_item_id
            )
            usage_record_id = usage_record.id

        tracked_request = TrackedRequest()
        tracked_request.user = user
        tracked_request.usage_record_id = usage_record_id
        tracked_request.endpoint = '/api/image-recognition/'
        tracked_request.save()
        text = request.data.get('url')
        my_verify = verify.Verify(text)
        links = my_verify.return_functional_links()
        linkd = my_verify.return_error_links()
        z = {
            "workinglink": links,
            "notworkinglinks": linkd
        }
        return Response(z, status=HTTP_200_OK)
        return Response({"Received incorrect data"}, status=HTTP_400_BAD_REQUEST)


class GrammerView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        user = get_user_from_tokenize(request)
        membership = user.membership
        file_serializer = FileSerializer(data=request.data)

        usage_record_id = None
        if user.is_member and not user.on_free_trial:
            usage_record = stripe.UsageRecord.create(
                quantity=1,
                timestamp=math.floor(datetime.datetime.now().timestamp()),
                subscription_item=membership.stripe_subscription_item_id
            )
            usage_record_id = usage_record.id

        tracked_request = TrackedRequest()
        tracked_request.user = user
        tracked_request.usage_record_id = usage_record_id
        tracked_request.endpoint = '/api/image-recognition/'
        tracked_request.save()
        text = request.data.get('sentence')
        result = GingerIt().parse(text)

        return Response(result, status=HTTP_200_OK)
        return Response({"Received incorrect data"}, status=HTTP_400_BAD_REQUEST)


class IPView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        user = get_user_from_tokenize(request)
        membership = user.membership
        file_serializer = FileSerializer(data=request.data)

        usage_record_id = None
        if user.is_member and not user.on_free_trial:
            usage_record = stripe.UsageRecord.create(
                quantity=1,
                timestamp=math.floor(datetime.datetime.now().timestamp()),
                subscription_item=membership.stripe_subscription_item_id
            )
            usage_record_id = usage_record.id

        tracked_request = TrackedRequest()
        tracked_request.user = user
        tracked_request.usage_record_id = usage_record_id
        tracked_request.endpoint = '/api/image-recognition/'
        tracked_request.save()
        text = request.data.get('ipaddress')
        test = DbIpCity.get(text, api_key='free')
        t = test.to_json()
        return Response(t, status=HTTP_200_OK)
        return Response({"Received incorrect data"}, status=HTTP_400_BAD_REQUEST)


class HolidayView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        user = get_user_from_tokenize(request)
        membership = user.membership
        file_serializer = FileSerializer(data=request.data)

        usage_record_id = None
        if user.is_member and not user.on_free_trial:
            usage_record = stripe.UsageRecord.create(
                quantity=1,
                timestamp=math.floor(datetime.datetime.now().timestamp()),
                subscription_item=membership.stripe_subscription_item_id
            )
            usage_record_id = usage_record.id

        tracked_request = TrackedRequest()
        tracked_request.user = user
        tracked_request.usage_record_id = usage_record_id
        tracked_request.endpoint = '/api/image-recognition/'
        tracked_request.save()
        text = request.data.get('date')
        me = request.data.get('Country')
        us_holidays = holidays.CountryHoliday(me)
        t = us_holidays.get(text)
        b = (text in us_holidays)
        z = {
            "holidayname": t,
            "isholiday": b
        }
        return Response(z, status=HTTP_200_OK)
        return Response({"Received incorrect data"}, status=HTTP_400_BAD_REQUEST)


class EmailfinderView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        user = get_user_from_tokenize(request)
        membership = user.membership
        file_serializer = FileSerializer(data=request.data)

        usage_record_id = None
        if user.is_member and not user.on_free_trial:
            usage_record = stripe.UsageRecord.create(
                quantity=1,
                timestamp=math.floor(datetime.datetime.now().timestamp()),
                subscription_item=membership.stripe_subscription_item_id
            )
            usage_record_id = usage_record.id

        tracked_request = TrackedRequest()
        tracked_request.user = user
        tracked_request.usage_record_id = usage_record_id
        tracked_request.endpoint = '/api/image-recognition/'
        tracked_request.save()
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        domain = request.data.get('domain')
        permuted_emails = email_permuter.all_email_permuter(first_name=firstname,
                                                            last_name=lastname,
                                                            domain_name=domain
                                                            )
        char_list = ['-', '_']
        res = [ele for ele in permuted_emails if all(
            ch not in ele for ch in char_list)]
        desiredwords = [firstname, lastname]
        list2 = [x for x in res if any(word in x for word in desiredwords)]
        d = [x for x in list2 if firstname in x]
        e = [x for x in list2 if lastname not in x]
        for element in e:
            if element in d:
                d.remove(element)
        a = list(set(d))
        print(a)
        z = {
            "emailaddress": a
        }
        return Response(z, status=HTTP_200_OK)
        return Response({"Received incorrect data"}, status=HTTP_400_BAD_REQUEST)


class LinkpreView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        user = get_user_from_tokenize(request)
        membership = user.membership
        file_serializer = FileSerializer(data=request.data)

        usage_record_id = None
        if user.is_member and not user.on_free_trial:
            usage_record = stripe.UsageRecord.create(
                quantity=1,
                timestamp=math.floor(datetime.datetime.now().timestamp()),
                subscription_item=membership.stripe_subscription_item_id
            )
            usage_record_id = usage_record.id

        tracked_request = TrackedRequest()
        tracked_request.user = user
        tracked_request.usage_record_id = usage_record_id
        tracked_request.endpoint = '/api/image-recognition/'
        tracked_request.save()
        url = request.data.get('url')
        preview = link_preview(url, parser="lxml")
        a = preview.title
        b = preview.description
        c = preview.image
        d = preview.force_title
        e = preview.absolute_image
        z = {
            "title": a,
            "description": b,
            "image": c,
            "force_title": d,
            "absolute_image": e
        }
        return Response(z, status=HTTP_200_OK)
        return Response({"Received incorrect data"}, status=HTTP_400_BAD_REQUEST)


class APIKeyView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        user = get_user_from_token(request)
        print(user)
        token_qs = Token.objects.filter(user=user)
        if token_qs.exists():
            token_serializer = TokenSerializer(token_qs, many=True)
            try:
                return Response(token_serializer.data, status=HTTP_200_OK)
            except:
                return Response({"message": "Did not receive correct data"}, status=HTTP_400_BAD_REQUEST)
        return Response({"message": "User does not exist"}, status=HTTP_400_BAD_REQUEST)
