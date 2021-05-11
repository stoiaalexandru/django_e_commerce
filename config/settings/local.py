from .base import *
import os

DEBUG = True
INTERNAL_IPS = ['127.0.0.1']
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', ]
SECRET_KEY = 'ltfar(==c+spc(#v8ugzvi$d*+l&$)jr2(&n8t*amvd2+oslvk'


CELERY_BROKER_URL = 'redis://:foobared@45.13.136.143:6379/3'

DATABASES = {
    'default': {

        'ENGINE': 'django.db.backends.postgresql',

        'NAME': 'django_e_commerce_db',

        'USER': 'andu',

        'PASSWORD': 'test1234',

        'HOST': '45.13.136.143',

        'PORT': '5432',

    }
}

EMAIL_HOST_USER = 'testingexamplemail123@gmail.com'
EMAIL_HOST_PASSWORD = 'TestingMotherfucker01'