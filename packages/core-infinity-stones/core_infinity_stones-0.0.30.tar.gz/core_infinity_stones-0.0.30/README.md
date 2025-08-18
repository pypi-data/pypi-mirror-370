# To Build and Deploy
python3 setup.py sdist bdist_wheel && twine upload dist/*

# Breaking Changes:

## v0.0.28
1- The `url` param form the logger initializer, was removed
2- the request_details param is mandatory
3- The `user_agent` param form the logger initializer, was moved inside the RequestDetails object.