import argparse
import argparse, json, os
import argparse, json, io, os
import logging
import urllib.request, urllib.error

logger = logging.getLogger()

sct_data_repos = ['sct_testing_data', 'sct_example_data', 'deepseg_lesion_models', 'deepseg_sc_models', 'deepseg_gm_models', 'pmj_models', 'optic_models', 'c2c3_disc_models', 'MNI-Poly-AMU', 'PAM50']
GH_TOKEN=os.environ["GH_TOKEN"].strip()


def create_release(target_repo, target_tag):
	'''
	Create a new release within the target repository.
	:return: release id on success.'''
	logger.info("Creating release")

	url = "https://api.github.com/repos/sct-data/{}/releases".format(target_repo)
	headers = {
		"Authorization": "token {}".format(GH_TOKEN),
		"Content-Type": "application/json",
	}
	payload = json.dumps({"tag_name": target_tag, "name": target_tag, "draft": False, "prerelease": False}).encode("utf-8")
	req = urllib.request.Request(url, headers=headers, method="POST", data=payload)

	with urllib.request.urlopen(req) as resp:
		if resp.getcode() != 201:
			raise RuntimeError("Bad response: %d / %s", resp.getcode(), resp.read())
		ret = json.loads(resp.read().decode('utf-8'))
		logger.info("ret: %s", ret)
		release_id = ret["id"]

	return release_id

def download_default_release_asset(target_repo, release_id):
	'''Download the default asset of a given release'''
	pass

def upload_github_asset(target_repo, release_id, asset_path):
	'''
	Uploads a release asset to a target release.
	'''
	logger.info("Uploading release asset")

	url = "https://uploads.github.com/repos/sct-data/{}/releases/{}/assets?name={}" \
		.format(target_repo, release_id, asset_path)
	headers = {
		"Authorization": "token {}".format(GH_TOKEN),
		"Content-Type": "application/octet-stream",
	}

	with io.open(asset_path, "rb") as fin:
		payload = fin.read()
	req = urllib.request.Request(url, headers=headers, method="POST", data=payload)
	with urllib.request.urlopen(req) as resp:
		if resp.getcode() != 201:
			raise RuntimeError("Bad response: %d / %s", resp.getcode(), resp.read())
		ret = json.loads(resp.read().decode('utf-8'))
		logger.info("ret: %s", ret)


def upload_to_osf():
	'''
	Uploads new version of the data to the Open Science Framework
	:return: osf new url (?)
	'''
	pass


def main():

	def parse_args():
		parser = argparse.ArgumentParser(
		description="Create a release on one of the repositories within sct-data organization")

		# Mandatory arguments
		parser.add_argument("--repo",
		help="Target repository of the release.",
		required=True,
		choices=(sct_data_repos))
		parser.add_argument("--tag",
		help="Tag to anchor the release.",
		required=True)

		# Optional arguments
		parser.add_argument("--osf",
		help="Whether to upload to OSF or not",
		type=int,
		choices=(0,1)
		)

		return parser.parse_args()

	args = parse_args()

	return gh_asset_url, osf_url




if __name__ == "__main__":
	res = main()
	raise SystemExit()
