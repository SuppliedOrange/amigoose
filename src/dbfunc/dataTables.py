from src.dbfunc import sqlfunc as sf
import os

class dataTables():
    def __init__(self,username):
        self.username = username or sf.existingUser()

    def initializeUser(self):
        dataTables = {}
        for dataTable in {settings,loggedInStatus,userData,postData}:
            dt = dataTable(self.username)
            dataTables[dt.getDataTableName()] = dt
        dataTables['dataTables'] = self
        return dataTables
            

class settings(dataTables):

    def getDataTableName(self):
        return "settings"

    # Preference table in Settings database
    def getPreference(self,column,fetchAll=False):
        sf.selectDB("settings")
        dat = sf.getData("preferences", ("username",self.username), column, fetchAll)
        return dat if fetchAll else dat[0]

    def updatePreference(self,column,value):
        sf.selectDB("settings")
        return sf.updateData("preferences", column, value, ("username",self.username))
        
    # All tables in Global database    
    def getGlobal(self, table, column, fetchAll=False):
        sf.selectDB("global")
        dat = sf.getData(table,(),column,fetchAll)
        return dat if fetchAll else dat[0]

    def updateGlobal(self,table,column,value):
        sf.selectDB("global")
        return sf.updateData(table, column, value, ())


class loggedInStatus(dataTables):

    def getDataTableName(self):
        return "loggedInStatus"

    def isLoggedIn(self):
        return bool(sf.getData('loginState',(),"username")[0])
    
    def isCurrentUser(self):
        return (sf.getData('loginState',(),"username")[0] == self.username)

class userData(dataTables):
    
    def getDataTableName(self):
        return "userData"
    
    def getProfileData(self,column,username=None):
        username = username or self.username
        sf.selectDB("userData")
        return sf.getData("profileData", ("username", username or self.username), column)

    def updateProfileData(self,column,value,username=None):
        username = username or self.username
        sf.selectDB("userData")
        return sf.updateData("profileData",column,value, ("username", username))
    
    def getSubredditData(self,column,username=None):
        username = username or self.username
        sf.selectDB("userData")
        return sf.getData("subredditData", ("username", username), column, fetchAll=True)
    
    def updateSubredditData(self,column,value,username=None):
        username = username or self.username
        sf.selectDB("userData")
        return sf.updateData("subredditData",column,value,("username",username))
    
    def getSubredditMembers(self,subreddit):
        sf.selectDB("userData")
        return sf.executeSQL("SELECT COUNT(subreddit) FROM subredditData WHERE subreddit = '" + subreddit +"' ").fetchone()
    
    def joinSubreddit(self,subreddit):

        sf.selectDB("postData")
        isSubreddit = sf.checkMatch("subreddits", ("name",subreddit))
        if not isSubreddit:
            return (False, "Subreddit does not exist")

        sf.selectDB("userData")
        inSubreddit = sf.checkMatch("subredditData", ("username", self.username), ("subreddit", subreddit))
        if inSubreddit:
            return (False, "Already in subreddit")
            
        import time
        sf.insertData( "subredditData", (self.username, subreddit, int(time.time())) )
        return (True,)

    def leaveSubreddit(self, subreddit):

        sf.selectDB("postData")
        isSubreddit = sf.checkMatch("subreddits", ("name",subreddit))
        if not isSubreddit:
            return (False, "Subreddit does not exist")
        
        sf.selectDB("userData")
        inSubreddit = sf.checkMatch("subredditData", ("username", self.username), ("subreddit", subreddit))
        if not inSubreddit:
            return (False, "Not in subreddit")
        
        sf.deleteData("subredditData", ("subreddit", subreddit), ("username", self.username))

        return (True,)


