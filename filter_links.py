import re

# Author Marcos Lopez - dev@scidentify.info
def get_ls_offerid(link):
  try:
    r = re.search('offerid=([\w.-]+).([\w.-]+)&', str(link)).group()
    r = str(r).replace('offerid=','')
    if str(r)[-1] == '&':
      return str(r).replace('&','')
    else:
      return str(r)
  except AttributeError:
    return 'none'


def get_cj_offerid(link):
  try:
    r = re.search('click-([\w.-]+)-([\w.-]+)', str(link)).group()
    r = str(r).split('-')[-1]
    return str(r)
  except:
    return 'none'


def filter_link(Website, website, link_str, replace_id=None):
  # important, must have somewhere stored the websites that have been used with commission junction merchants
  # cause if not it will not replace the right values from teh link text
  cj = []
  for i in Website.objects.all():
    if i.cj_id:
      cj.append({'domain': i.domain, 'cj_id':i.cj_id})

  for i in cj:
    if website == i['domain']:
      # website matches, use this id
      use_cj_id = i['cj_id']
      
  if not replace_id:
    for i in cj:
      if not i['cj_id'] == use_cj_id:
        link_str = link_str.replace('click-%s' % (i['cj_id']), 'click-%s' % (use_cj_id))

  if replace_id:
    link_str = link_str.replace('click-%s' % (replace_id), 'click-%s' % (use_cj_id))
  return link_str
