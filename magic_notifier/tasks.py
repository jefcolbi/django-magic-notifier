from __future__ import absolute_import, unicode_literals
from celery import shared_task

import requests
from django.conf import settings
from django.shortcuts import reverse
import traceback
from urllib.parse import quote
import os
import logging
