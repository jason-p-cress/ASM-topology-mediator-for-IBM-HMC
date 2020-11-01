#!/usr/bin/python

#######################################################
#
# IBM HMC REST mediator for topology inclusion into ASM
#
# 10/17/20 - Jason Cress (jcress@us.ibm.com)
#
#######################################################


import base64
import json
import re
from pprint import pprint
import os
import ssl
import xml.dom.minidom
import urllib2
import urllib
import xml.etree.ElementTree as ET
import csv
from collections import defaultdict
from multiprocessing import Process

def loadHmcServers(filepath, sep=',', comment_char='#'):

   ##########################################################################################
   #
   # This function reads the HMC server configuration file and returns a list of dictionaries
   #
   ##########################################################################################

   hmcList = []
   lineNum = 0
   with open(filepath, "rt") as f:
      for line in f:
         hmcDict = {}
         l = line.strip()
         if l and not l.startswith(comment_char):
            values = l.split(sep)
            if(len(values) < 4):
               print "Malformed server configuration entry on line number: " + str(lineNum)
            else:
               hmcDict["server"] = values[0]
               hmcDict["port"] = values[1]
               hmcDict["user"] = values[2]
               hmcDict["password"] = values[3]
               print str(hmcDict)
               hmcList.append(hmcDict)
         lineNum = lineNum + 1

   print "returning " + str(len(hmcList)) + " HMC servers to discover"
   return(hmcList)

def verifyAsmConnectivity(asmDict):
 
   ##################################################################
   #
   # This function verifies that the ASM server credentials are valid
   #
   ##################################################################

   return True

def loadAsmServer(filepath, sep=",", comment_char='#'):

   ################################################################################
   #
   # This function reads the ASM server configuration file and returns a dictionary
   #
   ################################################################################

   lineNum = 0
   with open(filepath, "rt") as f:
      for line in f:
         asmDict = {}
         l = line.strip()
         if l and not l.startswith(comment_char):
            values = l.split(sep)
            if(len(values) < 5):
               print "Malformed ASM server config line on line " + str(lineNum)
            else:
               asmDict["server"] = values[0]
               asmDict["port"] = values[1]
               asmDict["user"] = values[2]
               asmDict["password"] = values[3]
               asmDict["tenantid"] = values[4]
               if(verifyAsmConnectivity(asmDict)):
                  return(asmDict)
               else:
                  print "Unable to connect to ASM server " + asmDict["server"] + " on port " + asmDict["port"] + ", please verify server, username, password, and tenant id in " + mediatorHome + "config/asmserver.conf"
         
def createAsmRestListenJob(jobName):

   #####################################
   #
   # This function is currently not used
   #
   #####################################
   
   method = "POST"

   requestUrl = 'https://' + asmServerDict["server"] + ':' + asmServerDict["port"] + '/1.0/rest-observer/jobs/listen'

   jsonResource = '"unique_id":"HMC", "type": "listen", "parameters":{"provider": "HMC"}}'

   authHeader = 'Basic ' + base64.b64encode(asmServerDict["user"] + ":" + asmServerDict["password"])
   print "auth header is: " + str(authHeader)
   print "pushing the following json to ASM: " + jsonResource

   try:
      request = urllib2.Request(requestUrl, jsonResource)
      request.add_header("Content-Type",'application/json')
      request.add_header("Accept",'application/json')
      request.add_header("Authorization",authHeader)
      request.add_header("X-TenantId",asmServerDict["tenantid"])
      request.add_header("Provider","HMC")
      request.get_method = lambda: method

      response = urllib2.urlopen(request)
      xmlout = response.read()
      return True

   except IOError, e:
      print 'Failed to open "%s".' % requestUrl
      if hasattr(e, 'code'):
         print 'We failed with error code - %s.' % e.code
      elif hasattr(e, 'reason'):
         print "The error object has the following 'reason' attribute :"
         print e.reason
         print "This usually means the server doesn't exist,",
         print "is down, or we don't have an internet connection."
      return False

def createAsmResource(resourceDict):

   #######################################################
   #
   # Function to send a resource to the ASM rest interface
   #
   #######################################################

   method = "POST"

   #requestUrl = 'https://' + asmServerDict["server"] + ':' + asmServerDict["port"] + '/1.0/topology/resources'

   requestUrl = 'https://' + asmServerDict["server"] + ':' + asmServerDict["port"] + '/1.0/rest-observer/rest/resources'

   authHeader = 'Basic ' + base64.b64encode(asmServerDict["user"] + ":" + asmServerDict["password"])
   print "auth header is: " + str(authHeader)
   jsonResource = json.dumps(resourceDict)
   print "creating the following resource in ASM: " + jsonResource

   try:
      request = urllib2.Request(requestUrl, jsonResource)
      request.add_header("Content-Type",'application/json')
      request.add_header("Accept",'application/json')
      request.add_header("Authorization",authHeader)
      request.add_header("X-TenantId",asmServerDict["tenantid"])
      request.add_header("JobId","HMC")
      request.get_method = lambda: method

      response = urllib2.urlopen(request)
      xmlout = response.read()
      return True

   except IOError, e:
      print 'Failed to open "%s".' % requestUrl
      if hasattr(e, 'code'):
         print 'We failed with error code - %s.' % e.code
      elif hasattr(e, 'reason'):
         print "The error object has the following 'reason' attribute :"
         print e.reason
         print "This usually means the server doesn't exist,",
         print "is down, or we don't have an internet connection."
      return False


