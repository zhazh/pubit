# -*- coding: utf-8 -*-
"""
.apis.v1.schemas
================================
Provide resources for ajax request.
"""

from pubit.models import Pubitem

def pub_schema(pubitem):
    return dict(
        id = pubitem.id,
        uuid = pubitem.uuid,
        name = pubitem.name,
        description = pubitem.description,
        pubtime = pubitem.standard_pubtime,
        location = pubitem.location,
        password = pubitem.password,
        access = pubitem.access,
        allow_upload = pubitem.allow_upload
    )