from django.db import models
from django.core.validators import URLValidator, RegexValidator, EmailValidator, FileExtensionValidator
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

# 1. Trust Master Model
class Trust_Master(models.Model):
    trust_master_id = models.AutoField(primary_key = True)
    trust_master_name = models.CharField(max_length = 225)
    trust_master_description = models.CharField(max_length = 225)
    created_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f"ID: {self.trust_master_id} - {self.trust_master_name}"

# # 2. Trust Value
class Trust_Value(models.Model):
    trust_value_id = models.AutoField(primary_key = True)
    trust_master_id = models.ForeignKey(Trust_Master, on_delete = models.CASCADE)
    trust_value_name = models.CharField(max_length = 225)
    trust_value_description = models.TextField(blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add= True)

    def __str__(self) -> str:
        return f"{self.trust_value_id} - {self.trust_master_id.trust_master_name}"

# 3. Trust Details - pg4 - Search trust will look here...
class Trust_Details(models.Model):
    trust_id = models.AutoField(primary_key = True)

    TRUST_TYPES = [
        ('type1', 'TYPE1'),
        ('type2', 'TYPE2'),
    ]
    trust_type = models.CharField(max_length = 50, choices=TRUST_TYPES)

    TRUST_NATURES = [
        ('nature1', 'NATURE1'),
        ('nature2', 'NATURE2'),
    ]
    trust_nature = models.CharField(max_length = 50, choices=TRUST_NATURES)

    trust_name = models.CharField(max_length=225)
    trust_address = models.TextField(blank = False, null = False)
    # Trust_State = models.CharField()
    trust_city = models.CharField(max_length=50)

    TRUST_STATE = [
        ('Maharashtra', 'Maharashtra'),
        ('Delhi', 'Delhi')
    ]
    trust_state = models.CharField(max_length= 50, choices=TRUST_STATE, default= None)

    pincode = models.CharField(max_length=6, validators=[RegexValidator(regex=r'^\d{6}$', message="Pincode must be a 6-digit number.")])
    trust_creation_date = models.DateField()
    trust_govt_reg_no = models.CharField(max_length = 100, unique = True)           #trust government registeration number - should be unique... ask niel and kushal sir
    trust_website = models.URLField(validators = [URLValidator()], blank = True, null = True)
    trust_email_id = models.EmailField(validators=[EmailValidator()])
    trust_description = models.TextField(blank = True, null = True)

    trust_contact_no = models.CharField(max_length=10, validators=[
        RegexValidator(regex=r'^\+?1?\d{9,15}$',
                       message = "Enter a valid phone no."
        )
    ])

    #ask about these two to kushal sir.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

            #if the referenced user is deleted in the future, the created by field will be set to null. 

    def __str__(self):
        return f"{self.trust_name} - at {self.created_at}."
    

