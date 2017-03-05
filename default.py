# -*- coding: utf-8 -*-
#/*
# * 	 Created by Sergey Tolochko (sergey.tolochko@gmail.com) on 2011-03-07.
# * 	 Copyright (c) 2011 HD-Lab (hd-lab.ru). All rights reserved.
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# */

import xbmc
import xbmcplugin
import xbmcgui
import urllib, urllib2, re, math, datetime, os
import sys

### Script constants
__scriptname__ = "Yandex Weather"
__version__    = "1.0.9"
SITE_HOSTNAME = 'pogoda.yandex.ru'
SITE_URL      = 'http://%s' % SITE_HOSTNAME
SITE_ENCODING = 'cp1251'
XBMC_ENCODING = 'utf-8'

USER_AGENT = 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60'

print "[SCRIPT] '%s: version %s' initialized!" % (__scriptname__, __version__)

url = sys.argv[0]
handle = int(sys.argv[1])
#options = sys.argv[2]
options = ?city=Kursk
print "[SCRIPT] 'URL is %s', 'Options is %s'" % (url, options)

window = xbmcgui.Window(12600)

#if (window != None and xbmc.getSkinDir() != 'skin.confluence'):
if (window != None and xbmc.getSkinDir() != 'skin.confluence'):
    thumb = os.path.join( os.path.dirname(__file__), "ya_weather.png")
    image = xbmcgui.ControlImage(25, 675, 180, 41, thumb, 0xFFFF33)
    window.addControl(image)

def getHttp(plugurl):
##    plugurl = SITE_URL + urllib.quote(relative_url)
    print '[%s] getHttp: full url=%s)' % (__scriptname__, plugurl)

    request = urllib2.Request(plugurl)
    request.add_header('User-Agent', USER_AGENT)
    request.add_header('Host', SITE_HOSTNAME)
    request.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
    request.add_header('Accept-Language', 'ru,en;q=0.9')

    o = urllib2.urlopen(request)

    http = o.read()
    o.close()
##    print '[%s] getHttp: geturl=%s, len=%s, info=%s' % (__scriptname__, o.geturl(), len(http), o.info())
    return http

def getIcon(yandex_icon):
    return {
        '1' : '10',
        '2' : '16',
        '3' : '18',
        '4' : '11',
        '5' : '26',
        '6' : '30',
        '7' : '32',
        '8' : '4',
        '9' : '39',
        '10' : '39',
        '11' : '11',
        '12' : '15',
        '13' : '14',
        '14' : '39',
        '15' : '11',
        '16' : '26',
        '17' : '43',
        '18' : '21',
        'n1' : '11',
        'n2' : '46',
        'n3' : '6',
        'n4' : '11',
        'n5' : '29',
        'n6' : '33',
        'n7' : '31',
        'n8' : '47',
        'n9' : '45',
        'n10' : '45',
        'n11' : '45',
        'n12' : '46',
        'n13' : '46',
        'n14' : '45',
        'n15' : '45',
        'n16' : '31',
        'n17' : '43',
        'n18' : '33'
    }.get(yandex_icon, '')

def getDewPoint(temperature, humidity):
    a = 17.27
    b = 237.7
    f = (a * temperature) / (b + temperature) + math.log(humidity / 100.0)
    t = b * f / (a - f)
    return int(round(t))

def getFeelsLike(temperature, wind_speed):
    return round(13.12 + 0.6215 * temperature - 11.37 * math.pow(wind_speed, 0.16) + 0.3965 * temperature * math.pow(wind_speed, 0.16))


http = getHttp('http://op.yandex.ru/data/traffic.xml')
rep = re.compile('<rate>(.+?)</rate>').findall(http)
traff_image = None
window.setProperty('TrafficIndex', '')
if len(rep) > 0:
    traff = int(rep[0])
    if traff < 4:
        traff_image = 'green.png'
    elif traff < 6:
        traff_image = 'yellow.png'
    else:
        traff_image = 'red.png'
if traff_image != None:
    window.setProperty('TrafficIndex', os.path.join( os.path.dirname(__file__), traff_image))

if (url.endswith('/find')):
    ## sample options: ?city=London
    params = dict([part.split('=') for part in options.lstrip('?').split('&')])
    ##dlg = xbmcgui.DialogProgress()
    ##dlg.create(__scriptname__, 'Выполняется поиск...')
    http = getHttp(SITE_URL + urllib.quote('/search/?text=%s' % (params['city'].decode(XBMC_ENCODING).encode(SITE_ENCODING))))
    rep = re.compile('<a href="/(.+?)/">(.+?)</a></li>').findall(http)
    for arr in rep:
        listitem = xbmcgui.ListItem(arr[1], arr[0])
        xbmcplugin.addDirectoryItem(handle, url, listitem, False)
    if len(rep) == 0:
        rep2 = re.compile('<h2><b>(.+?)</b>').findall(http)
        rep3 = re.compile('<a href="/(.+?)/details/">').findall(http)
        if (len(rep2) > 0 and len(rep3) > 0):
            listitem = xbmcgui.ListItem(rep2[0], rep3[0])
            xbmcplugin.addDirectoryItem(handle, url, listitem, False)
    xbmcplugin.endOfDirectory(handle)
