from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.db.models import CharField, Value as V

from .models import address,Category, conference, conference_itemTable, skill, comment
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import UserCreationForm, UserCreateForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
import datetime
from django.db.models import Q
from django.core.files.storage import FileSystemStorage


# Create your views here.
def paper_view_service(request, paperId):
    if request.user.is_authenticated:
        conference_itemTable_obj    = conference_itemTable.objects.get( paper_id = 1)
        conference_obj              = conference.objects.get(conf_id = conference_itemTable_obj.conf_id_id )
        address_obj                 = address.objects.get(address_id = conference_obj.conf_loc_id_id)
        category_obj                = Category.objects.get( main_category = 1, sub_category = 1 )

        usergrp_obj = Group.objects.get(id=request.user.id)
        # usergrp_obj = auth_user_groups.object.get(user_id=request.user.id)
        if usergrp_obj.group_id == 3:           # Author
            ResubmitButton = True
            ActionButton   = False
            R1_Box         = True
            R2_Box         = True
        elif usergrp_obj.group_id == 2:         # Reviewer
            ResubmitButton = False
            ActionButton   = True
            R1_Box         = True
            R2_Box         = False
        else:                                   # Chairperson
            ResubmitButton = False
            ActionButton   = False
            R1_Box         = True
            R2_Box         = True


        days = conference_obj.conf_start_date - datetime.datetime.now().date()
        DaysDesc = ' '
        if days >= 0:
            DaysDesc = days + 'days until the conference begins'
        else:
            DaysDesc = 'This conference is ended'

        return render(request, 'PaperView.html', {
            'ConferenceName'        : conference_obj.name,
            'ConferenceDescription' : conference_obj.description,
            'City'                  : address_obj.city,
            'Country'               : address_obj.country,
            'ConferenceAbout'       : conference_obj.about,
            'Status'                : conference_itemTable_obj.status,
            'MainCategory'          : category_obj.main_category_desc,
            'SubCategory'           : category_obj.sub_category_desc,
            'conf_start_date'       : conference_obj.conf_start_date,
            'conf_end_date'         : conference_obj.conf_end_date,
            'DaysDesc'              : DaysDesc,
            'ResubmitButton'        : ResubmitButton,
            'ActionButton'          : ActionButton,
            'R1_Box'                : R1_Box,
            'R2_Box'                : R2_Box
        })
    else:
        return HttpResponse(" Page not found !!!!")

def conf_view(request, confId):

    if request.method == 'POST':
        uploaded_file= request.FILES['file']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        url = fs.url(name)

    conference_obj = conference.objects.get(conf_id=confId)
    address_obj = address.objects.get(address_id=conference_obj.conf_loc_id_id)
    category_obj = Category.objects.get(main_category=1, sub_category=1)

    days = conference_obj.conf_start_date - datetime.datetime.now().date()
    DaysDesc = ' '
    if days >= 0:
        DaysDesc = days + 'days until the conference begins'
    else:
        DaysDesc = 'This conference is ended'


    if request.user.is_authenticated:

        # usergrp_obj = auth_user_groups.object.get(user_id=request.user.id)
        usergrp_obj = Group.objects.get(id=request.user.id)
        button = False
        if usergrp_obj.group_id == 3:           # Author
            button = True
        else:
            button = False

        return render(request, 'ConferenceDescription.html',{
            'ConferenceName'        : conference_obj.name,
            'ConferenceDescription' : conference_obj.description,
            'City'                  : address_obj.city,
            'Country'               : address_obj.country,
            'ConferenceAbout'       : conference_obj.about,
            'MainCategory'          : category_obj.main_category_desc,
            'SubCategory'           : category_obj.sub_category_desc,
            'conf_start_date'       : conference_obj.conf_start_date,
            'conf_end_date'         : conference_obj.conf_end_date,
            'DaysDesc'              : DaysDesc,
            'buttonEnable'          : button,
            'sub_date'              : conference_obj.conf_Submission_date,
            'acceptance_date'       : conference_obj.conf_Submission_date - 60
        })
    else:
        button = False
        return render(request, 'ConferenceDescription.html', {
            'ConferenceName': conference_obj.name,
            'ConferenceDescription': conference_obj.description,
            'City': address_obj.city,
            'Country': address_obj.country,
            'ConferenceAbout': conference_obj.about,
            'MainCategory': category_obj.main_category_desc,
            'SubCategory': category_obj.sub_category_desc,
            'conf_start_date': conference_obj.conf_start_date,
            'conf_end_date': conference_obj.conf_end_date,
            'DaysDesc': DaysDesc,
            'buttonEnable': button,
            'sub_date': conference_obj.conf_Submission_date,
            'acceptance_date': conference_obj.conf_Submission_date - 60
        })

