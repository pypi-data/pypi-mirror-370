# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#   Jose Javier Merchante <jjmerchante@bitergia.com>
#

import logging

from grimoire_elk.elastic_mapping import Mapping as BaseMapping
from grimoire_elk.enriched.enrich import Enrich
from grimoirelab_toolkit.datetime import str_to_datetime
from grimoirelab_toolkit.uris import urijoin


logger = logging.getLogger(__name__)


class Mapping(BaseMapping):

    @staticmethod
    def get_elastic_mappings(es_major):
        """Get Elasticsearch mapping.

        :param es_major: major version of Elasticsearch, as string
        :returns:        dictionary with a key, 'items', with the mapping
        """

        mapping = """
        {
            "properties": {
               "translation_string_analyzed": {
                    "type": "text",
                    "index": true
               },
               "id": {
                    "type": "keyword"
               },
               "locale": {
                    "type": "keyword"
               }
            }
        }
        """

        return {"items": mapping}


class PontoonEnrich(Enrich):

    mapping = Mapping

    action_roles = ['user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.studies = []
        self.studies.append(self.enrich_demography)

    def get_field_author(self):
        return "user"

    def get_identities(self, item):
        """ Return the identities from an item """

        user = self.get_sh_identity(item, identity_field='user')
        return [user]

    def get_sh_identity(self, item, identity_field=None):
        identity = {}

        user = item  # by default a specific user dict is expected
        if isinstance(item, dict) and 'data' in item:
            user = item['data'][identity_field]
        elif isinstance(item, dict) and identity_field in item:
            user = item[identity_field]

        if not user:
            return identity

        identity['name'] = user['name']
        if '@' in user['name']:
            identity['email'] = user['name']
        else:
            identity['email'] = None
        identity['username'] = None
        return identity

    def get_project_repository(self, eitem):
        return eitem['origin']

    def get_field_unique_id(self):
        return "uuid"

    def get_rich_item(self, item):
        eitem = {}
        self.copy_raw_fields(self.RAW_FIELDS_COPY, item, eitem)

        action = item['data']

        eitem['id'] = action['id']

        eitem['type'] = action['type']
        eitem['date'] = str_to_datetime(action['date']).isoformat()

        eitem['user_name'] = action['user']['name']
        eitem['system_user'] = action['user']['system_user']
        eitem['user_pk'] = action['user']['pk']

        eitem['entity_pk'] = action['entity']['pk']
        eitem['entity_key'] = action['entity']['key']

        eitem['locale'] = action['locale']['code']
        eitem['locale_name'] = action['locale']['name']

        eitem['resource_pk'] = action['resource']['pk']
        eitem['resource_path'] = action['resource']['path']
        eitem['resource_format'] = action['resource']['format']

        eitem['translation_pk'] = action['translation']['pk']
        eitem['translation_string'] = action['translation']['string'][:self.KEYWORD_MAX_LENGTH]
        eitem['translation_string_analyzed'] = action['translation']['string']
        eitem['translation_errors'] = len(action['translation']['errors'])
        eitem['translation_warnings'] = len(action['translation']['warnings'])
        eitem['translation_approved'] = action['translation']['approved']
        eitem['translation_rejected'] = action['translation']['rejected']
        eitem['translation_pretranslated'] = action['translation']['pretranslated']
        eitem['translation_fuzzy'] = action['translation']['fuzzy']

        eitem['project_pk'] = action['project']['pk']
        eitem['project_name'] = action['project']['name']
        eitem['project_slug'] = action['project']['slug']

        origin = "/".join(item['origin'].split('/')[:-1])
        url = urijoin(origin,
                      action['locale']['code'],
                      action['project']['slug'],
                      action['resource']['path'])
        url += f"?string={action['entity']['pk']}"
        eitem['url'] = url

        if self.sortinghat:
            eitem.update(self.get_item_sh(action, self.action_roles, 'date'))

        if self.prjs_map:
            eitem.update(self.get_item_project(eitem))

        self.add_repository_labels(eitem)
        self.add_metadata_filter_raw(eitem)
        eitem.update(self.get_grimoire_fields(action['date'], "action"))

        return eitem
