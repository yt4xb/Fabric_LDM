# Fabric_LDM
###############################################################################

Installing and starting LDM with the deploy_LDM.py script.

1. Create a multiple-node slice in GENI using a broadcast node to enable multicast
2. Get the Ip address of the nodes
	1. Save Manifest As
	2. Choose a name <your_file> for this file
	3. python IP-extractor.py <your_file>
3. Edit the global variables in the deploy_LDM.py script to point to the ldm tar ball on your local machine.
	- LDM-VER should match the version on your local
	- Pack name should be .tar.gz assuming tarball gunzip file
	- LDM_PATH_PACK should be the path to the tar ball
	- RCV_NUM, the number of servers receiving LDM products
	- Path names in the whole file regarding the location of the LDM7 on your local to reflect the proper location
4. Run deployment
	- cat list | fab -f deploy_LDM7.py read_hosts deploy
		- There will be a lot of output. Success should look like this...

		Done.
		Disconnecting from root@152.54.14.33... done.
    Disconnecting from root@152.54.14.30... done.
		Disconnecting from root@152.54.14.31... done.

5. Log into the sender node and run the commands
	- "su - ldm" : this changes you to the ldm user where everything is installed
	- "regutil /queue/size"
	- This will output 5G if the python script has been unchanged.
	- Please run the command "regutil -s 2G /queue/size" if you are running on a XO Large GENI image. If you are running Extra large you are okay
6. Finally, check that the LDM program is running by running "ps aux | grep ldm" on both sender and receiver boxes.
   This command is outputting all running processes with various information associated with them, and then only showing those that contain "ldm".

More functions:
  Adding Loss
	  Assuming you have deployed, adding loss is as simplye as creating a new list, call it "lossy-list".
    This list will contain the IP addresses of the nodes to wish to add loss to.
    (This is simply an implementation of Iptables, using the GLOBAL loss rate specified in deploy_LDM7.py.
    Thus if you want to change the amount of loss, look to LOSS_RATE global).
		  - cat lossy-list | fab -f deploy_LDM7.py read_hosts add_loss

  Removing Loss
	  Same assumption as before, same lossy-list
			- cat lossy-list | fab -f deploy_LDM7.py read_hosts rm_loss
