#!/bin/bash
WS_PATH=/home/saulo/Work/exmakhina/poly/workspace
SCT_PATH=/home/saulo/Work/exmakhina/poly/sct
DATASET_REPO_PATH=/home/saulo/Work/exmakhina/poly/SCT-data

TMP_DIR=WS_PATH/tmp
mkdir -p $TMP_DIR
rm -r -f $TMP_DIR/*

# change to repo dir
cd $SCT_PATH
git checkout master

# data download loop
while read SHA;
do
	git checkout -q $SHA
	SCT_DOWN_PATH=$(find ./ -name sct_download_data.py)
	COMMIT_MSG_TITLE=$(git log -1 --pretty="%cd: %s" --date short)
	COMMIT_MSG_BODY=$(git log -1 --pretty="Data retrieved automatically from download urls in https://github.com/neuropoly/spinalcordtoolbox/commit/%h/${SCT_DOWN_PATH:2}")

	# create url diff lists
	$WS_PATH/urls_diff.py $SCT_PATH/$SCT_DOWN_PATH $TMP_DIR $SHA

	while read KEY;
	do
		rm -r $DATASET_REPO_PATH/$KEY
	done < $TMP_DIR/$SHA/keys_rm.txt
	while read KEY;
	do
		mkdir $DATASET_REPO_PATH/$KEY -p
		$WS_PATH/sct_download_data.py $KEY $DATASET_REPO_PATH/$KEY $WS_PATH/tmp/$SHA
	done < $TMP_DIR/$SHA/keys_add.txt

	# copy (overwriting) current download script to tmp
	cp $SCT_DOWN_PATH $TMP_DIR

	# Git actions
	cd $DATASET_REPO_PATH
	git add --all
	git commit -am "${COMMIT_MSG_TITLE}

	${COMMIT_MSG_BODY}"
	cd $SCT_PATH
done < <(git log --reverse --pretty=%h --follow scripts/sct_download_data.py)
