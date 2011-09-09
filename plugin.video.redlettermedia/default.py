import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import urllib, urllib2
import re
import urlresolver
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net

addon = Addon('plugin.video.redlettermedia', sys.argv)
xaddon = xbmcaddon.Addon(id='plugin.video.redlettermedia')
net = Net()

##### Queries ##########
play = addon.queries.get('play', None)
mode = addon.queries['mode']
url = addon.queries.get('url', None)

print 'Mode: ' + str(mode)
print 'Play: ' + str(play)
print 'URL: ' + str(url)


################### Global Constants #################################

MainUrl = 'http://www.redlettermedia.com/'
APIPath = 'http://blip.tv/players/episode/%s?skin=api'
AddonPath = xaddon.getAddonInfo('path')
IconPath = AddonPath + "/icons/"

######################################################################
                           
if play:

    html = net.http_GET(play).content
    
    #Check if it's a YouTube video first
    youtube = re.search('src="(http://www.youtube.com/embed/.+?)"',html)
    
    if youtube:
        stream_url = urlresolver.resolve(youtube.group(1))
    else:
    
        videos = re.compile('<embed.+?src="http://[a.]{0,2}blip.tv/[^#/]*[#/]{1}([^"]*)"', re.DOTALL).findall(html)
        if len(videos) > 1:
            parts = re.compile('<p>(<font size=4>|)(.+?):<br />.+?<embed.+?src="http://blip.tv/play/(.+?)"',re.DOTALL).findall(html)
            videolist = []
            for blank, name, id in parts:
                videolist.append(name) 
            dialog = xbmcgui.Dialog()
            index = dialog.select('Choose the video', videolist)
            if index >= 0:
                api_url = APIPath % videos[index]
            else:
                api_url = False       
        else:
            if videos:
                api_url = APIPath % videos[0]
            else:
                api_url = False
       
        if api_url:
            html = net.http_GET(api_url).content 
            stream_url = re.search('<role>Source</role>.+?<link type=".+?" href="(.+?)" />', html, re.DOTALL).group(1)
        else:
            stream_url = False
    
    #Play the stream
    if stream_url:
        addon.resolve_url(stream_url)  
       
    
if mode == 'main': 
    addon.add_directory({'mode': 'plinkett', 'url': MainUrl}, 'Plinkett Reviews', img=IconPath + 'plinkett.jpg')
    addon.add_directory({'mode': 'halfbag', 'url': MainUrl + 'half-in-the-bag/'}, 'Half in the Bag', img=IconPath + 'halfbag.jpg')
    addon.add_directory({'mode': 'featurefilms', 'url': MainUrl + 'films/'}, 'Feature Films')    
    addon.add_directory({'mode': 'shortfilms', 'url': MainUrl + 'shorts/'}, 'Short Films')        

elif mode == 'plinkett':
    url = addon.queries['url']
    html = net.http_GET(url).content
    
    r = re.search('Plinkett Reviews</a>.+?<ul class="sub-menu">(.+?)</ul>', html, re.DOTALL)
    if r:
        match = re.compile('<li.+?><a href="(.+?)">(.+?)</a></li>').findall(r.group(1))
    else:
        match = None

    # Add each link found as a directory item
    for link, name in match:
       addon.add_directory({'mode': 'plinkettreviews', 'url': link}, name)

elif mode == 'plinkettreviews':
    url = addon.queries['url']
    html = net.http_GET(url).content

    match = re.compile('<td.+?<a href="(.+?)".+?img src="(.+?)"').findall(html)
    for link, poster in match:
        #Very hackish way to eliminate videos I don't want in this section
        #r = re.search(url,link)
        #if not r:

        name = link.replace(url,'').replace('-',' ').replace('/',' ').title()
        if re.search(url,link):
            newlink = link
        else:
            newlink = url + link
        addon.add_video_item(newlink,{'title':name},img=poster)

elif mode == 'halfbag':
    url = addon.queries['url']
    html = net.http_GET(url).content

    match = re.compile('<td width=270><a href="(.+?)" ><img src="(.+?)"></a></td>').findall(html)
    
    episodenum = 1
    for link, poster in match:
        addon.add_video_item(link,{'title':'Episode ' + str(episodenum)},img=poster)
        #addon.add_directory({'mode': 'hbepisode', 'url': link}, 'Episode ' + str(episodenum), img=poster)
        episodenum += 1
    
elif mode == 'featurefilms':
    url = addon.queries['url']
    html = net.http_GET(url).content
    
    r = re.search('Feature Films</a>.+?<ul class="sub-menu">(.+?)</ul>', html, re.DOTALL)
    if r:
        match = re.compile('<li.+?<a href="(.+?)">(.+?)</a></li>').findall(r.group(1))
    else:
        match = None
           
    #poster = re.compile('<td><a href=".+?"><img src="(.+?)" ></a></td>').findall(html)

    #Add each link found as a directory item
    for link, name in match:
        addon.add_directory({'mode': 'film', 'url': link}, name)  

elif mode == 'shortfilms':
    url = addon.queries['url']
    html = net.http_GET(url).content

    r = re.search('Short Films</a><ul class="sub-menu">(.+?)</ul>)', html, re.DOTALL)
    if r:
        match = re.compile('<li.+?<a href="(.+?)">(.+?)</a></li>').findall(r.group(1))
            
    # Add each link found as a directory item
    for link, name in match:
       addon.add_directory({'mode': 'shortseason', 'url': link}, name)  

if not play:
    addon.end_of_directory()