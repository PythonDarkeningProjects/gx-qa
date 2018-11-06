#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2017 Felipe Ruiz  <felipe.de.jesus.ruiz.garcia@.intel.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import logging
import os
import tarfile


logger = logging.getLogger(__name__)


def upload_files_sshkey_auth(host, user, list_path_files, dest):
	"""Function intended to copy files through scp by ssh key authentification

		host : url or ip host to upload files
		user : user to authenticate in the remote host
		list_path_files : a lists of strings paths
			example : ["/home/gfx/results_iteration_1.txt", "/home/log.txt"]
		dest : string path for put the files on the server
	"""

	logger.info("preparing upload")

	if type(list_path_files) is not list:
		logger.info("invalid argument: list_path_files is not a list")
		return -1

	if not list_path_files:
		logger.info("list empty : no files to upload")
		return -1

	files = ''
	for item in list_path_files:
		files += item + ' '

	output = os.system(
		'scp -o "StrictHostKeyChecking no" -r {files} {user}@{host}:{dest}'
		.format(files=files, user=user, host=host, dest=dest))

	if not output:
		logger.info("upload files operation completed correctly")

	else:
		logger.info("something went wrong with scp")

	return output


def extract_results(tar_file, file_to_extract, new_name=None):
	"""Function extracts json result from tar file

		This function is intende to extact a json file indicate
		on file_to_extract from the tar_file.

		If the variable new_name is defined, the file to be extracted will be
		name with new_name str
		Otherwise, if new_name is not indicate, the file keep the origin name

		tar_file : str pathfile tar to extract
		file_to_extract : str namefile to extract from tar_file
		new_name : str new name for the file extracted
	"""

	logger.info("starting file extraction")
	tar = tarfile.open(tar_file)
	logger.info("reading tar file")
	for member_in_tar in tar.getmembers():
		logger.info("searching result file in tar")
		if file_to_extract in member_in_tar.name:
			logger.info("file result found")
			content = tar.extractfile(member_in_tar)
			logger.info("extracting file from tar")
			json = content.read()
			logger.info("parsing file to text")

			name = member_in_tar

			if new_name:
				name = new_name

			with open(name, 'w') as file_to_write:
				logger.info("saving file extracted")
				file_to_write.write(json)
				logger.info("file saved correctly")
