"""
urlresolver XBMC Addon
Copyright (C) 2013 Vinnydude

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

Special thanks for help with this resolver go out to t0mm0, jas0npc,
mash2k3, Mikey1234,voinage and of course Eldorado. Cheers guys :)
"""

import re, xbmc
from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
from urlresolver import common

net = Net()

class movreelResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "movreel"

    def __init__(self):
        p = self.get_setting('priority') or 1
        self.priority = int(p)
        self.net = Net()
        
    def get_media_url(self, host, media_id):
        try:
            web_url = self.get_url(host, media_id)
            html = self.net.http_GET(web_url).content
            if re.search('This server is in maintenance mode', html):
                raise Exception('File is currently unavailable on the host')
            
            data = {}
            r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)"', html)
            if r:
                for name, value in r:
                    data[name] = value
                data['referer'] = web_url 
            else:
                raise Exception('Cannot find data values')
            data['btn_download']='Continue to Video'
            xbmc.sleep(2000)
            html = net.http_POST(web_url, data).content
            
            r = re.search('href="([^"]+)">Download Link', html)
            if r:
                return r.group(1)
            else:
                raise Exception('Unable to locate Download Link')

        except Exception, e:
            common.addon.log('**** Movreel Error occured: %s' % e)
            return self.unresolvable(code=0, msg='Exception: %s' % e)

    def get_url(self, host, media_id):
        return 'http://www.movreel.com/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search('//(.+?)/([0-9a-zA-Z]+)',url)
        if r:
            return r.groups()
        else:
            return False
        return('host', 'media_id')

    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return (re.match('http://(www.)?movreel.com/' +
                         '[0-9A-Za-z]+', url) or
                         'movreel' in host)