def createAsmConnection(connectionDict):

   #########################################################
   #
   # Function to send a connection to the ASM rest interface
   #
   #########################################################
   
   method = "POST"

   requestUrl = 'https://' + asmServerDict["server"] + ':' + asmServerDict["port"] + '/1.0/rest-observer/rest/references'

   authHeader = 'Basic ' + base64.b64encode(asmServerDict["user"] + ":" + asmServerDict["password"])
   print "auth header is: " + str(authHeader)
   jsonResource = json.dumps(connectionDict)
   print "adding the following connection to ASM: " + jsonResource

   try:
      request = urllib2.Request(requestUrl, jsonResource)
      request.add_header("Content-Type",'application/json')
      request.add_header("Accept",'application/json')
      request.add_header("Authorization",authHeader)
      request.add_header("X-TenantId",asmServerDict["tenantid"])
      request.add_header("JobId","HMC")
      request.get_method = lambda: method

      response = urllib2.urlopen(request)
      xmlout = response.read()
      return True

   except IOError, e:
      print 'Failed to open "%s".' % requestUrl
      if hasattr(e, 'code'):
         print 'We failed with error code - %s.' % e.code
      elif hasattr(e, 'reason'):
         print "The error object has the following 'reason' attribute :"
         print e.reason
         print "This usually means the server doesn't exist,",
         print "is down, or we don't have an internet connection."
      return False
 

def shortenTag(tag):

   #############################################################################
   #
   # Function to chop off the xml namespace from the tag for easier manipulation
   #
   #############################################################################

   PATTERN = re.compile('^\{.*?\}(.*)')
   match = PATTERN.match(tag)
   shorttag = match.group(1)
   return shorttag



def hmcLogin(hmcDict):

   ##########################################################
   #
   # Function to login to the HMC
   #
   # Returns the API session key to use in subsequent queries
   #
   ##########################################################

   loginXml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><LogonRequest xmlns="http://www.ibm.com/xmlns/systems/power/firmware/web/mc/2012_10/" schemaVersion="V1_1_0"><Metadata><Atom/></Metadata><UserID kb="CUR" kxe="false">' + hmcDict["user"] + '</UserID><Password kb="CUR" kxe="false">' + hmcDict["password"] + '</Password></LogonRequest>'
   #dom = xml.dom.minidom.parseString(loginXml)
   #print dom.toprettyxml()

   method = "PUT"

   requestUrl = 'https://' + hmcDict["server"] + ':' + hmcDict["port"] + '/rest/api/web/Logon'

   #print requestUrl

   try:
      request = urllib2.Request(requestUrl, loginXml)
      request.add_header("Content-Type",'application/vnd.ibm.powervm.web+xml; type=LogonRequest')
      request.add_header("Accept",'application/vnd.ibm.powervm.web+xml; type=LogonResponse')
      request.get_method = lambda: method

      response = urllib2.urlopen(request)
      xmlout = response.read()

      # I am writing out the responses to keep a record of the API keys so if the code breaks before it logs out then I can go back and explicitly logout
      fh = open(mediatorHome + "/log/" + hmcServer + "-login-successes.txt", "a")
      fh.write(xmlout)
      fh.write("\n")
      fh.close


   except IOError, e:
      print 'Failed to open "%s".' % requestUrl
      if hasattr(e, 'code'):
         print 'We failed with error code - %s.' % e.code
      elif hasattr(e, 'reason'):
         print "The error object has the following 'reason' attribute :"
         print e.reason
         print "This usually means the server doesn't exist,",
         print "is down, or we don't have an internet connection."
      return False

   root = ET.fromstring(xmlout)

   apikey = root[1].text
   return(apikey)

def hmcLogout(hmcDict):

   ################################
   #
   # Function to log out of the HMC
   #
   ################################

   logoutXml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><LogoffRequest xmlns="http://www.ibm.com/xmlns/systems/power/firmware/web/mc/2012_10/" schemaVersion="V1_1_0"><Metadata><Atom/></Metadata><UserID kb="CUR" kxe="false">' + hmcDict["user"] + '</UserID><Password kb="CUR" kxe="false">' + hmcDict["password"] + '</Password></LogoffRequest>'
   #dom = xml.dom.minidom.parseString(loginXml)
   #print dom.toprettyxml()

   method = "DELETE"

   requestUrl = 'https://' + hmcDict["server"] + ':' + hmcDict["port"] + '/rest/api/web/Logon'

   #print requestUrl

   try:
      request = urllib2.Request(requestUrl, logoutXml)
      request.add_header("Content-Type",'application/vnd.ibm.powervm.web+xml; type=LogoffRequest')
      request.add_header("Accept",'application/vnd.ibm.powervm.web+xml; type=LogoffResponse')
      request.add_header("X-API-Session", hmcDict["sessionkey"])
      request.get_method = lambda: method

      response = urllib2.urlopen(request)
      #print response.read()

      # I am writing out the responses to keep a record of the API keys so if the code breaks before it logs out then I can go back and explicitly logout
      fh = open(mediatorHome + "/log/" + hmcServer + "-login-successes.txt", "a")
      fh.write("successfully logged out of session with key" + hmcDict["sessionkey"])
      fh.write("\n")
      fh.close

   except IOError, e:
      print 'Failed to open "%s".' % requestUrl
      if hasattr(e, 'code'):
         print 'We failed with error code - %s.' % e.code
      elif hasattr(e, 'reason'):
         print "The error object has the following 'reason' attribute :"
         print e.reason
         print "This usually means the server doesn't exist,",
         print "is down, or we don't have an internet connection."
      return False


