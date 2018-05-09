# >>> CraigslistHousing.show_filters(category='apa')
# Base filters:
# * bundle_duplicates = True/False
# * search_titles = True/False
# * posted_today = True/False
# * has_image = True/False
# * query = ...
# * search_distance = ...
# * zip_code = ...
# Section specific filters:
# * min_bedrooms = ...
# * min_bathrooms = ...
# * max_bedrooms = ...
# * private_room = True/False
# * wheelchair_acccess = True/False
# * no_smoking = True/False
# * is_furnished = True/False
# * max_ft2 = ...
# * max_bathrooms = ...
# * min_ft2 = ...
# * cats_ok = True/False
# * min_price = ...
# * dogs_ok = True/False
# * private_bath = True/False
# * max_price = ...
# * laundry = u'w/d in unit', u'w/d hookups', u'laundry in bldg', u'laundry on site', u'no laundry on site'
# * housing_type = u'apartment', u'condo', u'cottage/cabin', u'duplex', u'flat', u'house', u'in-law', u'loft', u'townhouse', u'manufactured', u'assisted living', u'land'
# * parking = u'carport', u'attached garage', u'detached garage', u'off-street parking', u'street parking', u'valet parking', u'no parking'

from craigslist import CraigslistHousing
from slackclient import SlackClient
from utils import in_area, check_for_record, store_in_db
import settings

#get results from craiglist
cl_h = CraigslistHousing(site=settings.CL_SITE, area=settings.CL_AREA, category=settings.CL_CATEGORY,
                         filters={'bundle_duplicates': True,
                                  'posted_today': settings.POSTED_TODAY,
                                  'min_bedrooms': settings.MIN_NUM_BEDROOMS,
                                  'max_bedrooms': settings.MAX_NUM_BEDROOMS,
                                  'cats_ok': settings.CATS_OK,
                                  'max_price': settings.MAX_PRICE,
                                  'min_price': settings.MIN_PRICE,
                                  'laundry': settings.LAUNDRY_OPTIONS,
                                  'parking': settings.PARKING_OPTIONS,
                                  'housing_type': settings.HOUSING_TYPE
                                  })

for result in cl_h.get_results(sort_by='newest', geotagged=True):
    if check_for_record(result):
        continue
    else:
        geotag = result["geotag"]
        #set blank area
        area = ""
        for a, coords in settings.AREAS.items():
            if geotag is not None and in_area(geotag, coords):
                area = a
        #couldn't find from Geotag, string search the listing
        if area == "":
            # print settings.NEIGHBORHOODS
            for hood in settings.NEIGHBORHOODS:
                if hood in result["where"].lower():
                    area = hood
        if area != "":
            # print "Reached slack portion", result
            store_in_db(result)
            sc = SlackClient(settings.SLACK_TOKEN)
            desc = "{0} | {1} | {2} | <{3}>".format(area, result["price"], result["name"].encode('utf-8').strip(), result["url"])
            sc.api_call(
                "chat.postMessage", channel=settings.SLACK_CHANNEL, text=desc,
                username=settings.SLACK_BOT_NAME, icon_emoji=':robot_face:'
            )
