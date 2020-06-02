#!/bin/bash
WS_PATH=/home/saulo/Work/exmakhina/poly/workspace
DATASET_REPO_PATH=/home/saulo/Work/exmakhina/poly/SCT-data
DATASET=PAM50
# git
OAUTH_TOKEN=PLACEHOLDER
USER=saulo-p
REPO=SCT-data
TMP=$WS_PATH/tmp
OUTPUT=$WS_PATH/output
OUTPUT_DIR=$WS_PATH/output
GIT_REST_URL=https://api.github.com/repos/saulo-p/SCT-data
GIT_UP_URL=https://uploads.github.com/repos/saulo-p/SCT-data

cd $DATASET_REPO_PATH
while read TAG;
do
	echo "Processing tag ${TAG}"

	printf -v payload '{"tag_name": "%s", "name": "sct-%s", "draft": false, "prerelease": false}' "${TAG}" "${TAG}"
	curl -H "Authorization: token ${OAUTH_TOKEN}" --data "${payload}" $GIT_REST_URL/releases

	commit_body=$(git log -1 $TAG --pretty="%b")
	SHA=${commit_body:106:8} # extract the commit id from the auto-generated message
	mkdir -p $OUTPUT_DIR/$TAG
	$WS_PATH/sct_download_data.py $DATASET $OUTPUT_DIR/$TAG $OUTPUT_DIR/$SHA z

	filename=$(ls $OUTPUT/$TAG)
	mv $OUTPUT_DIR/$TAG/$filename $DATASET_REPO_PATH
	$WS_PATH/upload-asset.sh github_api_token=$OAUTH_TOKEN owner=$USER repo=$DATASET_REPO_NAME tag=$TAG filename=$filename

	rm $DATASET_REPO_PATH/$filename
done < <(git tag --sort=committerdate)
