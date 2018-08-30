#!/bin/bash

set -ex

tag=0.0.11
sha=`curl --silent https://api.github.com/repos/asyncy/cli/git/trees/$tag | python3 -c "import sys, json; print(json.load(sys.stdin)['sha'])"`

pip=pip3.7
python=python3.7

BUILD_DIR=build

rm -rf $BUILD_DIR

mkdir $BUILD_DIR
cd $BUILD_DIR
virtualenv --python=$python .
source ./bin/activate
$pip install asyncy==$tag

git clone git@github.com:asyncy/homebrew-brew.git
cd homebrew-brew

$pip freeze | grep -v asyncy== | $python scripts/build.py $tag $sha > Formula/asyncy.rb
deactivate

brew update
brew install Formula/asyncy.rb
asyncy version | grep $tag
asyncy --help
cd homebrew-brew
git checkout -b release_$tag
git commit -a -m "Release $tag."
git push origin release_$tag
echo "Branch release_$tag created. Please open a PR and have it accepted."

rm -rf $BUILD_DIR
