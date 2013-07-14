import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import urllib, re, sys, os
try:
    import StorageServer
except:
    import storageserverdummy as StorageServer
cache = StorageServer.StorageServer("plugin.audio.alsi101ru", 24)

def getHttpText(HttpUrl):
    showMessage("getHttpText", HttpUrl)
    urldata = urllib.urlopen(HttpUrl)
    content = urldata.read().decode('cp1251')
    urldata.close()
    return content
def getFileText(filename):
    urldata =  open(os.path.join(pathname,filename), 'rb')
    content = urldata.read().decode('cp1251')
    urldata.close()
    return content
def showCategorymenu(url,showcategories,showstations):
    showMessage("showCategorymenu",url)
    #content = getHttpText(siteRoot+url)
    #content = getFileText("101.ru.htm")
    content = cache.cacheFunction(getHttpText,siteRoot+url)
    #categories
    s1 = re.compile('<div class="genres-menu" id="floating_menu">\r\n<ul class="tabs vertical">\n\n(.+?)\n\n</ul>', re.DOTALL).findall(content)
    if len(s1) == 0:
        #ERROR
        print("error")
        return
    s2 = re.compile('active(.+?)a href="(.+?)">(.+?)</a></li>', re.DOTALL).findall(s1[0])
    if len(s2) == 0:
        #ERROR
        print("error")
        return    
    activelink = urllib.unquote_plus(s2[0][1]).replace("&amp;","&");
    active = s2[0][2]
    #FOUND ACTIVE CATEGORY
    if showcategories == False:
        xbmcplugin.addDirectoryItem(handler, "", xbmcgui.ListItem("[COLOR FF00FF00] "+active+" [/COLOR]"), False)
    else:
        activelink = ""
    #print(u'active: '+activelink)
    s2 = re.compile('a href="(.+?)">(.+?)</a></li>', re.DOTALL).findall(s1[0])
    if len(s2) == 0:
        #ERROR
        print("error")
        return
    if showcategories == True:
        for link, name in s2:
            link = link.replace("&amp;","&");
            name = urllib.unquote_plus(name)
            if activelink != link:
                #print("category: " +" "+ link)
                #ITERATE CATEGORIES
                item = xbmcgui.ListItem(name)
                #item.setInfo(type='music', infoLabels = {'title': cat_name, 'album': cat_url, 'genre': cat_name, 'artist': '101.RU'})
                #addDir(name,link,"0","")
                dirurl = pluginpathname+"?function=1&param="+urllib.quote_plus(link)
                #print (dirurl)
                xbmcplugin.addDirectoryItem(handler, dirurl, item, True)
        if showstations == True:
            xbmcplugin.addDirectoryItem(handler, "", xbmcgui.ListItem("[COLOR FF00FF00] ------------------------ [/COLOR]"), False)
    #stations    
    s1 = re.compile('<ul class="list channels-new( compact|) focusing-new">\r\n\r\n(.+?)\r\n\r\n</ul>', re.DOTALL).findall(content)
    if len(s1) == 0:
        #ERROR
        print("error")
        return
    s2 = re.compile('<li>\r\n<span class="focus-pad"></span>\r\n<a class="image" href="(.+?)">(|<logo>)<img src="(.+?)" alt="(.+?)">(|</logo>)</a>\r\n<h2 class="title"><a href="(.+?)">(.+?)</a></h2>\r\n<span class="focus-new">\r\n<span class="h5 icon-left listeners focus-off"><i class="icon user active"></i>(.+?)</span>\r\n<span class="h5 h7 icon-left playing focus-on"><i class="icon stream active"></i>(.+?)</span>\r\n</span>', re.DOTALL).findall(s1[0][1])
    if len(s2) == 0:
        #ERROR
        print("error")
        return
    if showstations == True:
        for stationLink,dummylogo,imgLink,alt,dummylogo,stationLink2,stationName,listeners,trackName in s2:
            #print("station: "+stationLink+" "+imgLink+" "+listeners)
            #ITERATE STATIONS
            channel = stationLink2.split("channel=")[1]
            item = xbmcgui.ListItem("[COLOR FFFFFF00] "+stationName+" [/COLOR]", iconImage = imgLink, thumbnailImage = imgLink)
            dirurl = pluginpathname+"?function=2&param="+channel
            xbmcplugin.addDirectoryItem(handler, dirurl, item, False)
    xbmcplugin.endOfDirectory(handler)
def selectStation(stationNr):
    showMessage("selectStation",stationNr)
    #http://www.101.ru/play.m3u?uid=100&bit=1
    #uid = stationNr
    #bit = 1 | 2
    url = "/play.m3u?uid="+stationNr+"&bit=1"
    #content = getHttpText(siteRoot+url)
    #content = getFileText("station100.htm")
    content = cache.cacheFunction(getHttpText,siteRoot+url)
    s1 = re.compile('{"comment":"(.+?)","file":"(.+?)"}', re.DOTALL).findall(content)
    pList = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    pList.clear()
    for comment,link in s1:
        #print (comment +" "+link)
        #ITERATE STREAMS
        #item = xbmcgui.ListItem("[COLOR FFFFFF00] "+comment+" [/COLOR]")
        item = xbmcgui.ListItem(comment)
        dirurl = link #pluginpathname+"?function=1&param="+channel
        #xbmcplugin.addDirectoryItem(handler, dirurl, item, False)
        pList.add(url=dirurl, listitem=item)
    xbmc.Player().play(pList)
    #xbmcplugin.endOfDirectory(handler)
def showMessage(header, text, times = 4000):
    xbmc.log(text)
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(header, text, times, ""))


#START
print("START")
__settings__ = xbmcaddon.Addon(id='plugin.audio.alsi101ru')
__language__ = __settings__.getLocalizedString
siteRoot= "http://101.ru"
firstCategory = "/?an=port_allchannels"

argvLen = len(sys.argv)
pluginpathname = sys.argv[0]
pathname = __settings__.getAddonInfo( "path" )

#for i in range(len(sys.argv)):
#    print(i, sys.argv[i])


handler = 0
function = "0"
inputparameter = ""
inputparameters = []
inputparameterslength = 0
category = firstCategory
#print("mode= "+mode)

if argvLen>1:
    handler = int(sys.argv[1])
if argvLen>2:
    inputparameter = sys.argv[2]
    inputparameters = re.compile('function=(.+?)&param=(.+?)$', re.DOTALL).findall(inputparameter)
    inputparameterslength = len(inputparameters)
    if inputparameterslength>0:
        inputparameters = inputparameters[0]
        inputparameterslength = len(inputparameters)
#showMessage("sys.argv[2]",str(len(function)))
if inputparameterslength>0:
    function = inputparameters[0]

#for i in range(inputparameterslength):
#    print(i, inputparameters[i])

#print ("function: "+str(function))
if function == "0" or function == "":
    if inputparameterslength>1:
        category = urllib.unquote_plus(inputparameters[1])
    showCategorymenu( category , True, True)
elif function == "1":
    if inputparameterslength>1:
        category = urllib.unquote_plus(inputparameters[1])
    showCategorymenu( category , False, True)
elif function == "2":
    station = 1
    if inputparameterslength>1:
        station = urllib.unquote_plus(inputparameters[1])
    selectStation(station)