elif (url.endswith('/getweather')):
    ## sample options: ?area=UPXX0016
    params = dict([part.split('=') for part in options.lstrip('?').split('&')])
    http = getHttp(SITE_URL + urllib.quote('/%s/' % (params['area'].decode(XBMC_ENCODING).encode(SITE_ENCODING))))

    rep = re.compile('<h2><b>(.+?)</b>').findall(http)
    if len(rep) > 0:
        xbmcplugin.setProperty(handle, 'Location', rep[0])

    rep = re.compile('<span>Ветер: (.+?)</span>').findall(http)
    if len(rep) > 0:
        rep2 = re.compile(', (.+?) м/с').findall(rep[0])
        if len(rep2) > 0:
            currentWind = int(rep2[0])
        xbmcplugin.setProperty(handle, 'Current.Wind', rep[0])

    rep = re.compile('<span>Влажность: (.+?)%</span>').findall(http)
    if len(rep) > 0:
        humidity = rep[0]
        xbmcplugin.setProperty(handle, 'Current.Humidity', rep[0] + '%')

    rep = re.compile('<div>(.+?)</div>(\s+?)<span>Ветер:').findall(http)
    if len(rep) > 0:
        xbmcplugin.setProperty(handle, 'Current.Condition', rep[0][0])

    rep = re.compile('<span title="Погода сейчас">(.+?) °C</span>').findall(http)
    if len(rep) > 0:
        rep2 = re.compile('(.+?), вода(.+?)').findall(rep[0].replace('−', '-'))
        if len(rep2) > 0:
            currentTemperature = rep2[0][0].replace('−', '-')
        else:
            currentTemperature = rep[0].replace('−', '-')
        xbmcplugin.setProperty(handle, 'Current.Temperature', currentTemperature)
        if humidity != None:
            xbmcplugin.setProperty(handle, 'Current.DewPoint', str(getDewPoint(int(currentTemperature), int(humidity))))
        if currentWind != None:
            xbmcplugin.setProperty(handle, 'Current.FeelsLike', str(getFeelsLike(int(currentTemperature), currentWind)))

    rep2 = re.compile('<table class="b-current-weather">(.+?)</table>', re.DOTALL).findall(http)
    if len(rep2) > 0:
        rep = re.compile('<i class="b-wea-icon g-png"><img alt="" src="http://i.yandex.st/weather/i/icons/(.+?).png" /></i>').findall(rep2[0])
        if len(rep) > 0:
            xbmcplugin.setProperty(handle, 'Current.ConditionIcon', getIcon(rep[0]))

    xbmcplugin.setProperty(handle, 'Current.UVIndex', 'N/A')

    xbmcplugin.setProperty(handle, "Day%i.Title" % 0, datetime.date.today().strftime("%A"))

    outlooks = re.compile('/></i>(.+?)</td><td class=').findall(http)
    if len(outlooks) > 0:
        xbmcplugin.setProperty(handle, "Day%i.Outlook" % 0, outlooks[0])

    temp_day = re.compile('<b>(.+?)</b></td><td class=').findall(http)
    if len(temp_day) > 0:
        xbmcplugin.setProperty(handle, "Day%i.HighTemp" % 0, temp_day[0].replace('−', '-'))

    temp_night = re.compile('<span>(.+?)</span></td><td class="').findall(http)
    if len(temp_night) > 0:
        xbmcplugin.setProperty(handle, "Day%i.LowTemp" % 0, temp_night[0].replace('−', '-'))

    outlook_icons = re.compile('<i class="b-wea-icon g-png"><img alt="" src="http://i.yandex.st/weather/i/icons/(.+?).png" /></i>(.+?)</td>').findall(http)
    if len(outlook_icons) > 0:
        xbmcplugin.setProperty(handle, "Day%i.OutlookIcon" % 0, getIcon(outlook_icons[0][0]))

    for i in range (1, 4):
        day = datetime.date.today() + datetime.timedelta(days=i)
        xbmcplugin.setProperty(handle, "Day%i.Title" %i, day.strftime("%A"))

        if len(temp_day) > 0:
            xbmcplugin.setProperty(handle, "Day%i.HighTemp" % i, temp_day[i].replace('−', '-'))
        if len(temp_night) > 0:
            xbmcplugin.setProperty(handle, "Day%i.LowTemp" % i, temp_night[i].replace('−', '-'))
        if len(outlooks) > 0:
            xbmcplugin.setProperty(handle, "Day%i.Outlook" % i, outlooks[i])
        if len(outlook_icons) > 0:
            xbmcplugin.setProperty(handle, "Day%i.OutlookIcon" % i, getIcon(outlook_icons[i][0]))
    xbmcplugin.endOfDirectory(handle)