def paper_list(request, confId):

    # usergrp_obj    = auth_user_groups.object.get(user_id=request.user.id)
    usergrp_obj = Group.objects.get(id=request.user.id)
    if usergrp_obj.group_id == 1 | usergrp_obj.group_id == 2:
        conference_obj = conference.objects.get(conf_id=confId)
        skill_obj      = skill.objects.get( skill_category = conference_obj.main_category )
        action = False
        if usergrp_obj.group_id == 1:            # Chairperson
            conference_itemTable_obj = conference_itemTable.objects.get( conf_id_id  = confId )
            action = True
        elif usergrp_obj.group_id == 2:          # Reviewer
            conference_itemTable_obj = conference_itemTable.objects.get( Q(conf_id_id  = confId), Q(reviewer1_id = request.user.id) | Q(reviewer2_id = request.user.id) )

        paperlist = {}

        for item in conference_itemTable_obj:
            paperlist['paper_id'] = item.paper_id
            paperlist['user_id']  = item.user_id
            paperlist['name']     = User.get_full_name()
            paperlist['status']   = item.status
            paperlist['entry_date'] = item.entry_date
            paperlist['action']     = action
            paperlist['link']       ='cms/paperview/' + item.paper_id

        return render(request, 'ConferenceDescription.html', {
            'ConferenceName': conference_obj.name,
            'ConferenceDescription': conference_obj.description,
            'paperlist':paperlist,
            'reviewer_list': skill_obj
        })



def conferences_view(request):
    category=None
    category_query_param = request.GET.get('category')
    category_obj = Category.objects.all()
    conference_obj = conference.objects.all()
    main_category_list = category_obj.distinct('main_category')
    if category_query_param:
        conference_obj = conference_obj.filter(main_category = category_query_param)
        category = Category.objects.distinct('main_category').get(main_category=category_query_param)
        for main_category in main_category_list:
            if main_category.main_category == category_query_param:
                main_category.css = 'is-selected'
            else:
                main_category.css=''
                # main_category_list[category].css = 'isSelected'
    for conferences in conference_obj:
        address_list = address.objects.annotate(location= Concat('city', V(','), 'country')).get(address_id=conferences.conf_loc_id_id)
        conferences.location = address_list.location
        category_list = category_obj.filter(main_category=conferences.main_category,sub_category=conferences.sub_category).first()
        conferences.parent_category = category_list.main_category_desc
        conferences.child_category = category_list.sub_category_desc

    return render(request, 'conference.html',{'conference_obj':conference_obj,
                                              'category':category,
                                              'main_category_list':main_category_list,'url':'conferences'})

def user_conferences(request):
    user = User.objects.get(id=request.user.id)
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        category = None
        category_query_param = request.GET.get('category')
        category_obj = Category.objects.all()
        if user.groups.filter(name = 'Chairperson').exists():
            conference_obj = conference.objects.get(conf_ownerId=id)
        elif user.groups.filter(name='Reviewer').exists():
            conference_obj_item = conference_itemTable.objects.filter(Q(reviewer1_id=id) | Q(reviewer2_id=id))
            # conference_obj = conference.objects.filter(conf_)
            # for conference_item in conference_obj_item:
            print(conference_obj_item)
            # conference_obj = conference.objects.get(conf_id=conference_obj_item.conf_id_id)
        elif user.groups.filter(name='Author').exists():
            conference_obj = conference.objects.get(conf_ownerId=id)
        else:
            conference_obj = conference.objects.get(conf_ownerId=id)

    else:
        return redirect('error')
    return render(request, 'conference.html')

def error(request):
    return render(request,'error.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            my_group = Group.objects.get(name='Author')
            my_group.user_set.add(user)
            return redirect('/conference/user.user_name')
    else:
        form = UserCreateForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })

