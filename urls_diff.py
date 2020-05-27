#!/home/saulo/Work/exmakhina/poly/sct/python/envs/venv_sct/bin/python

# Download data from multiple sources
# modified from spinalcordtoolbox/download.py

import re
import json
import dictdiffer
import pickle

import os
import sys


def get_dict_urls(python_source):
	'''Receive download script source recreates the url dictionary'''

	def get_re(key, pattern):
		return pattern.replace("key", key)

	string_pattern = r"([\'\"](?P<key>\S+)[\'\"])"
	list_pattern = r"\[(?P<key>([\'\"]\S+[\'\"],?\s*)+)\]"

	key = get_re('key', string_pattern)

	dict_pair = key + r"\s*:\s*" + r"(" + get_re('value', string_pattern) + r"|" + get_re('list_value', list_pattern) + r")"
	pair_re = re.compile(dict_pair)

	try:
		open(python_source, 'r')
	except FileNotFoundError:
		return dict()
	else:
		fin = open(python_source, 'r')
		read_data = fin.read()

		ms = pair_re.finditer(read_data)

		d = dict()
		for m in ms:
			if m.group('value') is None:
				d[m.group('key')] = m.group('list_value').replace("'",'').replace('\n','').replace(' ','').split(',')
			else:
				d[m.group('key')] = m.group('value')

		return d

def dict_diff(dict_old, dict_new):
	add = list()
	rm = list()
	for diff in list(dictdiffer.diff(dict_old,dict_new)):
		if diff[0] == 'change':
			if type(diff[1]) is list:
				rm.append(diff[1][0])
				add.append(diff[1][0])
			else:
				rm.append(diff[1])
				add.append(diff[1])
		elif diff[0] == 'remove':
			for removed in diff[2]:
				rm.append(removed[0])
		elif diff[0] == 'add':
			for added in diff[2]:
				add.append(added[0])

	return set(add), set(rm)

if __name__ == "__main__":
	new_path = sys.argv[1]
	tmp_path = sys.argv[2]
	commit_id = sys.argv[3]

	commit_path = os.path.join(tmp_path, commit_id)
	os.mkdir(commit_path)

	urls_new = get_dict_urls(new_path)
	with open(os.path.join(commit_path,'urls.pickle'), 'wb') as fout:
		pickle.dump(urls_new, fout, protocol=pickle.HIGHEST_PROTOCOL)
	urls_old = get_dict_urls(os.path.join(tmp_path, 'sct_download_data.py'))

	add, rm = dict_diff(urls_old, urls_new)

	#TODO: commit_path instead of tmp_path
	with open(os.path.join(tmp_path, 'keys_rm.txt'), 'w') as fout:
		for k in rm:
			fout.write(k+"\n")
	with open(os.path.join(tmp_path, 'keys_add.txt'), 'w') as fout:
		for k in add:
			fout.write(k+"\n")
