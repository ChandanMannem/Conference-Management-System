from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import  Value as V
from django.contrib.auth import login

from .models import address,Category, conference, conference_itemTable, skill, comment
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import  UserCreateForm
import datetime
from django.db.models import Q
from django.core.files.storage import FileSystemStorage


# Create your views here.
def paper_view_service(request, paperId):
    paper_status = {
        '1': 'Abstract Not Submitted!',
        '2': 'Abstract Submitted',
        '3': 'Reviewer Assigned',
        '4': 'Reviewer Accepted',
        '5': 'Abstract Accepted',
        '6': 'Abstract Rejected',
        '7': 'Paper Submitted'
    }

    if request.method == 'POST':
        print('Printing---------------->', request.POST)
        conf_get_obj = conference_itemTable.objects.filter( Q(paper_id=paperId) , Q(reviewer1_id = request.user.id) | Q(reviewer2_id = request.user.id))
        comment_obj  = comment.objects.filter(user_id_id = request.user.id, paper_id_id=paperId)
        for list in conf_get_obj:
            if(list.reviewer1_id == request.user.id or list.reviewer2_id == request.user.id):
                conf_get_obj = list
                break
        if "action_resubmit" in request.POST:
            print('In Resubmit')
            uploaded_file = request.FILES['file']
            print('Inside post function', uploaded_file)
            fs = FileSystemStorage()
            name = fs.save(uploaded_file.name, uploaded_file)
            url = fs.url(name)
            conf_get_obj = conference_itemTable.objects.get(paper_id = paperId, user_id_id = request.user.id)
            conf_get_obj.pdf_link = url
            conf_get_obj.entry_date = datetime.datetime.now().date()
            conf_get_obj.save()
            page = "".join(['/cms/paperview/', str(conf_get_obj.paper_id)])
            return redirect(page)

        elif "action_accept" in request.POST:
            print('In Action Accept')

            if conf_get_obj.reviewer1_id == request.user.id:
                print('Inside If condition')
                conf_get_obj.reviewer1_status = '1'        # 1 for Accept, 2 for Reject
                comment_obj = comment(user_id_id = request.user.id, paper_id_id   = paperId,
                                      comment=request.POST['TextArea_1'] )

            if conf_get_obj.reviewer2_id == request.user.id:
                conf_get_obj.reviewer2_status = '1'        # 1 for Accept, 2 for Reject
                comment_obj = comment(user_id_id=request.user.id, paper_id_id=paperId,
                                      comment=request.POST['TextArea_1'])

            if conf_get_obj.reviewer1_status == '1' and conf_get_obj.reviewer2_status == '1':
                conf_get_obj.status = '4'

            conf_get_obj.save()
            comment_obj.save()
            page = "".join(['/cms/paperview/', str(paperId)])
            return redirect(page)

        elif "action_reject" in request.POST:
            print("Action Reject")
            if conf_get_obj.reviewer1_id == request.user.id:
                conf_get_obj.reviewer1_status = '2'  # 1 for Accept, 2 for Reject
                comment_obj = comment(user_id_id=request.user.id, paper_id_id=paperId,
                                      comment=request.POST['TextArea_1'])
                conf_get_obj.status = '6'

            if conf_get_obj.reviewer2_id == request.user.id:
                conf_get_obj.reviewer2_status = '2'  # 1 for Accept, 2 for Reject
                comment_obj = comment(user_id_id=request.user.id, paper_id_id=paperId,
                                      comment=request.POST['TextArea_1'])
                conf_get_obj.status = '6'

            conf_get_obj.save()
            comment_obj.save()
            page = "".join(['/cms/paperview/', str(paperId)])
            return redirect(page)
        else:
            return redirect('error')
    else:
        if request.user.is_authenticated:
            conference_itemTable_obj    = conference_itemTable.objects.get( paper_id = paperId)
            conference_obj              = conference.objects.get(conf_id = conference_itemTable_obj.conf_id_id )
            address_obj                 = address.objects.get(address_id = conference_obj.conf_loc_id_id)
            category_obj                = Category.objects.get( main_category = conference_obj.main_category ,
                                                                sub_category = conference_obj.sub_category )
            comments_obj                = comment.objects.filter(paper_id_id = paperId)
            grp_obj = request.user.groups.get()
            print("grp_obj-------->", grp_obj.id)
            role = grp_obj.id
            if grp_obj.id == 3:                        # Author
                ResubmitButton = False
                if conference_itemTable_obj.reviewer1_id == 0 and conference_itemTable_obj.reviewer2_id  == 0:
                    ResubmitButton = True
                ActionButton   = False
                R1_Box = False
                R2_Box = False
                R1_TEXT = ''
                R2_TEXT = ''

                length = len(comments_obj)
                if length == 0:
                    R2_TEXT = 'No comments from Reviewer 2 yet!'
                    R1_TEXT = 'No comments from Reviewer 1 yet!'
                    R1_Box = True
                    R2_Box = True
                else:
                    for item in comments_obj:
                        if (length == 1):
                            R2_TEXT = item.comment
                            R2_Box = True
                            break
                        else:
                            R1_TEXT = item.comment
                            length = length - 1
                            R1_BOX = True


            elif grp_obj.id == 2:                      # Reviewer
                ResubmitButton = False
                ActionButton   = False
                R1_TEXT = ''
                R2_TEXT = ''

                # Action Button
                if conference_itemTable_obj.reviewer1_id == request.user.id and conference_itemTable_obj.reviewer1_status == '':
                    ActionButton   = True
                    print('Action1')
                if conference_itemTable_obj.reviewer2_id == request.user.id and conference_itemTable_obj.reviewer2_status == '':
                    ActionButton   = True
                    print('Action2')

                R1_Box         = True
                R2_Box         = False
                comments_obj = comment.objects.filter(paper_id_id=paperId, user_id_id= request.user.id)
                for item in comments_obj:
                    R1_TEXT = item.comment
                    R1_BOX = True
                    break

            else:                                     # Chairperson
                ResubmitButton = False
                ActionButton   = False
                R1_Box = False
                R2_Box = False
                R1_TEXT = ''
                R2_TEXT = ''

                length = len(comments_obj)
                if length == 0:
                    R2_TEXT = 'No comments from Reviewer 2 yet!'
                    R1_TEXT = 'No comments from Reviewer 1 yet!'
                    R1_Box = True
                    R2_Box = True
                else:
                    for item in comments_obj:
                        if (length == 1):
                            R2_TEXT = item.comment
                            R2_Box = True
                            break
                        else:
                            R1_TEXT = item.comment
                            length = length - 1
                            R1_BOX = True


            days = (conference_obj.conf_start_date - datetime.datetime.now().date()).days
            DaysDesc = ' '
            if days >= 0:
                DaysDesc = " ".join([str(days), 'days until the conference begins'])
            else:
                DaysDesc = 'This conference is ended'

            print("Resubmit Button---->",ResubmitButton)
            print("Action Butoon------>", ActionButton)
            return render(request, 'PaperView.html', {
                'ConferenceName'        : conference_obj.name,
                'ConferenceDescription' : conference_obj.description,
                'City'                  : address_obj.city,
                'Country'               : address_obj.country,
                'ConferenceAbout'       : conference_obj.about,
                'Status'                : paper_status[conference_itemTable_obj.status],
                'MainCategory'          : category_obj.main_category_desc,
                'SubCategory'           : category_obj.sub_category_desc,
                'conf_start_date'       : conference_obj.conf_start_date,
                'conf_end_date'         : conference_obj.conf_end_date,
                'DaysDesc'              : DaysDesc,
                'ResubmitButton'        : ResubmitButton,
                'ActionButton'          : ActionButton,
                'R1_Box'                : R1_Box,
                'R2_Box'                : R2_Box,
                'paper_link'            : conference_itemTable_obj.pdf_link[11:],
                'R1_TEXT'               : R1_TEXT,
                'R2_TEXT'               : R2_TEXT,
                'role'                  : role
            })
        else:
            return redirect('error')

