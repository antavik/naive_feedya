# Naive FEEDya

*Feedya is like a russian name Fedor [ˈfʲɵdər].*

![Man and dog are reading](https://downloader.disk.yandex.ru/preview/7bcc70002034de8d5e59a9f9812c7f2aec7fe87892d2553c5ac1c869dbe90069/6069c814/sYd46tWI_4ttuoR-JlJYmy7TGLbrIi3H9PZ-VpbuF5akKRpNpvOarjp_JG80SE9T87bBXtDv5ZrMMboiL0EaRg%3D%3D?uid=0&filename=EB_065_01_1953_small.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v2&size=2048x2048)

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
