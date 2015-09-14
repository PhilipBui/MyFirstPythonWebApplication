'''
Created on Mar 26, 2012

@author: steve
'''
import sqlite3 as lite
import Cookie
import uuid
# this variable MUST be used as the name for the cookie used by this application
COOKIE_NAME = 'session'



def list_comments(db, limit=None):
    """return a list of all comments as tuples

       - tuples are (id, useremail, page, comment)
       if limit is provided it should be an integer and only that
       many comments will be returned
    """
    cur = db.cursor() 
    cur.execute("SELECT * FROM comments ORDER BY id DESC")      
    # No limit, fetch all
    if limit == None:
        rows = cur.fetchall()
    # Limit exists, return as many as limit
    else:
        rows = cur.fetchmany(limit)
    return rows


def list_comments_user(db, useremail):
    """return a list of this user's comments as tuples

       - tuples are (id, useremail, page, comment)
    """
    cur = db.cursor()
    cur.execute("SELECT * FROM comments WHERE useremail=:useremail ORDER BY id DESC",{"useremail": useremail})
    rows = cur.fetchall()
    return rows

def list_comments_page(db, page):
    """return a list of comments on this page as tuples

       - tuples are (id, useremail, page, comment)
    """
    cur = db.cursor()
    cur.execute("SELECT * FROM comments WHERE page=:page ORDER BY id DESC",{"page": page})
    rows = cur.fetchall()
    return rows

def get_user_details(db, useremail):
    """Given a user email, return a tuple containing all the user
    details from the database (nick, avatar).
    Return None if no such user is known"""
    cur = db.cursor()
    cur.execute("SELECT email FROM users WHERE email=:email", {"email": useremail})
    row = cur.fetchone()
    # Useremail doesn't exist, return None
    if row == None:
        return None
    # Useremail exists in row, return User Details
    if useremail in row:
        cur.execute("SELECT nick, avatar FROM users WHERE email=:email",{"email": useremail})
        rows = cur.fetchone()
        return rows
    # Return (None, None) in case of error.
    return (None, None)



def check_login(db, useremail, password):
    """returns True if password matches stored"""
    cur = db.cursor()
    # Crypt the password 
    password = db.crypt(password)
    cur.execute("SELECT password FROM users WHERE email=:email",{"email": useremail})
    row = cur.fetchone()
    # Password and useremail doesn't exist, return false
    if row == None:
        return False
    # Password exists, return true
    if password in row:
        return True
    # Password is false, return false
    else:
        return False


def add_comment(db, useremail, page, comment):
    """add a new comment for a page
       """
    cur = db.cursor()
    # Insert (useremail, page, comment) in the form of a tuple into database
    comment = ((useremail, page, comment))
    cur.execute("INSERT INTO comments(useremail, page, comment) VALUES(?,?,?)", comment)
    pass

def generate_session(db, useremail):
    """create a new session, return a cookie obj with session key
    user must be a valid user in the database, if not, return None
    There should only be one session per user at any time, if there
    is already a session active, the cookie should use the existing
    sessionid
    """
    cur = db.cursor()
    cur.execute("SELECT email FROM users WHERE email=:email",{"email": useremail})
    row = cur.fetchone()
    # User does not exist
    if row == None:
        return None
    # User exists
    if useremail in row:
        cur.execute("SELECT sessionid FROM sessions WHERE useremail=:useremail",{"useremail": useremail})
        rows2 = cur.fetchone()
        cookie = Cookie.SimpleCookie()
        # Session doesn't exist for useremail, create cookie and return it
        if rows2 == None:
            key = str(uuid.uuid4())
            session = (key, useremail)
            cur.execute("INSERT INTO sessions VALUES (?,?)", session)
            db.commit()
            cookie[COOKIE_NAME] = key
            return cookie
        # Session exists, return cookie
        else:
            cookie[COOKIE_NAME] = rows2[0]
            return cookie
    # User does not exist
    else:
        return None


def delete_session(db, useremail):
    """remove all session table entries for this user"""
    cur = db.cursor()
    cur.execute("SELECT sessionid FROM sessions WHERE useremail=:useremail",{"useremail": useremail})
    row = cur.fetchone()
    # Sessions exist for this user, delete them
    if row != None:
        cur.execute("DELETE FROM sessions WHERE sessionid=:sessionid", {"sessionid": row[0]})


def user_from_cookie(db, environ):
    """check whether HTTP_COOKIE set, if it is,
    and if our cookie is present, try to
    retrieve the user email from the sessions table
    return useremail or None if no valid session is present"""
    # If environ has cookies running
    if environ.has_key('HTTP_COOKIE'):
        cookie = Cookie.SimpleCookie(environ['HTTP_COOKIE'])
        # If sessionID exists in our cookie base
        if cookie.has_key(COOKIE_NAME):
            # Get the sessionID value from cookie
            sessionkey = cookie[COOKIE_NAME].value
            cur = db.cursor()
            cur.execute("SELECT useremail FROM sessions WHERE sessionid=?", (sessionkey,))
            result = cur.fetchone()
            
            # Useremail exists for sessionID return it
            if result != None:
                return result[0]
    # False result from any three methods above, return None
    else:
        return None

