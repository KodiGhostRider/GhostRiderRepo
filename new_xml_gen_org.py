# -*- coding: utf-8 -*-
#kodi israel advanced repo generator for python 3.4 win/linux 
#Still not in alph (soon)
#Dunes.
#version 0.8b
import os 
import re
import shutil
import sys 
import hashlib
from hashlib import md5
import zipfile
from io import StringIO
import requests
import subprocess
import urllib.request
from urllib.request import urlopen
import urllib
import xml.etree.ElementTree as ET
UpdateOnly=False
repo_xml="addons.xml"
force_update=0
local_repo_folder="repo"
github_addon_list="githubrepolist.txt"
BlackListAddonFIle="blacklist.txt"
repos_to_scan_folder="repositories"
def download_folder_url(url,repo_xml,local_repo_folder): #grabs a folder compare to local repo and download new or updated addons
    
    base="temp"
    skip=url.strip("/").count("/")
    skip=skip-2
    wget_cmd=" -nH -P "+base+" -m --reject index.html --cut-dirs="+str(skip)+"  " +url
    try :
        print("Grabbing from URL:",url," \n this will take some time please grab Some Coffee")
        FNULL = open(os.devnull, 'w')
        subprocess.call(["wget","-nH","-P",base,"-m","--reject","index.html","--cut-dirs="+str(skip),url], stdout=FNULL, stderr=subprocess.STDOUT)
    except Exception as e:
        print("wget failed is it installed ? ",e)
    addons = os.listdir( base )
    for addon_folder in addons:
        new_dict=dict()
        old_dict=dict()            
        if not os.path.isdir(base+os.sep+addon_folder) ==True:
            os.remove(base+os.sep+addon_folder)            
            continue
        print(addon_folder)
        tree_old = ET.parse(repo_xml)
        root_old = tree_old.getroot()
        try:
            tree_new = ET.parse(base+ os.sep + addon_folder +os.sep + "addon.xml")
            root_new = tree_new.getroot()
        except Exception as e:
            print("folder is not an addon ",addon_folder)
            continue
        for element_new in root_new.iter("addon"):
            new_dict[element_new.attrib['id']] = element_new.attrib['version']
            for element_old in root_old.iter("addon"):
                old_dict[element_old.attrib['id']] = element_old.attrib['version']  
            for key in new_dict:
                if compblacklist(key)==True: 
                    print(key," is in blacklist - ")
                    continue
                if key in old_dict.keys():
                    if new_dict[key]>old_dict[key]:
                        print("updating addon from folder:",key)
                        shutil.make_archive(local_repo_folder+os.sep+key+os.sep+key+"-"+new_dict[key],'zip',base,key)
                        print("remove folder",key)
                        shutil.rmtree(base+os.sep+key)
                    else:
                        print("remove folder",key)
                        shutil.rmtree(base+os.sep+key)                        
                        
                else: 
                    if UpdateOnly==False:
                        print("adding addon from folder: ",key,"-",new_dict[key])
                        try: 
                            os.makedirs(local_repo_folder+os.sep+key)
                        except Exception as e:
                            print("folder exists:", base+os.sep+key)
                        shutil.make_archive(local_repo_folder+os.sep+key+os.sep+key+"-"+new_dict[key],'zip',base,key)
                        print("remove folder",key)
                        shutil.rmtree(base+os.sep+key)                            
        
    
def cmp_github_with_repo(repo_xml,URL,local_repo_folder):
    if len(URL.rstrip("/").split("/"))>5:
        addon_xml=URL.replace("github.com","raw.githubusercontent.com").replace("/tree/","/") +"/addon.xml"
    else:
        addon_xml= URL + "/raw/master/addon.xml"
    BLAF=getblacklist(BlackListAddonFIle)
    new_dict=dict()
    old_dict=dict()    
    try:
        new_XML = ET.ElementTree(file=urlopen(addon_xml) )
        root_new=new_XML.getroot()
        try:
            tree_old = ET.parse(repo_xml)
            root_old = tree_old.getroot()
        except Exception as e:
            print('error with :' ,URL)
            print('cant get repo xml !\n%s\n' % e)
            return -1
    except Exception as e:
        print(addon_xml)
        print(URL)
        print('cant get github xml !\n%s\n' % e)
        return -1         
    for element_new in root_new.iter("addon"):
            new_dict[element_new.attrib['id']] = element_new.attrib['version']
            for element_old in root_old.iter("addon"):
                old_dict[element_old.attrib['id']] = element_old.attrib['version']  
            for key in new_dict:
                if compblacklist(key)==True: 
                    print(key," is in blacklist - ")
                    continue
                if key in old_dict.keys():
                    if new_dict[key]>old_dict[key] or 2>1:
                        print("adding addon from github:",key)
                        Craeate_addon_from_github(URL, local_repo_folder) #adding zip from github when addon  is updated
                else: 
                    if UpdateOnly==False:
                        print("Updading addon from github: ",key,"-",new_dict[key])
                        Craeate_addon_from_github(URL, local_repo_folder) #adding zip from github when addon is new 
    
    
    
    
    
