#!/bin/bash

set -e
#set -x

pip=pip3.7
python=python3.7

tag=$1

if [ $tag == '' ]; then
	echo "Usage:"
	echo "bash update_brew.sh <tag>"
	exit 1
fi

echo "Retrieving git SHA for tag $tag..."
sha=`curl --silent https://api.github.com/repos/asyncy/cli/git/trees/$tag | $python -c "import sys, json; print(json.load(sys.stdin)['sha'])"`

BUILD_DIR=`mktemp -d`

echo "Building in $BUILD_DIR..."

cd $BUILD_DIR
echo "Creating a virtualenv..."
virtualenv --python=$python . &> /dev/null
source ./bin/activate
echo "Installing asyncy==$tag..."
$pip install asyncy==$tag &> /dev/null

echo "Cloning asyncy/homebrew-brew..."
git clone git@github.com:asyncy/homebrew-brew.git &> /dev/null
cd homebrew-brew

echo "Running pip freeze and building Formula/asyncy.rb..."
$pip freeze | grep -v asyncy== | $python scripts/build.py $tag $sha > Formula/asyncy.rb
deactivate

echo "Updating brew..."
brew update
echo "Testing the formula locally with brew..."
brew install Formula/asyncy.rb
asyncy version | grep $tag
asyncy --help
git checkout -b release_$tag
git commit -a -m "Release $tag."
git push origin release_$tag
echo "Branch release_$tag created. Please open a PR and have it accepted."

cd ../..
echo "Cleaning $BUILD_DIR..."
rm -rf $BUILD_DIR
echo "Done!"
