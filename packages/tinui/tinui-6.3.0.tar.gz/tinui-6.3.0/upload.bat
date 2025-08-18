cd dist
del *
cd ..
python -m build
twine upload dist/*