def Craeate_addon_from_github(URL,local_repo_folder):
    archive_suffix="/archive/master.zip"
    print(URL)
    addonname=URL.strip('/').split('/')[-1]
    if not os.path.exists(local_repo_folder+os.sep+addonname):
        print("Making folder for addon in repo: ",addonname)
        os.makedirs(local_repo_folder+os.sep+addonname)                   
    download_file(URL+archive_suffix,local_repo_folder+os.sep+addonname+os.sep+"master.zip")
    try: 
        xml_frm_file,ziptype=zipfilehandler(local_repo_folder+os.sep+addonname+os.sep+"master.zip")
    except Exception as e:
        print("cannot create a zip from githuburl ",URL)
        return 
    root = ET.fromstring(xml_frm_file) 
    for element in root.iter("addon"):
        addon_name=element.attrib['id'] 
        addon_version=element.attrib['version']
    try:
        currntzip=zipfile.ZipFile(local_repo_folder+os.sep+addonname+os.sep+"master.zip")
        currntzip.extractall(local_repo_folder+os.sep+addonname+os.sep)
        currntzip.close()
        shutil.move(local_repo_folder+os.sep+addonname+os.sep+addon_name+"-master",local_repo_folder+os.sep+addonname+os.sep+addon_name)
        os.remove(local_repo_folder+os.sep+addonname+os.sep+"master.zip")
        shutil.make_archive(local_repo_folder+os.sep+addon_name+os.sep+addon_name+"-"+addon_version,'zip',local_repo_folder+os.sep+addon_name,addon_name)
        shutil.rmtree(local_repo_folder+os.sep+addonname+os.sep+addon_name)
    except Exception as e:
        print("could not save fil ",addonname)
def getreposlist(repos_to_scan_folder):
    addons = os.listdir( repos_to_scan_folder )
    for addon in addons:
        if ( addon == ".git" or addon == ".svn"  or  not addon.endswith(".zip")): 
            addons.remove(addon)
    return addons
    
def compblacklist(addon):
    BLAF=getblacklist(BlackListAddonFIle)
    for addon_black in BLAF:
        if addon.find(addon_black.strip()) !=-1: #return true if found
            return True
    return(False)
            
def getblacklist(BlackListAddonFIle):
    fileh=[]
    try:
        with open(BlackListAddonFIle,'r') as f:
            for line in f:
                fileh.append(line)
    except Exception as e:
        return None
    return fileh
    
def extract_art_from_zip(base):
    base="repo"
    addons = os.listdir( base )
    for addon in addons:
            try:
                    # skip any file or .git folder or .svn folder
                    if ( not os.path.isdir(base+os.sep+addon ) or addon == ".git" or addon == ".svn" or compblacklist(addon)==True): continue
                    # get zip files
                    _zip = os.listdir( base+ os.sep+ addon )
                    _zip = [ i for i in _zip if i.startswith( addon ) and i.endswith( ".zip" )]
                    # get sort files
                    _zip = [ (int(re.search('\d+', i).group(0)), i) for i in _zip ]
                    _zip.sort()
                    if(len(_zip))>1:
                                        _zip = [ i[1] for i in _zip ]
                                        _zip = os.path.join( base+ os.sep+ addon, _zip[-1] )
                    else:
                                        _zip=_zip[0][1]
                                        _zip = os.path.join( base+ os.sep+ addon, _zip )

                    # read zip file
                    zip = zipfile.ZipFile( open( _zip, 'rb' ) )
                    # get xml file
                    zip_file = zip.namelist()
                    # read xml file
                    try: 
                        zip.extract(addon+"/fanart.jpg",path=base+os.sep )
                    except Exception as e:
                        #print("no fanart in :",addon)
                        os.sep.strip()
                    try:
                        zip.extract(addon+"/icon.png",path=base+os.sep )
                    except Exception as e:
                        #print("no icon in :",addon)
                        os.sep.strip()
                    # close zip file
                    zip.close()
            except Exception as e:
                print("cant scan ",e)
