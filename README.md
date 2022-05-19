# Naive FEEDya

*Feedya is like a russian name Fedor [ˈfʲɵdər].*

Naive Feedya is a small news feed with simple web UI and filtering algorithm based on Naive Bayes classifier.


## How to run:

### Prod environment
1. Pull image
```
docker pull antonsve4/naive-feedya:main
```
2. Run image
```
docker run -it -e USERNAME=YOU-USERNAME -e PASSWORD=YOUR-PASSWORD /usr/share/python3/app/bin/python3 main.py
```
Check localhost path (default port 8008) ```/news``` (default path).

### Dev environment
1. Run project using docker-compose:
```
docker-compose -f docker-compose.dev.yml up
```
Check localhost path (default port 8008) ```/news``` (default path).

## Supported options:
- TBD


## How to run tests and code style check:
1. Run tests
```
docker-compose -f docker-compose.dev.yml run nf /usr/share/python3/app/bin/pytest
```
2. Check code style
```
docker-compose -f docker-compose.dev.yml run nf /usr/share/python3/app/bin/flake8
```
