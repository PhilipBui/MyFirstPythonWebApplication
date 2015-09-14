'''
Created on Mar 26, 2012

@author: steve
'''

from wsgiref import simple_server
import database, interface, templating
import cgi
import urllib

            #CSS to be applied in every page.
css =       """
            <HEAD>
                <STYLE TYPE='text/css'>
                    *{
                        margin: 0;
                        padding: 0;
                    }
                    BODY {
                        width: 100%;
                        height: 100%; 
                        font-family: Verdana, Arial, Helvetica, sans-serif;
                        font-size: 100%;
                        color: #666666;
                        background-color: #C0C0C0;
                    }
                    H1, H2 {
                        text-align: center
                    }
                    H3, P{
                        text-align: left;
                    }
                    A:LINK, A:VISITED { 
                        color: #B07060; 
                        text-decoration: underline; 
                        font-weight: normal;
                    }   
                    
                    A:HOVER {
                        color: #000000;
                        text-decoration: none;
                        font-weight: normal;
                    }
                    TABLE {
                        width: 98%;
                        border-collapse: separate;
                        border:solid white 10px;
                        margin-left: auto;  
                        margin-right: auto;  
                        -moz-border-radius:6px;
                    }
                    TD, TH {
                        height: 90px;
                        padding: 5px;
                        color: #606060;
                        background-color: #FFFFFF;
                    }
                    TH {
                        height: 30px;
                        background-color: #E8E8E8;
                    }
                    
                    input {
                        width: 200px;
                        height: 30px;
                    }
                    input.signin {
                        width: 80px;
                        height: 40px;
                        color: #FFFFFF;
                        background-color: #404040;
                        border: none; 
                    }
                    input.title {
                        font-size: 300%;
                        width: 800px;
                        height: 60px;
                    }
                    textarea {
                        font-size: 200%;
                        width: 1200px;
                        height: 500px;
                    }
                    #container {  
                        width: 90%;
                        background-color: #F0F0F0;
                        margin-left: auto;  
                        margin-right: auto;  
                    }
                    
                    #topnav {
                        background-color: #404040; 
                        float: left;
                        width: 100%;
                     }  
                    #topnav UL {
                        list-style-type: none;
                    }
                    #topnav LI {
                        display: inline;
                        float: left;
                    }
                    #topnav A:LINK, #topnav A:VISITED {
                        color: #FFFFFF;
                        text-decoration: none;
                        display: block;
                        width: 200px;
                        padding: 10px;
                        text-align: center;
                    }
                    #topnav A:HOVER {
                        background-color: #606060;
                    }
                    .selected A:LINK, .selected A:HOVER, .selected A:VISITED {
                        color: #000080;
                        background-color: #808080;
                    }
                    .topright {
                        float: right;
                    }
                    #error TABLE, #error TD {
                        width: 75%;
                        color: #800018;
                        background-color: #F8D8D8;
                        border: solid #E898A8 0.5px;
                        margin-left: auto;  
                        margin-right: auto;
                    }
                    #error TD {
                        border: none;
                    }
                </STYLE>
            </HEAD>
            """
            
            # Login form used in some pages.
signin_form = """
                <BR><BR><BR><BR><BR>
                <TABLE><TR><TH><H3> Sign in </H3></TH></TR>
                <TR><TD> 
                <FORM NAME = "login" METHOD="post">
                     <P><B> Email: </B></P>
                     <INPUT NAME='username' PLACEHOLDER = 'Email' TITLE='Sign in with your Email'> 
                     <P><B> Password </B></P>
                     <INPUT NAME='password' TYPE ='password' PLACEHOLDER='Password' TITLE='Password'><BR><BR>
                     <INPUT TYPE='submit' VALUE='Sign In' TITLE='Click here to login' CLASS='signin'>
                </FORM>
                </TD></TR></TABLE>
              """
              
