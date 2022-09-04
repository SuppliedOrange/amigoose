from email.mime import image
from typing import final
from PIL import Image, ImageChops, ImageDraw
from pathlib import Path
from . import externalFuncs
import os

def convertToPFP(imagePath,resize:tuple,cacheOutput:tuple=()):
    """
    Converts any image to a circular PNG (PFP-styled in my words)\n\n

    imagePath - String - Path for the image being converted\n
    resize - Tuple (Int, Int) - Width and Height for the image to be resized to\n
    cacheOutput - Tuple (name, type) - To cache the output\n
    """

    # Checking for cache existence
    basename = externalFuncs.getBasename(imagePath)

    illegalNames = ["defaultGoose.png", "goose.png", "joystick.png", "pizza.png", "travel.png"]

    if not cacheOutput and not basename in illegalNames:

        subredditCache = externalFuncs.getPath("./assets/remote_assets/cache/subreddit_pfps/subreddit@" + basename)
        userCache = externalFuncs.getPath("./assets/remote_assets/cache/user_pfps/user@" + basename)

        try: hasSubredditCache = (checkImage(subredditCache) and (getSize(subredditCache) == resize))
        except FileNotFoundError: hasSubredditCache = None
        try: hasUserCache = (checkImage(userCache) and (getSize(userCache) == resize))
        except FileNotFoundError: hasUserCache = None

        if (hasSubredditCache): return subredditCache
        elif (hasUserCache): return userCache

    # Cropping/Masking
    def crop_to_circle(im):
        bigsize = (im.size[0] * 3, im.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(im.size, Image.ANTIALIAS)
        mask = ImageChops.darker(mask, im.split()[-1])
        im.putalpha(mask)

    im = resizeImage(imagePath, resize) # Resizing image
    crop_to_circle(im)
    fp = externalFuncs.getPath("./assets/remote_assets/remotePFP.png")
    im.save(Path(fp)) # Save to remote image path.

    if cacheOutput:
        # cacheOutput -> (name, type "subreddit" || "user")
        createCache(*cacheOutput)

    return fp

def resizeImage(imagePath,resize:tuple,save=False):
    """
    To resize the image to a certain scale and returns the output as a PIL Image\n
    It can also be returned as a remote file\n\n
    
    imagePath - String - Path to image\n
    resize - Tuple (Int, Int) - Width and Height to resize to\n
    save - Boolean - To save the file to a remote image and return the path
    """
    im = Image.open(imagePath).convert('RGBA')
    im = im.resize(resize)
    if not save: return im
    fp = externalFuncs.getPath("./assets/remote_assets/remotePFP.png")
    im.save(Path(fp))
    return fp

def getImageDimensions(imagePath):
    if not checkImage(imagePath): return None
    im = Image.open(imagePath)
    width,height = im.size
    return (width,height)

def getPFP(username):
    """
    Returns the image path of the avatar of a specified user or the defaultGoose PFP path\n
    username - String - Username of the person's avatar to return
    """
    path = externalFuncs.getPath("./assets/user_assets/pfps/" + username.lower() + ".png")
    return path if checkImage(path) else externalFuncs.getPath("./assets/amigoose_assets/defaultGoose.png")

def getIcon(subreddit):
    """
    Returns the image path of the icon of a specified subreddit\n
    subreddit - String - Name of the subreddit's avatar to return
    """
    path = externalFuncs.getPath("./subreddits/pfps/" + subreddit.lower() + ".png")
    return path if checkImage(path) else None

def getLogo(logoType="dark"):
    """
    Get the path for the Amigoose logo\n\n
    logoType - String - "dark" or "light"
    """
    path = externalFuncs.getPath(f"./assets/amigoose_assets/amigoose_logo_{logoType}.png")
    return convertToB64(path)

def checkImage(imagePath):
    """
    Checks if a certain image path is valid\n\n
    imagePath - String - Path to the image being checked
    """
    if (imagePath and not type(imagePath) == str): return False
    if not Path(imagePath).is_file():
        return False
    try:
        im = Image.open(imagePath)
    except:
        return False
    return True

def loadResizedImageB64(imagePath, thresholdPixels):
    """
    Resizes the image dynamically and returns the Base64 data for it\n
    Please don't ask how this works. My brain works in ways I myself cannot understand\n\n

    imagePath - string - Path to the image
    """
    w,h = getImageDimensions(imagePath)
    y = max({w,h})
    #y = w if w > h else h
    y = (y // thresholdPixels) or 1
    w,h = [int(x / y) for x in (w,h)]
    return convertToB64(resizeImage(imagePath,(w,h),save=True))

def convertImage(origin,final):
    """
    Copies an image file from one place to another and allows you to also change it's name and extension\n\n

    origin - String - Path to the original file\n
    final - String - Path to the destination file, the file for it to be saved as
    """
    im = Image.open(origin)
    im.save(final)
    return final

def checkVideo(videoPath):
    if (videoPath and not type(videoPath) == str): return False
    if not Path(videoPath).is_file():
        return False
    extension = os.path.splitext(videoPath)[1]
    validVideoExtensions = (".mp4",".wav",".mov",".avi",".flv",".webm",".wmv")
    return extension in validVideoExtensions

def saveAsPFP(imagePath,name,subreddit=False):
    """
    Saves a subreddit's icon or a user's avatar to storage\n\n

    imagePath - String - Path to the image being saved as a PFP/Icon\n
    name - String - Name of the subreddit/user\n
    subreddit - Boolean - Whether we are dealing with a subreddit or not (defaults to user)
    """
    destDir = externalFuncs.getPath("./" + ("subreddits" if subreddit else "assets/user_assets") + "/pfps/")
    return copyFile(imagePath,destDir,name.lower() + ".png")

def copyFile(originPath,finalDir,basename=None):
    """
    Copies a file from one place to another. 
    """
    import shutil
    originBasename = os.path.basename(originPath)
    basename = basename or originBasename
    finalPath = finalDir + "\\" + basename
    if (os.path.isfile(finalPath)):
        # Found a file that already exists in it's place? OVERWRITE!
        os.remove(finalPath)
    shutil.copy(originPath,finalDir)
    os.rename(finalDir + "\\" + originBasename, finalPath)
    return finalPath

def convertToB64(filename):
    """
    Converts an image to Base 64 bytes format\n
    Used for changing images on windows real-time\n\n
    
    filename - String - File path of the image being converted to Base 64
    """
    import base64
    try:
        contents = open(filename, 'rb').read()
        return base64.b64encode(contents)
    except Exception as error:
        print(error)
        return None

def createCache(name, cacheType):
    """
    Creates a cache of a subreddit's icon or user's avatar and stores it in assets/remote_assets/cache/\n\n
    
    name - String - Name of the user/subreddit\n
    cacheType - String - 'subreddit' or 'user'\n
    """
    import shutil
    destDir = externalFuncs.getPath("./assets/remote_assets/cache/" + ("subreddit_pfps" if cacheType=="subreddit" else "user_pfps"))
    remotePath = externalFuncs.getPath("./assets/remote_assets/remotePFP.png")
    prefix = "subreddit@" if cacheType == "subreddit" else "user@"
    destFile = destDir + "\\" + prefix + name.lower() + ".png"

    # Check if image already exists, return that image.
    if (checkImage(destFile)):
        if (identicalImages(destFile,remotePath)):
            return destFile
        else: # If it's not an identical image, replace that image.
            os.remove(destFile)

    # If there are more than 99 items in cache, delete the first one.
    allDirectoryItems = [name for name in os.listdir(destDir) if os.path.isfile(name)]
    if (len(allDirectoryItems) > 99): os.remove(destDir + "\\" + allDirectoryItems[0])

    shutil.copy(remotePath, destDir)
    os.rename(destDir + "\\remotePFP.png", destFile)
    return destFile

def identicalImages(path1,path2):
    """
    Checks if two images are exactly identical\n\n

    path1 - String - Path of first image file\n
    path2 - String - Path of second image file\n
    """
    from PIL import Image
    im1,im2 = Image.open(path1).convert('RGB'), Image.open(path2).convert('RGB')
    return (list(im1.getdata()) == list(im2.getdata()))

def getSize(imagePath):
    """
    Gets the width/height of a certain image\n\n
    imagePath - String - Path to the image
    """
    from PIL import Image
    try:
        im= Image.open(imagePath).convert('RGB')
    except:
        return (0,0)
    width,height = im.size
    return (width,height)

def getFirstFrameOfVideo(videoPath):
    """
    Gets the first frame (image) of a video and saves it to a remote image and returns the image path.\n\n
    videoPath - String - Path to the video
    """
    from cv2 import VideoCapture, imwrite
    vidcap = VideoCapture(videoPath)
    success,image = vidcap.read()
    remotePath = externalFuncs.getPath("./assets/remote_assets/remotePFP.png")
    imwrite(remotePath, image) 
    return remotePath

'''
def honkImage(imageButtonElement, honkButtonElement):
    import time

    imagePath = honkButtonElement.metadata["url"]
    originalImage = Image.open(imagePath)
    w,h = getImageDimensions(imagePath)
    w,h = int(w/2), int(h/2)
    toResize = (w,w) if w<h else (h,h)
    honkImage = resizeImage(externalFuncs.getPath("./assets/amigoose_assets/HONK.png"), toResize)

    back_image = originalImage.copy()
    back_image.paste(honkImage, (0,h))
    remote_image_path = externalFuncs.getPath("./assets/remote_assets/remotePFP.png")
    back_image.save(remote_image_path)
    
    imageButtonElement.update(image_data=convertToB64(remote_image_path))
    imageButtonElement.update(image_data=convertToB64(imagePath))
'''