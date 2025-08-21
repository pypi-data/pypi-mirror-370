# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Bitergia
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

from perceval.backends.public_inbox.public_inbox import PublicInbox, PublicInboxCommand
from perceval.backends.topicbox.topicbox import Topicbox, TopicboxCommand
from perceval.backends.pontoon.pontoon import Pontoon, PontoonCommand
from .enriched.public_inbox import PublicInboxEnrich
from .enriched.topicbox import TopicboxEnrich
from .enriched.pontoon import PontoonEnrich
from .raw.public_inbox import PublicInboxOcean
from .raw.topicbox import TopicboxOcean
from .raw.pontoon import PontoonOcean


def get_connectors():
    return {
        "public_inbox": [PublicInbox, PublicInboxOcean, PublicInboxEnrich, PublicInboxCommand],
        "topicbox": [Topicbox, TopicboxOcean, TopicboxEnrich, TopicboxCommand],
        "pontoon": [Pontoon, PontoonOcean, PontoonEnrich, PontoonCommand]
    }