def Create_data(request):

    # 1.Arts & Humanities
    category_obj = Category(main_category=1001, sub_category=2001, main_category_desc='Arts & Humanities',
                         sub_category_desc='Art')
    category_obj.save()
    category_obj = Category(main_category=1001, sub_category=2002, main_category_desc='Arts & Humanities',
                            sub_category_desc='Education')
    category_obj.save()
    category_obj = Category(main_category=1001, sub_category=2003, main_category_desc='Arts & Humanities',
                            sub_category_desc='History')
    category_obj.save()
    category_obj = Category(main_category=1001, sub_category=2004, main_category_desc='Arts & Humanities',
                            sub_category_desc='Human Rights')
    category_obj.save()
    category_obj = Category(main_category=1001, sub_category=2005, main_category_desc='Arts & Humanities',
                            sub_category_desc='Languages / Literature')
    category_obj.save()
    category_obj = Category(main_category=1001, sub_category=2006, main_category_desc='Arts & Humanities',
                            sub_category_desc='Music')
    category_obj.save()
    category_obj = Category(main_category=1001, sub_category=2007, main_category_desc='Arts & Humanities',
                            sub_category_desc='Performing Arts')
    category_obj.save()
    category_obj = Category(main_category=1001, sub_category=2008, main_category_desc='Arts & Humanities',
                            sub_category_desc='Human Rights')
    category_obj.save()
    category_obj = Category(main_category=1001, sub_category=2009, main_category_desc='Arts & Humanities',
                            sub_category_desc='Regional / Cultural')
    category_obj.save()
    category_obj = Category(main_category=1001, sub_category=2010, main_category_desc='Arts & Humanities',
                            sub_category_desc='Visual Arts')
    category_obj.save()


    # 2.Business & Management
    category_obj = Category(main_category=1002, sub_category=3001, main_category_desc='Business & Management',
                            sub_category_desc='Accounting')
    category_obj.save()
    category_obj = Category(main_category=1002, sub_category=3002, main_category_desc='Business & Management',
                            sub_category_desc='Economics')
    category_obj.save()
    category_obj = Category(main_category=1002, sub_category=3003, main_category_desc='Business & Management',
                            sub_category_desc='Entrepreneurship / Innovation')
    category_obj.save()
    category_obj = Category(main_category=1002, sub_category=3004, main_category_desc='Business & Management',
                            sub_category_desc='Finance / Banking')
    category_obj.save()
    category_obj = Category(main_category=1002, sub_category=3005, main_category_desc='Business & Management',
                            sub_category_desc='Industry Specific')
    category_obj.save()
    category_obj = Category(main_category=1002, sub_category=3006, main_category_desc='Business & Management',
                            sub_category_desc='Law')
    category_obj.save()
    category_obj = Category(main_category=1002, sub_category=3007, main_category_desc='Business & Management',
                            sub_category_desc='Leadership')
    category_obj.save()
    category_obj = Category(main_category=1002, sub_category=3008, main_category_desc='Business & Management',
                            sub_category_desc='Manufacturing')
    category_obj.save()
    category_obj = Category(main_category=1002, sub_category=3009, main_category_desc='Business & Management',
                            sub_category_desc='Marketing')
    category_obj.save()
    category_obj = Category(main_category=1002, sub_category=3010, main_category_desc='Business & Management',
                            sub_category_desc='Visual Arts')
    category_obj.save()

    # 3.Engineering
    category_obj = Category(main_category=1003, sub_category=4001, main_category_desc='Engineering',
                            sub_category_desc='Architecture / Civil')
    category_obj.save()
    category_obj = Category(main_category=1003, sub_category=4002, main_category_desc='Engineering',
                            sub_category_desc='Chemical')
    category_obj.save()
    category_obj = Category(main_category=1003, sub_category=4003, main_category_desc='Engineering',
                            sub_category_desc='Electrical / Electronic')
    category_obj.save()
    category_obj = Category(main_category=1003, sub_category=4004, main_category_desc='Engineering',
                            sub_category_desc='Environmental')
    category_obj.save()
    category_obj = Category(main_category=1003, sub_category=4005, main_category_desc='Engineering',
                            sub_category_desc='Mechanical / Industrial')
    category_obj.save()
    category_obj = Category(main_category=1003, sub_category=4006, main_category_desc='Engineering',
                            sub_category_desc='Military / Defense')
    category_obj.save()
    category_obj = Category(main_category=1003, sub_category=4007, main_category_desc='Engineering',
                            sub_category_desc='Oil / Gas')
    category_obj.save()
    category_obj = Category(main_category=1003, sub_category=4008, main_category_desc='Engineering',
                            sub_category_desc='Renewable')
    category_obj.save()
    category_obj = Category(main_category=1003, sub_category=4009, main_category_desc='Engineering',
                            sub_category_desc='Energy / Nuclear')
    category_obj.save()
    category_obj = Category(main_category=1003, sub_category=4010, main_category_desc='Engineering',
                            sub_category_desc='Transportation')
    category_obj.save()

    # 4.Life Science
    category_obj = Category(main_category=1004, sub_category=5001, main_category_desc='Life Science',
                            sub_category_desc='Anatomy')
    category_obj.save()
    category_obj = Category(main_category=1004, sub_category=5002, main_category_desc='Life Science',
                            sub_category_desc='Biotechnology')
    category_obj.save()
    category_obj = Category(main_category=1004, sub_category=5003, main_category_desc='Life Science',
                            sub_category_desc='Botany')
    category_obj.save()
    category_obj = Category(main_category=1004, sub_category=5004, main_category_desc='Life Science',
                            sub_category_desc='Ecology')
    category_obj.save()
    category_obj = Category(main_category=1004, sub_category=5005, main_category_desc='Life Science',
                            sub_category_desc='Food Science / Forestry')
    category_obj.save()
    category_obj = Category(main_category=1004, sub_category=5006, main_category_desc='Life Science',
                            sub_category_desc='Genetics')
    category_obj.save()
    category_obj = Category(main_category=1004, sub_category=5007, main_category_desc='Life Science',
                            sub_category_desc='Microbiology')
    category_obj.save()
    category_obj = Category(main_category=1004, sub_category=5008, main_category_desc='Life Science',
                            sub_category_desc=' Neuroscience')
    category_obj.save()
    category_obj = Category(main_category=1004, sub_category=5009, main_category_desc='Life Science',
                            sub_category_desc='Pathology / Toxicology')
    category_obj.save()
    category_obj = Category(main_category=1004, sub_category=5010, main_category_desc='Life Science',
                            sub_category_desc='Zoology')
    category_obj.save()


    # 5.Technology & Telecoms
    category_obj.save()
    category_obj = Category(main_category=1005, sub_category=6001, main_category_desc='Technology & Telecoms',
                            sub_category_desc='Artificial Intelligence')
    category_obj.save()
    category_obj = Category(main_category=1005, sub_category=6002, main_category_desc='Technology & Telecoms',
                            sub_category_desc='Computer / Informatics')
    category_obj.save()
    category_obj = Category(main_category=1005, sub_category=6003, main_category_desc='Technology & Telecoms',
                            sub_category_desc='Data Mining')
    category_obj.save()
    category_obj = Category(main_category=1005, sub_category=6004, main_category_desc='Technology & Telecoms',
                            sub_category_desc='Hardware / Equipment')
    category_obj.save()
    category_obj = Category(main_category=1005, sub_category=6005, main_category_desc='Technology & Telecoms',
                            sub_category_desc='Information Technology')
    category_obj.save()
    category_obj = Category(main_category=1005, sub_category=6006, main_category_desc='Technology & Telecoms',
                            sub_category_desc='Internet / Online Services')
    category_obj.save()
    category_obj = Category(main_category=1005, sub_category=6007, main_category_desc='Technology & Telecoms',
                            sub_category_desc='Robotics')
    category_obj.save()
    category_obj = Category(main_category=1005, sub_category='6008', main_category_desc='Engineering',
                            sub_category_desc='Software')
    category_obj.save()
    category_obj = Category(main_category=1005, sub_category=6009, main_category_desc='Engineering',
                            sub_category_desc='Telecommunication')
    category_obj.save()


    # 6.Medicine & Health
    category_obj.save()
    category_obj = Category(main_category=1006, sub_category=7001, main_category_desc='Medicine & Health',
                            sub_category_desc='Dentistry')
    category_obj.save()
    category_obj = Category(main_category=1006, sub_category=7002, main_category_desc='Medicine & Health',
                            sub_category_desc='Medical Speciality')
    category_obj.save()
    category_obj = Category(main_category=1006, sub_category=7003, main_category_desc='Medicine & Health',
                            sub_category_desc='Nursing')
    category_obj.save()
    category_obj = Category(main_category=1006, sub_category=7004, main_category_desc='Medicine & Health',
                            sub_category_desc='Nutrition / Sport')
    category_obj.save()
    category_obj = Category(main_category=1006, sub_category=7005, main_category_desc='Medicine & Health',
                            sub_category_desc='Pharmaceutical')
    category_obj.save()
    category_obj = Category(main_category=1006, sub_category=7006, main_category_desc='Medicine & Health',
                            sub_category_desc='Public Health')
    category_obj.save()
    category_obj = Category(main_category=1006, sub_category=7007, main_category_desc='Medicine & Health',
                            sub_category_desc='Rehabilitation / Therapy')
    category_obj.save()
    category_obj = Category(main_category=1006, sub_category=7008, main_category_desc='Medicine & Health',
                            sub_category_desc='Speech / Language')
    category_obj.save()
    category_obj = Category(main_category=1006, sub_category=7009, main_category_desc='Medicine & Health',
                            sub_category_desc='Veterinary')
    category_obj.save()

    # ************************************Address Table*******************************************
    address_obj =  address(city='London', country='United Kingdom', phone='9876543215')
    address_obj.save()
    address_obj = address(city='Amsterdam', country='Netherlands', phone='9876543215')
    address_obj.save()
    address_obj = address(city='THESSALONIKI', country='Greece', phone='9876543215')
    address_obj.save()
    address_obj = address(city='Lisbon', country='Portugal', phone='9876543215')
    address_obj.save()
    address_obj = address(city='Moscow', country='Russia', phone='9876543215')
    address_obj.save()
    address_obj = address(city='New Delhi', country='India', phone='9876543215')
    address_obj.save()
    address_obj = address(city='Macau', country='China', phone='9876543215')
    address_obj.save()
    address_obj = address(city='Warsaw', country='Poland', phone='9876543215')
    address_obj.save()
    address_obj = address(city='Kyoto', country='Japan', phone='9876543215')
    address_obj.save()
    address_obj = address(city='Osaka', country='Japan', phone='9876543215')
    address_obj.save()
    address_obj = address(city='Mumbai', country='India', phone='9876543215')
    address_obj.save()
    address_obj = address(city='Texas', country='US', phone='9876543215')
    address_obj.save()

    #***************************************Conference Table****************************************
    conf_obj = conference(name = 'PEDIATRICS 2020',
        main_category = 1001,
        sub_category = 2001,
        conf_ownerId = 1,
        paper_Accepted = 0,
        conf_loc_id_id = 1,
        conf_deadline = '2020-04-06',
        description = '17th World Congress on Pediatrics and Neonatology 2020',
        about = 'Pediatrics 2020 welcomes attendees, presenters, and exhibitors from all over the world to Japan. We are delighted to invite you all to attend and register for the Pediatrics conference “17th World Congress on Pediatric and Neonatology” which is going to be held during April 20-21, 2020 at Tokyo, Japan which divulges the evolution in Pediatrics and Neonatology for a healthy future. Make memories and share your views in this wonderful platform which is loaded with bundle of opportunities and moments to capture',
        conf_Submission_date = '2020-03-06',
        conf_start_date = '2020-04-20',
        conf_end_date = '2020-04-20' )
    conf_obj.save()

    conf_obj = conference(name='ICTEL2020',
                          main_category=1001,
                          sub_category=2002,
                          conf_ownerId=1,
                          paper_Accepted=0,
                          conf_loc_id_id=2,
                          conf_deadline='2020-04-06',
                          description = '15th ICTEL 2020 – International Conference on Teaching, Education & Learning, 10-11 August, Amsterdam',
                          about = 'Conference Name: 15th ICTEL 2020 – International Conference on Teaching, Education & Learning, 10-11 August, Amsterdam Conference Dates: 10-11 August 2020 Conference Venue: NH Hotel Amsterdam-Zuid, Van Leijenberghlaan 221, 1082 GG Amsterdam Deadline for Abstract/Paper Submissions: 08 August 2020 Contact E-Mail ID: convener@eurasiaresearch.info Organising Scholarly Association: Teaching & Education Research Association (TERA) TERA President: Dr. Brenda B. Corpuz, Dean, College of Education Technological Institute of the Philippines, Philippines Conference Language: English Conference Themes: Teaching, Education & Learning',
                          conf_Submission_date = '2020-03-06',
                          conf_start_date = '2020-04-20',
                          conf_end_date = '2020-04-20' )
    conf_obj.save()

    conf_obj = conference(name='ECIE 2020',
                          main_category=1002,
                          sub_category=3002,
                          conf_ownerId=2,
                          paper_Accepted=0,
                          conf_loc_id_id=3,
                          conf_deadline='2020-04-06',
                          description='15th European Conference on Innovation and Entrepreneurship 2020',
                          about= 'The European Conference on Innovation and Entrepreneurship has been running now for 15 years. This event has been held in Northern Ireland, France, Belgium, Portugal, and Finland to mention some of the countries who have hosted it. The conference is generally attended by participants from more than 40 countries and attracts an interesting combination of academic scholars, practitioners and individuals who are engaged in various aspects of innovation and entrepreneurship teaching and research. For the 6th consecutive year, ECIE hosts the final round The Innovation & Entrepreneurship Teaching Excellence Awards.',
                          conf_Submission_date='2020-03-06',
                          conf_start_date='2020-04-20',
                          conf_end_date='2020-04-20')
    conf_obj.save()

    conf_obj = conference(name='EAR20ROME CONFERENCE',
                          main_category=1002,
                          sub_category=3004,
                          conf_ownerId=2,
                          paper_Accepted=0,
                          conf_loc_id_id=4,
                          conf_deadline='2020-04-06',
                          description='19th European Academic Research Conference on Global Business, Economics, Finance & Management Sciences 2020',
                          about='Best Paper, Best Presenter and Best Posters Awards! A 10% Group Discount on the ‘registration fee’ available for a group comprising three members. A 5% discount is applicable for those who register and complete conference fee payment on or before the deadline – May 10, 2020 (The discount offers are not applicable to one day attendance). For more details please visit: www.globalbizresearch.org E-mail: italyconf@globalbizresearch.org Conference link: http://globalbizresearch.org/Rome_Conference_2020_Jul2/',
                          conf_Submission_date='2020-03-06',
                          conf_start_date='2020-04-20',
                          conf_end_date='2020-04-20')
    conf_obj.save()

    conf_obj = conference(name='RISK ANALYSIS 2020',
                          main_category=1003,
                          sub_category=4001,
                          conf_ownerId=3,
                          paper_Accepted=0,
                          conf_loc_id_id=5,
                          conf_deadline='2020-04-06',
                          description='12th International Conference on Risk Analysis and Hazard Mitigation 2020',
                          about='The conference covers a series of important topics of current research interests and many practical applications. It is concerned with all aspects of Risk Analysis and hazard mitigation, associated with both natural and anthropogenic hazards.',
                          conf_Submission_date='2020-03-06',
                          conf_start_date='2020-04-20',
                          conf_end_date='2020-04-20')
    conf_obj.save()

    conf_obj = conference(name='ICPEAM2020',
                          main_category=1003,
                          sub_category=4002,
                          conf_ownerId=3,
                          paper_Accepted=0,
                          conf_loc_id_id=6,
                          conf_deadline='2020-04-06',
                          description='International Conference on Process Engineering and Advanced Materials 2020',
                          about='The Chemical Engineering Department, Universiti Teknologi PETRONAS (UTP) is pleased to announce the International Conference on Process Engineering and Advanced Materials (ICPEAM2020) to be held in Sarawak, Malaysia, from 14 to 16 July 2020. The IR 4.0 entails the integration of digital, physical and biological systems and it is evolving at an exponential rate. ICPEAM2020 will serve as the intersection of industrial expertise, engineers, scientists, academicians and scholars to disseminate the latest findings from their areas of expertise that embrace the “Sustainable Future: The Inevitable Change',
                          conf_Submission_date='2020-03-06',
                          conf_start_date='2020-04-20',
                          conf_end_date='2020-04-20')
    conf_obj.save()

    conf_obj = conference(name='DENTAL SCIENCE 2020',
                          main_category=1006,
                          sub_category=7001,
                          conf_ownerId=3,
                          paper_Accepted=0,
                          conf_loc_id_id=7,
                          conf_deadline='2020-04-06',
                          description='11th International Conference on Dental Science and Advanced Dentistry 2020',
                          about='11th International Conference on Dental Science and Advanced Dentistry will be an inventive and helpful universal social event reflecting the heading of worldwide meetings on Dental and Oral health and offers a broad assortment of redirection to individuals from all foundations. The conference is on August 24-25, 2020 at Berlin, Germany based on the topic “Advanced Research & Future of Dental Science -Education and Practice”.',
                          conf_Submission_date='2020-03-06',
                          conf_start_date='2020-04-20',
                          conf_end_date='2020-04-20')
    conf_obj.save()

    conf_obj = conference(name='(ICOPH 2020)',
                          main_category=1006,
                          sub_category=7002,
                          conf_ownerId=3,
                          paper_Accepted=0,
                          conf_loc_id_id=8,
                          conf_deadline='2020-04-06',
                          description='6th International Conference on Public Health 2020',
                          about='WELCOME TO PUBLIC HEALTH 2020, Public Health Conference 2020 will facilitate discussions on a wide range of topics related to improving health at all levels through collaboration and open dialogue and steering tomorrow’s agenda to improve research, education, healthcare, and policy outcomes. So mark your calendars to attend the 6th International Conference Public Health 2020. If you would like to present, start by submitting a abstract now. View the Call for Papers here as well as Step-by-Step guide to submitting the abstract.',
                          conf_Submission_date='2020-03-06',
                          conf_start_date='2020-04-20',
                          conf_end_date='2020-04-20')
    conf_obj.save()

    conf_obj = conference(name='ICSGCE 2020',
                          main_category=1005,
                          sub_category=6001,
                          conf_ownerId=2,
                          paper_Accepted=0,
                          conf_loc_id_id=9,
                          conf_deadline='2020-04-06',
                          description='2020 (8th) International Conference on Smart Grid and Clean Energy Technologies (ICSGCE 2020)',
                          about='Publication： 1. All papers registered to ICSGCE will be included in the Proceedings of ICSGCE 2020 which will be submitted to IEEE and reviewed by the IEEE Conference Publication Program for publication in IEEE Xplore. 2. Alternatively, the authors can select to publish their papers in IJEETC (International Journal of Electrical and Electronic Engineering & Telecommunications) which is a SCOPUS indexed journal. 3. All papers registered to Special Session on EET will be published by Journal of Electronic Science and Technology (JEST, ISSN: 1674-862X) which is indexed by Scopus and EI INSPEC.',
                          conf_Submission_date='2020-03-06',
                          conf_start_date='2020-04-20',
                          conf_end_date='2020-04-20')
    conf_obj.save()

    conf_obj = conference(name='ISSM 2020',
                          main_category=1005,
                          sub_category=6002,
                          conf_ownerId=2,
                          paper_Accepted=0,
                          conf_loc_id_id=10,
                          conf_deadline='2020-04-06',
                          description='2020 2nd International Conference on Information System and System Management (ISSM 2020)',
                          about='Proceedings Submitted papers will be Peer-Reviewed (Double blind, and conducted by the technical program committee) and the accepted ones will be published in the conference proceedings, which will be submitted for indexing in Ei Compendex, Scopus, IET etc. major databases.',
                          conf_Submission_date='2020-03-06',
                          conf_start_date='2020-04-20',
                          conf_end_date='2020-04-20')
    conf_obj.save()

    conf_obj = conference(name='HEART CONGRESS 2020',
                          main_category=1004,
                          sub_category=4001,
                          conf_ownerId=2,
                          paper_Accepted=0,
                          conf_loc_id_id=11,
                          conf_deadline='2020-04-06',
                          description='World Congress on Heart Diseases 2020',
                          about='Heart Congress invites all the participants across the world to attend World Congress on Heart Diseases to be held during July 27-28, 2020 in Madrid, Spain which includes prompt keynote presentations, Oral talks, e-Poster presentations, Young Research Forum(YRF) and Exhibitions.',
                          conf_Submission_date='2020-03-06',
                          conf_start_date='2020-04-20',
                          conf_end_date='2020-04-20')
    conf_obj.save()

    conf_obj = conference(name='ANALYTICON-2020',
                          main_category=1004,
                          sub_category=4002,
                          conf_ownerId=2,
                          paper_Accepted=0,
                          conf_loc_id_id=12,
                          conf_deadline='2020-04-06',
                          description='2nd Analytical and Bioanalytical Methods Conference (exi) S 2020',
                          about='Our aim is to bridge the gap between renowned academicians, industrialists and upcoming researchers and provide a common platform to amalgamate experience, wisdom and vision from experts from which all attendees can benefit. We welcome all participants worldwide and encourage sharing of knowledge through oral/poster presentations, symposiums and networking sessions. Conference Registration clicks here https://www.eventbrite.com/e/2nd-analytical-and-bioanalytical-methods-conference-exi-s-tickets-74250239465',
                          conf_Submission_date='2020-03-06',
                          conf_start_date='2020-04-20',
                          conf_end_date='2020-04-20')
    conf_obj.save()

    return HttpResponse("Data Created")