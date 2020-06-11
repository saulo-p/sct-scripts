import argparse, json, io, os
import logging
import urllib.request, urllib.error

logger = logging.getLogger()

def create_release(target_repo, target_tag, gh_token):
	'''
	Create a new release within the target repository.
	:return: release id on success.'''
	logger.info("Creating release")

	url = "https://api.github.com/repos/sct-data/{}/releases".format(target_repo)
	headers = {
		"Authorization": "token {}".format(gh_token),
		"Content-Type": "application/json",
	}
	payload = json.dumps({"tag_name": target_tag, "name": target_tag, "draft": False, "prerelease": False}).encode("utf-8")
	req = urllib.request.Request(url, headers=headers, method="POST", data=payload)

	with urllib.request.urlopen(req) as resp:
		if resp.getcode() != 201:
			raise RuntimeError("Bad response: {} / {}".format(resp.getcode(), resp.read()))
		ret = json.loads(resp.read().decode('utf-8'))
		logger.info("ret: %s", ret)
		release_id = ret["id"]

	return release_id

def download_default_release_asset(target_repo, release_id, gh_token):
	'''Download the default asset of a given release'''
	from tqdm import tqdm
	logger.info("Downloading release default asset")

	url = "https://api.github.com/repos/sct-data/{}/releases/{}".format(target_repo, release_id)
	headers = {
		"Authorization": "token {}".format(gh_token),
		"Content-Type": "application/octet-stream",
	}

	class TqdmUpTo(tqdm):
		def update_to(self, num_blocks, block_size, total_size):
			if total_size is not None and self.total is None:
				self.total = total_size
			self.update(num_blocks * block_size - self.n)  # will also set self.n = b * bsize

	req = urllib.request.Request(url, headers=headers, method="GET")
	with urllib.request.urlopen(req) as resp:
		if resp.getcode() != 200:
			raise RuntimeError("Bad response: {} / {}".format(resp.getcode(), resp.read()))
		ret = json.loads(resp.read().decode('utf-8'))
		logger.info("ret: %s", ret)

		with TqdmUpTo(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc='Downloading') as t:
			urllib.request.urlretrieve(ret['zipball_url'], ret['tag_name']+'.zip', t.update_to)
			t.total = t.n

def upload_github_asset(target_repo, release_id, asset_path, gh_token):
	'''
	Uploads a release asset to a target release.
	'''
	logger.info("Uploading release asset")

	url = "https://uploads.github.com/repos/sct-data/{}/releases/{}/assets?name={}" \
		.format(target_repo, release_id, asset_path)
	headers = {
		"Authorization": "token {}".format(gh_token),
		"Content-Type": "application/octet-stream",
	}

	with io.open(asset_path, "rb") as fin:
		payload = fin.read()
	req = urllib.request.Request(url, headers=headers, method="POST", data=payload)
	with urllib.request.urlopen(req) as resp:
		if resp.getcode() != 201:
			raise RuntimeError("Bad response: {} / {}".format(resp.getcode(), resp.read()))
		ret = json.loads(resp.read().decode('utf-8'))
		logger.info("ret: %s", ret)

def upload_to_osf(osf_project_id, osf_username, osf_password, asset_path, upload_path):
	'''
	Uploads new version of the data to the Open Science Framework.
	:return: osf download url of the newly uploaded asset.
	'''
	from osfclient import OSF

	osf = OSF()
	osf.login(username=osf_username, password=osf_password)

	project_storage = osf.project(osf_project_id).storage()

	logger.info('Uploading file to OSF project [%s]', osf_project_id)
	with open(asset_path, 'rb') as fup:
		try:
			project_storage.create_file(upload_path, fup)
		except Exception as e:
			logger.error('Upload error: %s', e)
		else:
			for file in project_storage.files:
				# compare strings instead of os.path.samefile() because objects are in different file systems.
				if file.path == upload_path:
					return file._download_url

def update_release_(target_repo, release_id, osf_url):
	'''
	Include link to osf data in the github release
	'''
	pass



def main(args_in=None):

	def parse_args():
		parser = argparse.ArgumentParser(
		description="Create a release on one of the repositories within sct-data organization")

		parser.add_argument("repository",
		help="Target repository of the release (within the sct-data organization)",
		# choices=(sct_data_repos))
		type=str)
		parser.add_argument("tag",
		help="Target tag of the new release.",
		type=str)

		parser.add_argument("--github_token",
		help="GitHub's authentication token. Assumes the user has pushing rights to the target repository. Alternatively can be set to envar GH_TOKEN.",
		type=str)
		osf_args = parser.add_argument_group()
		osf_args.add_argument("--osf-project",
		help="OSF project id to upload assets. If empty no osf actions will be performed. Alternatively can be set to envar OSF_PROJECT.",
		type=str)
		parser.add_argument("--osf-user",
		help="OSF username. Alternatively can be set to envar OSF_USERNAME.",
		type=str)
		parser.add_argument("--osf-password",
		help="OSF password. Alternatively can be set to envar OSF_PASSWORD.",
		type=str)


		args = parser.parse_args(args=args_in)

		sct_data_repos = ['sct_testing_data', 'sct_example_data', 'deepseg_lesion_models', 'deepseg_sc_models', 'deepseg_gm_models', 'pmj_models', 'optic_models', 'c2c3_disc_models', 'MNI-Poly-AMU', 'PAM50'] # list_org_repos()
		if args.repository not in sct_data_repos:
			parser.error("{} is not a valid sct-data repository.".format(args.repository))

		#TODO (maybe): validate tag

		if args.github_token is None:
			try:
				args.github_token = os.environ['GH_TOKEN']
			except:
				parser.error("GitHub token is required.")
		if args.osf_project is not None:
			try:
				args.osf_user = os.environ['OSF_USERNAME'] if args.osf_user is None else args.osf_user
				args.osf_password = os.environ['OSF_PASSWORD'] if args.osf_password is None else args.osf_password
			except:
				parser.error("OSF username and password are required for OSF upload.")


		return args


	return


if __name__ == "__main__":
	res = main()
	raise SystemExit()