def download_file(url,path):
	local_filename=path
    # NOTE the stream=True parameter
	print("Downloding zip from:",url," To Path: ",path)
	try:
		r = requests.get(url, stream=True,timeout=5)
		print("Saving: ", path)
		with open(local_filename, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024): 
				if chunk: # filter out keep-alive new chunks
					f.write(chunk)
					f.flush()
	except Exception as e:
		print("failed to get file:",url)
		return -1
	return local_filename



def zipfilehandler(zipfilename ):#get addon.xml from zipfile 
        
        xml_text=""
        try:
                czip = zipfile.ZipFile(zipfilename , mode="r")
        except Exception as e:
                        print('An error occurred reading zip!\n%s\n' % e)
                        return 
        for filea in czip.namelist():
                rc=str.find(filea,"addon.xml")
                if rc != -1:
                        fs_xm=czip.open(filea,'r')
                        for line in fs_xm.readlines():
                                xml_text+=line.decode("utf-8") 
                        return xml_text,filea.split(".")[0]
        print("zip does not contain addon.xml: ",zipfilename)
        return -1
#Compare ripos url with our own and return a dict of changed or new items 
def compare_repos(old_xml, new_xml_url,UpdateOnly): 
        BLAF=getblacklist(BlackListAddonFIle)
        new_dict=dict()
        headers={ 
        'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0',
		'Referer':'http://www.google.com'
		}
        old_dict=dict()
        target_dict=dict()
        req = urllib.request.Request(new_xml_url,headers={'User-Agent':'Mozilla/5.0','Referer':''})
        try:
                rcp=urllib.request.urlopen(req)
                new_XML = ET.parse(rcp)
                root_new=new_XML.getroot()
        except Exception as e:
                print('cant open new addon.xml!\n%s\n %s' % (e,new_xml_url))
                return -1        
        try:
                tree_old = ET.parse(old_xml)
                root_old = tree_old.getroot()
        except Exception as e:
                print ('cant open old addon.xml url !\n%s\n' % e)
                return -1
        for element_new in root_new.iter("addon"):
                new_dict[element_new.attrib['id']] = element_new.attrib['version']
        for element_old in root_old.iter("addon"):
                old_dict[element_old.attrib['id']] = element_old.attrib['version']  
        for key in new_dict:
            if compblacklist(key)==True: 
                print(key," is in blacklist - ")
                continue
            if key in old_dict.keys():
                if new_dict[key]>old_dict[key]:
                    target_dict[key]=new_dict[key] #better
            else: 
                if UpdateOnly==False:
                    target_dict[key]=new_dict[key]
        return target_dict
                
        


def get_repo_zip(src_repo,dst_repo,addon_dict):
        try:
                for key in addon_dict:
                    print("Downloading %s version:%s",key,addon_dict[key])
                    if not os.path.exists(dst_repo+os.sep+key):
                        print("Making folder for addon in repo: ",key)
                        os.makedirs(dst_repo+os.sep+key)                    
                    zip_url=src_repo +os.sep +key+os.sep+key+"-"+addon_dict[key]+".zip"
                    download_file(zip_url,dst_repo+os.sep+key+os.sep+key+"-"+addon_dict[key]+".zip" )
                    print(zip_url)
                    #grab file to our ripo        
        except Exception as e:
                print ('no updated to repo!\n%s\n' % e)
                return -1 

def get_repo_data(repo_zip):
    xml,ziptype=zipfilehandler(repo_zip)
    root = ET.fromstring(xml)
    for element in root.iter('datadir'):
        type_of_data=element.attrib['zip']
    for elem in root.iter('addon'):
        print('%s %s version: %s' % (elem.attrib['id'], elem.tag, elem.attrib['version']))
    for thing in root.findall('extension'):
        if not thing.find("datadir") is None:
            data_dir_text=thing.find("datadir").text
        if not thing.find("info") is None:
            xml_addon_txt=thing.find("info").text
    try :
        return xml_addon_txt,data_dir_text,type_of_data
    except Exception as e:
        print ("xml for repository: ",repo_zip, "is not a repository")
        sys.exit(0) 


