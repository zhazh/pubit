# -*- coding: utf-8 -*-
"""
.apis.v1.schemas
================================
Provide resources for ajax request.
"""
from pubit.node import DirectoryNode

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
    node_desc = dict(
        id = nodeitem.id,
        name = nodeitem.name,
        path = nodeitem.path,
        parent_path = '' if nodeitem.parent_path is None else nodeitem.parent_path,
        size = nodeitem.size,
        type = nodeitem.type,
        create = nodeitem.create,
        visit = nodeitem.visit,
        modify = nodeitem.modify,
    )
    if isinstance(nodeitem, DirectoryNode):
        node_desc['children'] = list()
        for subnode in nodeitem.children():
            node_desc['children'].append(
                dict(
                    id = subnode.id,
                    name = subnode.name,
                    path = subnode.path,
                    parent_path = subnode.parent_path,
                    size = subnode.size,
                    type = subnode.type,
                    create = subnode.create,
                    visit = subnode.visit,
                    modify = subnode.modify,
                )
            )
    return node_desc