def topnav(environ):
    # Function that defines the top navigation bar, and what appears in it.
    session = str(interface.user_from_cookie(db, environ))
    if session == 'None':
        topnav = """ 
        <DIV ID='topnav'>
            <DIV CLASS='topleft'>
                <UL>
                    <H3><LI><A HREF='/' TITLE='Philip's Webpage'> Philip </A></LI></H3>
                    <DIV CLASS='SELECTED'> <LI><A HREF='/' TITLE ='Homepage'> Home </a></LI> </DIV>
                </UL>
            </DIV>
            <DIV CLASS = "topright">
                <FORM NAME = "login" METHOD="post">
                    <INPUT NAME='username' PLACEHOLDER = 'Email' TITLE='Username or email'> <INPUT NAME='password' TYPE = 'password' PLACEHOLDER='Password' TITLE='Password'>
                    <INPUT TYPE='submit' VALUE='Sign In' TITLE="Click here to login" CLASS='signin'>
                </FORM>
            </DIV>
        </DIV>
        <DIV ID = 'container'>
        <BR><BR><BR><BR>
                    """
    else:
         nick, avatar = interface.get_user_details(db, session)
         topnav = """
                    <DIV ID ='topnav'>
                        <DIV CLASS = 'topleft'>
                            <UL>
                                <H3> <LI><A HREF='/' TITLE="Philip's Webpage"> Philip </A></LI> </H3>
                    """
         if environ['PATH_INFO'] == '/':
             topnav += "<DIV CLASS ='selected'> <LI><A HREF='/' TITLE='Homepage'> Home </A></LI> </DIV>"
         else:
             topnav += "<LI><A HREF='/' TITLE='Homepage'> Home </A></LI>"
         if environ['PATH_INFO'] == '/my':
             topnav += "<DIV CLASS='selected'> <LI><A HREF='/my' TITLE='Go to my comments'> My Comments </A></LI> </DIV>"
         else:
             topnav += "<LI><A HREF='/my' TITLE='Go to my comments'> My Comments </A></LI>"
         if environ['PATH_INFO'] == '/comment':
             topnav += "<DIV CLASS='selected'>  <LI><A HREF='/comment' TITLE='Go to add a comment'> Add Comment </A></LI> </DIV>"
         else:
             topnav += "<LI><A HREF='/comment' TITLE='Go to add a comment'> Add Comment </A></LI>"
         topnav += """
                            </UL>
                        </DIV>
                        <DIV CLASS = 'topright'>
                            <UL>
                                <LI><A HREF='/my' TITLE='Go to my profile'> %s </A></LI>
                                <LI><A HREF='/logout' TITLE='Logout'> Sign Out </A></LI>
                            </UL>
                        </DIV>
                    </DIV>
                    <DIV ID = 'container'>
                    <BR><BR><BR><BR>
                    """ % (nick)
    return topnav
              
def comments(comment_list):
    # Function to add comments from a tuple of tuples
    comment_page = ""
    if comment_list != None:
        for id, useremail, page, comment in comment_list:
            user_details = interface.get_user_details(db, useremail)
            if user_details[1] == 'mary':
                # Get picture of mary online
                avatar_url = 'http://i.imgur.com/AVSXTkb.png'
            elif user_details[1] == 'bob':
                # Get picture of bob online
                avatar_url = 'http://i.imgur.com/ReA9ucT.png'
            else:
                # Get picture of default only
                avatar_url = 'http://i.imgur.com/PTkEfBS.png'
            comment_page += "<TABLE><TR><TH><H3><IMG SRC='%s' ALT='' HEIGHT ='60' WIDTH = '60'> %s commented on " % (avatar_url, user_details[0])
            webpage = str(page).replace('http://', '')
            comment_page += "<A HREF='%s'> %s </A> &nbsp&nbsp&nbsp" % (str(page), webpage)
            url = "http://localhost:8000/conversation?page="+urllib.quote(str(page), safe='')
            comment_page += "<A HREF='%s' TITLE = 'View all comments on this webpage'>(View all) </A> </H3></TH></TR>" % (url)            
            comment_page += "<TR><TD> %s </TD></TR></TABLE><BR>" % (str(comment))
    return comment_page

