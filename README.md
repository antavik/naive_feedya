# Naive FEEDya

*Feedya is like a russian name Fedor [ˈfʲɵdər].*

Naive Feedya is a small news feed with simple web UI and filtering algorithm based on Naive Bayes classifier.


## How to run:

### Prod environment
1. Prepare ```naive_feedya/.env``` file and set ```USERNAME``` and ```PASSWORD``` vars there.
2. Run project using docker-compose:
```
docker-compose -f docker-compose.prod.yml up
```
Check localhost path (default port 8008) ```/feed/news```

### Dev environment
1. Run project using docker-compose:
```
docker-compose -f docker-compose.dev.yml up
```
Check localhost path (default port 8008) ```/feed/news```


## How to run tests and code style check:
1. Run tests
```
docker-compose -f docker-compose.dev.yml run nf pytest
```
2. Check code style
```
docker-compose -f docker-compose.dev.yml run nf flake8
```
