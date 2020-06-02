#!/bin/bash
WS_PATH=/home/saulo/Work/exmakhina/poly/workspace
SCT_PATH=/home/saulo/Work/exmakhina/poly/sct
DATASET_REPO_PATH=/home/saulo/Work/exmakhina/poly/SCT-data

TMP_DIR=$WS_PATH/tmp/
mkdir -p $TMP_DIR
rm -r -f $TMP_DIR/*


cd $SCT_PATH
git checkout master

#### list sct repo tags: sort (date,tag) pairs based on date
tags_file=$TMP_DIR/tag_sorted.txt
while read TAG;
do
	DATE=$(git log -1 --format=%cd --date=short $TAG)
	echo "${DATE} ${TAG}" >> $TMP_DIR/tag_dated.txt
done < <(git tag)
sort -r $TMP_DIR/tag_dated.txt > $tags_file

#### apply sct tags to corresponding data commits
cd $DATASET_REPO_PATH
while read SHA;
do
	commit_msg=$(git log -1 $SHA --pretty="%s")
	commit_date=${commit_msg:0:10}

	re='^[0-9]+$'
	if ! [[ ${commit_date:0:3} =~ $re ]] ; then
		continue
	fi

	tag_str="--"
	while read DATE_TAG;
	do
		following_release=$tag_str

		dt=($DATE_TAG)
		date_str=${dt[0]}
		tag_str=${dt[1]}

		com_date=$(date -d $commit_date +%s)
		tag_date=$(date -d $date_str +%s)
		if [ $com_date -ge $tag_date ];
		then
			if ! [ $following_release = "--" ]; then
				git tag $following_release $SHA
			fi
			break
		fi
	done < $tags_file
done < <(git log --pretty=%h)
