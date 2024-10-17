from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Trust_Master, Trust_Value, Trust_Details, Trustee_Details, Document_Details, Mailing_Template, Resolution, Master, MasterValue, MeetingScheduler
from .serializers import TrustMasterSerializer, TrustValueSerializer, TrustDetailsSerializer, TrusteeDetailsSerializer, DocumentDetailsSerializer , MailingTemplateSerializer, ResolutionSerializer, MasterSerializer, MeetingSchedulerSerializer

from django.http import JsonResponse
from django.db.models import Q

from django.conf import settings
from django.core.mail import send_mail
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

import datetime



#1. Trust_Master class views
class TrustMasterListCreateView(generics.ListCreateAPIView):            #get and post method for making changes to the model
    queryset = Trust_Master.objects.all()
    serializer_class = TrustMasterSerializer

class TrustMasterDetailView(generics.RetrieveUpdateDestroyAPIView):     #for applying update, put, patch, and delete operations
    queryset = Trust_Master.objects.all()
    serializer_class = TrustMasterSerializer

#2. Trust_Value class views
class TrustValueListCreateView(generics.ListCreateAPIView):
    queryset = Trust_Value.objects.all()
    serializer_class = TrustValueSerializer

class TrustValueDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trust_Value.objects.all()
    serializer_class = TrustValueSerializer


#3. Trust_Details class views
class TrustDetailsListCreateView(generics.ListCreateAPIView):
    queryset = Trust_Details.objects.all()
    serializer_class = TrustDetailsSerializer
    permission_classes = [IsAuthenticated]
           #done to avoid null

class TrustDetailsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trust_Details.objects.all()
    serializer_class = TrustDetailsSerializer

# 4. Trustee_Details class views
class TrusteeDetailsListCreateView(generics.ListCreateAPIView):
    queryset = Trustee_Details.objects.all()
    serializer_class = TrusteeDetailsSerializer
    permission_classes = [IsAuthenticated]

class TrusteeDetailsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trustee_Details.objects.all()
    serializer_class = TrusteeDetailsSerializer


# 5. Document Details
class DocumentDetailsListCreateView(generics.ListCreateAPIView):
    queryset = Document_Details.objects.all()
    serializer_class = DocumentDetailsSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

class DocumentDetailsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document_Details.objects.all()
    serializer_class = DocumentDetailsSerializer
    permission_classes = [IsAuthenticated]


# # 6. Mailing Template
class MailingTemplateListCreateView(generics.ListCreateAPIView):
    queryset = Mailing_Template.objects.all()
    serializer_class = MailingTemplateSerializer
    
class MailingTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mailing_Template.objects.all()
    serializer_class = MailingTemplateSerializer
        
# 7. Resolution 
class ResolutionListCreateView(generics.ListCreateAPIView):
    queryset = Resolution.objects.all()
    serializer_class = ResolutionSerializer

class ResolutionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Resolution.objects.all()
    serializer_class = ResolutionSerializer

# 8. Master
class MasterListCreateView(generics.ListCreateAPIView):
    queryset = Master.objects.all()
    serializer_class = MasterSerializer

class MasterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Master.objects.all()
    serializer_class = MasterSerializer


# 9. Master Value
class MasterValueListCreateView(generics.ListCreateAPIView):
    queryset = Master.objects.all()
    serializer_class = MasterSerializer

class MasterValueDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Master.objects.all()
    serializer_class = MasterSerializer


# 10. Meeting Scheduler
class MeetingSchedulerListCreateView(generics.ListCreateAPIView):
    queryset = MeetingScheduler.objects.all()
    serializer_class = MeetingSchedulerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        meeting = serializer.save()

        print("Meeting created:", meeting.meeting_id)
        print("Associated trustees:", meeting.meeting_with.all())

        return Response(serializer.data, status=status.HTTP_201_CREATED)

        # if serializer.is_valid():
        #     meeting = serializer.save()
        #     return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        # return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class MeetingSchedulerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MeetingScheduler.objects.all()
    serializer_class = MeetingSchedulerSerializer

###########
#Google meet scheduler:
SCOPES = ['https://www.googleapis.com/auth/calendar']
class GoogleMeetScheduler(APIView):

    #handles the calendar service - via the google developer console. 
    def get_calendar_service(self):
        creds = None                #for user auth

        #token.json stores the user's refresh and access tokens
        try:        
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print("Failed to load credentials: ", e)

        #asks the user to login if no valid credentials are available...
        if not creds or not creds.valid:                
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            else:
                flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token: 
                token.write(creds.to_json())

        service = build('calendar', 'v3', credentials = creds)

        return service

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



########### SEARCH FUNCTIONS
#Trust List Search
def search_trust(request):
    search_query = request.GET.get('search')
    trust_type = request.GET.get('trust_type')

    trust = Trust_Details.objects.filter(
        trust_name__icontains = search_query,
        trust_type = trust_type
    ).values()

    if trust.exists():
        return JsonResponse(list(trust), safe = False)
    
    return JsonResponse({'message' : None}, status = status.HTTP_404_NOT_FOUND)


#Trustee Search
def search_trustee(request):
    search_query = request.GET.get('search')

    trustee = Trustee_Details.objects.filter(
        trustee_name__icontains = search_query
    ).values()

    if trustee.exists():
        return JsonResponse(list(trustee), safe=False)

    return JsonResponse({'message' :  None}, status = status.HTTP_404_NOT_FOUND)

#Master Search
def search_master_list(request):
    search_query = request.GET.get('search')
    master = Master.objects.filter(
        master_name__icontains = search_query
    ).values()

    if master.exists():
        return JsonResponse(list(master), safe = False)

    return JsonResponse({'message' : None}, status = status.HTTP_404_NOT_FOUND)

#Master List search
def search_master_value(request):
    search_query = request.GET.get('search')
    master_value = MasterValue.objects.filter(
        Q(master_name__master_name__icontains=search_query) |
        Q(master_value_name__icontains=search_query)
    ).values(
        'master_value_id', 
            'master_name__master_name',  
            'master_value_name',
            'created_at', 
            'updated_at'
    )
    
    if master_value.exists():
        return JsonResponse(list(master_value), safe=False)

    return JsonResponse({'message' : None}, status = status.HTTP_404_NOT_FOUND)
    