def getUomData(hmcDict, uomType):

   ###########################################
   #
   # This function grabs uom data from the HMC
   #
   ###########################################

   #print "logging in..."
   hmcDict["sessionkey"] = hmcLogin(hmcDict)
   #print "Session key is " + hmcDict["sessionkey"]
 
   method = "GET"

   requestUrl = 'https://' + hmcDict["server"] + ':' + hmcDict["port"] + '/rest/api/uom/' + uomType

   #print requestUrl

   try:
      request = urllib2.Request(requestUrl)
      request.add_header("Content-Type",'application/vnd.ibm.powervm.uom+xml; Type=' + uomType)
      request.add_header("Accept",'application/vnd.ibm.powervm.uom+xml; Type=' + uomType)
      request.add_header("X-API-Session", hmcDict["sessionkey"])
      request.get_method = lambda: method

      response = urllib2.urlopen(request)
      managedSystemData = response.read()

   except IOError, e:
      print 'Failed to open "%s".' % requestUrl
      if hasattr(e, 'code'):
         print 'We failed with error code - %s.' % e.code
      elif hasattr(e, 'reason'):
         print "The error object has the following 'reason' attribute :"
         print e.reason
         print "This usually means the server doesn't exist,",
         print "is down, or we don't have an internet connection."
      return False

   #print "logging out..."
   hmcLogout(hmcDict)

   return(managedSystemData)

def getCna(id):

   ########################################################
   #
   # returns a dict with client network adapter information
   #
   ########################################################

   cnaDict = {}

   tagsOfInterest = { "MACAddress", "LocalPartitionID", "PortVLANID", "AssociatedVirtualSwitch" }

   cnaDict["cnaId"] = id

   msXpath = ".//*[{http://www.w3.org/2005/Atom}id='" + id + "']/{http://www.w3.org/2005/Atom}content/{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}ClientNetworkAdapter/*"
   for entry in cnaRoot.findall(msXpath):
      shorttag = shortenTag(entry.tag)
      if(shorttag in tagsOfInterest):
         if(shorttag == "AssociatedVirtualSwitch"):
            for avs in entry.getchildren():
               shorttag = shortenTag(avs.tag)
               PATTERN = re.compile('.*/VirtualSwitch/(.*)')
               match = PATTERN.match(avs.attrib["href"])
               associatedVswitchId = match.group(1)
               print "found associated virtual switch with the id: " +associatedVswitchId + ", connecting to " + id
               connectionDict = { "_fromUniqueId": id, "_toUniqueId": associatedVswitchId, "_edgeType": "connectedTo"}
               connectionsList.append(connectionDict)
         if(shorttag == "VirtualNetworks"):
            for avs in entry.getchildren():
               shorttag = shortenTag(avs.tag)
               PATTERN = re.compile('.*/VirtualNetwork/(.*)')
               match = PATTERN.match(avs.attrib["href"])
               associatedVnetworkId = match.group(1)
               print "found associated virtual network with the id: " +associatedVnetworkId + ", connecting to " + id
               connectionDict = { "_fromUniqueId": id, "_toUniqueId": associatedVnetworkId, "_edgeType": "connectedTo"}
               connectionsList.append(connectionDict)
         else:
            #print "Property " + shorttag + " = " + entry.text + ", attrib = " + str(entry.attrib) 
            cnaDict[shorttag] = entry.text

## relevant ASM key mappings

   cnaDict["uniqueId"] = id
   cnaDict["name"] = cnaDict["MACAddress"]
   cnaDict["entityTypes"] = [ "networkinterface" ]

   return cnaDict

def getVios(id):

   #########################################
   #
   # returns a dict with VIOS information
   #
   #########################################

   viosDict = {}

   tagsOfInterest = { "LogicalSerialNumber", "OperatingSystemVersion", "AssociatedManagedSystem" }

   viosDict["viosId"] = id

   msXpath = ".//*[{http://www.w3.org/2005/Atom}id='" + id + "']/{http://www.w3.org/2005/Atom}content/{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}VirtualIOServer/*"
   for entry in viosRoot.findall(msXpath):
      shorttag = shortenTag(entry.tag)
      if(shorttag in tagsOfInterest):
         if(shorttag == "AssociatedManagedSystem"):
            PATTERN = re.compile('.*/ManagedSystem/(.*)')
            match = PATTERN.match(entry.attrib["href"])
            viosDict["AssociatedManagedSystem"] = match.group(1)
         else:
            print "getting VIOS property " + shorttag
            viosDict[shorttag] = entry.text

   ## relevant ASM key mappings

   viosDict["uniqueId"] = id
   viosDict["name"] = "VIOS" + viosDict["LogicalSerialNumber"]
   viosDict["entityTypes"] = [ "switch" ]


   return viosDict


