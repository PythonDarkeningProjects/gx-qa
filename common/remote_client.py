"""Provides a client to perform actions on remote Linux systems"""

import paramiko


class RemoteClient(object):
	"""Connects to a remote Linux host over SSH.

	:param host_ip: the server ip to connect to
	:param user: the username to authenticate as (defaults to the current local
	username)
	:param password: used for password authentication; is also used for private
	key decryption when using an rsa_file (if needed)
	:param rsa_file: an optional private RSA key to use for authentication
	"""

	def __init__(
		self, host_ip, user=None, password=None, rsa_file=None, timeout=10):
		self.host_ip = host_ip
		self.user = user
		self.password = password
		self.pkey = rsa_file
		key = paramiko.RSAKey.from_private_key(self.pkey) if self.pkey else None
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(
			self.host_ip, username=user, password=password, pkey=key, timeout=timeout)
		self.ssh_client = ssh

	def __del__(self):
		self.ssh_client.close()

	def run_command(self, command, timeout=30):
		"""Runs a shell command in the remote host.

		:param command: the command to be executed
		:param timeout: the limit time for executed the ssh command
		:return: a tuple that contains the exit code of the command executed,
		and the output message of the command.

		Example:
		run_command('hostname')    -> (0, 'my-linux-server')
		run_command('bad') -> (127, 'bash: bad: command not found')
		"""
		_, ssh_stdout, ssh_stderr = self.ssh_client.exec_command(
			command, timeout=timeout)
		stdout = ssh_stdout.read().strip()
		stderr = ssh_stderr.read().strip()
		return ssh_stdout.channel.recv_exit_status(), stderr or stdout

	def isdir(self, path, sudo=False):
		"""Validates if a directory exist in a remote system.

		:param path: the path of the directory to be validated
		:param sudo: this needs to be set to True for directories that require
		root permission
		:return: True if the directory exists, False otherwise
		"""
		status, _ = self.run_command(
			'{prefix}test -d {path}'.format(path=path, prefix='sudo ' if sudo else ''))
		return True if not status else False

	def isfile(self, path, sudo=False):
		"""Validates if a file exist in a remote system.

		:param path: the path of the file to be validated
		:param sudo: this needs to be set to True for files that require
		root permission
		:return: True if the file exists, False otherwise
		"""
		status, _ = self.run_command(
			'{prefix} test -f {path}'.format(path=path, prefix='sudo' if sudo else ''))
		return True if not status else False

	def makedirs(self, path, sudo=False):
		"""Creates a dir in a remote system.

		:param path: str : the path of the dir to be create.
		:param sudo: this needs to be set to True for files that require
			root permission
		:return: True if the dir exists, False if dir otherwise
		"""
		status, _ = self.run_command(
			'{prefix} mkdir -p {path}'.format(path=path, prefix='sudo' if sudo else ''))

		return self.isdir(path, sudo)

	def open_remote_file(self, remote_file):
		"""Reads data from a remote file.

		:param remote_file: the full path to the file to be read
		:return: a file-like object that can be used to read data from the file
		"""
		sftp_client = self.ssh_client.open_sftp()
		return sftp_client.open(remote_file)
