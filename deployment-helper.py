import argparse, tempfile
import io, json, logging, os, sys
import urllib.request, urllib.error

logger = logging.getLogger('sct-data-release')

def create_release(target_repo, target_tag, gh_token):
	'''
	Create a new release within the target repository.
	:return: release id on success.'''
	logger.info("Creating a new release at sct-data/%s at tag %s", target_repo, target_tag)

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
		logger.debug("ret: %s", ret)
		release_id = ret["id"]

	logger.info("Release (id:%s) successfully createad.", release_id)
	return release_id

def download_default_release_asset(target_repo, release_id, gh_token, target_dir):
	'''
	Download the default asset of a given release
	:return: relative path to downloaded file.
	'''
	from tqdm import tqdm
	logger.info("Downloading release default assets.")

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
		logger.debug("ret: %s", ret)

		downloaded_asset_path = os.path.join(target_dir, ret['tag_name']+'.zip')
		with TqdmUpTo(unit='B', unit_scale=True, unit_divisor=1024, miniters=1) as t:
			urllib.request.urlretrieve(ret['zipball_url'], downloaded_asset_path, reporthook=t.update_to)
			t.total = t.n

	return downloaded_asset_path

def upload_github_asset(target_repo, release_id, asset_path, gh_token):
	'''
	Uploads a release asset to a target release.
	:return: Download link of the uploaded asset.
	'''
	logger.info("Uploading default release asset to sct-data/%s", target_repo)

	asset_name = os.path.basename(asset_path)
	url = "https://uploads.github.com/repos/sct-data/{}/releases/{}/assets?name={}" \
		.format(target_repo, release_id, asset_name)
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
		logger.debug("ret: %s", ret)

	logger.info("Release asset uploaded successfully.")
	return ret['browser_download_url']

def upload_to_osf(osf_project_id, osf_username, osf_password, asset_path):
	'''
	Uploads new version of the data to the Open Science Framework.
	:return: osf download url of the newly uploaded asset.
	'''
	from osfclient import OSF

	osf = OSF()
	osf.login(username=osf_username, password=osf_password)

	project_storage = osf.project(osf_project_id).storage()

	logger.info('Uploading asset to OSF (project id:%s)', osf_project_id)
	with open(asset_path, 'rb') as fup:
		upload_path = os.path.join('/data', os.path.basename(asset_path))
		try:
			project_storage.create_file(upload_path, fup)
		except Exception as e:
			logger.exception('Upload error.')
		else:
			for file in project_storage.files:
				# compare strings instead of os.path.samefile() because objects are in different file systems.
				if file.path == upload_path:
					return file._download_url

def update_release_with_osf_url(target_repo, release_id, gh_token, osf_url):
	'''
	Include osf download url (in case osf upload was performed) to the Github release
	'''
	logger.info("Uploading release with OSF download url.")

	url = "https://api.github.com/repos/sct-data/{}/releases/{}".format(target_repo, release_id)
	headers = {
		"Authorization": "token {}".format(gh_token),
		"Content-Type": "application/json",
	}

	payload = json.dumps({"body": "Asset also available at {}".format(osf_url)}).encode("utf-8")
	req = urllib.request.Request(url, headers=headers, method="PATCH", data=payload)

	with urllib.request.urlopen(req) as resp:
		if resp.getcode() != 200:
			raise RuntimeError("Bad response: {} / {}".format(resp.getcode(), resp.read()))
		ret = json.loads(resp.read().decode('utf-8'))
		logger.debug("ret: %s", ret)


def main(args_in=None):
	def list_org_repos():
		url = "https://api.github.com/orgs/sct-data/repos"
		headers = {
			"Content-Type": "application/json",
		}
		req = urllib.request.Request(url, headers=headers, method="GET")

		with urllib.request.urlopen(req) as resp:
			if resp.getcode() != 200:
				raise RuntimeError("Bad response: {} / {}".format(resp.getcode(), resp.read()))
			ret = json.loads(resp.read().decode('utf-8'))
			logger.debug("ret: %s", ret)

			sct_data_repos = list()
			for repo in ret:
				sct_data_repos.append(repo['name'])

		return sct_data_repos

	def list_repo_tags(repo):
		url = "https://api.github.com/repos/sct-data/{}/tags".format(repo)
		headers = {
			"Content-Type": "application/json",
		}
		req = urllib.request.Request(url, headers=headers, method="GET")

		with urllib.request.urlopen(req) as resp:
			if resp.getcode() != 200:
				raise RuntimeError("Bad response: {} / {}".format(resp.getcode(), resp.read()))
			ret = json.loads(resp.read().decode('utf-8'))
			logger.debug("ret: %s", ret)

			tags = list()
			for tag in ret:
				tags.append(tag['name'])

		return tags

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

		parser.add_argument("--log-level",
		default="INFO",
		help="logger level (eg. INFO, see Python logger docs)")
		parser.add_argument("--log-verbose",
		default=False,
		help="False: logs to sct-data-release.log, True: also prints to stdout.")
		parser.add_argument("--github-token",
		help="GitHub's authentication token. Assumes the user has pushing rights to the target repository. Alternatively can be set to envar GITHUB_TOKEN.",
		type=str)
		osf_args = parser.add_argument_group()
		osf_args.add_argument("--osf-project",
		help="OSF project id to upload assets. If empty no osf actions will be performed. Alternatively can be set to envar OSF_PROJECT.",
		type=str)
		parser.add_argument("--osf-username",
		help="OSF username. Alternatively can be set to envar OSF_USERNAME.",
		type=str)
		parser.add_argument("--osf-password",
		help="OSF password. Alternatively can be set to envar OSF_PASSWORD.",
		type=str)


		args = parser.parse_args(args=args_in)

		if args.repository not in list_org_repos():
			parser.error("{} is not a valid sct-data repository.".format(args.repository))
		if args.tag not in list_repo_tags(args.repository):
			parser.error("{} is not a valid tag of sct-data/{}.".format(args.tag, args.repository))

		if args.github_token is None:
			try:
				args.github_token = os.environ['GITHUB_TOKEN']
			except:
				parser.error("GitHub token is required.")
		if args.osf_project is not None:
			try:
				args.osf_username = os.environ['OSF_USERNAME'] if args.osf_username is None else args.osf_username
				args.osf_password = os.environ['OSF_PASSWORD'] if args.osf_password is None else args.osf_password
			except:
				parser.error("OSF username and password are required for OSF upload.")

		return args


	args = parse_args()

	logging.basicConfig(filename='./sct-data-release.log', level=args.log_level)
	if args.log_verbose:
		logger.addHandler(logging.StreamHandler(sys.stdout))

	# Release pipeline
	release_id = create_release(args.repository, args.tag, args.github_token)

	with tempfile.TemporaryDirectory() as tmpdirname:
		default_asset_path = download_default_release_asset(args.repository, release_id, args.github_token, tmpdirname)

		urls = dict()
		urls['github'] = upload_github_asset(args.repository, release_id, default_asset_path, args.github_token)

		if args.osf_project is not None:
			urls['osf'] = upload_to_osf(args.osf_project, args.osf_username, args.osf_password, default_asset_path)

			update_release_with_osf_url(args.repository, release_id, args.github_token, urls['osf'])

	return urls


if __name__ == "__main__":
	urls = main()

	print("Download urls:", urls)