def getVswitch(id):

   #########################################
   #
   # returns a dict with vSwitch information
   #
   #########################################

   vSwitchDict = {}

   tagsOfInterest = { "SwitchID", "SwitchMode", "SwitchName" }

   vSwitchDict["vSwitchId"] = id

   msXpath = ".//*[{http://www.w3.org/2005/Atom}id='" + id + "']/{http://www.w3.org/2005/Atom}content/{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}VirtualSwitch/*"
   for entry in vSwitchRoot.findall(msXpath):
      shorttag = shortenTag(entry.tag)
      if(shorttag in tagsOfInterest):
         print "getting vSwitch property " + shorttag
         vSwitchDict[shorttag] = entry.text

## relevant ASM key mappings

   vSwitchDict["uniqueId"] = id
   vSwitchDict["name"] = vSwitchDict["SwitchName"]
   vSwitchDict["entityTypes"] = [ "switch" ]

   return vSwitchDict 

def getVnetwork(id):

   #########################################
   #
   # returns a dict with vNetwork information
   #
   #########################################

   vNetworkDict = {}

   tagsOfInterest = { "NetworkID", "NetworkMode", "NetworkName" }

   vNetworkDict["vNetworkId"] = id

   msXpath = ".//*[{http://www.w3.org/2005/Atom}id='" + id + "']/{http://www.w3.org/2005/Atom}content/{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}VirtualNetwork/*"
   for entry in vNetworkRoot.findall(msXpath):
      shorttag = shortenTag(entry.tag)
      #if(shorttag in tagsOfInterest):
      #   print "getting vNetwork property " + shorttag
      if(shorttag == 'AssociatedSwitch'):
         print "here is an associated switch, let's see if we can grab it..."
         PATTERN = re.compile('.*/VirtualSwitch/(.*)')
         match = PATTERN.match(entry.attrib["href"])
         associatedVswitchId = match.group(1)
         print "found associated virtual switch with the id: " +associatedVswitchId + ", connecting this interface"
         vNetworkDict["AssociatedSwitch"] = associatedVswitchId
         connectionDict = { "_fromUniqueId": id, "_toUniqueId": associatedVswitchId, "_edgeType": "connectedTo"}
         connectionsList.append(connectionDict)
      else:
         vNetworkDict[shorttag] = entry.text

## relevant ASM key mappings

   vNetworkDict["uniqueId"] = id
   vNetworkDict["name"] = vNetworkDict["NetworkName"]
   vNetworkDict["entityTypes"] = [ "network" ]

   return vNetworkDict 

def getLpar(id):

   #######################################################################
   #
   # returns a dict with lpar information, including where lpar is running
   #
   #######################################################################

   lparDict = {}

   tagsOfInterest = {"LogicalSerialNumber", "OperatingSystemVersion", "PartitionID", "PartitionName", "PartitionState", "PartitionType", "PartitionUUID", "ResourceMonitoringIPAddress", "AssociatedManagedSystem", "MACAddressPrefix", "MigrationState"}
  
   lparDict["lparId"] = id

   msXpath = ".//*[{http://www.w3.org/2005/Atom}id='" + id + "']/{http://www.w3.org/2005/Atom}content/{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}LogicalPartition/*"
#   print "LPARROOT: " + str(lparRoot)
   for entry in lparRoot.findall(msXpath):
      shorttag = shortenTag(entry.tag)
      if(shorttag in tagsOfInterest):
         if(shorttag == "AssociatedManagedSystem"):
            print "found associatedManagedSystem for LPAR"
            PATTERN = re.compile('.*/ManagedSystem/(.*)')
            match = PATTERN.match(entry.attrib["href"])
            associatedManagedSystemId = match.group(1)
            print "found associated managed system with the id: " + associatedManagedSystemId + ", connecting it to " + id
            connectionDict = { "_fromUniqueId": id, "_toUniqueId": associatedManagedSystemId, "_edgeType": "runsOn"}
            connectionsList.append(connectionDict)
            lparDict[shorttag] = associatedManagedSystemId
         else:
            print "Adding property " + entry.text + " to LPAR definition"
            lparDict[shorttag] = entry.text

## relevant ASM key mappings

   lparDict["uniqueId"] = id
   lparDict["name"] = lparDict["PartitionName"]
   lparDict["entityTypes"] = [ "vm" ]

   return lparDict


