from lxml import html
import feedparser
# Author - Marcos Lopez - dev@scidentify.info

class RSSParse(object):

  data = ''
  return_data = []
  

  def __init__(self, url):
    """
    Parse the differnt kinds of structure sfor RSS feed
    and return back in consistent form for the site to fuck with
    """
    self.data = feedparser.parse(url)

  def parse_dict(self):
    try:
      merchantimg_dict = self.data.feed.image.href
    except (AttributeError, KeyError):
      merchant_img = 'no-img'

    html_rows = []
    
    parse_text = None
    for i in self.data.entries:
      try:
        parse_text = i.summary
      
        try:
          html_parse = html.fromstring(parse_text)
        except:
          html_parse = None
      except AttributeError:
        html_parse = None

      html_image = None
      html_link = i.link
      html_title = i.title
  
      # try to overwtite with summary_detail which contains more info
      try:
        val = i.summary_detail['value']
        if '$' in val:
          html_title = html.fromstring(val).text_content()
          if '$' in i.title and len(i.title) > len(html_title):
            html_title = i.title

      except AttributeError:
        html_title = i.title
      
      

      if html_parse is not None:
        if len(html_parse.cssselect('img')) > 0:
          for img in html_parse.cssselect('img'):
            html_image = img.get('src')


        if not html_image:
          if len(html_parse.cssselect('img')) > 0:
            for img in html_parse.cssselect('img'):
              html_image = img.get('src')
      

      if not html_image:
        try:
          html_image = i.enclosures[0].href
        except (KeyError, AttributeError, IndexError):
          html_image = None
  
      # parse out the date somehow
      for spaces in html_title.split(' '):
        splitter = None
        if '/' in spaces:
          splitter = '/'
        elif '-' in spaces:
          splitter = '-'
        else:
          expires = 'n'
          end_date_month = ''
          end_date_day = ''

        if splitter:
          expires = 'y'
          try:
            end_date_month = str(spaces).split(splitter)[0]
          except:
            end_date_month = ''
          try:
            end_date_day = str(spaces).split(splitter)[1]
          except:
            end_date_day = ''



      # try to get the price out too
      price = ''
      for spaces in html_title.split(' '):
        if '$' in spaces and '.' in spaces:
          price = spaces.replace('$','').replace(',','').replace('-','')

      d = {
        'parse_text': parse_text,
        'html_parse': html_parse,
        'html_image': html_image,
        'html_link': html_link,
        'html_title': html_title,
        'price': price,
        'end_date_day': end_date_day,
        'end_date_month': end_date_month,
        'expires': 'expires',
      }
      html_rows.append(d)   

    return html_rows
    

  def parse(self):
    # get merchant image
    # i want to modify this to also return a dict containing the unique values incase i want to build 
    # the layout through the template instead of using data|safe
    try:
      merchantimg_dict = self.data.feed.image.href
    except (AttributeError, KeyError):
      merchant_img = 'no-img'

    html_rows = []

    for i in self.data.entries:
      parse_text = i.summary
      html_parse = html.fromstring(parse_text)
      html_image = None
      html_link = i.link
      html_title = i.title

      # check if summary contains some type of structure, non lazy devs!
      if '<table ' in i.summary:
        html_data = str(i.summary).replace('\n','').replace('<span>','').replace('</span>','').replace('<td width="10">','')
      else:
        # check if image is already in summary
        if len(html_parse.cssselect('img')) > 0:
          for img in html_parse.cssselect('img'):
            html_image = img.get('src')
  
        html_data = '<table border="1" cellpadding="1" cellspacing="1" width="100%"><tr>'
        if html_image:
          html_data += """
            <td valign="top"><a href="%s" target="_blank"><img src="%s" width="120" height="120" border="0"/></a></td>
          """ % (html_link, html_image)
        else:
          # check for the image in enclosures
          try:
            html_image = i.enclosures[0].href
            html_data += """
              <td valign="top"><a href="%s" target="_blank"><img src="%s" border="0" width="120" height="120"/></a></td>
            """ % (html_link, html_image)
          except (KeyError, AttributeError, IndexError):
            html_image = None

        html_data += """<td valign="top" style="padding-top:15px;">
            <a href="%s" target="_blank">%s</a></td>
        """ % ( html_link, html_title )
        html_data += "</tr></table>"



      html_rows.append(html_data)
    

    return html_rows
