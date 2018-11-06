"""Provides a client to perform actions on a remote Linux Kernel"""

import os

from common.remote_client import RemoteClient


class KernelClient(RemoteClient):
	"""Provides a client to perform functions related to the Linux Kernel.

	This class provides various functions that interact with the Linux kernel,
	they set or collect information from it. Most of these functions (if not
	all), need root privileges to run.

	:param host_ip: the server ip to connect to
	:param user: the username to authenticate as (defaults to the current local
	username)
	:param password: used for password authentication; is also used for private
	key decryption when using an rsa_file (if needed)
	:param rsa_file: an optional private RSA key to use for authentication
	"""

	def __init__(self, host_ip, user='gfx', password='linux', rsa_file=None):
		super(KernelClient, self).__init__(
			host_ip=host_ip,
			user=user,
			password=password,
			rsa_file=rsa_file)

	def get_firmware_version(self):
		"""Gets the firmware version loaded into the kernel.

		Collects the required GUC, HUC and DMC firmware versions for the host's
		kernel, and its load status.
		:return: a tuple with the required values for GUC, HUC and DMC firmwares,
		if the firmwares failed to be loaded or have a different version than the
		expected one, it returns None for that firmware
		"""
		# initialize values
		guc_version = None
		huc_version = None
		dmc_version = None

		# Make sure the dri data is available
		dri_path = '/sys/kernel/debug/dri/0'
		if self.isdir(dri_path, sudo=True):

			# get the GUC requirements
			guc_file = os.path.join(dri_path, 'i915_guc_load_status')
			if self.isfile(guc_file, sudo=True):
				error_code, output = self.run_command(
					"sudo cat {guc} | egrep 'version:|status:'".format(guc=guc_file))
				if not error_code:
					# the output should contain something similar to this:
					# status: fetch SUCCESS, load SUCCESS\n\tversion: wanted 9.39, found 9.39
					# so we need to process the output to grab the values we want
					output = output.split('\n')
					status = output[0]
					version = output[1].replace(',', '').split()
					# grab the firmware version only if the version found matches the
					# wanted version
					guc_version = version[4] if version[2] == version[4] else None
					# finally verify "fetch" and "load" have both SUCCESS status,
					# if they don't then return None as firmware version
					guc_version = guc_version if status.count('SUCCESS') == 2 else None

			# get the HUC requirements
			huc_file = os.path.join(dri_path, 'i915_huc_load_status')
			if self.isfile(huc_file, sudo=True):
				error_code, output = self.run_command(
					"sudo cat {huc} | egrep 'version:|status:'".format(huc=huc_file))
				if not error_code:
					output = output.split('\n')
					status = output[0]
					version = output[1].replace(',', '').split()
					huc_version = version[4] if version[2] == version[4] else None
					huc_version = huc_version if status.count('SUCCESS') == 2 else None

			# get the DMC requirements
			dmc_file = os.path.join(dri_path, 'i915_dmc_info')
			if self.isfile(dmc_file, sudo=True):
				error_code, output = self.run_command(
					"sudo cat {dmc} | egrep 'loaded:|version:'".format(dmc=dmc_file))
				if not error_code:
					# the output of this file is a little different and should contain
					# something similar to this:
					# fw loaded: yes\nversion: 1.4
					output = output.split('\n')
					status = output[0].split()[2]
					version = output[1].split()[1]
					dmc_version = version if status == 'yes' else None

		return guc_version, huc_version, dmc_version