def getManagedSystem(id):

   ###########################################################################   
   #
   # returns a dict with managed system information based on managed system id
   #
   ###########################################################################   

   managedSystemDict = {}

   managedSystemDict["managedSystemId"] = id

   tagsOfInterest = {"Hostname", "SystemName", "PrimaryIPAddress", "SystemFirmware", "SystemLocation", "SystemType", "Model", "SerialNumber", "MachineType", "State"}

   msXpath = ".//*[{http://www.w3.org/2005/Atom}id='" + id + "']/{http://www.w3.org/2005/Atom}content/{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}ManagedSystem"
   #print msXpath
   for objects in uomRoot.findall(msXpath):
      for objectitem in objects:
         #print(objectitem.tag, objectitem.attrib, objectitem.text)
         shorttag = shortenTag(objectitem.tag)
         #print "shorttag is " + shorttag
         if(shorttag in tagsOfInterest):
            managedSystemDict[shorttag] = objectitem.text
            #print "system " + shorttag + " is " + str(objectitem.text)
   msXpath = ".//*[{http://www.w3.org/2005/Atom}id='" + id + "']/{http://www.w3.org/2005/Atom}content/{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}ManagedSystem/{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}MachineTypeModelAndSerialNumber/*"
   for mtype in uomRoot.findall(msXpath):
      shorttag = shortenTag(mtype.tag)
      if(shorttag in tagsOfInterest):
         managedSystemDict[shorttag] = mtype.text

   ## relevant ASM key mappings

   managedSystemDict["uniqueId"] = id
   managedSystemDict["name"] = managedSystemDict["Hostname"]
   managedSystemDict["entityTypes"] = [ "server" ]


   #print(managedSystemDict)
   return(managedSystemDict)

