# SharedKernel
this is a shared kernel package

# Change Log
### Version 2.2.3
- add paginate to mongo repository
### Version 2.2.2
- update on audit logging queries
- added is_audit to update_one parameters
### Version 2.2.1
- fixbug requirements
### Version 2.2.0
- implement Audit logging
### Version 2.1.2
- Update pydantic parse_object with model_validate
### Version 2.1.0
- Implement persian string normalizer
### Version 2.0.3
- Fix boto3 version
### Version 2.0.2
- Fix FastApi dependency
### Version 2.0.1
- Fix minor bugs
### Version 2.0.0
- Update pydantic version
- Delete vector databases
- Implement JsonStringModel
### Version 1.9.0
- Implement DataFormatConverter
### Version 1.8.0
- Implement persian number normalizer
### Version 1.7.3
- Add optional folder name for s3 uploader to save the file in
### Version 1.7.2
- Fix bug of to_diff_persian_date_time_string
### Version 1.7.1
- Update BaseDocument initial values
### Version 1.7.0
- Implement S3 Uploader
### Version 1.6.10
- Add updated_on to BaseDocument
- Update phonenumber normalizer
### Version 1.6.9
- Delete milvus
### Version 1.6.8
- Fix Date Converter Bug
### Version 1.6.7
- Fix bug and remove additional features
### Version 1.6.6
- Fix bug of phonenumber normalizer
### Version 1.6.5
- Update on the JWTBearer (Save decoded token in request state)
### Version 1.6.4
- Update normlizer package
### Version 1.6.3
- Fix minor bug in phone normalizer
### Version 1.6.2
- Minor update: normalize function name
### Version 1.6.1
- Minor update normalize functions
### Version 1.6
- Add phone number normalizer
### Version 1.5.2
- Add created_on to base_document
### Version 1.5.1
- fix mongo repository bug
### Version 1.5.0
- implement date converter
  -  example: فردا - دیروز - یک ماه قبل
### Version 1.4.5
- upgrade fastapi version
### Version 1.4.4
- Fix regex masking bugs
### Version 1.4.3
- Fix collection bug in MongoGenericRepository
### Version 1.4.2
- Fix minor bugs
### Version 1.4.1
- Fix minor bug in MongoGenericRepository
### Version 1.4.0
- Implement date convertor for jalali and georgian
### Version 1.3.0
- Implement Sentry For Log Exceptions
### Version 1.2.0
- Implement Regex Masking
# Create Package
    python3 -m pip install --upgrade build
    python3 -m build
    python3 -m pip install --upgrade twine
    python3 -m twine upload dist/*

# Pypi
pip install sharedkernel
