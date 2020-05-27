#!/bin/bash
SCT_PATH=/home/saulo/Work/exmakhina/poly/sct
WS_PATH=/home/saulo/Work/exmakhina/poly/workspace

# Create dictionary pickle objects for all commits
# (This workaround is not ideal, original specs asked for release with git archive)
cd $SCT_PATH
git checkout master
while read SHA; do
	echo "Pickling commit ${SHA}"
	git checkout -q $SHA
	down_script_path=$(find ./ -name sct_download_data.py)

	# create url diff lists
	$WS_PATH/urls_diff.py $SCT_PATH/$down_script_path $WS_PATH/output $SHA

	rm -r -f $WS_PATH/tmp/*
	cp $down_script_path $WS_PATH/tmp
done < <(git log --reverse --pretty=%h --follow scripts/sct_download_data.py)
