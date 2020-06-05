import argparse
import logging

logger = logging.getLogger()
sct_data_repos = ['sct_testing_data', 'sct_example_data', 'deepseg_lesion_models', 'deepseg_sc_models', 'deepseg_gm_models', 'pmj_models', 'optic_models', 'c2c3_disc_models', 'MNI-Poly-AMU', 'PAM50']

def create_release(target_repo, target_tag):
	'''Create a new release within the target repository.'''
	pass

def download_default_release_asset(target_repo, release_id):
	'''Download the default asset of a given release'''
	pass

def upload_github_asset(target_repo, release_id):
	'''Upload provided artifact as release asset'''
	pass

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
