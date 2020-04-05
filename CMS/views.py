from django.shortcuts import render
from .models import address, user_table, Category, conference, conference_itemTable, skill, comment

# Create your views here.
def paper_view_service(request):
    conference_itemTable_obj    = conference_itemTable.objects.get( paper_id = 1)
    conference_obj              = conference.objects.get(conf_id = conference_itemTable_obj.conf_id_id )
    address_obj                 = address.objects.get(address_id = conference_obj.conf_loc_id_id)
    category_obj                = Category.objects.get( main_category = 1, sub_category = 1 )

    print('****************************')
    print(conference_obj.name)
    print(conference_obj.description)
    print(address_obj.city)
    print(address_obj.country)
    print(conference_obj.about)
    print(conference_itemTable_obj.status)
    print(conference_obj.main_category)
    print(conference_obj.sub_category)
    print(category_obj.main_category)
    print(category_obj.sub_category)


    return render(request, 'PaperView.html', {
        'ConferenceName'        : conference_obj.name,
        'ConferenceDescription' : conference_obj.description,
        'City'                  : address_obj.city,
        'Country'               : address_obj.country,
        'ConferenceAbout'       : conference_obj.about,
        'Status'                : conference_itemTable_obj.status,
        'MainCategory'          : category_obj.main_category_desc,
        'SubCategory'           : category_obj.sub_category_desc,
    })