def conf_view(request, confId):

    if request.method == 'POST':
        conf_item_obj = conference_itemTable.objects.filter(user_id=request.user.id, conf_id=confId)
        error = 0
        for item in conf_item_obj:
            if item.pdf_link == " ":
                error = 1
                conf_item_obj = item
                break;
        if error != 1:
            uploaded_file= request.FILES['file']
            print('Inside post function', uploaded_file)
            fs = FileSystemStorage()
            name = fs.save(uploaded_file.name, uploaded_file)
            url = fs.url(name)
            # conf_get_obj = conference_itemTable.objects.filter(user_id = request.user.id, conf_id = confId )
            if len(conf_item_obj) == 0:
                conf_item_obj = conference_itemTable( user_id_id  = request.user.id, conf_id_id = confId, status = 2, description = 'Uploaded',
                                         reviewer1_id = 0, reviewer2_id= 0, pdf_link  = url, entry_date = datetime.datetime.now().date() )

                conf_item_obj.save()
                print('Inside If', conf_item_obj.paper_id)
            else:
                print('Inside else', len(conf_item_obj))
                for item in conf_item_obj:
                    item.pdf_link = url
                    item.entry_date = datetime.datetime.now().date()
                    # item.save()
                    conf_item_obj = item
                    break
        # page =  "".join(['/cms/paperview/', str(item.paper_id)])
            # print('Length of conf_item->', len(conf_item_obj))
        if conf_item_obj.paper_id != 0:
            return redirect('/cms/paperview/' + str(conf_item_obj.paper_id))
        else:
            return HttpResponse("<h1>You don't have any active papers for this conference <h1>")
    else:

        conference_obj = conference.objects.get(conf_id=confId)
        address_obj = address.objects.get(address_id=conference_obj.conf_loc_id_id)
        category_obj = Category.objects.get(main_category=conference_obj.main_category, sub_category=conference_obj.sub_category)

        days = (conference_obj.conf_start_date - datetime.datetime.now().date()).days
        DaysDesc = ' '
        if days >= 0:
            DaysDesc = " ".join([str(days), 'days until the conference begins'])
        else:
            DaysDesc = 'This conference is ended'


        if request.user.is_authenticated:

            grp_obj = request.user.groups.get()
            subtractDate = datetime.timedelta(60)
            button = False
            if grp_obj.id == 3:           # Author
                conf_get_obj = conference_itemTable.objects.filter(user_id=request.user.id, conf_id=confId)
                if len(conf_get_obj) == 0:
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
                'acceptance_date'       : conference_obj.conf_Submission_date - subtractDate
            })
        else:
            button = False
            subtractDate = datetime.timedelta(60)
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
                'acceptance_date': conference_obj.conf_Submission_date - subtractDate
            })


