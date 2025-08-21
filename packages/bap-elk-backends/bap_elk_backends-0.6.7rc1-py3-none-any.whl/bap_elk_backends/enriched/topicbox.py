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

from grimoire_elk.elastic_mapping import Mapping as BaseMapping
from grimoire_elk.enriched.enrich import Enrich, metadata
from grimoirelab_toolkit.datetime import str_to_datetime
from grimoirelab_toolkit.uris import urijoin


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
                 "Subject_analyzed": {
                   "type": "text",
                   "fielddata": true,
                   "index": true
                 }
           }
        } """

        return {"items": mapping}


class TopicboxEnrich(Enrich):

    mapping = Mapping

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.studies = []
        self.studies.append(self.enrich_demography)

    def get_field_author(self):
        return "from"

    def get_identities(self, item):
        """ Return the identities from an item """

        item = item['data']

        if 'from' in item and item['from']:
            user = self.get_sh_identity(item['from'])
            yield user

    def get_sh_identity(self, item, identity_field=None):
        identity = {f: None for f in ['email', 'name', 'username']}

        user = item  # by default a specific user dict is expected
        if isinstance(item, dict) and 'data' in item:
            user = item['data'][identity_field]

        if isinstance(user, list):
            user = user[0]

        if not user:
            return identity

        identity['username'] = None
        identity['email'] = user['email']
        identity['name'] = user['name']
        if not identity['name'] and identity['email']:
            identity['name'] = identity['email'].split('@')[0]
        return identity

    def get_project_repository(self, eitem):
        return eitem['origin']

    @metadata
    def get_rich_item(self, item):
        eitem = {}

        self.copy_raw_fields(self.RAW_FIELDS_COPY, item, eitem)

        message = item['data']

        eitem['Date'] = message['sentAt']
        eitem['Subject'] = message['subject'][:self.KEYWORD_MAX_LENGTH]
        eitem['Subject_analyzed'] = message['subject']
        eitem['Message-ID'] = message['messageId'][0]
        eitem['topicbox_message_id'] = message['id']
        eitem["email_date"] = str_to_datetime(item["metadata__updated_on"]).isoformat()
        eitem["list"] = item["origin"]
        eitem["root"] = not bool('inReplyTo' in message and message['inReplyTo'])
        eitem["thread_url"] = urijoin(item['origin'], message['threadId'])
        eitem["url"] = f"{eitem['thread_url']}-{message['id']}"

        eitem["body_extract"] = message['preview']
        if message['textBody']:
            eitem["size"] = message['textBody'][0]['size']
        else:
            eitem['size'] = 0

        # Time zone
        try:
            message_date = str_to_datetime(message['sentAt'])
            eitem["tz"] = int(message_date.strftime("%z")[0:3])
        except Exception:
            eitem["tz"] = None

        eitem['thread'] = message['threadId']
        eitem['group'] = item["origin"].strip('/').split('/')[-1]

        if self.sortinghat:
            eitem.update(self.get_item_sh(item))

        if self.prjs_map:
            eitem.update(self.get_item_project(eitem))

        self.add_repository_labels(eitem)
        self.add_metadata_filter_raw(eitem)
        eitem.update(self.get_grimoire_fields(message['sentAt'], "message"))

        return eitem
