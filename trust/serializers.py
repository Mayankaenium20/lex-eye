from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

from .models import Trust_Master, Trust_Value, Trust_Details, Trustee_Details, Document_Details 
from .models import Mailing_Template, Resolution, Master, MasterValue, MeetingScheduler

from .google_meet_scheduler import GoogleMeetScheduler
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail

#for displaying the dropdown for trustee_details model -> api -> frontend 

#1. trust master model serializer
class TrustMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trust_Master
        fields = '__all__'

#2. trust value model serializier
class TrustValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trust_Value
        fields = '__all__'

#3. trust details model serializer
class TrustDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trust_Details
        fields = '__all__'

# 4. Trustee Details model serializer
class TrusteeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trustee_Details
        fields = '__all__'
    
# 5. Document Details model serializer
class DocumentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document_Details
        fields = '__all__'  

    
# # 6. Mailing Template model serializer
class MailingTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing_Template
        fields = '__all__'


# 7. Resolution model serializer
class ResolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resolution
        fields = '__all__'

# 8. Master model serializer
class MasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Master
        fields = "__all__" 


# 9. MasterValue model serialier
class MasterValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterValue
        fields = '__all__'


# 10. MeetingScheduler model serialiser

# Creating a new trustee_detailsserialiser to help with Meeting SchedulerSerialiser as we only need trustee_name for searching. Not all the fields from the model.
class Trustee_DetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trustee_Details
        fields = ['trustee_name']  

class MeetingSchedulerSerializer(serializers.ModelSerializer):
    trust = serializers.CharField()
    meeting_with = Trustee_DetailsSerializer(many=True)

    class Meta:
        model = MeetingScheduler
        fields = '__all__'

    def create(self, validated_data):
        trust_name = validated_data.pop('trust')
        meeting_with_data = validated_data.pop('meeting_with')

        # Fetch the Trust instance - error if the trust itself doesn't exist.
        try:
            trust_instance = Trust_Details.objects.get(trust_name=trust_name)
        except Trust_Details.DoesNotExist:
            raise serializers.ValidationError("Trust does not exist.")
        
        #extraction of names for validation later...
        trustee_names = [data['trustee_name'] for data in meeting_with_data]
        trustees = Trustee_Details.objects.filter(trust_id = trust_instance, trustee_name__in = trustee_names)

        if len(trustees) != len(trustee_names):
            missing_names = set(trustee_names) - {t.trustee_name for t in trustees}
            print(missing_names)
            raise serializers.ValidationError(f"The following trustees don't exist in this trust: {', '.join(missing_names)}")
        #done to avoid N+1 db query problem.

        # for trustee_data in meeting_with_data:
        #     trustee_name = trustee_data.get('trustee_name')
        #     try:
        #         trustee_instance = Trustee_Details.objects.get(trustee_name=trustee_name)
        #         meeting_scheduler.meeting_with.add(trustee_instance)
        #     except Trustee_Details.DoesNotExist:
        #         raise serializers.ValidationError(f"Trustee '{trustee_name}' does not exist.")

        # return meeting_scheduler
        with transaction.atomic():
            meeting_scheduler = MeetingScheduler.objects.create(
                trust = trust_instance, **validated_data
            )

            #collects the trustee names in bulk 
            print(trustees)
            meeting_scheduler.meeting_with.set(trustees)

            #preparing for emails: 
            trustee_emails = [t.trustee_email for t in trustees]
            meeting_title = validated_data.get('meeting_title')
            meeting_link = validated_data.get('meeting_link')
            meeting_date = validated_data.get('meeting_time_date')
            meeting_from = validated_data.get('meeting_time_from')
            meeting_to = validated_data.get('meeting_time_to')
            meeting_desc = validated_data.get('meeting_description')

            subject = f"Meeting Scheduled: {meeting_title}"
            message = (
                f"Dear trustee, \n\n"
                f"A new meeting has been scheduled.\n\n"
                f"Title: {meeting_title}\n"
                f"Date: {meeting_date}\n"
                f"Time: {meeting_from} - {meeting_to}\n"
                f"Meeting Agenda: {meeting_desc}\n"
                f"Link: {meeting_link}\n"
                f"Thank you. Regards."
            )

            try: 
                send_mail(
                    subject, 
                    message,
                    settings.DEFAULT_FROM_EMAIL, 
                    trustee_emails, 
                    fail_silently = False,
                )

            except Exception as e:
                raise serializers.ValidationError(f"Error sending email: {str(e)}")
        
        return meeting_scheduler
