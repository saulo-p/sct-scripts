#!/bin/bash
WS_PATH=/home/saulo/Work/exmakhina/poly/workspace
SCT_PATH=/home/saulo/Work/exmakhina/poly/sct
REPO_PATH=/home/saulo/Work/exmakhina/poly/SCT-data

mkdir -p $WS_PATH/tmp/
rm -r -f $WS_PATH/tmp/*

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
	$WS_PATH/urls_diff.py $SCT_PATH/$SCT_DOWN_PATH $WS_PATH/tmp $SHA

	while read KEY;
	do
		rm -r $REPO_PATH/$KEY
	done < $WS_PATH/tmp/$SHA/keys_rm.txt
	while read KEY;
	do
		mkdir $REPO_PATH/$KEY -p
		$WS_PATH/sct_download_data.py $KEY $REPO_PATH/$KEY $WS_PATH/tmp/$SHA
	done < $WS_PATH/tmp/$SHA/keys_add.txt

	# clear tmp lists before next iteration
	#TODO: after changing keys_add and keys_rm to commit folder, rm only sct_download_data from tmp (if cp overwrites just remove line)
	rm -r $WS_PATH/tmp/*
	# copy current download script to tmp
	cp $SCT_DOWN_PATH $WS_PATH/tmp

	# Git actions
	cd $REPO_PATH
	git add --all
	git commit -am "${COMMIT_MSG_TITLE}

	${COMMIT_MSG_BODY}"
	cd $SCT_PATH
done < <(git log --reverse --pretty=%h --follow scripts/sct_download_data.py)
