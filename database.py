'''
Created on Mar 26, 2012

@author: steve
'''

import sqlite3

class COMP249Db():
    '''
    Provide an interface to the database for a COMP249 web application
    '''


    def __init__(self, dbname="comp249.db"):
        '''
        Constructor
        '''

        self.dbname = dbname
        self.conn = sqlite3.connect(self.dbname)
        ### ensure that results returned from queries are strings rather
        # than unicode which doesn't work well with WSGI
        self.conn.text_factory = str

    def cursor(self):
        """Return a cursor on the database"""

        return self.conn.cursor()

    def commit(self):
        """Commit pending changes"""

        self.conn.commit()

    def delete(self):
        """Destroy the database file"""
        pass


    def crypt(self, password):
        """Return a one-way hashed version of the password suitable for
        storage in the database"""

        import hashlib

        return hashlib.sha1(password).hexdigest()



    def create_tables(self):
        """Create and initialise the database tables
        This will have the effect of overwriting any existing
        data."""

        sql = """
DROP TABLE IF EXISTS users;
CREATE TABLE users (
           email text unique primary key,
           password text,
           nick text,
           avatar text
);

DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions (
            sessionid text unique primary key,
            useremail text,
            FOREIGN KEY(useremail) REFERENCES users(email)
);

DROP TABLE IF EXISTS comments;
CREATE TABLE comments (
            id integer unique primary key autoincrement,
            useremail text,
            page text,
            comment text,
            FOREIGN KEY(useremail) REFERENCES users(email)
);"""

        self.conn.executescript(sql)
        self.conn.commit()


    def sample_data(self):
        """Generate some sample data for testing the web
        application. Erases any existing data in the
        database"""

        import random
                #  email,         pass,   nick             avatar
        users = [('bob@here.com', 'bob', 'Bob Bobalooba', 'bob'),
                 ('jim@there.com', 'jim', 'The Jimbulator', 'default'),
                 ('mary@where.com', 'mary', 'Mary, Contrary', 'mary')]

        pages = ['http://pwp.stevecassidy.net/',
                 'http://pwp.stevecassidy.net/web/webworks.html',
                 'http://pwp.stevecassidy.net/web/html.html',
                 'http://pwp.stevecassidy.net/wsgi/python-wsgi.html',
                 ]

        lorem = """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut
labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip
ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat
nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id
est laborum."""


        # create one entry per unit for each user
        cursor = self.cursor()
        for email, password, nick, avatar in users:
            sql = "INSERT INTO users VALUES (?, ?, ?, ?)"
            cursor.execute(sql, (email, self.crypt(password), nick, avatar))


        # create some comments, do it this way so that we have a mix of
        # users in the default ordering
        for count in range(2):
            for page in pages:
                for email, password, nick, avatar in users:
                    # maybe add a comment
                    if random.choice([True, False]):
                        sql = 'INSERT INTO comments (useremail, page, comment) VALUES (?, ?, ?)'

                        start = random.choice(range(30))
                        length = random.choice(range(len(lorem)))
                        comment = lorem[start:start+length]
                        # now create the database entry for this user/unit
                        cursor.execute(sql, (email, page, comment))

        # commit all updates to the database
        self.commit()

if __name__=='__main__':
    # if we call this script directly, create the database and make sample data
    db = COMP249Db()
    db.create_tables()
    db.sample_data()