def main_page(environ, start_response):
    # Main Page of the website
    main_page_text = "<H1> Welcome to Philip's Webpage </H1><BR><H2> Recent Comments </H2>"
    main_page_comments = comments(interface.list_comments(db, 10))
    headers = [('content-type', 'text/html')]
    start_response('200 OK', headers)
    page = ["<HTML>", css, topnav(environ), main_page_text, main_page_comments,"</DIV></HTML>"]
    return page

def login_page(environ, start_response):
    # Page to login.
    login_page_text = "<BR><BR><BR><BR><BR>"
    headers = [('content-type', 'text/html')]
    start_response('200 OK', headers)
    page = ["<HTML>", css, topnav(environ), login_page_text, signin_form, "</DIV></HTML>"]
    return page

def login_success(cookie, environ, start_response):
    # User logged in successfuly, return a page saying so.
    login_success_text = "<H1> Login successful, redirecting you to the main page </H1> <BR>"
    login_success_text += "<H2> Or click <A HREF='/'>here</A> if it takes too long. </H2>"
    headers = [('Set-Cookie', str(cookie)),('content-type', 'text/html'),('location', '/')]
    start_response('302 Found', headers)
    page = ["<HTML>", css, topnav(environ), login_success_text, "</DIV></HTML>"]
    return page

def conversation_page(environ, start_response):
    # Page that displays all conversations about the web site the user requested.
    url = environ['QUERY_STRING']
    url = urllib.unquote(url)
    url = url.replace('page=', '')
    webpage = url.replace('http://','')
    conversation_text = "<H1> Recent comments on %s </H1>" % (webpage)
    conversation_comments = comments(interface.list_comments_page(db, url))
    if conversation_comments != '':
        headers = [('content-type', 'text/html')]
        start_response('200 OK', headers)
        page = ["<HTML>", css, topnav(environ), conversation_text, conversation_comments, "</DIV></HTML>"]
        return page
    else:
        return conversation_invalid(environ, start_response)
    
def my_comments(environ, start_response):
    # Page to look at your own comments.
    username = interface.user_from_cookie(db, environ)
    user_details = interface.get_user_details(db, username)
    my_page_text = "<H1> Welcome back %s! </H1><BR><H2> Your recent comments </H2>" % (user_details[0])
    my_page_comments = comments(interface.list_comments_user(db, username))
    headers = [('content-type', 'text/html')]
    start_response('200 OK', headers)
    page = ["<HTML>", css, topnav(environ), my_page_text, my_page_comments, "</DIV></HTML>" ]
    return page

def add_comment(environ, start_response):
    # Page to add a comment.
    add_comment_text = """
    <H1> Add a new comment </H1>
    <BR><BR><BR><BR><BR>
    <TABLE><TR><TH><H3> Posting a new comment </H3></TH></TR>
    <TR><TD>
    <FORM METHOD='post'>
    <H3> Website URL </H3>
    <INPUT NAME='website' TITLE='Enter the website you would like to talk about' CLASS='form' VALUE='http://'><BR>
    <TEXTAREA NAME= 'addcomment'> Enter your comments here... </TEXTAREA><BR>
    <INPUT NAME = 'add' TYPE='submit' VALUE='Submit'>
    </FORM>
    </TD></TR></TABLE>
    """
    headers = [('content-type', 'text/html')]
    start_response('200 OK', headers)
    page = ["<HTML>", css, topnav(environ), add_comment_text, "</DIV></HTML>"]
    return page

