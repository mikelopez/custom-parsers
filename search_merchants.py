from datetime import datetime
from settings import PRODUCT_VIEW
# Author - Marcos Lopez - dev@scidentify.info
def getmerchant(obj, mid):
  try:
    mer = obj.objects.get(mid=mid)
    merchant_logo = mer.get_short_merchant_logo()
    merchant_name = mer.name
  except obj.DoesNotExist:
    #print 'NOT FOUND MID %s' % prs['merchantid'] # DEBUG
    mer = None
    merchant_logo = None
    merchant_name = None
  return mer, merchant_logo, merchant_name

def build_ls_response(tmplink_id, merchant_name, merchant_logo, data):
  """ build the linkshare response data dictionary to append to affiliated_products """
  d = {
        'id': None,
        'tmpurl_id': tmplink_id,
        'linkid': data['linkid'],
        'jump_url': data['linkurl'],
        'url': '/%s/%s' % (PRODUCT_VIEW, data['productname']),
        'amount': data['price'],
        'imgurl': data['imgurl'],
        'format_price': '$%s' % (data['price']),
        'merchant': merchant_name,
        'merchant_id': data['merchantid'],
        'merchant_logo_short': merchant_logo,
        'actual_name': data['productname'],
        'filter_name': data['productname'],
        'description': data['description_short'].replace('&gt;','').replace('&lt;',''),
        'description_long': data['description_long'].replace('&gt;','').replace('&lt;',''),
        'category': data['category_pri'],
        'wordscore': word_score(data['search_string'], data['productname'])
  }
  return d
  

def build_cj_response(tmplink_id, merchant_name, merchant_logo, data):
  d = {
        'id': None,
        'tmpurl_id': tmplink_id,
        'linkid': data['linkid'],
        'jump_url': data['buyurl'],
        'url': '/%s/%s' % (PRODUCT_VIEW, data['name']),
        'amount': data['price'],
        'imgurl': data['imageurl'],
        'format_price': '$%s'%(data['price']),
        'merchant': merchant_name,
        'merchant_id': data['advertiserid'],
        'merchant_logo_short': merchant_logo,
        'actual_name': data['name'],
        'filter_name': data['name'],
        'description': data['description'].replace('&gt;','').replace('&lt;',''),
        'description_long': data['description'].replace('&gt;','').replace('&lt;',''),
        'category': '',
        'wordscore': word_score(data['search_string'], data['name'])
  }
  return d

def word_score(searchstring, product_name):
  """ return count of how many times a word in search strin is found in title"""
  score = 0
  for i in searchstring.split(' '):
    try:
      if str(i.lower()) in str(product_name).lower():
        score += 1
    except UnicodeEncodeError:
      try:
        if i.lower() in product_name.lower():
          score += 1
      except:
        # fuck it, skip it, catchall!
        pass

  return score

def linkshare_search(request, search_string, obj_ls, AffiliateMerchants, TempRedirects, website):
  """ search through linkshare network for the search_string """
  try:
    page = int(request.GET.get('page', 1))
  except:
    page = 1
  # no break on pg 0
  print page
  if page < 1:
    print 'page less than 1'
    page = 1
  data = {}
  maxlimit = 25
  affiliated_products = []
  merchants_used = []
  ls = obj_ls(debugbool=True)
  ls.product_results = []
  ls.logtime = datetime.now()

  ls.SetParameter('MaxResults', maxlimit)
  ls.SetParameter('keyword', search_string)
  ls.SetParameter('pagenumber', page)
  #ls.SetParameter('sorttype', 'dsc')
  #ls.SetParameter('sort', 'retailprice')

  try:
    ls.FetchHTTP()
    ls.ProcessData()
    # if theres about 50 products, there might be a next page 
    if len(ls.product_results) == 0:
      pass
    if len(ls.product_results) > (maxlimit - 1):
      linkshare_next = True

    merchants_used = []
    full_count = len(ls.product_results)

    for prs in ls.product_results:
      # set search string in dict data to read from data building function above
      prs['search_string'] = search_string
      # get the merchant object
      mer, merchant_logo, merchant_name = getmerchant(AffiliateMerchants, prs['merchantid'])
      addit = False
      tmplink = TempRedirects(linkhref=prs['linkurl'], website=website)
      tmplink.save()
      affiliated_products.append(
          build_ls_response(tmplink.id, merchant_name, merchant_logo, prs)
      )
      if not prs['merchantid'] in merchants_used:
        merchants_used.append(prs['merchantid'])

  except UnicodeEncodeError:
    ls._process_log('UnicodeEncodeError on fetchhttp with key %s' % (l.urldata_dict))
    ls.product_results = []
  return affiliated_products, merchants_used





def cj_search(request, search_string, obj_cj, AffiliateMerchants, TempRedirects, website):
  """ search cj for product searched on get or post """
  try:
    page = int(request.GET.get('page', 1))
  except:
    page = 1
  # no break on pg 0
  print page
  if page < 1:
    print 'page less than 1'
    page = 1

  maxlimit = 25
  merchants_used = []
  affiliated_products = []

  cj = obj_cj(debugbool=True, website_id=website.cj_id)
  cj.cj_SetKeyword(search_string)
  #cj.cj_urldata_dict['sort-by'] = 'Price'
  #cj.cj_urldata_dict['sort-order'] = 'desc'
  cj.cj_urldata_dict['page-number'] = page
  cj.cj_urldata_dict['records-per-page'] = maxlimit
  cj.cj_fetch()
  prs = ''
  for prs in cj.cj_product_results:
    # set search string in dict data to read from data building function above
    prs['search_string'] = search_string
    # get merchant object
    mer, merchant_logo, merchant_name = getmerchant(AffiliateMerchants, prs['advertiserid'])
    tmplink = TempRedirects(linkhref=prs['buyurl'], website=website)
    tmplink.save()
    affiliated_products.append(
        build_cj_response(tmplink.id, merchant_name, merchant_logo, prs)
    )
    if not prs['advertiserid'] in merchants_used:
      merchants_used.append(prs['advertiserid'])
    
  return affiliated_products, merchants_used
