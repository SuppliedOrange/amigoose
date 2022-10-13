from src.dbfunc import sqlfunc as sf
import os


class dataTables():
    def __init__(self, username):
        self.username = username or sf.existingUser()

    def initializeUser(self):
        dataTables = {}
        for dataTable in {settings, loggedInStatus, userData, postData}:
            dt = dataTable(self.username)
            dataTables[dt.getDataTableName()] = dt
        dataTables['dataTables'] = self
        return dataTables


class settings(dataTables):

    def getDataTableName(self):
        return "settings"
    
    # Preference table in Settings database
    def getPreference(self, column, fetchAll=False):
        sf.selectDB("settings")
        dat = sf.getData("preferences", ("username",
                         self.username), column, fetchAll)
        return dat if fetchAll else dat[0]

    def updatePreference(self, column, value):
        sf.selectDB("settings")
        return sf.updateData("preferences", column, value, ("username", self.username))

    # All tables in Global database
    def getGlobal(self, table, column, fetchAll=False):
        sf.selectDB("global")
        dat = sf.getData(table, (), column, fetchAll)
        return dat if fetchAll else dat[0]

    def updateGlobal(self, table, column, value):
        sf.selectDB("global")
        return sf.updateData(table, column, value, ())


class loggedInStatus(dataTables):

    def getDataTableName(self):
        return "loggedInStatus"

    def isLoggedIn(self):
        return bool(sf.getData('loginState', (), "username")[0])

    def isCurrentUser(self):
        return (sf.getData('loginState', (), "username")[0] == self.username)


