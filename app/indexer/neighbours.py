# SPDX-FileCopyrightText: 2022 PeARS Project, <community@pearsproject.org>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

from app.api.models import Urls
from app.utils_db import get_db_url_vector
from app.utils import convert_to_array, cosine_similarity


def sim_to_matrix_url(target_url, n):
    cosines = {}
    target = convert_to_array(get_db_url_vector(target_url))
    for u in Urls.query.all():
        cos = cosine_similarity(target, convert_to_array(u.vector))
        cosines[u.url] = cos
    c = 0
    neighbours = []
    for url in sorted(cosines, key=cosines.get, reverse=True):
        if c < n:
            # print(t,cosines[t])
            title = Urls.query.filter(Urls.url == url).first().title
            snippet = Urls.query.filter(Urls.url == url).first().snippet
            url = Urls.query.filter(Urls.url == url).first().url
            neighbours.append([url, title, snippet])
            c += 1
        else:
            break
    return neighbours, len(cosines)


def neighbour_urls(target_url, dm_dict):
    neighbours, num_db_entries = sim_to_matrix_url(target_url, 50)
    return neighbours, num_db_entries