def dispatchHmc(hmcDict, asmServerDict):
   
   ###########################################################################
   #
   # Main dispatcher function for HMC discovery
   #
   # This is spawned as its own process up to the configured number of threads
   #
   ###########################################################################

   global managedSystemList
   global lparList
   global vSwitchList
   global viosList
   global cnaList
   global trunkList
   global seaList
   global connectionsList
   global hmcServer
   global logXmlOutput

   hmcServer = hmcDict["server"]
   
   if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
   getattr(ssl, '_create_unverified_context', None)):
      ssl._create_default_https_context = ssl._create_unverified_context
   
   getManagedSystemData = 1
   getLogicalPartitionData = 1
   getVswitchData = 1
   getVnetworkData = 1
   getClientNetworkAdapterData = 1
   getViosData = 1
   sendToAsm = 1
   logXmlOutput = 1
   
   managedSystemData = getUomData(hmcDict, "ManagedSystem")

   if(logXmlOutput == 1):
      fh = open(mediatorHome + "/log/" + hmcServer + "-managedSystemData.xml", "w")
      fh.write(managedSystemData)
      fh.write("\n")
      fh.close

   logicalPartitionData = getUomData(hmcDict, "LogicalPartition")
   
   if(logXmlOutput == 1):
      fh = open(mediatorHome + "/log/" + hmcServer + "-logicalPartitionData.xml", "w")
      fh.write(managedSystemData)
      fh.write("\n")
      fh.close
   
   
   #createAsmRestListenJob("HMC")
   #exit()
   
   ###############################################
   #
   # This first parses systems managed by this HMC
   #
   ###############################################

   global uomRoot
   
   uomRoot = ET.fromstring(managedSystemData)
   print uomRoot.tag
   
   namespaces = {'http://www.w3.org/2005/Atom'}
   
   managedSystemList = []
   connectionsList = []
   trunkList = []
   seaList = []
   
   managedSystemCount = 0
   for entry in uomRoot.findall('.//{http://www.w3.org/2005/Atom}entry'):
      print "Entry #" + str(managedSystemCount)
      # grab managed system properties
      for managedSystem in entry:
         if(managedSystem.tag == '{http://www.w3.org/2005/Atom}id'):
            id=managedSystem.text
            print "found entry with id of " + id
            managedSystemList.append(getManagedSystem(id))
      #print "The dict id for this managed system is " + managedSystemList[managedSystemCount]["managedSystemId"] + " which should match my id of " + id
   
   
   
      managedSystemCount = managedSystemCount + 1
   
   print "Number of managed systems: " + str(len(managedSystemList))
   #print managedSystemList
   
   
   ######################
   #
   # Next we parse the LPARs
   #
   ###########################################
   
   lparList = []
   global lparRoot
   
   if getLogicalPartitionData == 1:
   
      lparCount = 0
      #print "Logical Partition Data Returned: " + logicalPartitionData
      lparRoot = ET.fromstring(logicalPartitionData)
      for lparEntry in lparRoot.findall('.//{http://www.w3.org/2005/Atom}entry'):
         print "lpar entry #" + str(lparCount)
         for lparData in lparEntry:
            if(lparData.tag == '{http://www.w3.org/2005/Atom}id'):
               lparId=lparData.text
               print "found lpar entry with id of " + lparId
               lparList.append(getLpar(lparId))
         lparCount = lparCount + 1
   
      #print lparList
      print "Number of LPARs: " + str(len(lparList))
   
   ###############################################
   #
   # For each managed system, obtain its vSwitches
   #
   ###############################################
   
   vSwitchList = []
   global vSwitchRoot
   
   if getVswitchData == 1:
   
      for ms in managedSystemList:
         print "obtaining virtual switches for managed system id: " + ms["managedSystemId"]
         virtualSwitchData = getUomData(hmcDict, "/ManagedSystem/" + ms["managedSystemId"] + "/VirtualSwitch")
         try:
            vSwitchRoot = ET.fromstring(virtualSwitchData)
            vSwitchCount = 0
            for vSwitchEntry in vSwitchRoot.findall('.//{http://www.w3.org/2005/Atom}entry'):
               newSwitch = {}
               #print "vSwitch entry #" + str(vSwitchCount)
               for vSwitchData in vSwitchEntry:
                  if(vSwitchData.tag == '{http://www.w3.org/2005/Atom}id'):
                     vSwitchId = vSwitchData.text
                     #print "found vSwitch entry with id of " + vSwitchId
                     connectionDict = { "_fromUniqueId": vSwitchId, "_toUniqueId": ms["managedSystemId"], "_edgeType": "runsOn"}
                     connectionsList.append(connectionDict)
                     newSwitch = getVswitch(vSwitchId)
                     newSwitch["SwitchName"] = newSwitch["SwitchName"] + " on " + ms["Hostname"]
                     vSwitchList.append(newSwitch)
                     #vSwitchList.append(getVswitch(vSwitchId))
                     #vSwitch[vSwitchCount]["SwitchName"] = vSwitch[vSwitchCount]["SwitchName"] + " on " + ms["SystemName"]
   
               vSwitchCount = vSwitchCount + 1
            if(logXmlOutput == 1):
               fh = open(mediatorHome + "/log/" + hmcServer + "-" + ms["name"] + "-virtualSwitchData.xml", "w")
               fh.write(virtualSwitchData)
               fh.write("\n")
               fh.close
         except:
            print "No vSwitch data returned for managed system id: "  + ms["managedSystemId"]
   
         #print virtualSwitchData
      
   ############################################################################################
   #
   # For each LPAR, obtain client network adapters, and connect them to the appropriate vSwitch
   #
   ############################################################################################
   
   cnaList = []
   global cnaRoot
   
   if getClientNetworkAdapterData == 1:
      for lp in lparList:
         print "obtaining client network adapters for lpar: " + lp["lparId"]
         clientNetworkAdapterData = getUomData(hmcDict,"/LogicalPartition/" + lp["lparId"] + "/ClientNetworkAdapter")
         #print clientNetworkAdapterData
   
         try:
            cnaRoot = ET.fromstring(clientNetworkAdapterData)
            cont = 1
         except:
            print "No data or malformed data returned from querying CNA information for lpar: " + lp["lparId"]
            print "LPAR state is " + lp["PartitionState"]
            cont = 0
   
         if(cont == 1):
            cnaCount = 0
            for cnaEntry in cnaRoot.findall('.//{http://www.w3.org/2005/Atom}entry'):
               #print "cna entry #" + str(cnaCount)
               for cnaProp in cnaEntry:
                  if(cnaProp.tag == '{http://www.w3.org/2005/Atom}id'):
                     cnaId = cnaProp.text
                     #print "found cna entry with id of " + cnaId
                     cnaList.append(getCna(cnaId))
                     connectionDict = { "_fromUniqueId": lp["lparId"], "_toUniqueId": cnaId, "_edgeType": "contains"}
                     connectionsList.append(connectionDict)
   
               cnaCount = cnaCount + 1
   
      if(logXmlOutput == 1):
         fh = open(mediatorHome + "/" + hmcServer + "-clientNetworkAdapterData.xml", "w")
         fh.write(clientNetworkAdapterData)
         fh.write("\n")
         fh.close
   
   ################################################
   #
   # For each managed system, obtain VIOS instances
   #
   ################################################
   
   viosList = []
   global viosRoot
   
   if getViosData == 1:
   
      for ms in managedSystemList:
         print "getting vios network info for managed system named " + ms["Hostname"]
         viosData = getUomData(hmcDict, "/ManagedSystem/" + ms["managedSystemId"] + "/VirtualIOServer")
         try:
            viosRoot = ET.fromstring(viosData)
            cont = 1
         except:
            print "No VIOS data returned for managed system " + ms["Hostname"]
            cont = 0

         if(logXmlOutput == 1): 
            fh = open(mediatorHome + "/log/" + hmcServer + "-" + ms["Hostname"] + "-viosData.xml", "w")
            fh.write(viosData)
            fh.write("\n")
            fh.close
   
   
         if(cont == 1):
            viosCount = 0
            for viosEntry in viosRoot.findall('.//{http://www.w3.org/2005/Atom}entry'):
               for viosProp in viosEntry:
                  if(viosProp.tag == '{http://www.w3.org/2005/Atom}id'):
                     viosId = viosProp.text
                     viosList.append(getVios(viosId))
                     connectionDict = { "_fromUniqueId": viosId, "_toUniqueId": ms["managedSystemId"], "_edgeType": "runsOn" }
                     connectionsList.append(connectionDict)
               print "checking for any trunk adapters..." 

               ########################
               # Get trunk port entries
               ########################
   
               msXpath = ".//*[{http://www.w3.org/2005/Atom}id='" + viosId + "']/{http://www.w3.org/2005/Atom}content/{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}VirtualIOServer/{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}TrunkAdapters/{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}TrunkAdapter"
               for trunkEntry in viosRoot.findall(msXpath):
                  trunkDict = {}
                  for trunkProp in trunkEntry:
                     trunkDict[shortenTag(trunkProp.tag)] = trunkProp.text
                     print "trunkProp.tag is " + trunkProp.tag
                     if(trunkProp.tag == '{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}DeviceName'):
                        print "found trunk entry device: " + trunkProp.text
                        trunkDict["name"] = "Trunk-" + trunkProp.text
                        trunkDict["uniqueId"] = "Trunk-" + trunkProp.text + viosId
                     if(trunkProp.tag == '{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}AssociatedVirtualSwitch'):
                        print "here is an associated virtual switch, let's see if we can grab it..."
                        for avs in trunkProp.getchildren():
                           shorttag = shortenTag(avs.tag)
                           print shorttag
                           PATTERN = re.compile('.*/VirtualSwitch/(.*)')
                           match = PATTERN.match(avs.attrib["href"])
                           associatedVswitchId = match.group(1)
                           print "found associated virtual switch with the id: " +associatedVswitchId + ", connecting this interface"
                           trunkDict["AssociatedVirtualSwitch"] = associatedVswitchId
   
                  trunkDict["entityTypes"] = [ "networkinterface" ]
                  connectionDict = { "_fromUniqueId": viosId, "_toUniqueId": trunkDict["uniqueId"], "_edgeType": "contains" }
                  connectionsList.append(connectionDict)
                  trunkList.append(trunkDict)
   
                  if(trunkDict.has_key("AssociatedVirtualSwitch")):
                     connectionDict = { "_fromUniqueId": trunkDict["uniqueId"], "_toUniqueId": associatedVswitchId, "_edgeType": "connectedTo"}
                     connectionsList.append(connectionDict)
   
               #####################################
               # Get Shared Etherenet Adapters (SEA)
               #####################################
   
               msXpath = ".//*[{http://www.w3.org/2005/Atom}id='" + viosId + "']/{http://www.w3.org/2005/Atom}content/{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}VirtualIOServer/{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}SharedEthernetAdapters/{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}SharedEthernetAdapter"
               for seaEntry in viosRoot.findall(msXpath):
                  seaDict = {}
                  for seaProp in seaEntry:
                     seaDict[shortenTag(seaProp.tag)] = seaProp.text
                     print "seaProp.tag is " + seaProp.tag
                     if(seaProp.tag == '{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}DeviceName'):
                        print "found sea entry device: " + seaProp.text
                        seaDict["name"] = "SEA-" + seaProp.text
                        seaDict["uniqueId"] = "SEA-" + seaProp.text + "-" + viosId
                     if(seaProp.tag == '{http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/}AssociatedVirtualSwitch'):
                        print "here is an associated virtual switch, let's see if we can grab it..."
                        for avs in seaProp.getchildren():
                           shorttag = shortenTag(avs.tag)
                           print shorttag
                           PATTERN = re.compile('.*/VirtualSwitch/(.*)')
                           match = PATTERN.match(avs.attrib["href"])
                           associatedVswitchId = match.group(1)
                           print "found associated virtual switch with the id: " +associatedVswitchId + ", connecting this interface"
                           seaDict["AssociatedVirtualSwitch"] = associatedVswitchId
   
                  seaDict["entityTypes"] = [ "networkinterface" ]
                  connectionDict = { "_fromUniqueId": viosId, "_toUniqueId": seaDict["uniqueId"], "_edgeType": "contains" }
                  connectionsList.append(connectionDict)
                  print "Appending SEA: " + str(seaDict)
                  seaList.append(seaDict)
   
                  if(seaDict.has_key("AssociatedVirtualSwitch")):
                     connectionDict = { "_fromUniqueId": seaDict["uniqueId"], "_toUniqueId": associatedVswitchId, "_edgeType": "connectedTo"}
                     connectionsList.append(connectionDict)
   

               viosCount = viosCount + 1
   
            print "number of VIOS for server " + ms["Hostname"] + " is " + str(viosCount)

   ######################################################
   #
   # For each managed system, obtain its virtual networks
   #
   ######################################################

   vNetworkList = []
   global vNetworkRoot

   if getVnetworkData == 1:

      for ms in managedSystemList:
         print "obtaining virtual networks for managed system id: " + ms["managedSystemId"]
         virtualNetworkData = getUomData(hmcDict, "/ManagedSystem/" + ms["managedSystemId"] + "/VirtualNetwork")
         try:
            vNetworkRoot = ET.fromstring(virtualNetworkData)
            vNetworkCount = 0
            for vNetworkEntry in vNetworkRoot.findall('.//{http://www.w3.org/2005/Atom}entry'):
               newNetwork = {}
               #print "vNetwork entry #" + str(vNetworkCount)
               for vNetworkData in vNetworkEntry:
                  if(vNetworkData.tag == '{http://www.w3.org/2005/Atom}id'):
                     vNetworkId = vNetworkData.text
                     #print "found vNetwork entry with id of " + vNetworkId
                     connectionDict = { "_fromUniqueId": vNetworkId, "_toUniqueId": ms["managedSystemId"], "_edgeType": "runsOn"}
                     connectionsList.append(connectionDict)
                     newNetwork = getVnetwork(vNetworkId)
                     newNetwork["NetworkName"] = newNetwork["NetworkName"] + " on " + ms["Hostname"]
                     vNetworkList.append(newNetwork)

               vNetworkCount = vNetworkCount + 1
            if(logXmlOutput == 1):
               fh = open(mediatorHome + "/log/" + hmcServer + "-" + ms["name"] + "-virtualNetworkData.xml", "w")
               fh.write(virtualNetworkData)
               fh.write("\n")
               fh.close
         except:
            print "No vNetwork data returned for managed system id: "  + ms["managedSystemId"]

         #print virtualSwitchData
   
   
   #### Data collection complete
   
   
   print "Number of Managed Systems (Hypervisors): " + str(len(managedSystemList))
   print "Number of LPARs: " + str(len(lparList))
   print "Number of Virtual Switches: " + str(len(vSwitchList))
   print "Number of Client Network Adapters: " + str(len(cnaList))
   print "Number of connections: " + str(len(connectionsList))
   print "Number of VIOS: " + str(len(viosList))
   print "Nubmer of VIOS trunks: " + str(len(trunkList))

   ##################
   #
   # Send data to ASM
   #
   ##################
   
   if(sendToAsm == 1):
      for managedSystem in managedSystemList:
         createAsmResource(managedSystem)
      for lpar in lparList:
         createAsmResource(lpar)
      for vswitch in vSwitchList:
         createAsmResource(vswitch)
      for vios in viosList:
         createAsmResource(vios)
      for cna in cnaList:
         createAsmResource(cna)
      for trunk in trunkList:
         createAsmResource(trunk)
      for sea in seaList:
         createAsmResource(sea)
      for vnetwork in vNetworkList:
         createAsmResource(vnetwork)
      for connection in connectionsList:
         createAsmConnection(connection)
         
   
   # For future consideration....

   ######################
   #
   # For each managed system, obtain its virtual networks
   #
   ######################################################
   #print "these are the managed system ids:"
   for ms in managedSystemList:
       virtualNetworkData = getUomData(hmcDict, "/ManagedSystem/" + id + "/VirtualNetwork/")

   if(logXmlOutput == 1):
      fh = open(mediatorHome + "/log/" + hmcServer + "-" + ms["name"] + "-virtualData.xml", "w")
      fh.write(virtualSwitchData)
      fh.write("\n")
      fh.close
   fh = open("virtualNetworkData.xml", "w")
   fh.write(virtualNetworkData)
   fh.write("\n")
   fh.close
   ######################
   #
   # For each managed system, obtain host ethernet adapters
   #
   ######################################################
   #for ms in managedSystemList:
   #   print "checking for host ethernet adapters for managed system named " + ms["Hostname"]
   #   hostEthernetAdapterData = getUomData(hmcDict, "/ManagedSystem/" + ms["managedSystemId"] + "/HostEthernetAdapter")
   #
   #   fh = open("hostEthernetAdapterData.xml", "a")
   #   fh.write(hostEthernetAdapterData)
   #   fh.write("\n")
   #   fh.close
   
