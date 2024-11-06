###########
#Google meet scheduler:
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from django.core.mail import send_mail

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

import datetime
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']
class GoogleMeetScheduler(APIView):

    #handles the calendar service - via the google developer console. 
    def get_calendar_service(self):
        creds = None                #for user auth
        base_path = os.path.dirname(os.path.abspath(__file__))  # get the current script directory
        client_secret_path = os.path.join(base_path, 'google auth client folder', 'client_secret.json')
        token_path = os.path.join(base_path, 'token.json')


        #token.json stores the user's refresh and access tokens
        try:    
            if os.path.exists(token_path):    
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print("Failed to load credentials: ", e)

        #asks the user to login if no valid credentials are available...
        if not creds or not creds.valid:                
            try:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
                    creds = flow.run_local_server(port=0)

                with open('token.json', 'w') as token: 
                    token.write(creds.to_json())

            except Exception as e:
                raise Exception(f"Error obtaining credentials: {e}")

        #building and returning the google calendar service obj
        try:
            service = build('calendar', 'v3', credentials = creds)
            return service
        except Exception as e:
            raise Exception(f"Error initializing Google Calendar service: {e}")

    #handles the meet link generation and events. 
    def create_google_meet_link(self, meeting_title, meeting_date, meeting_from, meeting_to):
        service = self.get_calendar_service()

        event = {
            'summary' : meeting_title,
            'start' : {
                'dateTime' : f"{meeting_date}T{meeting_from}",
                'timeZone' : 'Asia/Kolkata',
            },

            'end' : {
                'dateTime' : f'{meeting_date}T{meeting_to}',
                'timeZone' : 'Asia/Kolkata',
            },

            'conferenceData' : {
                'createRequest' : {
                    'requestID' : 'sample123', 
                    'conferenceSolutionKey' : {'type' : 'hangoutsMeet'}
                }
            },
        }

        #creating the event with the google meet link...
        event = service.events().insert(calendarId = 'primary', body = event, conferenceDataVersion = 1).execute()
        return event['hangoutLink']

    #marks as an endpoint to the post function...
    def post(self, request): 
        meeting_title = request.data.get('meeting_title')
        meeting_date = request.data.get('meeting_time_date')
        meeting_from = request.data.get('meeting_time_from')
        meeting_to = request.data.get('meeting_time_to')
        trustee_emails = request.data.get('trustee_emails', [])              #emails to be passed here, while requesting

        try:
            meet_link = self.create_google_meet_link(meeting_title, meeting_date, meeting_from, meeting_to)

            subject = f"Meeting Scheduled: {meeting_title}"
            message = (
                f"Dear Trustee,\n\n"
                f"A new meeting has been scheduled.\n\n"
                f"Title: {meeting_title}\n"
                f"Date: {meeting_date}\n"
                f"Time: {meeting_from} to {meeting_to}\n"
                f"Join Link: {meet_link}\n\n"
                f"Thank you.\nRegards."
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, trustee_emails)

            return Response({"meeting_link" : meet_link}, status = status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({"error" : str(e)}, status = status.HTTP_400_BAD_REQUEST)


