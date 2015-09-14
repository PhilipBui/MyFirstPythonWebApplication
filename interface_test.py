'''
Created on Mar 26, 2012

@author: steve
'''
import unittest

from database import COMP249Db

# import the module to be tested
import interface

class Test(unittest.TestCase):


    def setUp(self):
        # open an in-memory database for testing
        self.db = COMP249Db(':memory:')
        self.db.create_tables()

        # generate some test data

        import random
                #  email,         pass,   nick             avatar
        self.users = [('bob@here.com', 'bob', 'Bob Bobalooba', 'default'),
                 ('jim@there.com', 'jim', 'The Jimbulator', 'default'),
                 ('mary@where.com', 'mary', 'Mary, Contrary', 'default')]

        self.pages = ['http://pwp.stevecassidy.net/',
                 'http://pwp.stevecassidy.net/web/webworks.html',
                 'http://pwp.stevecassidy.net/web/html.html',
                 'http://pwp.stevecassidy.net/wsgi/python-wsgi.html',
                 ]

        self.comments = []
        # create one entry per unit for each user
        cursor = self.db.cursor()
        id = 0
        for email, password, nick, avatar in self.users:
            sql = "INSERT INTO users VALUES (?, ?, ?, ?)"
            cursor.execute(sql, (email, self.db.crypt(password), nick, avatar))

            for page in self.pages:

                    sql = 'INSERT INTO comments (id, useremail, page, comment) VALUES (?, ?, ?, ?)'

                    comment = "Comment %d by %s on %s" % (id, nick, page)
                    # now create the database entry for this user/unit
                    cursor.execute(sql, (id, email, page, comment))
                    self.comments.append((id, email, page, comment))
                    id += 1

        # commit all updates to the database
        self.db.commit()



    def tearDown(self):
        self.db.delete()

    def test_check_login(self):

        for email, password, first, last in self.users:
            # try the correct password
            self.assertTrue(interface.check_login(self.db, email, password), "Password check failed for email %s" % email)

            # and now incorrect
            self.assertFalse(interface.check_login(self.db, email, "badpassword"), "Bad Password check failed for email %s" % email)

        # check for an unknown email
        self.assertFalse(interface.check_login(self.db, "user@here.com", "badpassword"), "Bad Password check failed for unknown email")




    def test_generate_session(self):
        """The generate_session procedure makes a new session cookie
        to be returned to the client
        If there is already a session active for this user, return the
        same session key in the cookie"""

        # run tests for all test users
        for email, password, first, last in self.users:
            cookie = interface.generate_session(self.db, email)

            self.assertNotEqual(cookie, None, "No cookie returned from generate_session")

            # look for the cookie
            self.assertTrue(cookie.has_key(interface.COOKIE_NAME), "Cookie from generate_session has no entry for defined cookie name")

            # get the value and verify that it is in the sessions table
            sessionid = cookie[interface.COOKIE_NAME].value

            cursor = self.db.cursor()
            cursor.execute('select useremail from sessions where sessionid=?', (sessionid,))

            stored_useremail = cursor.fetchone()[0]
            self.assertEqual(email, stored_useremail)

            # now try to make a new session for one of the users

            cookie2 = interface.generate_session(self.db, email)
            # look for the cookie
            self.assertTrue(cookie2.has_key(interface.COOKIE_NAME), "Cookie from generate_session has no entry for defined cookie name")

            # sessionid should be the same as before

            self.assertEqual(cookie2[interface.COOKIE_NAME].value, sessionid)

        # try to generate a session for an invalid user

        cookie = interface.generate_session(self.db, "user@here.com")
        self.assertEqual(cookie, None, "Invalid user should return None from generate_session")


    def test_delete_session(self):
        """The delete_session procedure should remove all sessions for
        a given user in the sessions table.
        Test relies on working generate_session"""

        # run tests for all test users
        for email, password, first, last in self.users:
            cookie = interface.generate_session(self.db, email)

            self.assertNotEqual(cookie, None, "generate_session failing, can't run delete_session tests")

            # get the value and verify that it is in the sessions table
            sessionid = cookie[interface.COOKIE_NAME].value

            # now remove the session
            interface.delete_session(self.db, email)

            # now check that the session is not present

            cursor = self.db.cursor()
            cursor.execute('select sessionid from sessions where useremail=?', (email,))

            rows = cursor.fetchall()
            self.assertEqual(rows, [], "Expected no results for sessions query from deleted session, got %s" % (rows,))




    def test_get_user_details(self):
        """The get_user_details procedure returns user first and last name given
        the email address"""


        for email, password, nick, avatar in self.users:

            stored_nick, stored_avatar = interface.get_user_details(self.db, email)

            self.assertEqual(nick, stored_nick)
            self.assertEqual(avatar, stored_avatar)

        # test an unknown user
        result = interface.get_user_details(self.db, 'unknown@nowhere.com')
        self.assertEqual(result, None, 'Expected None result for unknown user in get_user_details')



    def test_user_from_cookie(self):
        """The user_from_cookie procedure finds the name of the logged in
        user from the session cookie if present

        Test relies on working generate_cookie
        """
        import Cookie
        # first test with no cookie
        environ = dict()
        email_from_cookie = interface.user_from_cookie(self.db, environ)
        self.assertEquals(email_from_cookie, None, "Expected None in case with no cookie, got %s" % str(email_from_cookie))


        cookie = Cookie.SimpleCookie()
        cookie[interface.COOKIE_NAME] = 'fake sessionid'
        environ = {'HTTP_COOKIE': cookie[interface.COOKIE_NAME].OutputString()}

        email_from_cookie = interface.user_from_cookie(self.db, environ)

        self.assertEquals(email_from_cookie, None, "Expected None in case with invalid session id, got %s" % str(email_from_cookie))


        # run tests for all test users
        for email, password, first, last in self.users:

            cookie = interface.generate_session(self.db, email)

            self.assertNotEqual(cookie, None, "generate_session failing, can't run user_from_cookie tests")

            environ = {'HTTP_COOKIE': cookie[interface.COOKIE_NAME].OutputString()}


            email_from_cookie = interface.user_from_cookie(self.db, environ)

            self.assertEqual(email_from_cookie, email)


    def test_list_comments(self):
        """The list_comments procedure should return a list of tuples
        one for each of the comment entries in the database, each tuple
        should contain """

        clist = interface.list_comments(self.db)

        # we should have the same number of comments as we created
        self.assertEquals(len(clist), len(self.comments), "Wrong number of comments returned from list_units, expected %d, got %d" % (len(self.comments), len(clist)))

        # comments should be in order so the largest id should be first
        self.assertEquals(clist[0][0], self.comments[-1][0], "Wrong comment id first in comment list, expected %d, got %d" % (clist[0][0], self.comments[-1][0]))

        # and the comment list should be ordered by id
        ids = [c[0] for c in clist]
        self.assertEqual(sorted(ids, reverse=True), ids, "List of comments returned is not in large-to-small order: %s" % (ids,))

        # try the limit argument
        clist = interface.list_comments(self.db, 3)
        self.assertEquals(len(clist), 3, "Wrong number of comments returned from list_comments with a limit argument, expected 3, got %d" % (len(clist),))


    def test_list_comments_user(self):
        """The list_comments_user procedure should return a list of tuples
        one for each of the comment entries in the database entered by the
        given user, each tuple
        should contain e"""

        # grab a test user email address
        testuser = self.users[0][0]

        comments = interface.list_comments_user(self.db, testuser)

        # this time only those where the user is our test user
        refcomments = [u for u in self.comments if u[1] == testuser]

        # we should have the same units in self.units
        self.assertEquals(len(comments), len(refcomments), "Wrong number of comments returned from list_comments_user")

        # check that all comments in our list are present in the returned list
        for comment in refcomments:
            self.assertTrue(comment in comments, "Didn't find comment %s in list returned from list_comments_user %s" % (comment, comments))

        # comments should be in order so the largest id should be first
        self.assertEquals(refcomments[-1][0], comments[0][0], "Wrong comment id first in comment list, expected %d, got %d" % (refcomments[-1][0], comments[0][0]))

        # and the comment list should be ordered by id
        ids = [c[0] for c in comments]
        self.assertEqual(sorted(ids, reverse=True), ids, "List of comments returned is not in large-to-small order: %s" % (ids,))





    def test_list_comments_page(self):
        """The list_comments_user procedure should return a list of tuples
        one for each of the comment entries in the database entered by the
        given user, each tuple
        should contain e"""

        # grab a test user email address
        testpage = self.pages[0]

        comments = interface.list_comments_page(self.db, testpage)

        # this time only those where the user is our test user
        refcomments = [u for u in self.comments if u[2] == testpage]

        # we should have the same units in self.units
        self.assertEquals(len(comments), len(refcomments), "Wrong number of comments returned from list_comments_page")

        # check that all comments in our list are present in the returned list
        for comment in refcomments:
            self.assertTrue(comment in comments, "Didn't find comment %s in list returned from list_comments_page %s" % (comment, comments))

        # comments should be in order so the largest id should be first
        self.assertEquals(refcomments[-1][0], comments[0][0], "Wrong comment id first in comment list, expected %d, got %d" % (refcomments[-1][0], comments[0][0]))

        # and the comment list should be ordered by id
        ids = [c[0] for c in comments]
        self.assertEqual(sorted(ids, reverse=True), ids, "List of comments returned is not in large-to-small order: %s" % (ids,))


    def test_add_comment(self):
        """The add_comment procedure adds a new comment for a user
        Test relies on list_comments_user working properly"""

        useremail = "bob@here.com"
        page = "http://example.com/"
        firstcomment = "First Comment"
        secondcomment = "Second Comment"

        interface.add_comment(self.db, useremail, page, firstcomment)

        # now retrieve the info and verify
        comments = interface.list_comments_user(self.db, useremail)
        # our comment should be the first
        i, e, p, c = comments[0]
        self.assertEquals((useremail, page, firstcomment), (e, p, c), "Stored comment not found first in comments list, got %s instead" % str(comments[0]))

        # do it again to check we don't lose the above
        interface.add_comment(self.db, useremail, page, secondcomment)
        # now retrieve the info and verify
        comments = interface.list_comments_user(self.db, useremail)
        # our comment should be the first
        i, e, p, c = comments[0]
        self.assertEquals((useremail, page, secondcomment), (e, p, c), "Second stored comment not found first in comments list, got %s instead" % str(comments[0]))
        i, e, p, c = comments[1]
        self.assertEquals((useremail, page, firstcomment), (e, p, c), "First stored comment not found second in comments list, got %s instead" % str(comments[0]))


if __name__ == "__main__":
    unittest.main()