def comment_successful(environ, start_response):
    # Comment is added successfully, return a page saying so.
    comment_successful_text = "<H1> We have successfully added your comment. Redirecting you to the main page. </H1>"
    comment_successful_text += "<H2> Or click <A HREF='/'>here</A> if it takes too long. </H2>"
    headers = [('content-type', 'text/html'), ('location', '/')]
    start_response('302 Found', headers)
    page = ["<HTML>", css, topnav(environ), comment_successful_text, "</DIV></HTML>"]
    return page

def logout(environ, start_response):
    # User is logged out, return a page saying so.
    logout_text = "<TABLE><TR><TH><H3> Logout successful."
    logout_text += "Please click <A HREF='/'>here</A> to return to the main page. </H3></TH></TR></TABLE>"
    headers = [('content-type', 'text/html')]
    start_response('200 OK', headers)
    page = ["<HTML>", css, topnav(environ), logout_text, "</DIV></HTML>"]
    return page

def invalid(environ, start_response):
    # Username or password is incorrect, return a page saying so.
    invalid_text = "<DIV ID='error'> <TABLE><TR><TD> Username or password incorrect. Please try again. </TD></TR></TABLE> </DIV>"
    headers = [('content-type', 'text/html')]
    start_response('200 OK', headers)
    page = ["<HTML>", css, topnav(environ), invalid_text, signin_form, "</DIV></HTML>"]
    return page

def conversation_invalid(environ, start_response):
    # Conversation is invalid or cannot be found, return a page saying so.
    conversation_invalid_text = """
    <DIV ID ='error'> <TABLE><TR><TD> Conversation could not be found. Please try again. </TD></TR></TABLE> </DIV>
    <BR><BR><BR><BR><BR>
    <TABLE><TR><TH><H3> Sorry, we couldn't locate the page you are requesting to view. 
    Please click <A HREF='/'>here</A> to return to the main page. Error:[#404]</H3></TH></TR>
    <TR><TD> Need Help? <BR> <A HREF='/login'>Click here to login</A></TD></TR>
    </TABLE>     
    """
    headers = [('content-type', 'text/html')]
    start_response('404 Not Found', headers)
    page = ["<HTML>", css, topnav(environ), conversation_invalid_text, "</DIV></HTML>"]
    return page

def comment_unsuccessful(environ, start_response):
    # Error with the comment being tried to add, return with this page saying so.
    comment_unsuccessful_text = """
    <H1> Add a new comment </H1>
    <DIV ID='error'> <TABLE><TR><TD> Invalid comment. Please check the URL or comment and try again. </TD></TR></TABLE> </DIV> <BR> 
    <TABLE><TR><TH><H3> Posting a new comment </H3></TH></TR>
    <TR><TD>
    <FORM METHOD='post'>
    <H3> Website URL </H3>
    <INPUT NAME='website' TITLE='Enter the website you would like to talk about' CLASS='form' VALUE='http://'><BR>
    <TEXTAREA NAME= 'addcomment'> Enter your comments here... </TEXTAREA><BR>
    <INPUT NAME = 'add' TYPE='submit' VALUE='Submit'>
    </FORM>
    </TD></TR></TABLE>
    """
    headers = [('content-type', 'text/html')]
    start_response('200 OK', headers)
    page = ["<HTML>", css, topnav(environ), comment_unsuccessful_text, "</DIV></HTML>"]
    return page

def no_permission(environ, start_response):
    # No permission page, returning when unlogged user tries to add a comment or do something unauthorized.
    no_permission_text = """
    <DIV ID='error'> <TABLE><TR><TD> You must be logged in to view this page. </TD></TR></TABLE> </DIV> <BR>
    <TABLE><TR><TH><H3> Ooops! You do not have permission to view this page. 
    Please click <A HREF='/'>here</A> to return to the main page. Error:[#401]</H3></TH></TR>
    <TR><TD> Need Help? <BR> <A HREF='/login'>Click here to login</A></TD></TR>
    </TABLE>     
    """
    headers = [('content-type', 'text/html')]
    start_response('401 Unauthorized', headers)
    page = ["<HTML>", css, topnav(environ), no_permission_text, "</DIV></HTML>"]
    return page

