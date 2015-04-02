import facebook
from pymongo import MongoClient

"""
Scrapes facebook pages and puts the posts which are in all
the pages (based on text) in a mongodb database.
"""

class FacebookAnalysis(object):
    """Gets Facebook page data and analyses it"""

    def __init__(self, *args):
        """ Takes in an optional parameters accessToken and db collection name
             in a tuple which can be of length 0, 1 or 2 depending on the number
             of parameters inputed. If the collection already exists then
             commong pages are intersection of what exists already in the 
             db collection and the common posts in new specified pages"""
        if args: 
            token = args[0]
            self.accessToken = token
            self.graph = facebook.GraphAPI(self.accessToken)
        else : 
            self.graph = facebook.GraphAPI()
        self.mongoClient = MongoClient('localhost', 27017)
        self.dbName = "test_database"
        if len(args) == 2:
            self.collectionName = args[1]
        else: self.collectionName = "common_posts"  # default
        self.db = self.mongoClient[self.dbName]
        self.postsCollection = self.db[self.collectionName]

        # If first page to be scraped then just add in
        # all the posts from the page to the database
        # since this is a trivial intersection
        self.scrapingFirstPage = (self.postsCollection.count() == 0)

        # Keeps the posts in the current page being scraped
        # for constant time lookup later in clean database
        self.postMessages = dict()

    def insertPost(self, post):
        if self.scrapingFirstPage and "message" in post:
            self.postsCollection.insert(post)
        if "message" in post:
            self.postMessages[post["message"]] = True

    def cleanDatabase(self):
        # Removes posts from the database which are not in current
        # page being scraped
        if not self.scrapingFirstPage:
            removeIdList = []
            for post in self.postsCollection.find():
                if post["message"] not in self.postMessages:
                    removeIdList += [post["id"]]
            for postid in removeIdList:
                self.postsCollection.remove({"id": postid})
        # reset post id's
        self.postMessages = dict()


    def scrapePageForPosts(self, pageID):
        if self.scrapingFirstPage:
            print "First page to be scraped for collection"
        page = self.graph.get_object(id=pageID)
        pageID = page['id']
        pagePosts = self.graph.get_connections(id=pageID,
                     connection_name = "posts", limit = 100)
        for post in pagePosts['data']:
            self.insertPost(post)
        lastPostTime = pagePosts['data'][-1]['created_time']
        while len(pagePosts['data']) > 1:
            try:
                pagePosts = self.graph.get_connections(id=pageID,
                                connection_name = "posts",
                                limit = 100, until = lastPostTime)
            except:
                print "Could not get all pages for page ID =", (pageID)
                break
            if lastPostTime == pagePosts['data'][-1]['created_time']:
                # got all posts from the page
                break
            lastPostTime = pagePosts['data'][-1]['created_time']
            for post in pagePosts['data']:
                self.insertPost(post)
        self.cleanDatabase()
        self.scrapingFirstPage = False

    def commonPages(self):
        for post in self.postsCollection.find():
            print post["message"].encode('utf-8')

    def scrapePages(self, pageIDs):
        for pageID in pageIDs:
            self.scrapePageForPosts(pageID)
        self.commonPages()


accessToken = ""            

fb = FacebookAnalysis(accessToken, "abc_def_common_posts")

testPages = ["https://www.facebook.com/pages/Def/440444466118878?ref=hl", 
        "https://www.facebook.com/pages/Abc/659032697534369?ref=hl",
        "https://www.facebook.com/pages/Md5/359859484202849?__mref=message_bubble"]

fb.scrapePages(testPages)