class userData(dataTables):

    def getDataTableName(self):
        return "userData"

    def getProfileData(self, column, username=None):
        username = username or self.username
        sf.selectDB("userData")
        return sf.getData("profileData", ("username", username or self.username), column)

    def updateProfileData(self, column, value, username=None):
        username = username or self.username
        sf.selectDB("userData")
        return sf.updateData("profileData", column, value, ("username", username))

    def getSubredditData(self, column, username=None):
        username = username or self.username
        sf.selectDB("userData")
        return sf.getData("subredditData", ("username", username), column, fetchAll=True)

    def updateSubredditData(self, column, value, username=None):
        username = username or self.username
        sf.selectDB("userData")
        return sf.updateData("subredditData", column, value, ("username", username))

    def getSubredditMembers(self, subreddit):
        sf.selectDB("userData")
        return sf.executeSQL("SELECT COUNT(subreddit) FROM subredditData WHERE subreddit = '" + subreddit + "' ").fetchone()

    def joinSubreddit(self, subreddit):

        sf.selectDB("postData")
        isSubreddit = sf.checkMatch("subreddits", ("name", subreddit))
        if not isSubreddit:
            return (False, "Subreddit does not exist")

        sf.selectDB("userData")
        inSubreddit = sf.checkMatch(
            "subredditData", ("username", self.username), ("subreddit", subreddit))
        if inSubreddit:
            return (False, "Already in subreddit")

        import time
        sf.insertData("subredditData", (self.username,
                      subreddit, int(time.time())))
        return (True,)

    def leaveSubreddit(self, subreddit):

        sf.selectDB("postData")
        isSubreddit = sf.checkMatch("subreddits", ("name", subreddit))
        if not isSubreddit:
            return (False, "Subreddit does not exist")

        sf.selectDB("userData")
        inSubreddit = sf.checkMatch(
            "subredditData", ("username", self.username), ("subreddit", subreddit))
        if not inSubreddit:
            return (False, "Not in subreddit")

        sf.deleteData("subredditData", ("subreddit", subreddit),
                      ("username", self.username))

        return (True,)
    
    def changeUsername(self, new_username):

        username = self.username
        super().__init__(username)
        userDB = self.initializeUser()

        import os
        import pickle

        sf.selectDB("accounts")
        # Update passwords
        sf.updateData("passwords","username",new_username,("username", username))
        # Update tokens
        sf.updateData("tokens","username",new_username, ("username", username))
        # Update preferences
        userDB["settings"].updatePreference("username", new_username)
        # Update login state
        userDB["settings"].updateGlobal("loginState","username",new_username)
        # Update profile data
        self.updateProfileData("username",new_username)
        # Update subreddit data
        self.updateSubredditData("username", new_username)
        
        sf.selectDB("postdata")
        # Update subreddits
        sf.updateData("subreddits", "owner", new_username, ("owner", username))

        # Update all .dat files by the user and rename them. The name of resource link does not matter as they're never accessed directly.
        try:
            post_uuids = sf.getData("postmaps", ("author", username), "uuid", fetchAll=True)

            # Method copied and concated from func/externalFuncs.py
            def getPostIdentityAndThenGetPostFileData(uuid):
                data = userDB["postData"].getPostsBy(uuid=uuid, fetchAll=False)
                dataFile = os.path.abspath(f'./subreddits/posts/{data[1].lower()}/{data[0].lower()}+{data[2]}.dat')
                import pickle
                f = open(dataFile,"rb")
                return pickle.load(f)
            
            for uuid in post_uuids:
                post = getPostIdentityAndThenGetPostFileData(uuid)
                subreddit, author, uuid = post["subreddit"].lower(), post["author"].lower(), post["uuid"].lower()

                # Rename the .dat file
                postpath = os.path.abspath(f"./subreddits/posts/{subreddit}/{author}+{uuid}.dat")
                newpostpath = os.path.abspath(f"./subreddits/posts/{subreddit}/{new_username.lower()}+{uuid}.dat")
                os.rename(postpath, newpostpath)

                # Change the author and update the file
                post["author"] = new_username
                with open(newpostpath, 'wb') as f:
                    pickle.dump(post, f)
                
        except Exception as e: print(e)

        sf.selectDB("postdata")
        # Update postmaps
        sf.updateData("postmaps", "author", new_username, ("author", username))
        # Update honkLogs
        sf.updateData("honkLogs", "author", new_username, ("author", username))
        # Update comments
        sf.updateData("comments", "author", new_username, ("author", username))

        # Note that profile picture is not changed here. You'll need to do it manually (check profileManager)

    def deleteAccount(self):
        username = self.username

        super().__init__(username)        
        userDB = self.initializeUser()

        import os

        sf.selectDB("accounts")
        # Drop the token related to the username
        sf.deleteData("tokens", ("username", username))
        # Drop the password related to the username
        sf.deleteData("passwords", ("username", username))

        sf.selectDB("settings")
        # Drop all preferences related to the user
        sf.deleteData("preferences", ("username", username))

        sf.selectDB("userData")
        # Drop all profile data related to the user
        sf.deleteData("profileData", ("username", username))
        # Remove their subreddits
        sf.deleteData("subredditData", ("username", username))

        sf.selectDB("postData")
        # Remove all their comments
        sf.deleteData("comments", ("author", username))
        # Remove all their honks
        sf.deleteData("honklogs", ("author", username))
        # Remove all their posts
        try:
            post_uuids = sf.getData("postmaps", ("author", username), "uuid", fetchAll=True)
            post_uuids = post_uuids.fetchall()
            post_uuids = [x[0] for x in post_uuids]
            [userDB["postData"].deletePost(uuid) for uuid in post_uuids]
        except: pass
        # Surrender all their subreddits to the user named "admin"
        sf.updateData("subreddits", "owner", "admin", ("owner", username))
        
        # Log the user out if the current user is the user being deleted
        if sf.existingUser() == username:
            sf.deleteData("loginState", ("username", username))
        # Remove the user's pfp if it exists.
        if (os.path.exists(os.path.abspath("./assets/user_assets/pfps/" + username + ".png"))):
            os.remove(os.path.abspath(
                "./assets/user_assets/pfps/" + username + ".png"
                ))
        
        return (True, "Success")