def paper_list(request, confId):
    paper_status = {
        '1': 'Abstract Not Submitted!',
        '2': 'Abstract Submitted',
        '3': 'Reviewer Assigned',
        '4': 'Reviewer Accepted',
        '5': 'Abstract Accepted',
        '6': 'Abstract Rejected',
        '7': 'Paper Submitted'
    }

    if request.method == 'POST':
        print('*****************************',request.POST)
        if 'action_button' in request.POST:
            conf_get_obj = conference_itemTable.objects.get(paper_id= int(request.POST['paper_id']))
            if request.POST['action'] == '1':
                conf_get_obj.status = '5'
            if request.POST['action'] == '2':
                conf_get_obj.status = '6'
            conf_get_obj.save()
            page = "".join(['/cms/paperlist/', str(conf_get_obj.conf_id_id)])
            return redirect(page)

        elif 'submit' in request.POST:
            conf_get_obj = conference_itemTable.objects.get(paper_id=int(request.POST['paper_id']))
            action = request.POST['action']
            print('********************', len(action))
            if len(action) == 1:
                conf_get_obj.status = '3'
                if conf_get_obj.reviewer1_id == 0 and conf_get_obj.reviewer2_id == 0:
                    conf_get_obj.reviewer1_id = int(action)
                    conf_get_obj.reviewer1_status = ''
                    conf_get_obj.reviewer2_status = ''
                    conf_get_obj.save()
                else:
                    if conf_get_obj.reviewer1_id == int(action):
                        conf_get_obj.reviewer2_id = 0
                        conf_get_obj.reviewer2_status = ''
                        conf_get_obj.save()

                    if conf_get_obj.reviewer2_id == int(action):
                        conf_get_obj.reviewer1_id = 0
                        conf_get_obj.reviewer1_status = ''
                        conf_get_obj.save()
            else:
                [reviewer1, reviewer2] = action.split(',')
                conf_get_obj.status = '3'
                print('-----------------------------------------------------------------------------')
                print(reviewer1, reviewer2)
                if conf_get_obj.reviewer2_status == '' and conf_get_obj.reviewer1_status == '':
                    print('Inside 1st if condition')
                    conf_get_obj.reviewer1_id = int(reviewer1)
                    conf_get_obj.reviewer2_id = int(reviewer2)
                    print('Conference get object------>', conf_get_obj)
                    conf_get_obj.save()

                else:

                    if conf_get_obj.reviewer1_status != '' and conf_get_obj.reviewer2_status == '':
                        print('Inside else 1 condition')
                        conf_get_obj.reviewer2_id = int(reviewer1)
                        conf_get_obj.save()
                    else:
                        print('Inside else 2 condition')
                        conf_get_obj.reviewer1_id = int(reviewer1)
                        conf_get_obj.save()

            page = "".join(['/cms/paperlist/', str(conf_get_obj.conf_id_id)])
            return redirect(page)
        else:
            return redirect(error)
    else:
        print('Group object')
        grp_obj = request.user.groups.get()
        print('Group object---->', grp_obj.id)
        if  grp_obj.id == 1 or grp_obj.id == 2:
            conference_obj = conference.objects.get(conf_id=confId)
            skill_obj      = skill.objects.filter( skill_category = conference_obj.main_category )
            action = False
            conference_itemTable_obj = []
            if grp_obj.id == 1:            # Chairperson
                conference_itemTable_obj = conference_itemTable.objects.filter( conf_id_id  = confId )
                action = True
            elif grp_obj.id == 2:          # Reviewer
                conference_itemTable_obj = conference_itemTable.objects.filter( Q(conf_id_id  = confId), Q(reviewer1_id = request.user.id) | Q(reviewer2_id = request.user.id) )

            paperlist = []
            for item in conference_itemTable_obj:
                paper = {}
                try:
                    user_obj = User.objects.get(id = item.user_id_id)
                    paper['name'] = " ".join([user_obj.first_name, user_obj.last_name])
                except User.DoesNotExist:
                    paper['name'] = " "

                paper['paper_id'] = item.paper_id
                paper['user_id']  = item.user_id_id
                paper['status']   = paper_status[item.status]
                paper['entry_date'] = item.entry_date
                paper['link']       ='/cms/paperview/' + str(item.paper_id)

                if item.status == '5':
                    paper['action_status'] = 1
                    paper['action_disable'] = True
                elif item.status == '6':
                    paper['action_status'] = 2
                    paper['action_disable'] = True
                else:
                    paper['action_status'] = 0
                    paper['action_disable'] = False

                if int(item.status) >= 4 :
                    paper['reviewer_disable'] = True
                else:
                    paper['reviewer_disable'] = False
                paper['r1'] = item.reviewer1_id
                paper['r2'] = item.reviewer2_id
                paperlist.append(paper)

            print('PaperList--->', paperlist)
            return render(request, 'PaperList.html', {
                'ConferenceName': conference_obj.name,
                'ConferenceDescription': conference_obj.description,
                'paperlist':paperlist,
                'reviewer_list': skill_obj,
                'action' : action
            })
        else:
            return redirect(error)


