#!/bin/bash
WS_PATH=/home/saulo/Work/exmakhina/poly/workspace
REPO_PATH=/home/saulo/Work/exmakhina/poly/SCT-data
# git
OAUTH_TOKEN=PLACEHOLDER
GIT_REST_URL=https://api.github.com/repos/saulo-p/SCT-data
GIT_UP_URL=https://uploads.github.com/repos/saulo-p/SCT-data

cd $REPO_PATH
git tag > $WS_PATH/tmp/tags_list.txt
tac $WS_PATH/tmp/tags_list.txt > $WS_PATH/tags_list.txt

while read TAG;
do
	echo "Processing tag ${TAG}"

	printf -v payload '{"tag_name": "%s", "name": "sct-data-%s", "draft": false, "prerelease": false}' "${TAG}" "${TAG}"
	curl -H "Authorization: token ${OAUTH_TOKEN}" --data "${payload}" $GIT_REST_URL/releases

	git archive ${TAG} | gzip > $WS_PATH/tmp/$TAG.tar.gz

	mv $WS_PATH/tmp/$TAG.tar.gz $REPO_PATH/$TAG.tar.gz
	filename=$TAG.tar.gz
	$WS_PATH/upload-asset.sh github_api_token=$OAUTH_TOKEN owner=saulo-p repo=SCT-data tag=$TAG filename=$filename
	# curl -H "Authorization: token ${OAUTH_TOKEN}" --data-binary @"${filename}" $GIT_UP_URL/releases/$release_id/assets?name=$filename

	rm $REPO_PATH/$TAG.tar.gz
done < $WS_PATH/tags_list.txt

# rm $WS_PATH/tmp/*