class Generator:#update addons.xml to reflect local addon folder
        """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file. Must be run from the root of
        the checked-out repo. Only handles single depth folder structure.
        """
        def __init__( self ):
                # generate files
                self._generate_addons_file()
                self._generate_md5_file()
                # notify user
                print("Finished updating addons xml and md5 files")

        def _generate_addons_file( self ):
                # addon list
                base="repo"
                addons = os.listdir( base )
                # final addons text
                addons_xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n"
                # loop thru and add each addons addon.xml file
                for addon in addons:
                        try:
                                # skip any file or .git folder or .svn folder
                                if ( not os.path.isdir(base+os.sep+addon ) or addon == ".git" or addon == ".svn" ): continue
                                # get zip files
                                _zip = os.listdir( base+ os.sep+ addon )
                                _zip = [ i for i in _zip if i.startswith( addon ) and i.endswith( ".zip" ) ]
                                # get sort files								
                                _zip = [ (int(re.search('\d+', i).group(0)), i) for i in _zip ]
                                _zip.sort()
                                if(len(_zip))>1:
                               	        _zip = [ i[1] for i in _zip ]
                                        _zip = os.path.join( base+ os.sep+ addon, _zip[-1] )
                                else:
                                        _zip=_zip[0][1]
                                        _zip = os.path.join( base+ os.sep+ addon, _zip )
                                # read zip file
                                try:
                                     zip = zipfile.ZipFile( open( _zip, 'rb' ) )
                                except Exception as e:
                                    print("zip is not ok: " + _zip)
                                    continue
                                xml_file = zip.namelist()
                                xml_file = [i for i in xml_file if i.endswith(addon+"/addon.xml" )][0]
                                # read xml file
                                xml_file = zip.read( xml_file )
                                # close zip file
                                zip.close()
                                # split lines for stripping
                                xml_lines = xml_file.splitlines()
                                # new addon
                                addon_xml = ""
                                # loop thru cleaning each line
                                try: 
                                    RST=ET.fromstring(xml_file)
                                    for line in xml_lines:
                                        # skip encoding format line
                                        if ( str(line,'utf-8').find( "<?xml" ) >= 0 ):
                                            if(str(line,'utf-8').find( "><" ) >= 0 ):
                                                addon_xml +="<" + str(line,'utf-8').split("><").rstrip()[1] + "\n"											 
                                            continue
                                        # add line
                                        addon_xml += str(line,'utf-8').rstrip() + "\n"
                                        # we succeeded so add to our final addons.xml text
                                    addons_xml += addon_xml.rstrip() + "\n\n"
                                except Exception as e:
                                    print("failed to add the xml from addon " +addon)
                        except Exception as e:
                                # missing or poorly formatted addon.xml
                                print("Excluding for %s" % (  e, ))
                                # clean and add closing tag
                addons_xml = addons_xml.strip() + u"\n</addons>\n"
                # save file
                self._save_file( addons_xml.encode( "UTF-8" ), file="addons.xml" )

        def _generate_md5_file( self ):
                try:
                        # create a new md5 hash
                        md5file=open( "addons.xml",'rb').read()
                        m = hashlib.md5(md5file)
                        # save file
                        self._save_file( m.hexdigest().encode('utf-8'), file="addons.xml.md5")
                except Exception as e:
                        # oops
                        print("An error occurred creating addons.xml.md5 file!\n%s" % ( e, ))
        def _save_file( self, data, file ):
                try:
                        # write data to the file
                        open( file, "w", encoding='utf-8' ).write( data.decode("utf-8") )
                except Exception as e:
                        # oops
                        print("An error occurred saving %s file!\n%s" % ( file, e, ))


def update_local_repo_from_all_repos(): #main repos scan loop
    for addon_repo in getreposlist(repos_to_scan_folder):
        new_repo_xml,new_repo_data,repo_data_type_is_zip=get_repo_data(repos_to_scan_folder+os.sep+addon_repo)
        if repo_data_type_is_zip is True or repo_data_type_is_zip == "true":
            print(addon_repo,"- ziptype is ",repo_data_type_is_zip)
            print(new_repo_xml)
            trg_dict=compare_repos("addons.xml",new_repo_xml,UpdateOnly)
            get_repo_zip(new_repo_data,local_repo_folder,trg_dict)
        else:
            trg_dict_zip=compare_repos("addons.xml",new_repo_xml,UpdateOnly)
            download_folder_url(new_repo_data,repo_xml,local_repo_folder)
	
def main():
    Generator() #executing this creates the repos addon.xml and reflect changes in zip files
    
    def RUN():
        update_local_repo_from_all_repos()     
        for URL in open(github_addon_list,'r').readlines():
            if URL.startswith('http'):
                cmp_github_with_repo(repo_xml,URL.strip(),local_repo_folder)
        extract_art_from_zip(local_repo_folder)
        Generator() # running again to reflect changes in zip file 
    RUN()
    Generator()

main()


