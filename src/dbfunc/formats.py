# every table in the database and their formats

class Format():
    def __init__ (self, table, syntax, columns):
        self.table = table 
        self.syntax = syntax 
        self.columns = columns 

# Formats:

tokens = Format(
    "tokens",

    """
    username varchar(255) PRIMARY KEY,
    token varchar(255) 
    """,

    "(username,token)"
)

passwords = Format(
    "passwords",

    """
    username varchar(255) PRIMARY KEY,
    password varchar(255)
    """,

    "(username,password)"
)

preferences = Format(
    "preferences",

    """
    username varchar(255) PRIMARY KEY,
    theme varchar(255),
    font varchar(255),
    opacity float NOT NULL
    """,

    "(username,theme,font,opacity)"
)

loginState = Format(
    "loginState",

    """
    username varchar(255)
    """,

    "(username)"
)

loginManager = Format(
    "loginManager",

    """
    defaultFont varchar(255),
    hidePasswordLogin bool,
    hidePasswordRegister bool,
    loginStyle varchar(255)
    """,

    "(defaultFont,hidePasswordLogin,hidePasswordRegister,loginStyle)"
)

profileData = Format(
    "profileData",

    """
    username varchar(255) PRIMARY KEY,
    honks int unsigned,
    accountCreated int unsigned,
    bio varchar(255)
    """,

    "(username,honks,accountCreated,bio)"
)

subredditData = Format(
    "subredditData",

    """
    username varchar(255) PRIMARY KEY,
    subreddit varchar(255),
    dateJoin int unsigned
    """,

    "(username,subreddit,dateJoin)"
)

subreddits = Format(
    "subreddits",

    """
    name varchar(255) PRIMARY KEY,
    description varchar(255),
    owner varchar(255) NOT NULL,
    dateCreated int unsigned
    """,

    "(name, description, owner, dateCreated)"
)

postmaps = Format(
    "postmaps",

    """
    author varchar(255) NOT NULL,
    subreddit varchar(255),
    uuid varchar(255) PRIMARY KEY,
    honks int DEFAULT 0,
    resourceLink varchar(255),
    dateCreated int unsigned
    """,

    "(author, subreddit, uuid, resourceLink, dateCreated)"
)

honkLogs = Format(
    "honkLogs",

    """
    author varchar(255) NOT NULL,
    subreddit varchar(255),
    uuid varchar(255) UNIQUE
    """,

    "(author, subreddit, uuid)"
)

comments = Format(
    "comments",

    """
    author varchar(255) NOT NULL,
    post_uuid varchar(255),
    uuid varchar(255) UNIQUE,
    content varchar(255) DEFAULT "",
    dateCreated int unsigned,
    FOREIGN KEY (post_uuid) REFERENCES postmaps(uuid)
    """,

    "(author, post_uuid, uuid, content, dateCreated)"
)


# Database-table map
formats = {
    "accounts": {
        "tokens": tokens,
        "passwords": passwords
    },
    "settings": {
        "preferences": preferences
    },
    "global": {
        "loginState": loginState,
        "loginManager": loginManager
    },
    "userdata": {
        "profileData": profileData,
        "subredditData": subredditData
    },
    "postdata": {
        "subreddits": subreddits,
        "postmaps": postmaps,
        "honkLogs": honkLogs,
        "comments": comments
    }
}