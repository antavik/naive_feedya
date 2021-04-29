# Naive FEEDya

*Feedya is like a russian name Fedor [ˈfʲɵdər].*

Naive Feedya is a small news feed with simple web UI and filtering algorithm based on Naive Bayes classifier.


### Warning:
Currently application doesn't have login mechanism.


### TODO:
- [ ] Login system
- [ ] Preperations to publish in web


### How to run:
```
docker-compose -f docker-compose-dev.yml up
```
Check localhost ```127.0.0.1:8008/feed/news```


### How to run tests and code style check:
1. Run tests
```
docker-compose -f docker-compose-dev.yml run naive_feedya pytest
```
2. Check code style
```
docker-compose -f docker-compose-dev.yml run naive_feedya flake8
```
