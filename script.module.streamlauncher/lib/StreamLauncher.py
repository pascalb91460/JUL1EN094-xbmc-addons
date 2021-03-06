#-*- coding: utf-8 -*-
# version 0.1.6 par JUL1EN094
#---------------------------------------------------------------------
'''
    StreamLauncher XBMC Module
    Copyright (C) 2013 JUL1EN094

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
#---------------------------------------------------------------------
# IMPORTS
#xbmc and generals tools
import xbmc, xbmcgui, xbmcplugin, xbmcaddon 
import os, sys, shutil, re
import time
import urllib
#print_exc
from traceback import print_exc
#urlresolver
import urlresolver
#for RemoveDisallowedFilenameChars() 
import unicodedata
import string
validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
#---------------------------------------------------------------------
#streamLauncherDownloader Variables :
DOWNLOADING = 1
PAUSED = 2
STOPPED = 3
ERROR = 4
CONNECTING = 5
UNDEFINED = 6
FINISHED = 7
#---------------------------------------------------------------------
# PATH
__addonID__    = "script.module.streamlauncher"
__addon__      = xbmcaddon.Addon( __addonID__ )
__addonDir__   = xbmc.translatePath(__addon__.getAddonInfo( "path" ))
__imagesDir__  = xbmc.translatePath(os.path.join( __addonDir__, 'resources', 'images'))
__OkLogo__     = xbmc.translatePath(os.path.join(__imagesDir__,'greeninch.png'))
__ErrorLogo__  = xbmc.translatePath(os.path.join(__imagesDir__,'redx.png'))
#---------------------------------------------------------------------

class StreamLauncher():
    def __init__(self, url=False, Infos=False, Type=False, dlfolder=False, precachesize=False, intro = False, introtime = False, needdebrid = False, KeepDownloadedFile=False, useragent=False):
        #mode 
        self.mode             = False
        #url d'entrée
        self.linkurl          = False
        #need debrid
        self.needdebrid       = False
        #url débridée
        self.debridurl        = False
        #url envoyé au lecteur xbmc
        self.videoPlayerUrl   = False
        #downloader
        self.downloader       = False
        #cookie
        self.cookie           = False
        #informations de la video
        self.infos            = False
        #taille du precache
        self.precachesize     = False
        #répertoire de téléchargement global
        self.dlfolder         = False 
        #répertoire de téléchargement de la video
        self.videolocalfolder = False                
        #video d'introduction
        self.intro            = False
        #video d'introduction : durée
        self.introtime        = False
        #video : nom du fichier video en local
        self.videolocalname   = False  
        #video  : durée totale de la vidéo lue
        self.videototaltime   = False
        #video  : durée de la vidéo lue déjà visionnée
        self.videotimewatched = False
        #extension de la video
        self.extension        = False
        #Conservation du fichier téléchargé
        self.KeepDownloadedFile = KeepDownloadedFile  
        
        #-------------
        #détermination du lien : self.linkurl
        if url :
            self.linkurl = url
        else :
            self.linkurl = self.getLinkUrl()
        if not self.linkurl :
            return None
        #-------------
        #détermination des infos + infos['Title'] (necessaire) : self.infos
        if Infos :
            self.infos = Infos
        else :
            self.infos = {}
        if 'Title' not in self.infos: 
            self.infos['Title'] = self.getInfosTitle()
        if 'Title' not in self.infos:
            return None
        #-------------
        #détermination du mode : self.mode
        if (Type == 'stream') or (Type == 'local') or (Type == 'download') :
            self.mode = Type
        else :
            self.mode  = self.getMode()
        if not self.mode :
            return None
        #-------------            
        #détermination de l'intro et de sa durée
        if intro and introtime :
            self.intro     = intro
            self.introtime = introtime
        #-------------
        #détermination du répertoire de téléchargement si necessaire : self.dlfolder
        if (self.mode == 'local') or (self.mode == 'download') :
            if dlfolder :
                self.dlfolder = dlfolder
            else :
                self.dlfolder = self.getDlFolder()
            if not self.dlfolder :
                return None
        #-------------
        #détermination de la taille du precache si necessaire : self.precachesize
        if self.mode == 'local' : 
            if precachesize :
                self.precachesize = precachesize
            else :
                self.precachesize = self.getPrecacheSize()
            if not self.precachesize :
                return None
        #-------------
        #détermination du besoin de debrider : self.needdebrid
        if needdebrid :
            self.needdebrid = True
        else :
            self.needdebrid = False
        #-------------
        #détermination de l'agent utilisateur web : self.useragent
        if useragent :
            self.useragent = useragent
        else :
            self.useragent = "Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0.1"
        #-------------
        ## STREAM 
        if self.mode == 'stream' :
            self.LaunchStream() 
        ## DOWNLOAD 
        if self.mode == 'download' :
            self.LaunchDownload()                 
        ## LOCAL 
        if self.mode == 'local' : 
            self.LaunchLocal() 
        #-------------
        
    def getClassInfos(self):
        classinfos = {}
        classinfos['cookie']           = self.cookie
        classinfos['debridurl']        = self.debridurl
        classinfos['dlfolder']         = self.dlfolder
        classinfos['downloader']       = self.downloader
        classinfos['extension']        = self.extension  
        classinfos['infos']            = self.infos
        classinfos['intro']            = self.intro
        classinfos['introtime']        = self.introtime
        classinfos['linkurl']          = self.linkurl
        classinfos['mode']             = self.mode
        classinfos['needdebrid']       = self.needdebrid
        classinfos['precachesize']     = self.precachesize
        classinfos['videolocalfolder'] = self.videolocalfolder
        classinfos['videoPlayerUrl']   = self.videoPlayerUrl
        classinfos['videolocalname']   = self.videolocalname
        classinfos['videototaltime']   = self.videototaltime
        classinfos['videotimewatched'] = self.videotimewatched
        return classinfos 
    
    def getDlFolder(self):
        dialog = xbmcgui.Dialog()
        dlfolder = dialog.browse(0, 'Répertoire de téléchargement', 'files')
        return dlfolder
    
    def getInfosTitle(self):
        if self.linkurl :
            infos = {}
            infos['Title'] = self.linkurl.split('/')[-1]
            if infos['Title'] == '' :
                infos['Title'] = self.linkurl.split('/')[-2]
            return infos['Title']
        else :
            return False    
    
    def getLinkUrl(self):
        data   = False
        dialog = xbmcgui.Dialog()
        hosts  = ['Mixture','Purevid','Autres']
        host   = dialog.select('Sélectionner l\'hébergeur', hosts)
        # purevid link
        if host == 0 :
            linkprefix = 'http://www.mixturecloud.com/video=' 
            needsufix  = True
        # mixture link
        elif host == 1 :
            linkprefix = 'http://www.purevid.com/v/'
            needsufix  = True
        # autres
        else  :
            linkprefix = 'http://www.'
            needsufix  = False
        # Si on a choisi un host connu
        if needsufix :
            keyboard = xbmc.Keyboard('','Entrer l\'id de la video')
            keyboard.doModal()
            if (keyboard.isConfirmed()):
                sufix = keyboard.getText()
                if host == 1 :
                    sufix = sufix+'/'
                data = linkprefix + sufix
        # Sinon (host inconnu)
        else :       
            keyboard = xbmc.Keyboard(linkprefix)
            keyboard.doModal()
            if (keyboard.isConfirmed()):
                data = keyboard.getText()
        # On retourne l'url si définie
        if data :
            return data
        # Sinon on retourne False
        else :
            return False
        
    def getMode(self):
        dialog = xbmcgui.Dialog()
        result = dialog.select('Action', ['Télécharger et Lire', 'Télécharger en arrière plan', 'Lire sur Internet'])
        if result == 0 :
            return 'local'
        elif result == 1 :
            return 'download'
        elif result == 2 :
            return 'stream'
        else :
            return False
            
    def getPrecacheSize(self):
        dialog = xbmcgui.Dialog()
        size   = dialog.numeric(0, 'Taille du pre-cache(% du film)','10')
        if (size) and (0 <= int(size) <= 100) :
            return int(size)
        else :
            return False
    
    def getVideoLocalTree(self,url,dlfolder):
        try :
            url_no_token = url.split('?token=')[0]
            extension = url_no_token.split('.')[-1]
            try :
                video_name = self.RemoveDisallowedFilenameChars(unicode(self.infos['Title']))[:128].rstrip('. ')
            except :
                video_name = self.RemoveDisallowedFilenameChars(unicode(url_no_token.split('/')[-1].split('.')[0]))[:128].rstrip('. ')
            localfiledirectory = os.path.join(dlfolder, video_name)
            if not os.path.exists(localfiledirectory):
                os.makedirs(localfiledirectory, mode=0777)
            return localfiledirectory, video_name+'.'+extension, extension 
        except :
            print_exc()
            return False, False, False    
        
    def LaunchDownload(self) :
        try :
            launching       = True
            step            = 0
            progress_launch = xbmcgui.DialogProgress()
            progress_launch.create('Séquence de lancement video')
            #Boucle lancement d'une video
            while launching :
                if progress_launch.iscanceled() :
                    progress_launch.close()
                    launching = False
                    time.sleep(0.1) 
                #ETAPE 0  : démarrage
                if step  == 0 :
                    try :
                        progress_launch.update( 0, 'Démarrage...')
                        step = 1
                        time.sleep(0.1)
                    except :
                        print_exc()
                        progress_launch.close()
                        xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors de la création du lanceur",5000,'+__ErrorLogo__+')')
                        launching = False
                        time.sleep(0.1)        
                #ETAPE 1 : définition de videoPlayerUrl --> url qui sera téléchargée
                if step == 1 :
                    try :
                        #si débridage
                        if self.needdebrid :
                            progress_launch.update( 10, 'Débridage...')
                            self.debridurl      = urlresolver.HostedMediaFile(url=self.linkurl).resolve()
                            progress_launch.update( 30, 'Définition de l\'url de la video lue...')
                            if self.debridurl :
                                self.videoPlayerUrl = self.debridurl
                                step = 2
                                time.sleep(0.1)
                            else :
                                progress_launch.close()
                                xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors du débridage de la video",5000,'+__ErrorLogo__+')')
                                launching = False
                                time.sleep(0.1)
                        # si non débridage
                        elif not self.needdebrid :
                            progress_launch.update( 30, 'Définition de l\'url...')
                            self.videoPlayerUrl = self.linkurl
                            step = 2
                            time.sleep(0.1)
                    except :
                        print_exc()
                        progress_launch.close()
                        xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors de la définition de l\'url de la video lue",5000,'+__ErrorLogo__+')')
                        launching = False
                        time.sleep(0.1)            
                #ETAPE 2 : Définition et création du répertoire local
                if step == 2 :
                    try :
                        progress_launch.update( 35, 'Répertoire local...')
                        #Si lien fait appel à un autre plugin :
                        if self.videoPlayerUrl[:6]=='plugin' :  
                            progress_launch.update( 90, 'Lancement d\'un autre plugin XBMC...')
                            progress_launch.close()
                            launching = False
                            time.sleep(0.1)
                            xbmc.executebuiltin('XBMC.RunPlugin('+self.videoPlayerUrl+')')                  
                        #Sinon répertoire de destination :
                        else :
                            self.videolocalfolder, self.videolocalname, self.extension = self.getVideoLocalTree(self.videoPlayerUrl,self.dlfolder)
                            progress_launch.update( 50, 'Répertoire local OK...')
                            step = 3
                            time.sleep(0.1)   
                    except :
                        print_exc()
                        progress_launch.close()
                        xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors de l\'envoie de l\'url définie à XBMC",5000,'+__ErrorLogo__+')')
                        launching = False
                        time.sleep(0.1)
                #ETAPE 3 : création de l'instance du downloader
                if step == 3 :
                    try :
                        progress_launch.update( 60, 'Downloader...')
                        #création de l'instance du downloader (SimpleDownloader)
                        import SimpleDownloader as simpledownloader
                        self.downloader = simpledownloader.SimpleDownloader()
                        if '|Cookie=' in self.videoPlayerUrl :
                            self.cookie = urllib.unquote_plus(re.findall('Cookie=(.*)',self.videoPlayerUrl)[0]).replace('&',';')
                            self.videoPlayerUrl = self.videoPlayerUrl.split('|')[0]
                        params = { "url": self.videoPlayerUrl, "download_path": self.videolocalfolder, "Title": self.infos['Title'], "cookie": self.cookie }
                        progress_launch.update( 80, 'Downloader OK...')
                        step = 4
                        time.sleep(0.1)
                    except :
                        print_exc()
                        progress_launch.close()
                        xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors de la création de l\'instance du downloader",5000,'+__ErrorLogo__+')')
                        launching = False
                        time.sleep(0.1)            
                #ETAPE 4 : Download
                if step == 4 :            
                    try :
                        progress_launch.update( 90, 'Lancement du téléchargement') 
                        self.downloader.download(self.videolocalname, params) 
                        xbmcplugin.endOfDirectory(int(sys.argv[1]),succeeded=True)
                        progress_launch.close()
                        launching = False
                        time.sleep(0.1) 
                    except :
                        print_exc()
                        progress_launch.close()
                        xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors de lancement du téléchargement",5000,'+__ErrorLogo__+')')
                        launching = False
                        time.sleep(0.1)
        except :
            print_exc() 
                
    def LaunchLocal(self):
        try :
            tempurl         = False
            launching       = True
            step            = 0
            progress_launch = xbmcgui.DialogProgress()
            progress_launch.create('Séquence de lancement video')
            #Boucle lancement d'une video
            while launching :
                if progress_launch.iscanceled() :
                    progress_launch.close()
                    launching = False
                    time.sleep(0.1) 
                #ETAPE 0  : démarrage
                if step  == 0 :
                    try :
                        progress_launch.update( 0, 'Démarrage...')
                        step = 1
                        time.sleep(0.1)
                    except :
                        print_exc()
                        progress_launch.close()
                        xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors de la création du lanceur",5000,'+__ErrorLogo__+')')
                        launching = False
                        time.sleep(0.1)        
                #ETAPE 1 : définition de tempurl --> url qui sera téléchargée
                if step == 1 :
                    try :
                        #si débridage
                        if self.needdebrid :
                            progress_launch.update( 10, 'Débridage...')
                            self.debridurl = urlresolver.HostedMediaFile(url=self.linkurl).resolve()
                            progress_launch.update( 30, 'Url de la video téléchargée...')
                            if self.debridurl :
                                tempurl = self.debridurl
                                step = 2
                                time.sleep(0.1)
                            else :
                                progress_launch.close()
                                xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors du débridage de la video",5000,'+__ErrorLogo__+')')
                                launching = False
                                time.sleep(0.1)
                        # si non débridage
                        elif not self.needdebrid :
                            progress_launch.update( 30, 'Url de la video téléchargée...')
                            tempurl = self.linkurl
                            step    = 2
                            time.sleep(0.1)
                    except :
                        print_exc()
                        progress_launch.close()
                        xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors de la définition de l\'url de la video lue",5000,'+__ErrorLogo__+')')
                        launching = False
                        time.sleep(0.1)            
                #ETAPE 2 : Définition et création du répertoire local
                if step == 2 :
                    try :
                        progress_launch.update( 35, 'Répertoire local...')
                        #Si lien fait appel à un autre plugin :
                        if tempurl[:6]=='plugin' :  
                            progress_launch.update( 90, 'Lancement d\'un autre plugin XBMC...')
                            progress_launch.close()
                            launching = False
                            time.sleep(0.1)
                            xbmc.executebuiltin('XBMC.RunPlugin('+tempurl+')')                  
                        #Sinon répertoire de destination :
                        else :
                            self.videolocalfolder, self.videolocalname, self.extension = self.getVideoLocalTree(tempurl,self.dlfolder)
                            progress_launch.update( 50, 'Répertoire local OK...')
                            step = 3
                            time.sleep(0.1)   
                    except :
                        print_exc()
                        progress_launch.close()
                        xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors de l\'envoie de l\'url définie à XBMC",5000,'+__ErrorLogo__+')')
                        launching = False
                        time.sleep(0.1)
                #ETAPE 3 : création de l'instance du downloader
                if step == 3 :
                    try :
                        progress_launch.update( 60, 'Downloader...')
                        #création de l'instance du downloader (StreamLauncherDownloader)
                        import StreamLauncherDownloader as sldownloader
                        if self.extension == 'mp4' or self.extension == 'MP4':
                            self.downloader = sldownloader.MP4download(tempurl,self.videolocalfolder,useragent = self.useragent)
                        elif self.extension == 'flv' or self.extension == 'FLV':
                            self.downloader = sldownloader.FLVdownload(tempurl,self.videolocalfolder,useragent = self.useragent)
                        else :
                            self.downloader = sldownloader.DownloadFile(tempurl,self.videolocalfolder,useragent = self.useragent)                        
                        progress_launch.update( 80, 'Downloader OK...')
                        step = 4
                        time.sleep(0.1)
                    except :
                        print_exc()
                        progress_launch.close()
                        xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors de la création de l\'instance du downloader",5000,'+__ErrorLogo__+')')
                        launching = False
                        time.sleep(0.1)            
                #ETAPE 4 : Download
                if step == 4 :            
                    try :
                        progress_launch.update( 90, 'Lancement du téléchargement')
                        self.downloader.start()
                        step = 5
                        time.sleep(0.1)
                    except :
                        print_exc()
                        progress_launch.close()
                        xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors du lancement du téléchargement",5000,'+__ErrorLogo__+')')
                        launching = False
                        time.sleep(0.1) 
                #Etape 5 : Lancement de la video
                if step == 5:
                    progress_launch.close()
                    launching   = False 
                    isPrecached = self.preCache()
                    if isPrecached :
                        download_info = {}
                        download_info = self.downloader.getInfos()
                        self.PlayVideo(download_info['localfilename'])
        except :
            print_exc()        
    
    def LaunchStream(self) :
        try :
            launching       = True
            step            = 0
            progress_launch = xbmcgui.DialogProgress()
            progress_launch.create('Séquence de lancement video')
            #Boucle lancement d'une video
            while launching :
                if progress_launch.iscanceled() :
                    progress_launch.close()
                    launching = False
                    time.sleep(0.1) 
                #ETAPE 0  : démarrage
                if step  == 0 :
                    try :
                        progress_launch.update( 0, 'Démarrage...')
                        step = 1
                        time.sleep(0.1)
                    except :
                        print_exc()
                        progress_launch.close()
                        xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors de la création du lanceur",5000,'+__ErrorLogo__+')')
                        launching = False
                        time.sleep(0.1)
                #ETAPE 1 : définition de videoPlayerUrl
                if step == 1 :
                    try :
                        #si débridage
                        if self.needdebrid :
                            progress_launch.update( 25, 'Débridage de la vidéo...')
                            self.debridurl      = urlresolver.HostedMediaFile(url=self.linkurl).resolve()
                            progress_launch.update( 50, 'Définition de l\'url de la video lue...')
                            if self.debridurl :
                                self.videoPlayerUrl = self.debridurl
                                step = 2
                                time.sleep(0.1)
                            else :
                                progress_launch.close()
                                xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors du débridage de la video",5000,'+__ErrorLogo__+')')
                                launching = False
                                time.sleep(0.1)
                        # si non débridage
                        elif not self.needdebrid :
                            progress_launch.update( 50, 'Définition de l\'url de la video...')
                            self.videoPlayerUrl = self.linkurl
                            step = 2
                            time.sleep(0.1)
                    except :
                        print_exc()
                        progress_launch.close()
                        xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors de la définition de l\'url de la video lue",5000,'+__ErrorLogo__+')')
                        launching = False
                        time.sleep(0.1)
                #ETAPE 2 : Envoie de videoPlayerUrl à XBMC
                if step == 2 :
                    try :
                        progress_launch.update( 80, 'Envoie de l\'url définie à XBMC...')
                        progress_launch.close()
                        launching = False
                        time.sleep(0.1)                        
                        #Si lien fait appel à un autre plugin :
                        if self.videoPlayerUrl[:6]=='plugin' :
                            xbmc.executebuiltin('XBMC.RunPlugin('+self.videoPlayerUrl+')')                   
                        #Sinon on lance la séquence de lecture :
                        else :
                            self.PlayVideo(self.videoPlayerUrl)   
                    except :
                        print_exc()
                        progress_launch.close()
                        xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors de l\'envoie de l\'url définie à XBMC",5000,'+__ErrorLogo__+')')
                        launching = False
                        time.sleep(0.1)
        except :
            print_exc()
            return False
    
    def PlayVideo(self, url, resume=False):
        print "PLAYVIDEO"
        #check if intro needed
        isIntro = False
        if not resume and self.intro and self.introtime :
            isIntro = True    
        #chargement des infos
        icone = ''
        try:
            icone = self.infos['Thumb']
        except:
            icone = ''
        listitem = xbmcgui.ListItem(self.infos['Title'], iconImage="DefaultVideo.png", thumbnailImage=icone)
        listitem.setInfo(type='video', infoLabels=self.infos)
        #chargement de la playlist
        playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
        playlist.clear()
        if isIntro :
            playlist.add(self.intro)
        playlist.add(url,listitem=listitem)
        #lecture de la video
        xbmc.Player().play(playlist)
        #Tant que le film est en lecture
        notplaying = True 
        while notplaying :
            if xbmc.Player().isPlaying() :
                notplaying = False
            time.sleep(0.1)
        if isIntro :
            time.sleep(int(self.introtime))
        if resume :          
            xbmc.Player().seekTime(self.videotimewatched)
        notnotif = False
        if self.mode == 'local' :
            notnotif = True
        if xbmc.Player().isPlaying() :
            self.videototaltime = xbmc.Player().getTotalTime() 
            while xbmc.Player().isPlaying() : 
                self.videotimewatched = xbmc.Player().getTime()     #recup la durée  visionnée
                if self.videototaltime == 0:
                    self.videototaltime = xbmc.Player().getTotalTime() #recup la durée totale de la video (répond 0.0 si on le met plus tôt) 
                if notnotif and self.mode == 'local':
                    try :
                        download_info = self.downloader.getInfos()
                        if download_info['status'] == FINISHED :
                            xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Téléchargement terminé",10000,'+__OkLogo__+')')
                            notnotif = False
                    except :
                        pass
                time.sleep(0.5)
        #La lecture du film est stoppée 
        print 'Player stopped'
        #si on est en mode local, on gère la suite :
        if self.mode == 'local' :
            download_info = self.downloader.getInfos()
            for item in download_info.items():
                print str(item[0])+' : '+str(item[1])    
            #Si le film est complet
            if download_info['status'] == FINISHED : 
                if not self.KeepDownloadedFile :
                    if not xbmcgui.Dialog().yesno("StreamLauncher", "Fichier complet : \""+ self.infos['Title'] +"\"\nSouhaitez-vous le conserver ?") :
                        shutil.rmtree(self.videolocalfolder)
            #Sinon si le film est incomplet, on demande quoi faire
            elif download_info['status'] == DOWNLOADING  :
                #Si relance de la lecture
                if xbmcgui.Dialog().yesno("StreamLauncher", "Fichier incomplet : \""+ self.infos['Title'] +"\"\nRelancer la lecture ?") :
                    self.PlayVideo(url,resume=True)
                #Sinon on demande si on continue le téléchargement
                else :
                    #Si on ne continue pas 
                    if not xbmcgui.Dialog().yesno("StreamLauncher", "Fichier incomplet : \""+ self.infos['Title'] +"\"\nSouhaitez-vous poursuivre le téléchargement ?") :
                        self.downloader.stop()
                        notremove = True
                        while notremove:
                            try :
                                shutil.rmtree(self.videolocalfolder)
                                notremove = False
                            except :
                                pass
                                time.sleep(0.1)
                    #Sinon si on continue le téléchargement jusqu'à la fin ou l'annulation
                    else :
                        caching1 = True 
                        progress1 = xbmcgui.DialogProgress()
                        progress1.create('Téléchargement','Si vous annulez, le fichier en cache sera supprimé')
                        while caching1 :
                            download_info = self.downloader.getInfos()
                            if download_info['status'] == DOWNLOADING : 
                                progress1.update(int(download_info['downloaded'])*100/int(download_info['size']))
                                time.sleep(0.5)
                            elif download_info['status'] == FINISHED :
                                caching1 = False
                                progress1.close()
                                xbmcgui.Dialog().ok('StreamLauncher','Téléchargement terminé')
                                time.sleep(0.1)
                            if progress1.iscanceled() :
                                caching1 = False
                                progress1.close()
                                self.downloader.stop()
                                notremove = True
                                while notremove:
                                    try :
                                        shutil.rmtree(self.videolocalfolder)
                                        notremove = False
                                    except :
                                        pass
                                time.sleep(0.1)
            #Sinon si le téléchargement est en erreur
            else :
                xbmcgui.Dialog().ok('StreamLauncher','Erreur pendant le téléchargement\nLe Fichier en cache sera supprimé')
                try :
                    self.downloader.stop()
                except :
                    pass
                notremove = True
                while notremove:
                    try :
                        shutil.rmtree(self.videolocalfolder)
                        notremove = False
                    except :
                        pass
           
    def preCache(self):
        #Boucle pré-cache
        step     = 0
        caching  = True
        progress = xbmcgui.DialogProgress()
        progress.create('Mise en cache')
        while caching :
            #ANNULATION : 
            if progress.iscanceled() :
                try :
                    self.downloader.stop()
                except :
                    pass
                if os.path.exists(self.videolocalfolder) :
                    notremove = True
                    while notremove:
                        try :
                            shutil.rmtree(self.videolocalfolder)
                            notremove = False
                        except :
                            pass 
                caching = False
                time.sleep(0.1)
                return False        
            #ETAPE 3 : Connexion au fichier distant 
            elif step == 0 :  
                progress.update( 10, 'Connexion au fichier distant en cours...')          
                try : 
                    download_info = {}
                    download_info = self.downloader.getInfos()
                    if download_info['status'] != DOWNLOADING :
                        time.sleep(0.5)
                    else :           
                        step = 1
                        perc = 10
                        time.sleep(0.5)
                except :
                    print_exc()
                    xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors de la connexion au fichier distant",5000,'+__ErrorLogo__+')')
                    progress.close()
                    try :
                        self.downloader.stop()
                    except :
                        pass
                    if os.path.exists(self.videolocalfolder) :
                        notremove = True
                        while notremove:
                            try :
                                shutil.rmtree(self.videolocalfolder)
                                notremove = False
                            except :
                                pass 
                    caching = False
                    time.sleep(0.5)
                    return False
            #ETAPE 1 : pre-cache
            elif step == 1 :
                progress.update( perc, 'Pre-cache...')
                try :
                    download_info = {}
                    download_info = self.downloader.getInfos()
                    PRECACHESIZE  = (int(self.precachesize) * int(download_info['size']))/100
                    if download_info['downloaded'] < PRECACHESIZE :
                        perc = 10 + int((float(download_info['downloaded']) / PRECACHESIZE) * 90)
                        progress.update( perc, 'Pre-cache...')
                        time.sleep(0.5)
                    else :
                        progress.close()
                        time.sleep(0.5)                         
                        step = 2
                except:
                    print_exc()            
                    xbmc.executebuiltin('XBMC.Notification("StreamLauncher","Erreur lors de la connexion au fichier distant",5000,'+__ErrorLogo__+')')
                    progress.close()
                    try :
                        self.downloader.stop()
                    except :
                        pass
                    if os.path.exists(self.videolocalfolder) :
                        notremove = True
                        while notremove:
                            try :
                                shutil.rmtree(self.videolocalfolder)
                                notremove = False
                            except :
                                pass 
                    caching = False
                    time.sleep(0.5)
                    return False                
            #ETAPE 1 : pre-cache
            elif step == 2 :                
                #Lecture
                self.videolocalname = os.path.split(download_info['localfilename'])[-1]
                caching = False
                time.sleep(0.5)
                return True        
    
    def printClassInfos(self):
        try :
            ls = {}
            ls = self.getClassInfos()
            print '-----------------------------'
            print 'StreamLauncher : ClassInfos'
            print '-----------------------------'
            for item in ls.items() :
                print str(item[0])+' : '+str(item[1])
            print '-----------------------------'
        except :
            print_exc()        
    
    def RemoveDisallowedFilenameChars(self, filename):
        cleanedFilename = unicodedata.normalize('NFKD', filename).encode('utf-8', 'ignore')
        return ''.join(c for c in cleanedFilename if c in validFilenameChars)
