# auth in .pypirc
(cd ui_server/rl-tools/static/ui_server/generic && ./download_dependencies.sh)
rm -rf ../ui-server/dist
pip install --upgrade build twine
python3 -m build --sdist
python3 -m twine upload dist/*
