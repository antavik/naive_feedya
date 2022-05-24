# Naive FEEDya

*Feedya is like a russian name Fedor [ˈfʲɵdər].*

Naive Feedya is a small news feed with simple web UI and filtering algorithm based on Naive Bayes classifier.
Now it supports only russian and english languages.


## How to run:

### Prod environment
1. Pull image
```
docker pull antonsve4/naive-feedya:main
```
2. Run image
```
docker run -it \
-e USERNAME=YOU-USERNAME -e PASSWORD=YOUR-PASSWORD -e CONFIG_NAME=your-conf.ini \
/usr/share/python3/app/bin/python3 main.py
```
Check ```localhost:8008/news``` or ```localhost:8008/spam```.

### Dev environment
1. Run project using docker-compose:
```
docker-compose -f docker-compose.dev.yml up
```
Check ```localhost:8008/news``` or ```localhost:8008/spam```.

## Supported options:
- ```DEV_MODE``` – boolean switcher of development mode, default value ```false```.
- ```USERNAME``` – username to login, required for production mode.
- ```PASSWORD``` – password to login, required for production mode.
- ```APP_LANG``` – language of the parser, default ```english```.
- ```CACHE_PATH``` – path to cache folder to store feeds and classifier data, default value ```/var/lib/naive_feedya/```.
- ```CONFIG_NAME``` – name of a feeds config, required for production mode.
- ```PATH_PREFIX``` – path to build UI links.
- ```LOGGING_FILE_ENABLE``` – boolean switcher to save logs in file.

## How to run tests and code style check:
1. Run tests
```
docker-compose -f docker-compose.dev.yml run nf /usr/share/python3/app/bin/pytest
```
2. Check code style
```
docker-compose -f docker-compose.dev.yml run nf /usr/share/python3/app/bin/flake8
```
