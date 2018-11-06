# intel-gpu-tools 

## Description : intel-gpu-tools is a package of tools for debugging the Intel graphics driver, including a GPU hang dumping program, performance monitor, and performance microbenchmarks for regression testing the DRM

## Folders descriptions :

- autouploader

	This folder contains the following files :
		
		1 - autoUploader.py, is a tool that helps in automated/manual way to upload reports to Test Report Center (TRC)
		2 - config.yml, which is the configuration file for autoUploader.py
		3 - mergeTRCLink.py, which is a tool that helps to merge/update current TRC reports with more test cases (useful in intel-gpu-tools clones executions).

- firmwares

	This folder contains the following files : 
		
		1 - firmwares.py, which helps to install the following firmwares for validate intel-gpu-test cases and more tests

			## GUC

			Is designed to perform graphics workload scheduling on the various graphics parallel engines. In this scheduling model, host software submits work through one of the 256 graphics doorbells and this invokes the scheduling operation on the appropriate graphics engine. Scheduling operations include determining which workload to run next, submitting a workload to a command streamer, pre-empting existing workloads running on an engine, monitoring progress and notifying host software when work is done.

			## DMC

			Provides additional graphics low-power idle states. It provides capability to save and restore display registers across these low-power states independently from the OS/Kernel.

			## HUC

			Is designed to offload some of the media functions from the CPU to GPU. These include but are not limited to bitrate control, header parsing. For example in the case of bitrate control, driver invokes HuC in the beginning of each frame encoding pass, encode bitrate is adjusted by the calculation done by HuC. Both the HuC hardware and the encode hardcode reside in GPU. Using HuC will save unnecessary CPU-GPU synchronization.


			The available products for firmwares installation are :
				
				- KabyLake
				- SkyLake
				- Broxton
				- GeminiLake
				- CoffeLake (that uses KabiLake firmwares)


- runner.d
	
	This folder contains the following files : 

		1 - dmesg.sh, which is a tools for split the dmesg in the following states

			emerg     - system is unusable
  			alert     - action must be taken immediately
  			crit      - critical conditions
  			err       - error conditions
  			warn      - warning conditions
  			notice    - normal but significant condition
  			info      - informational
  			debug     - debug-level messages


  		2 - runner.py, which is a tool in develpment that helps to run a specific intel-gpu-tools testlist and throw results in the following formats : 
  			- html files
  			- csv files
  			- json files
  			- dmesg for each single test case

  		3 - runner.yml, which is the configuratio file for runner.py



# Useful links : 
Reference manual   : https://01.org/linuxgraphics/gfx-docs/igt
Repository on cgit : https://cgit.freedesktop.org/xorg/app/intel-gpu-tools
Results on TRC     : https://otcqarpt.jf.intel.com/gfx/platforms/filter