def show_404_app(environ, start_response):
    # 404 error Page
    error404 = """
    <H1> Sorry, we couldn't find that! </H1>
    <TABLE><TR><TH><H3> Sorry, we couldn't locate the page you are requesting to view. 
    Please click <A HREF='/'>here</A> to return to the main page. Error:[#404]</H3></TH></TR>
    <TR><TD> Need Help? <BR> <A HREF='/login'>Click here to login</A></TD></TR>
    </TABLE>     
    """
    headers = [('content-type', 'text/html')]
    start_response('404 Not Found', headers)
    page = ["<HTML>", css, topnav(environ), error404, "</DIV></HTML>"]
    return page

def application(environ, start_response):
    """Demo WSGI application"""   
    formdata = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])
    if formdata.has_key('username') and formdata.has_key('password'):
        username = formdata.getvalue('username')
        password = formdata.getvalue('password')
        if interface.check_login(db, username, password) == True:
            cookie = interface.generate_session(db, username)
            # Correct username or password, return a page saying so.
            return login_success(cookie, environ, start_response)
        else:
            # Invalid username or password, return a page with an error box saying so.
            return invalid(environ, start_response)
    elif formdata.has_key('username') or formdata.has_key('password'):
        # Invalid username or password, return a page with an error box saying so.
        return invalid(environ, start_response)
    
    session = str(interface.user_from_cookie(db, environ)) 
    if formdata.has_key('website') and formdata.has_key('addcomment'):
        if formdata.getvalue('website') == 'http://':
            # Shouldn't post a comment about http://!
            return comment_unsuccessful(environ, start_response)
        elif session != 'None':
            topic = formdata.getvalue('website')
            comment = formdata.getvalue('addcomment')
            interface.add_comment(db, session, topic, comment)
            #Comment successfully added. Return a page saying so, with a redirect link to main page.
            return comment_successful(environ, start_response)
        else:
            # Unlogged users should receive a 404 Not Found error
            return no_permission(environ, start_response)
    elif formdata.has_key('website') or formdata.has_key('addcomment'):
        if session != 'None':
            #Invalid form returned. Return a page showing an error box and how to fix it.
            return comment_unsuccessful(environ, start_response)
        else:
            # Unlogged users should receive a 404 Not Found error.
            return no_permission(environ, start_response)  
          
    if environ['PATH_INFO'] == '/':
        return main_page(environ, start_response)
    elif environ['PATH_INFO'] == '/login':
        return login_page(environ, start_response)
    elif environ['PATH_INFO'] == '/my':
        if session != 'None':
            return my_comments(environ, start_response)
        else:
            return show_404_app(environ, start_response)
    elif environ['PATH_INFO'] == '/conversation':
        return conversation_page(environ, start_response)
    elif environ['PATH_INFO'] == '/comment':
        if session != 'None':
            return add_comment(environ, start_response)
        else:
            #Unlogged users should be told they do not have permission to access this page.
            return no_permission(environ, start_response)
    elif environ['PATH_INFO'] == '/logout':
        if session != 'None':
            interface.delete_session(db, session)
            return logout(environ, start_response)
        else:
            # Unlogged users should receive a 404 Not Found error.
            return show_404_app(environ, start_response)
    else:
        # Path invalid, return 404 Not Found
        return show_404_app(environ, start_response)


if __name__ == '__main__':

    # initialise the database and create sample data
    # note that this means you get new sample data for each run
    db = database.COMP249Db()
    db.create_tables()
    db.sample_data()

    host = 'localhost'
    port = 8000

    server = simple_server.make_server(host, port, application)
    print "Listening on http://%s:%d/" % (host, port)
    server.serve_forever()