######################################
#
#  ----   Main multiprocess dispatcher
#
######################################

if __name__ == '__main__':


   global mediatorHome
   global logHome
   global configHome
   global asmDict
   global discoveryConfigDict

   hmcDictList = []
   asmDict = {}
   configDict = {}

   # verify directories and load configurations

   mediatorBinDir = os.path.dirname(os.path.abspath(__file__))
   extr = re.search("(.*)bin", mediatorBinDir)
   if extr:
      mediatorHome = extr.group(1)
      print "Mediator home is: " + mediatorHome
   else:
      print "FATAL: unable to find mediator home directory. Is it installed properly? bindir = " + mediatorBinDir
      exit()

   if(os.path.isdir(mediatorHome + "log")):
      logHome = extr.group(1)
   else:
      print "FATAL: unable to find log directory at " + mediatorHome + "log"
      exit()

   if(os.path.isfile(mediatorHome + "/config/hmclist.conf")):
      hmcDictList = loadHmcServers(mediatorHome + "/config/hmclist.conf")
   else:
      print "FATAL: unable to find HMC server list file " + mediatorHome + "/config/hmclist.conf"
      exit()

   print "Number of HMCs to discover: " + str(len(hmcDictList))

   if(os.path.isfile(mediatorHome + "/config/asmserver.conf")):
      asmServerDict = loadAsmServer(mediatorHome + "/config/asmserver.conf")
   else:
      print "FATAL: unable to find HMC server list file " + mediatorHome + "/config/asmserver.conf"
      exit()

   #if(os.path.isfile(mediatorHome + "/config/discovery.conf")):
      #discoveryConfigDict = loadDiscoveryConfig(mediatorHome + "/config/discovery.conf")
   #else:
   #   print "FATAL: unable to find HMC server list file " + mediatorHome + "/config/discovery.conf"
   #   exit()


   ##########################################################
   #
   # For each HMC entry, spawn a separate process to discover
   #
   ##########################################################
 
   hmcCount = 1
   for hmcDict in hmcDictList:
      print "Discovering HMC Server " + str(hmcCount) + ": " + hmcDict["server"]
      p = Process(target=dispatchHmc, args=(hmcDict,asmServerDict))
      p.start()
      hmcCount = hmcCount + 1

   exit()

   #p.join()

