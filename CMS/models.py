from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class address(models.Model):
    address_id      = models.AutoField(primary_key=True)                                # Address ID
    city            = models.CharField(max_length=30)                                   # City
    zip_code        = models.CharField(max_length=10, blank=True)                       # Zipcode
    address_line1   = models.CharField(max_length=50, blank=True)                       # Address Line 1
    address_line2   = models.CharField(max_length=50, blank=True)                       # Address Line 2
    country         = models.CharField(max_length=30)                                   # Country
    phone           = models.BigIntegerField(blank=True)                                # Phone Number
    email           = models.EmailField(blank=True)                                     # Email address
    map_link        = models.CharField(max_length=100, blank=True)                      # Map Link (Not mandatory)

class Category(models.Model):
    main_category       = models.IntegerField()                                         # Main Category ID
    sub_category        = models.IntegerField()                                         # Sub Category ID
    main_category_desc  = models.CharField( max_length= 50, blank=False)                # Main Category Description
    sub_category_desc   = models.CharField( max_length= 50, blank=False)                # Sub Category Description

class conference(models.Model):
    conf_id                     = models.AutoField(primary_key=True)                    # Conference Id
    name                        = models.CharField( max_length= 50, blank=False)        # Conference Short Name
    main_category               = models.IntegerField()                                 # Conference Main Category Id
    sub_category                = models.IntegerField()                                 # Conference Sub Category Id
    conf_ownerId                = models.IntegerField()                                 # Foreign Key
    paper_Accepted              = models.IntegerField(blank=True)                      # Number of papers accepted
    conf_loc_id                 = models.ForeignKey(address, on_delete=models.CASCADE)  # Foreign Key - Conference Address Id
    conf_deadline               = models.DateField(blank=False)                         # Submission DeadLine
    description                 = models.TextField()                                    # Conference Description
    about                       = models.TextField()                                    # About Conference
    conf_Submission_date        = models.DateField(blank= False)                        # Conference Abstract Submission Date
    conf_start_date             = models.DateField(blank= False)                        # Conference Start Date
    conf_end_date               = models.DateField(blank= True)                        # Conference End Date


class conference_itemTable(models.Model):
    # Choices
    STATUS_CHOICES = [
        ('1', 'Abstract Not Submitted'),
        ('2', 'Abstract Submitted'),
        ('3', 'Reviewer Assigned'),
        ('4', 'Review In Progress'),
        ('5', 'Abstract Accepted'),
        ('6', 'Abstract Rejected'),
        ('7', 'Paper Submitted')
    ]
    paper_id        = models.AutoField(primary_key=True)                                    # Paper Id
    user_id         = models.ForeignKey(User, on_delete=models.CASCADE)                     # Author Id
    conf_id         = models.ForeignKey(conference, on_delete=models.CASCADE)               # Conference Id
    status          = models.CharField(max_length=1, choices=STATUS_CHOICES, default='1')   # Conference Status
    reviewer1_id    = models.IntegerField(blank=True)                                       # Reviewer1 ID
    reviewer2_id    = models.IntegerField(blank=True)                                       # Reviewer2 ID
    reviewer1_status= models.CharField(max_length=20, blank=True)                           # Reviewer1 Status {Accept/Reject}
    reviewer2_status= models.CharField(max_length=20, blank=True)                           # Reviewer2 Status {Accept/Reject}
    description     = models.TextField()                                                    # Author's Description
    pdf_link        = models.CharField(max_length=50,blank=True)                            # PDF Link
    entry_date      = models.DateField(blank= True)                                        # Submitted date

class skill(models.Model):
    skill_id        = models.AutoField(primary_key=True)                                # Skill ID
    user_name      = models.CharField(max_length= 50)                                   # Skill Name
    user_id         = models.ForeignKey(User, on_delete=models.CASCADE)                 # User ID
    skill_category  = models.IntegerField(blank=True)                                   # Skill Match

class comment(models.Model):
    comment_id = models.AutoField(primary_key=True)                                     # Comment ID
    user_id    = models.ForeignKey(User, on_delete=models.CASCADE)                # Reviewer ID
    paper_id   = models.ForeignKey(conference_itemTable, on_delete=models.CASCADE)      # Paper ID
    comment    = models.TextField()                                                     # Comment Description






