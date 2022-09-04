def parentHandler(parent:dict):
    """
    parent -> {
        Type - Type of window to open - String
        LayoutArgs - Arguments for the parent window layout - String | Tuple
        WatchArgs - Arguments for watching the parent window - String | Tuple
    }
    """
    def handleParameters(key):
        return parent[key] if key in parent.keys() else None
        
    parentType = handleParameters("type")
    layoutArgs = handleParameters("layoutArgs")
    watchArgs = handleParameters("watchArgs")
    
    if parentType == "profile":
        from src.app.profile.profile import profile
        profile.start(argsWindow=layoutArgs, argsWatch=watchArgs)

    elif parentType == "subreddit":
        from src.app.subreddit.subreddit import subreddit
        subreddit.start(argsWindow=layoutArgs, argsWatch=watchArgs)
    
    elif parentType == "search":
        from src.app.home.search.search import search
        search.start(argsWindow=layoutArgs)
    
    elif parentType == "createPostTitle":
        from src.app.post.createPost.createPostTitle import createPostTitle
        createPostTitle.start(argsWindow=layoutArgs, argsWatch=watchArgs)
    
    elif parentType == "viewPostText":
        from src.app.post.viewPost.viewPostText import viewPostText
        viewPostText.start(argsWindow=layoutArgs, argsWatch=watchArgs)
    
    elif parentType == "viewPostImage":
        from src.app.post.viewPost.viewPostImage import viewPostImage
        viewPostImage.start(argsWindow=layoutArgs, argsWatch=watchArgs)