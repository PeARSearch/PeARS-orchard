# SPDX-FileCopyrightText: 2022 PeARS Project, <community@pearsproject.org>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

# Detect whether page is under CC license and
# a snippet can be extracted from it.


def open_site(url):
    '''Checking for wikipedia or SO page'''
    for i in ["wikipedia.org", "stackoverflow.com"]:
        if i in url:
            return True
    return False


def cc_img(bs_obj):
    '''Checking for CC logo'''
    imgs = bs_obj.find_all('img')
    for img in imgs:
        src = img['src']
        for i in ["creativecommons.org", "cc-by"]:
            if i in src:
                return True
    return False


def is_cc(url, bs_obj):
    '''If page is CC-licensed, get snippet'''
    if open_site(url) or cc_img(bs_obj):
        return True
    else:
        return False
