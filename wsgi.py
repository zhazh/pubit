# -*- coding: utf-8 -*-
"""
wsgi
========================
enterpoint for gunicorn.
command:
```
$ gunicorn --workers=2 --bind=0.0.0.0:5000 wsgi:app
``` 
--workers: thread number, change it by yourself.
"""

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from pubit import create_app
app = create_app('production')