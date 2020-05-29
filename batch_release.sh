#!/bin/bash
WS_PATH=/home/saulo/Work/exmakhina/poly/workspace
REPO_PATH=/home/saulo/Work/exmakhina/poly/SCT-data
DATASET=PAM50
# git
OAUTH_TOKEN=PLACEHOLDER
USER=saulo-p
REPO=SCT-data
TMP=$WS_PATH/tmp
OUTPUT=$WS_PATH/output
GIT_REST_URL=https://api.github.com/repos/saulo-p/SCT-data
GIT_UP_URL=https://uploads.github.com/repos/saulo-p/SCT-data

mkdir -p $WS_PATH/tmp/
rm -r -f $WS_PATH/tmp/*


cd $REPO_PATH
while read TAG;
do
	echo "Processing tag ${TAG}"

	printf -v payload '{"tag_name": "%s", "name": "sct-%s", "draft": false, "prerelease": false}' "${TAG}" "${TAG}"
	curl -H "Authorization: token ${OAUTH_TOKEN}" --data "${payload}" $GIT_REST_URL/releases

	commit_body=$(git log -1 $TAG --pretty="%b")
	SHA=${commit_body:106:8} # extract the commit id from the auto-generated message
	mkdir -p $OUTPUT/$TAG
	$WS_PATH/sct_download_data.py $DATASET $OUTPUT/$TAG $OUTPUT/$SHA z

	filename=$(ls $OUTPUT/$TAG)
	mv $OUTPUT/$TAG/$filename $REPO_PATH
	$WS_PATH/upload-asset.sh github_api_token=$OAUTH_TOKEN owner=$USER repo=$REPO tag=$TAG filename=$filename

	rm $REPO_PATH/$filename
done < <(git tag --sort=committerdate)