def conferences_view(request, past_conferences=None, category=None):
    order_by = request.GET.get('order_by')
    category_obj = Category.objects.all()
    main_category_list = category_obj.distinct('main_category')
    if past_conferences is None:
        conference_obj = conference.objects.filter(conf_start_date__gte=datetime.datetime.now())
        if order_by is not None:
            conference_obj = order_conferences(order_by, conference_obj)
        if category is not None:
            category_conferences_obj = category_conferences(category, order_by, conference_obj)
            conference_obj = category_conferences_obj['conference_obj']
            category = category_conferences_obj['category']
    else:
        conference_obj = conference.objects.filter(conf_start_date__lt=datetime.datetime.now())
        if category is not None:
            conference_obj = conference.objects.filter(conf_start_date__lt=datetime.datetime.now())
            category_conferences_obj = category_conferences(category, order_by, conference_obj)
            conference_obj = category_conferences_obj['conference_obj']
            category = category_conferences_obj['category']
        else:
            if order_by is not None:
                conference_obj = conference.objects.filter(conf_start_date__lt=datetime.datetime.now())
                conference_obj = order_conferences(order_by, conference_obj)
    for conferences in conference_obj:
        address_list = address.objects.annotate(location=Concat('city', V(','), 'country')).get(
            address_id=conferences.conf_loc_id_id)
        conferences.location = address_list.location
        category_list = category_obj.filter(main_category=conferences.main_category,
                                            sub_category=conferences.sub_category).first()
        conferences.parent_category = category_list.main_category_desc
        conferences.child_category = category_list.sub_category_desc
    if request.user.is_authenticated:
        user_grp = request.user.groups.get()
        grp_id = user_grp.id
    else:
        grp_id = 0
    return render(request, 'conference.html', {'conference_obj': conference_obj,
                                               'category': category,
                                               'main_category_list': main_category_list, 'order_by': order_by,
                                               'past_conferences': past_conferences, 'user_grp':grp_id})


