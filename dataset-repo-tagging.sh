#!/bin/bash
WS_PATH=/home/saulo/Work/exmakhina/poly/workspace
SCT_PATH=/home/saulo/Work/exmakhina/poly/sct
REPO_PATH=/home/saulo/Work/exmakhina/poly/SCT-data

rm $WS_PATH/tmp/*

#### list sct repo tags
tags_file=$WS_PATH/tmp/tag_sorted.txt
cd $SCT_PATH
git checkout master

while read TAG;
do
	DATE=$(git log -1 --format=%cd --date=short $TAG)
	echo "${DATE} ${TAG}" >> $WS_PATH/tmp/tag_dated.txt
done < <(git tag)

#sort tags based on date
sort -r $WS_PATH/tmp/tag_dated.txt > $tags_file

#### apply sct tags to corresponding data commits
cd $REPO_PATH

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
