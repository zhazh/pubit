# -*- coding: utf-8 -*-
"""
.apis.v1.schemas
================================
Provide resources for ajax request.
"""

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

def node_schema(nodeitem):
    return dict(
        create = nodeitem.create,
        name = nodeitem.name,
        path = nodeitem.path,
        parent_path = nodeitem.parent_path,
        size = nodeitem.size,
        type = nodeitem.type,
    )

def dir_schema(nodeitem):
    return dict(
        text = nodeitem.name,
        path = nodeitem.path,
        state = 'closed',
        children = True,
    )