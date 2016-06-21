import json
import models
from utils import subdict, exsubdict, todt, delall, msid2doi, doi2msid
import logging
import requests
from datetime import datetime
from django.conf import settings

LOG = logging.getLogger(__name__)

def striptz(dtstr):
    "strips the timezone component of a stringified datetime"
    return dtstr[:dtstr.find('T')]

def import_article_version(article, article_data, create=True, update=False):
    expected_keys = ['title', 'version', 'update', 'pub-date', 'status']
    kwargs = subdict(article_data, expected_keys)

    try:
        doi = article_data['doi']
        version = int(kwargs['version'])
        version_date = kwargs.get('update')
        datetime_published = kwargs['pub-date']
        
        context = {'article': doi, 'version': version}
        LOG.info("importing ArticleVersion", extra=context)
        
        if version_date and version == 1:
            # this is so common it's not even worth a debug
            #LOG.warn("inconsistency: a v1 has an 'update' date", extra=context)

            d1, d2 = striptz(version_date), striptz(datetime_published)
            if d1 != d2:
                c = {}; c.update(context);
                c.update({'pub-date': datetime_published, 'update': version_date})
                LOG.warn("double inconsistency: not only do we have an 'update' date for a v1, it doesn't match the date published", extra=c)

                # 'update' date occurred before publish date ...
                if d1 < d2:
                    LOG.warn("triple inconsistency: not only do we have an 'update' date for a v1 that doesn't match the date published, it was actually updated *before* it was published", extra=c)
                

        if not version_date and version > 1:
            LOG.warn("inconsistency: a version > 1 does not have an 'update' date", extra=context)
            if settings.FAIL_ON_NO_UPDATE_DATE:
                msg = "no 'update' date found for ArticleVersion"
                LOG.warn(msg, extra=context)
                raise ValueError(msg)
            msg = "no 'update' date found for ArticleVersion, using None instead"
            LOG.warn(msg, extra=context)
            version_date = None #kwargs['pub-date'] # this was just confusing

        # post process data
        kwargs.update({
            'article':  article,
            'version': version,
            'datetime_published': todt(version_date),
            'status': kwargs['status'].lower(),
        })
        delall(kwargs, ['pub-date', 'update'])
    except KeyError:
        LOG.error("expected keys invalid/not present", \
                      extra={'expected_keys': expected_keys})
        raise

    try:
        avobj = models.ArticleVersion.objects.get(article=article, version=kwargs['version'])
        if not update:
            msg = "Article with version does exists but update == False"
            LOG.warn(msg, extra=context)
            raise AssertionError(msg)
        LOG.debug("ArticleVersion found, updating")
        for key, val in kwargs.items():
            setattr(avobj, key, val)
        avobj.save()
        LOG.info("updated existing ArticleVersion", extra=context)
        return avobj
    
    except models.ArticleVersion.DoesNotExist:
        if not create:
            msg = "ArticleVersion with version does not exist and create == False"
            LOG.warn(msg, extra=context)
            raise

    LOG.debug("ArticleVersion NOT found, creating", extra=context)
    avobj = models.ArticleVersion(**kwargs)
    avobj.save()
    LOG.info("created new ArticleVersion", extra=context)
    return avobj

def import_article(journal, article_data, create=True, update=False):
    if not article_data or not isinstance(article_data, dict):
        raise ValueError("given data to import is empty/invalid")
    expected_keys = ['doi', 'volume', 'path', 'article-type', 'manuscript_id']

    # data wrangling
    try:
        kwargs = subdict(article_data, expected_keys)

        # JATS XML doesn't contain the manuscript ID. derive it from doi
        if not kwargs.has_key('manuscript_id') and kwargs.has_key('doi'):
            kwargs['manuscript_id'] = doi2msid(kwargs['doi'])

        elif not kwargs.has_key('doi') and kwargs.has_key('manuscript_id'):
            kwargs['doi'] = msid2doi(kwargs['manuscript_id'])

        context = {'article': kwargs['doi']}

        LOG.info("importing Article", extra=context)

        # post process data
        kwargs.update({
            'journal':  journal,
            'volume': int(kwargs['volume']),
            'website_path': kwargs['path'],
            'type': kwargs['article-type'],
        })
        delall(kwargs, ['path', 'article-type'])
    except KeyError:
        raise ValueError("expected keys invalid/not present: %s" % ", ".join(expected_keys))
    
    # attempt to insert
    article_key = subdict(kwargs, ['doi', 'version'])
    try:
        article_obj = models.Article.objects.get(**article_key)
        avobj = import_article_version(article_obj, article_data, create, update)
        LOG.info("Article exists, updating", extra=context)
        for key, val in kwargs.items():
            setattr(article_obj, key, val)
        article_obj.save()
        return article_obj, avobj

    except models.Article.DoesNotExist:
        # we've been told not to create new articles.
        # this is now a legitimate exception
        if not create:
            raise
    article_obj = models.Article(**kwargs)
    article_obj.save()
    avobj = import_article_version(article_obj, article_data, create, update)
    LOG.info("created new Article %s" % article_obj)
    return article_obj, avobj

def import_article_from_json_path(journal, article_json_path, *args, **kwargs):
    "convenience function. loads the article data from a json file"
    return import_article(journal, json.load(open(article_json_path, 'r')), *args, **kwargs)

#
# import article from a github repo
# this is tied to eLife right now, but there is some code to make this more robust:
# src/publisher/super_lazy_repo_lookup.py
#

def github_url(doi, version=None):
    assert version == None, "fetching specific versions of articles from github is not yet supported!"
    if '/' in doi:
        # we have a full doi
        fname = "%s.xml.json" % doi.lower().split('/')[1].replace('.', '')
    else:
        # assume we have a pub-id (doi sans publisher id, the 'eLife.00003' in the '10.7554/eLife.00003'
        fname = doi.replace('.', '') + ".xml.json"
    return "https://raw.githubusercontent.com/elifesciences/elife-article-json/master/article-json/" + fname

def fetch_url(url):
    try:
        LOG.info("fetching url %r", url)
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 404:
            logging.warning("given url %r returned a 404", url)
    except ValueError:
        logging.warning("got a response but it wasn't json")
    except:
        logging.exception("unhandled exception attempting to fetch url %r", url)
        raise

def import_article_from_github_repo(journal, doi, version=None):
    if not doi or not str(doi).strip():
        raise ValueError("bad doi") # todo - shift into a utility?
    return import_article(journal, fetch_url(github_url(doi, version)))
