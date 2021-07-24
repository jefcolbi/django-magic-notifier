from __future__ import absolute_import, unicode_literals

import logging
import os
import traceback
from urllib.parse import quote

import requests
from celery import shared_task
from django.conf import settings
from django.shortcuts import reverse