class postData(dataTables):

    def getDataTableName(self):
        return "postData"

    # SUBREDDIT STUFF

    def getSubreddits(self, subreddit, column):
        sf.selectDB("postData")
        return sf.getData("subreddits", ("name", subreddit), column)

    def getAllSubreddits(self):
        sf.selectDB("postData")
        return sf.getData("subreddits", (), "name", fetchAll=True)

    def updateSubreddits(self, subreddit, column, value):
        sf.selectDB("postData")
        return sf.updateData("subreddits", column, value, ("name", subreddit))

    def makeSubreddit(self, name, description):
        # Adding rows related to subreddit
        import time
        sf.selectDB("postData")
        sf.insertData("subreddits", (name, description,
                      self.username, int(time.time())))
        sf.selectDB("userData")
        sf.insertData("subredditData", (self.username, name, int(time.time())))
        # Adding subreddit posts folder
        try:
            os.makedirs(os.path.abspath("./subreddits/posts/" +
                        name.lower() + "/"), exist_ok=True)
        except:
            pass
        # Note that tags and icons are not handled here.

    def deleteSubreddit(self, name):
        # Dropping rows related to subreddit
        sf.selectDB("postData")
        sf.executeSQL("DELETE FROM subreddits WHERE name = \"" +
                      name + "\"", commit=True)
        sf.selectDB("userData")
        sf.executeSQL(
            "DELETE FROM subredditData WHERE subreddit = \"" + name + "\"", commit=True)
        # Removing subreddit from tags
        from src.dbfunc.jsonfunc import loadData, updateFile
        tags = loadData()
        subredditTags = list(
            filter(lambda x: name in tags[x], tags.keys())).copy()
        for tag in subredditTags:
            tags[tag].remove(name)
            if not tags[tag]:
                del tags[tag]
        updateFile(tags)
        # Removing subreddit icon
        try:
            os.remove(os.path.abspath(
                "./subreddits/pfps/" + name.lower() + ".png"))
        except:
            pass
        # Removing subreddit posts folder
        try:
            os.removedirs(os.path.abspath(
                "./subreddits/pfps/" + name.lower() + "/"))
        except:
            pass
            
        

    # POST MAP STUFF

    def createPostMap(self, author, subreddit, uuid, resourceLink, dateCreated):
        sf.selectDB("postData")
        sf.insertData("postmaps", (author, subreddit,
                      uuid, resourceLink, dateCreated))

    def getPostsBy(self, subreddit=None, author=None, uuid=None, fetchAll=True, orderby="dateCreated", column="*"):
        sf.selectDB("postData")
        queries = ""

        if not subreddit and not author and not uuid:
            return None

        else:
            queries += " WHERE"

        if (subreddit):
            queries += f' subreddit = "{subreddit}" '
        if (author):
            if (queries != " WHERE"):
                queries += "AND"
            queries += f' author = "{author}" '
        if (uuid):
            if (queries != " WHERE"):
                queries += "AND"
            queries += f' uuid = "{uuid}" '
        result = sf.executeSQL(
            "SELECT " + column + " FROM POSTMAPS" + queries + "ORDER BY " + orderby + " DESC")
        return result.fetchall() if fetchAll else result.fetchone()

    def getPostsBySubredditList(self, column="*", subreddits=[], limit=50):
        # Initially when I started this project, I had an idea to optimize the posts and have unlimited posts in a single page. However, it is currently september 27 and I don't want to put this off any longer.
        # It's a good idea, but it's not the best project to implement it on. This project has it's flaws and someday I'll make a better social media with better optimization.
        # But for now, why don't we give our CPU a hard time and call this project cool because it's intricately designed?
        if not subreddits:
            return []
        sf.selectDB("postData")
        sublist = "('" + "','".join(subreddits) + "')"
        query = f"select {column} from postmaps where subreddit in " + \
            sublist + " order by dateCreated desc"
        result = sf.executeSQL(query)
        try:
            return result.fetchall()
        except:
            return []

    def deletePost(self, uuid):
        sf.selectDB("postData")

        # Method copied and concated from func/externalFuncs.py
        def getPostIdentityAndThenGetPostFileData(uuid):
            data = self.getPostsBy(uuid=uuid, fetchAll=False)
            dataFile = os.path.abspath(f'./subreddits/posts/{data[1].lower()}/{data[0].lower()}+{data[2]}.dat')
            import pickle
            f = open(dataFile,"rb")
            return pickle.load(f)

        post = getPostIdentityAndThenGetPostFileData(uuid)
        author, subreddit = post["author"].lower(), post["subreddit"]
        # Remove the resource link for it, if it exists.
        rl = sf.getData("postmaps", ("uuid", uuid), "resourceLink")[0]
        if (rl and os.path.isfile(rl)):
            os.remove(rl)
        # Remove all comments related to the post, this first because it's connected to postmaps as a foriegn key.
        sf.deleteData("comments", ("post_uuid", uuid))
        # Remove the postmap for it.
        sf.deleteData("postmaps", ("uuid", uuid), ("author", author))
        # Remove the .dat file for the post.
        os.remove(os.path.abspath(
            f'./subreddits/posts/{subreddit}/{author}+{uuid}.dat'))
        # Remove all honks related to the post.
        sf.deleteData("honklogs", ("uuid", uuid))

    def checkHonk(self, author, uuid):
        sf.selectDB("postData")
        return sf.checkMatch("honkLogs", ("author", author), ("uuid", uuid))

    def getHonks(self, uuid):
        sf.selectDB("postData")
        honks = sf.getData("honkLogs", ("uuid", uuid), "count(*)")
        return honks[0]

    def toggleHonk(self, honker, uuid, subreddit):
        
        # Note that "honker" here is the person who initiated the honk. The UUID and Subreddit is the post's data.
        sf.selectDB("postData")
        isHonked = sf.checkMatch("honkLogs", ("author", honker), ("uuid", uuid))
        honks = self.getHonks(uuid)
        post_author = sf.getData("postmaps", ("uuid", uuid), "author")[0]
        newHonks = honks - 1 if isHonked else honks + 1

        if not isHonked:
            # Add a log to honklogs, update respective post's map with the number of honks.
            sf.insertData("honkLogs", (honker, subreddit, uuid))
            sf.updateData("postmaps", "honks", newHonks, ("uuid", uuid))
            # Update the same on the author's profiledata.
            sf.selectDB("userData")
            sf.updateData("profiledata", "honks", newHonks, ("username", post_author))
            return True  # Inserted honk
        else:
            # Add a log to honklogs, update respective post's map with the number of honks.
            sf.deleteData("honkLogs", ("author", honker), ("uuid", uuid))
            sf.updateData("postmaps", "honks", newHonks, ("uuid", uuid))
            # Update the same on the author's profiledata. This was so unnecessary. I don't like this but it's too late to change the entire system.
            sf.selectDB("userData")
            sf.updateData("profiledata", "honks", newHonks, ("username", post_author))
            return False  # Removed honk
        

    # Comment stuff

    def getCommentsBy(self, post_uuid=None, username=None, orderby="dateCreated desc"):
        sf.selectDB("postData")
        query = "select * from comments where"

        if post_uuid:
            query += f" post_uuid = '{post_uuid}'"
        if username:
            query += f" author = '{username}'"

        query += f" order by {orderby}"

        comments = sf.executeSQL(query)

        commentPool = []
        commentTitles = ["author", "post_uuid",
                         "uuid", "content", "dateCreated"]
        for comment in comments:
            comment = dict(zip(commentTitles, comment))
            commentPool.append(comment)
        return commentPool

    def makeCommentForPost(self, post_uuid, content, author):
        import uuid
        COMMENT_UUID = uuid.uuid4().hex
        from time import time
        CURRENT_TIME = int(time())
        sf.selectDB("postData")
        sf.insertData("comments", (author, post_uuid,
                      COMMENT_UUID, content, CURRENT_TIME))

    def deleteComment(self, uuid):
        sf.selectDB("postData")
        sf.deleteData("comments", ("uuid", uuid))
