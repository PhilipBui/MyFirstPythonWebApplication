'''
Created on 07/03/2012

@author: steve
'''

# define a page template - HTML text with %xxxx where we want
# content to be inserted by the generate_page procedure
PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <title>%title</title>
  </head>

  <body>

    %nav

     <h1>%title</h1>

    <div class="content">
      %content
    </div>


    <footer class='footer'>
    <hr>
        <p>Commentr is a class project for COMP249 at Macquarie University</p>

        <p>Copyright &copy; <a href="http://web.science.mq.edu.au/~cassidy/">Steve Cassidy</a>, 2013</p>
    </footer>

  </body>
</html>"""

def navigation(links):
    """Generate a set of navigation links enclosed in
    a UL element from a list of
    links, each link is a pair (url, text) which is
    turned into the HTML <a href="url">text</a>, each
    link is embedded in a <li> inside a <ul>
    Return the HTML as a string"""

    nav = "<ul class='nav'>\n"
    for link in links:
        nav += "<li><a href='%s'>%s</a></li>\n" % link
    nav += "</ul>\n"

    return nav

def quote_content(text):
    """Return a sanitised version of the text suitable for inclusion in
    an HTML page"""

    text = str(text)
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")

    return text

def generate_page(content, template=PAGE_TEMPLATE):
    """Generate an HTML page, for every
    key in the dictionary content, substitute the value
    whereever %key occurs.
    If there are any remaining %xxxx occurences in the
    page that have not been replaced, they should be
    removed.
    Return a string containing the generated HTML page"""

    import re
    page = template
    for key in content.keys():
        page = page.replace("%"+key, content[key])

    page = re.sub("%[a-z]+", "", page)

    return page


