This package allows integration of HMC topology information into the ASM topology. It 
collects data from the HMC REST interface for the following objects:

**ManagedSystem** - Hypervisor information<br>
**LogicalPartition** - LPARs and relationship to ManagedSystem<br>
**VirtualSwitch** - Virtual switch(es) that are configured on managed systems, and the LPAR
                and VIOS interfaces that connect to them<br>
**ClientAdapters** - Virtual Network Adapters that are configured on LPARs, and their
                 connections to Virtual Switches<br>
**TrunkAdapters** - VIOS trunk adapters<br>
**SharedEthernetAdapters** - VIOS Shared Ethernet Adapters<br>


Configuring the topology mediator:
=================================

Two configuration files must be configured:

     config/asmserver.conf - contains connection details for the ASM server in the form:
	
         #asmServer,asmPort,asmUser,asmPassword,asmTenantId

     config/hmclist.conf - contains a list of HMCs to be discovered in the form:

         #hmcServer,hmcPort,username,password

Additionally, a third file allows you to limit the discovery and control the number of
concurrent HMCs that are interrogated:

     config/discovery.conf

Running the topology mediator:
=============================

Simply run 'bin/getHMCData.py' to launch the mediator and it will consult each of the
HMCs listed in the hmclist.conf, and populate the ASM topology with the HMC data.


