from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from .models import Trust_Master, Trust_Value, Trust_Details, Trustee_Details, Document_Details, Mailing_Template, Resolution, Master, MasterValue, MeetingScheduler
from .serializers import TrustMasterSerializer, TrustValueSerializer, TrustDetailsSerializer, TrusteeDetailsSerializer, DocumentDetailsSerializer , MailingTemplateSerializer, ResolutionSerializer, MasterSerializer, MeetingSchedulerSerializer

from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db import transaction
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


# 10. Meeting Scheduler - get/ post
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

# Modify Meet: edits
#todo updates to be done: 
# todo 1. meet link check
# todo 2. time_date shouldn't be invalid, as the meet has been updaed, 
# todo 3. an email with the updated details must be sent to the participants
@api_view(['PUT', 'PATCH', 'DELETE'])
def modify_meets(request, meeting_title):
    try:
        # Fetching the meeting instance by its unique title
        meeting = MeetingScheduler.objects.get(meeting_title=meeting_title)
    except MeetingScheduler.DoesNotExist:
        return Response({'error': 'Meeting not found!'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle PUT/PATCH requests to update the meeting
    if request.method in ['PUT', 'PATCH']:
        # Get updated data
        new_meeting_title = request.data.get('meeting_title')
        meeting_time_date = request.data.get('meeting_time_date')
        meeting_time_from = request.data.get('meeting_time_from')
        meeting_time_to = request.data.get('meeting_time_to')
        meeting_template = request.data.get('meeting_template')
        meeting_description = request.data.get('meeting_description')
        meeting_type = request.data.get('meeting_type')
        meeting_link = request.data.get('meeting_link')
        meeting_with_data = request.data.get('meeting_with', [])

        #* CHECK TO NOT ALLOW THE USER ADD THE MEET PRIOR TO THE CURRENT TIME
        current_datetime = timezone.now()

        if meeting_time_date and meeting_time_from:
            meeting_datetime = timezone.make_aware(datetime.combine(meeting_time_date, meeting_time_from))
            if meeting_datetime < current_datetime:
                return Response({'error': 'Meeting date and time cannot be in the past.'}, status=status.HTTP_400_BAD_REQUEST)

        if meeting_time_date and meeting_time_to:
            meeting_datetime = timezone.make_aware(datetime.combine(meeting_time_date, meeting_time_to))
            if meeting_datetime < current_datetime:
                return Response({'error': 'Meeting date and time cannot be in the past.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update only the fields provided in the request
        if new_meeting_title:
            meeting.meeting_title = new_meeting_title  # Updating the title

        if meeting_time_date:
            meeting.meeting_time_date = meeting_time_date

        if meeting_time_from:
            meeting.meeting_time_from = meeting_time_from

        if meeting_time_to:
            meeting.meeting_time_to = meeting_time_to

        if meeting_template:
            meeting.meeting_template = meeting_template

        if meeting_description:
            meeting.meeting_description = meeting_description

        if meeting_type:
            meeting.meeting_type = meeting_type

        if meeting_link:
            meeting.meeting_link = meeting_link

        if meeting_with_data:
            trustee_names = [data['trustee_name'] for data in meeting_with_data]                    #* storing the trustee names in the list form 
            trustees = Trustee_Details.objects.filter(trustee_name__in=trustee_names)

            if trustees.count() != len(trustee_names):
                missing_names = set(trustee_names) - {t.trustee_name for t in trustees}             #* checks for the trustee names's existence in the db
                return Response({'error': f'Invalid trustee names: {", ".join(missing_names)}'}, status=status.HTTP_400_BAD_REQUEST)
            
            meeting.meeting_with.set(trustees)

        # Save the meeting changes
        try:
            with transaction.atomic():                                          #* fail safe method: if a transaction fails, all the changes done are reverted.
                meeting.save()                                                  #? if successfull, save the changes
            return Response({'message': 'Meeting updated successfully'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handle DELETE request to delete the meeting
    elif request.method == 'DELETE':
        meeting.delete()
        return Response({'message': 'Meeting deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class MeetingSchedulerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MeetingScheduler.objects.all()
    serializer_class = MeetingSchedulerSerializer


# 11. Meetings by Month view class: pg 8
class MeetingByMonthView(APIView):
    def get(self, request):
        try:
            month = int(request.query_params.get('month'))
            year = int(request.query_params.get('year'))                                #*typecasting to int - to work with the 'extract' fns 

            if month < 1 or month > 12:
                return Response({"error" : "Invalid Month"}, status = status.HTTP_400_BAD_REQUEST)

            #filtering the meets 
            meetings = MeetingScheduler.objects.annotate(                               #* annotate fn: adds new fields to the query resultn dynamically, done for the ease of executing filtering aggregating and sorting, without modifying the db.
                meeting_month = ExtractMonth('meeting_time_date'),
                meeting_year = ExtractYear('meeting_time_date')
            ).filter(meeting_month = month, meeting_year = year)

            result = {}                                                                 #*dict containing the title and trust name will be returned. 
            for meeting in meetings:
                date = meeting.meeting_time_date.strftime('%Y-%m-%d')

                if date not in result:
                    result[date] = []
                
                result[date].append({
                    'meeting_title' : meeting.meeting_title,
                    'trust_name' : meeting.trust.trust_name
                })
                
            return Response(result, status = status.HTTP_200_OK)

        except ValueError:
            return Response({"error" : "something's wrong with the M/Y."}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error' : str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

########### SEARCH FUNCTIONS
# Trust List Search
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



#MEET SEARCH VIEWS: 
#! NOTICES VIEW: for the meetings that haven't happend yet. 
def notices_view(request):
    search_query = request.GET.get('search', '').strip()                    #search query parameter: removes white spaces
    filters = Q(is_proceeding = False)                                     # TODO false: the meeting hasn't happened yet. Attribs returned in JSON format

    if search_query:
        filters = filters & (
            Q(meeting_title__icontains = search_query) |             
            Q(meeting_description__icontains = search_query) |
            Q(trust__trust_name__icontains = search_query) |
            Q(meeting_type__icontains = search_query)
        ) 

    meetings = MeetingScheduler.objects.filter(filters).values(             #* returns the following attribs to the user
        'meeting_id', 'meeting_title', 'trust__trust_name', 
        'meeting_time_date', 'meeting_time_from', 'meeting_time_to', 'meeting_type', 'meeting_link',
    )


    if meetings.exists():
        return JsonResponse(list(meetings), safe = False, status = status.HTTP_200_OK)
    
    return JsonResponse({'message' : 'No upcoming meets found!'}, status = status.HTTP_404_NOT_FOUND)

#! PROCEEDINGS VIEW: for the meetings that have already happened.
def proceedings_view(request):
    search_query = request.GET.get('search', '').strip()
    filters = Q(is_proceeding = True)

    if search_query:
        filters = filters & (
            Q(meeting_title__icontains = search_query) |
            Q(meeting_description__icontains = search_query) |
            Q(trust__trust_name__icontains = search_query) |
            Q(meeting_type__icontains = search_query)
        )

    meetings = MeetingScheduler.objects.filter(filters).values(
        'meeting_id', 'meeting_title', 'trust__trust_name', 
        'meeting_time_date', 'meeting_time_from', 'meeting_time_to', 'meeting_type'
    )

    if meetings.exists():
        return JsonResponse(list(meetings), safe = False, status = status.HTTP_200_OK)

    else:
        return JsonResponse({'message' : 'No elapsed meets found!'}, status = status.HTTP_404_NOT_FOUND)


# NOTICE MEETINGS DETAILS: pg view details data. modify and delete coded before in the "modify_meets" defined before - line 133
@api_view(['GET'])
def view_meeting_details(request, meeting_title):
    if not meeting_title:
        return JsonResponse({'error' : 'Meeting title not provided.'})
    
    try: 
        meeting = MeetingScheduler.objects.get(meeting_title = meeting_title)
    
        meeting_details = {
            'meeting_title': meeting.meeting_title,
            'meeting_type': meeting.meeting_type,
            'meeting_template': meeting.meeting_template,
            'meeting_time_date': meeting.meeting_time_date,
            'meeting_time_from': meeting.meeting_time_from,
            'meeting_time_to': meeting.meeting_time_to,
            'meeting_description': meeting.meeting_description,
            'meeting_link': meeting.meeting_link,
            'trust': meeting.trust.trust_name,
            'meeting_with': [t.trustee_name for t in meeting.meeting_with.all()]            
        }       #created at and updated at attributes skipped here. 

        return JsonResponse(meeting_details, safe = False, status = status.HTTP_200_OK)

    except MeetingScheduler.DoesNotExist:
        return JsonResponse({'error' : 'Meeting not found!'}, status = status.HTTP_404_NOT_FOUND)