def user_conferences(request, past_conferences=None, category=None):
    user = User.objects.get(id = request.user.id)
    order_by = request.GET.get('order_by')
    if request.user.is_authenticated:
        category_obj = Category.objects.all()
        conference_obj = {}
        if past_conferences is None:
            if user.groups.filter(name='Chairperson').exists():
                conference_obj = conference.objects.filter(conf_start_date__gte=datetime.datetime.now(),
                                                           conf_ownerId=request.user.id)
            elif user.groups.filter(name='Reviewer').exists():
                conference_obj_item = conference_itemTable.objects.filter(
                    Q(reviewer1_id=request.user.id) | Q(reviewer2_id=request.user.id))
                for conference_item in conference_obj_item:
                    conference_obj = conference.objects.filter(conf_start_date__gte=datetime.datetime.now(),
                                                               conf_id=conference_item.conf_id_id)
            elif user.groups.filter(name='Author').exists():
                conference_obj_item = conference_itemTable.objects.filter(user_id=request.user.id)
                for conference_item in conference_obj_item:
                    conference_obj = conference.objects.filter(conf_start_date__gte=datetime.datetime.now(),
                                                               conf_id=conference_item.conf_id_id)
        else:
            if user.groups.filter(name='Chairperson').exists():
                conference_obj = conference.objects.filter(conf_start_date__gte=datetime.datetime.now(),
                                                           conf_ownerId=request.user.id)
            elif user.groups.filter(name='Reviewer').exists():
                conference_obj_item = conference_itemTable.objects.filter(
                    Q(reviewer1_id=request.user.id) | Q(reviewer2_id=request.user.id))
                for conference_item in conference_obj_item:
                    conference_obj = conference.objects.filter(conf_start_date__gte=datetime.datetime.now(),
                                                               conf_id=conference_item.conf_id_id)
            elif user.groups.filter(name='Author').exists():
                conference_obj_item = conference_itemTable.objects.filter(user_id=request.user.id)
                print("inside filter", conference_obj_item)
                for conference_item in conference_obj_item:
                    conference_obj = conference.objects.filter(conf_start_date__gte=datetime.datetime.now(),
                                                               conf_id=conference_item.conf_id_id)
        main_category_list = category_obj.distinct('main_category')
        if category is not None:
            category_conferences_obj = category_conferences(category, order_by, conference_obj)
            conference_obj = category_conferences_obj['conference_obj']
            category = category_conferences_obj['category']
        if order_by is not None:
            conference_obj = order_conferences(order_by, conference_obj)
        for conferences in conference_obj:
            address_list = address.objects.annotate(location=Concat('city', V(','), 'country')).get(
                address_id=conferences.conf_loc_id_id)
            conferences.location = address_list.location
            category_list = category_obj.filter(main_category=conferences.main_category,
                                                sub_category=conferences.sub_category).first()
            conferences.parent_category = category_list.main_category_desc
            conferences.child_category = category_list.sub_category_desc
    else:
        return redirect('error')
    return render(request, 'conference.html', {'conference_obj': conference_obj,
                                               'category': category,
                                               'main_category_list': main_category_list})


def order_conferences(order_by: object, conference_obj) -> object:
    if order_by == 'alphabetical':
        conference_obj = conference_obj.filter().order_by('description')
    elif order_by == 'submission_deadline':
        conference_obj = conference_obj.filter().order_by(
            'conf_Submission_date')
    elif order_by == 'conference_start_date':
        conference_obj = conference_obj.filter().order_by(
            'conf_start_date')
    return conference_obj


def category_conferences(category: int, order_by: object, conference_obj: object) -> object:
    if order_by is not None:
        conference_obj = order_conferences(order_by, conference_obj)
    else:
        conference_obj = conference_obj.filter(main_category=category)
    category = Category.objects.distinct('main_category').get(main_category=category)
    return {'conference_obj': conference_obj, 'category': category}


def error(request):
    return render(request, 'error.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            my_group = Group.objects.get(name='Author')
            my_group.user_set.add(user)
            login(request, user)
            return HttpResponseRedirect("/cms/conferences/")
    else:
        form = UserCreateForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })


    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            #my_group = Group.objects.get(name='Author')
            #my_group.user_set.add(user)
            return redirect('conferences')
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