# 4. Trustee Details - pg5 - Search trustee will look here... Added trustee's list
class Trustee_Details(models.Model):
    trustee_id = models.AutoField(primary_key = True)
    trust_id = models.ForeignKey(Trust_Details, on_delete = models.CASCADE)

    TRUSTEE_DESIGNATION_VALUES = [
        ('pos1' , '<pos_name>'),
        ('pos2' , '<pos_name2>')
    ]
    trustee_designation_vals = models.CharField(max_length = 100, choices = TRUSTEE_DESIGNATION_VALUES)

    TRUSTEE_MANAGER_OF = [
        ('manager1', 'Manager 1'),
        ('manager2', 'manager 2')
    ]
    trustee_manager_of = models.CharField(max_length = 50, choices = TRUSTEE_MANAGER_OF)

    TRUSTEE_CLASS_OF_PERSON = [
        ('class1', 'A'),
        ('class2', 'B')
    ]
    trustee_class_of_person = models.CharField(max_length = 100, choices= TRUSTEE_CLASS_OF_PERSON)

    trustee_name = models.CharField(max_length= 225)

    TRUSTEE_GENDER = [
        ('M', 'MALE'),
        ('F', 'FEMALE'),
        ('O', "OTHERS")
    ]
    trustee_gender = models.CharField(max_length=10, choices=TRUSTEE_GENDER)
    trustee_dob = models.DateField()
    trustee_occupation = models.CharField(max_length = 100)
    trustee_address = models.TextField() 
    trustee_email = models.EmailField(validators=[EmailValidator()])
    trustee_contact_no = models.CharField(max_length = 10, 
                                          validators = [RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number.")])
    trustee_trust_joining_date = models.DateField(blank = False, null = False)

    TRUSTEE_STATUS_VALUES = [
        ('status1', 'A')
    ]
    trustee_status_values = models.CharField(max_length = 30, choices=TRUSTEE_STATUS_VALUES)

    # trustee_joining_date = models.DateField(null = False)
    # trustee_last_date = models.DateField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.trustee_id} - {self.trustee_name}"


#5. Document Details 
class Document_Details(models.Model):
    document_id = models.AutoField(primary_key=True)
    trust_id = models.ForeignKey('Trust_Details', on_delete=models.CASCADE)

    DOCUMENT_TYPES = [
        ('type1', 'Type 1'),
        ('type2', 'Type 2'),
    ]
    document_type = models.CharField(max_length=100, choices=DOCUMENT_TYPES)

    DOCUMENT_SUBTYPES = [
        ('subtype1', 'Subtype 1'),
        ('subtype2', 'Subtype 2'),
    ]
    document_subtype = models.CharField(max_length=100, choices = DOCUMENT_SUBTYPES)

    document_name = models.CharField(max_length=255)
    document_attachment = models.FileField(upload_to='documents/', validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    document_description = models.TextField(blank = True, null = True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Document: {self.document_name} - {self.document_id}"

# 6. Mailing Templates
class Mailing_Template(models.Model):
    mailing_temp_id = models.AutoField(primary_key=True)
    trust_id = models.ForeignKey(Trust_Details, on_delete = models.CASCADE)

    TEMPLATE_FOR_CHOICES = [
        ('notification', 'Notification'),
        ('reminder', 'Reminder'),
        ('newsletter', 'Newsletter'),
    ]
    template_for = models.CharField(max_length=50, choices = TEMPLATE_FOR_CHOICES)

    mailing_temp_name = models.CharField(max_length = 255)
    mailing_temp_desc = models.TextField(blank = True, null = True)
    mailing_temp_attachment = models.FileField(upload_to='mailing/templates/',
                                               validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
                                               blank=True, 
                                               null = True)

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Mailing templates: {self.mailing_temp_id} - {self.mailing_temp_name}"
    

# 7. Resolution
class Resolution(models.Model):
    resolution_id = models.AutoField(primary_key = True)
    trust_id = models.ForeignKey('Trust_Details', on_delete = models.CASCADE)

    RESOLUTION_TYPE_CHOICES = [
        ('main', 'Main'),
        ('supplement', 'Supplement'),
    ]
    resolution_type = models.CharField(max_length = 50, choices = RESOLUTION_TYPE_CHOICES, default='main')

    resolution_title = models.CharField(max_length=255)
    resolutions_description = models.TextField(blank = True, null = True)
    resolution_attachment = models.FileField(upload_to = 'resolutions/',
                                             validators = [FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])],
                                             blank = True, 
                                             null = True)
    resolution_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f"{self.resolution_title} - {self.resolution_type} ({self.resolution_date})"
    
# 8. Master - pg10 - added master's search here 
class Master(models.Model):
    master_id = models.AutoField(primary_key=True)
    master_name = models.CharField(max_length = 255)
    master_description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.master_id} - {self.master_name}"
    

# 9. Added value to master's list search: 
class MasterValue(models.Model):
    master_value_id = models.AutoField(primary_key=True)
    master_name = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='values')
    master_value_name = models.CharField(max_length=255)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.master_value_id} - {self.master_value_name} ({self.master_name.master_name})"


#Meeting scheduler calender
class MeetingScheduler(models.Model):
    meeting_id = models.AutoField(primary_key = True)
    meeting_title  = models.CharField(max_length = 150, null = False, blank=False, default = "Meet")
    
    MEETING_TYPE = [
        ('online', 'Online'), 
        ('offline', 'Offline')
    ]
    meeting_type = models.CharField(max_length = 10, choices = MEETING_TYPE)

    MEETING_TEMPLATE = [
        ('temp1', 'TEMP1'),
        ('temp2', 'TEMP2')
    ]
    meeting_template = models.CharField(max_length = 50, choices = MEETING_TEMPLATE)

    meeting_time_date = models.DateField(null = False)
    meeting_time_from = models.TimeField(null = False)
    meeting_time_to = models.TimeField(null = False)

    meeting_description = models.TextField(blank = True, null = True)
    meeting_link = models.URLField(null = False, validators = [URLValidator()])

    #meeting links will be sent to the trustee belonging to that particular trust
    trust = models.ForeignKey(Trust_Details, on_delete=models.CASCADE)
    meeting_with = models.ManyToManyField(Trustee_Details, related_name = 'meetings')

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)


    def __str__(self):
        return f"Meeting on {self.meeting_time_date} - {self.meeting_type} - {self.meeting_title}"