class postData(dataTables):

    def getDataTableName(self):
        return "postData"

    # SUBREDDIT STUFF    

    def getSubreddits(self,subreddit,column):
        sf.selectDB("postData")
        return sf.getData("subreddits", ("name", subreddit), column)
    
    def getAllSubreddits(self):
        sf.selectDB("postData")
        return sf.getData("subreddits", (), "name", fetchAll=True)
        
    def updateSubreddits(self,subreddit,column,value):
        sf.selectDB("postData")
        return sf.updateData("subreddits", column, value, ("name", subreddit))
    
    def makeSubreddit(self, name, description):
        # Adding rows related to subreddit
        import time
        sf.selectDB("postData")
        sf.insertData("subreddits", (name, description, self.username, int(time.time()) ))
        sf.selectDB("userData")
        sf.insertData( "subredditData", (self.username, name, int(time.time())) )
        # Adding subreddit posts folder
        try:
            os.makedirs(os.path.abspath("./subreddits/posts/" + name.lower() + "/"), exist_ok=True)
        except:
            pass
        # Note that tags and icons are not handled here.
    
    def deleteSubreddit(self,name):
        # Dropping rows related to subreddit
        sf.selectDB("postData")
        sf.executeSQL("DELETE FROM subreddits WHERE name = \"" + name + "\"",commit=True)
        sf.selectDB("userData")
        sf.executeSQL("DELETE FROM subredditData WHERE subreddit = \"" + name + "\"",commit=True)
        # Removing subreddit from tags
        from src.dbfunc.jsonfunc import loadData,updateFile
        tags = loadData()
        subredditTags = list(filter(lambda x: name in tags[x], tags.keys())).copy()
        for tag in subredditTags:
            tags[tag].remove(name)
            if not tags[tag]:
                del tags[tag]
        updateFile(tags)
        # Removing subreddit icon
        try:
            os.remove(os.path.abspath("./subreddits/pfps/" + name.lower() + ".png"))
        except:
            pass

        # Removing subreddit posts folder
        try:
            os.removedirs(os.path.abspath("./subreddits/pfps/" + name.lower() + "/"))
        except:
            pass
        
    # POST MAP STUFF

    def createPostMap(self, author, subreddit, uuid, resourceLink, dateCreated):
        sf.selectDB("postData")
        sf.insertData("postmaps", (author, subreddit, uuid, resourceLink, dateCreated))

    def getPostsBy(self, subreddit=None, author=None, uuid=None, fetchAll=True, column="*"):
        sf.selectDB("postData")
        queries = ""
        if (subreddit):
            queries += f' WHERE subreddit = "{subreddit}" '
        if (author):
            if (queries): queries += "AND"
            queries += f' WHERE author = "{author}" '
        if (uuid):
            if (queries): queries += "AND"
            queries += f' WHERE uuid = "{uuid}" '

        if not subreddit and not author and not uuid:
            return None

        result = sf.executeSQL("SELECT " + column + " FROM POSTMAPS" + queries + "ORDER BY dateCreated DESC")
        return result.fetchall() if fetchAll else result.fetchone()

    '''
    def getPost(self, uuid, column="*"):
        sf.selectDB("postData")
        post = sf.getData("postmaps", ("uuid",uuid), column)
        return post
        #Removed this, check if it causes problems.
    '''

    def deletePost(self, author, uuid, subreddit, resourceLink):
        sf.selectDB("postData")
        author = author.lower()
        sf.deleteData("postdata", (("uuid",uuid), ("author",author)) )
        os.remove(os.path.abspath(f'./subreddits/posts/{subreddit}/{author}+{uuid}.dat'))
        if (os.path.isfile(resourceLink)): os.remove(resourceLink)

    def checkHonk(self, author, uuid):
        sf.selectDB("postData")
        return sf.checkMatch("honkLogs",("author", author), ("uuid",uuid))
    
    def getHonks(self, uuid):
        sf.selectDB("postData")
        honks = sf.getData("honkLogs", ("uuid", uuid), "author", fetchAll=True)
        return len(honks)

    def toggleHonk(self, author, uuid, subreddit):
        sf.selectDB("postData")
        isHonked = sf.checkMatch("honkLogs", ("author", author), ("uuid",uuid))
        if not isHonked:
            sf.insertData("honkLogs", (author,subreddit,uuid))
            return True # Inserted honk
        else:
            sf.deleteData("honkLogs", ("author", author), ("uuid", uuid))
            return False # Removed honk
        
    # Comment stuff

    def getCommentsForPost(self, uuid):
        sf.selectDB("postData")
        comments = sf.executeSQL(f"select * from comments where uuid = '{uuid}' order by dateCreated desc")
        commentPool = []
        commentTitles = ["author", "uuid", "content", "dateCreated"]
        for comment in comments:
            comment = dict(zip(commentTitles, comment))
            commentPool.append(comment)
        return commentPool