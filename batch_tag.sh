#!/bin/bash
WS_PATH=/home/saulo/Work/exmakhina/poly/workspace
SCT_PATH=/home/saulo/Work/exmakhina/poly/sct
REPO_PATH=/home/saulo/Work/exmakhina/poly/SCT-data

###################################################################
# #clear tmp/
# rm $WS_PATH/tmp/*

# cd $SCT_PATH
# git checkout master

# git tag > $WS_PATH/tag_list.txt
# while read TAG;
# do
# # DATE=$(git log -1 --format=%ai $TAG)
# DATE=$(git log -1 --format=%cd --date=short $TAG)

# echo "${DATE} ${TAG}" >> $WS_PATH/tmp/tag_dated.txt
# done < $WS_PATH/tag_list.txt

# sort $WS_PATH/tmp/tag_dated.txt > $WS_PATH/tmp/tag_sorted.txt
# tac $WS_PATH/tmp/tag_sorted.txt > $WS_PATH/tag_sorted.txt


###################################################################
while read DATE_TAG;
do
dt=($DATE_TAG) #array
date_str=${dt[0]}
tag=${dt[1]}

arg_date=$(date -d ${1} +%s)
tag_date=$(date -d ${date_str} +%s)
if [ $arg_date -ge $tag_date ];
then
	echo $tag
	exit
fi
done < $WS_PATH/tag_sorted.txt

echo "Untagged"