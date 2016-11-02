from core import middleware as mware
import uuid
from datetime import timedelta
import base
from os.path import join
import json
from publisher import ajson_ingestor, models, fragment_logic as fragments, utils, logic, ejp_ingestor
from django.test import Client
from django.core.urlresolvers import reverse
from django.conf import settings
#from unittest import skip
SCHEMA_IDX = settings.SCHEMA_IDX # weird, can't import directly from settigns ??

class V2ContentTypes(base.BaseCase):
    def setUp(self):
        self.c = Client()
        self.msid = 16695
        self.ajson_fixture_v1 = join(self.fixture_dir, 'ajson', 'elife-16695-v1.xml.json') # poa
        self.ajson_fixture_v2 = join(self.fixture_dir, 'ajson', 'elife-16695-v2.xml.json') # vor

    def test_accept_types(self):
        "various accept headers return expected response"
        ajson_ingestor.ingest_publish(json.load(open(self.ajson_fixture_v1, 'r')))
        cases = [
            "*/*",
            "application/vnd.elife.article-poa+json; version=1, application/vnd.elife.article-vor+json; version=1",
            "application/vnd.elife.article-poa+json; version=1",
            "application/vnd.elife.article-vor+json; version=1", # yes, even though the returned result is a poa
            # vor v1 or v2
            "application/vnd.elife.article-vor+json; version=1, application/vnd.elife.article-vor+json; version=2",
        ]
        for header in cases:
            resp = self.c.get(reverse('v2:article-version', kwargs={'id': self.msid, 'version': 1}), HTTP_ACCEPT=header)
            self.assertEqual(resp.status_code, 200)

    def test_unacceptable_types(self):
        ajson_ingestor.ingest_publish(json.load(open(self.ajson_fixture_v1, 'r')))
        cases = [
            # vor v2 or v3
            "application/vnd.elife.article-vor+json; version=2, application/vnd.elife.article-vor+json; version=3",
            # poa v2
            "application/vnd.elife.article-poa+json; version=2",
            # ??
            "application/foo.bar.baz; version=1"
        ]
        for header in cases:
            resp = self.c.get(reverse('v2:article-version', kwargs={'id': self.msid, 'version': 1}), HTTP_ACCEPT=header)
            self.assertEqual(resp.status_code, 406, "failed on case %r, got: %s" % (header, resp.status_code))

    def test_response_types(self):
        # ingest the poa and vor versions
        for path in [self.ajson_fixture_v1, self.ajson_fixture_v2]:
            ajson_ingestor.ingest_publish(json.load(open(path, 'r')))

        # map the known types to expected types
        art_list_type = 'application/vnd.elife.articles-list+json;version=1'
        art_poa_type = 'application/vnd.elife.article-poa+json;version=1'
        art_vor_type = 'application/vnd.elife.article-vor+json;version=1'
        art_history_type = 'application/vnd.elife.article-history+json;version=1'

        case_list = {
            reverse('v2:article-list'): art_list_type,
            reverse('v2:article', kwargs={'id': self.msid}): art_vor_type,
            reverse('v2:article-version-list', kwargs={'id': self.msid}): art_history_type,
            reverse('v2:article-version', kwargs={'id': self.msid, 'version': 1}): art_poa_type,
            reverse('v2:article-version', kwargs={'id': self.msid, 'version': 2}): art_vor_type,
        }

        # test
        for url, expected_type in case_list.items():
            resp = self.c.get(url)
            self.assertEqual(resp.status_code, 200,
                             "url %r failed to complete: %s" % (url, resp.status_code))
            self.assertEqual(resp.content_type, expected_type,
                             "%r failed to return %r: %s" % (url, expected_type, resp.content_type))

class V2Content(base.BaseCase):
    def setUp(self):
        ingest_these = [
            #"elife-01968-v1.xml.json",

            "dummyelife-20125-v1.xml.json", # poa
            "dummyelife-20125-v2.xml.json", # poa
            "dummyelife-20125-v3.xml.json", # vor

            # NOT VALID, doesn't ingest
            #"elife-16695-v1.xml.json",
            #"elife-16695-v2.xml.json",
            #"elife-16695-v3.xml.json", # vor

            "dummyelife-20105-v1.xml.json", # poa
            "dummyelife-20105-v2.xml.json", # poa
            "dummyelife-20105-v3.xml.json" # poa, UNPUBLISHED
        ]
        ajson_dir = join(self.fixture_dir, 'ajson')
        for ingestable in ingest_these:
            path = join(ajson_dir, ingestable)
            ajson_ingestor.ingest_publish(json.load(open(path, 'r')))

        self.msid1 = 20125
        self.msid2 = 20105

        # 2 article, 6 versions, 5 published, 1 unpublished
        self.unpublish(self.msid2, version=3)

        # an unauthenticated client
        self.c = Client()
        # an authenticated client
        self.ac = Client(**{
            'REMOTE_ADDR': '10.0.2.6',
            mware.CGROUPS: 'user',
            mware.CID: str(uuid.uuid4()),
            mware.CUSER: 'pants'
        })

    def test_article_list(self):
        "a list of published articles are returned to an unauthenticated response"
        resp = self.c.get(reverse('v2:article-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/vnd.elife.articles-list+json;version=1')
        data = json.loads(resp.content)

        # valid data
        utils.validate(data, SCHEMA_IDX['list'])

        # correct data
        self.assertEqual(data['total'], 2) # two results, [msid1, msid2]
        av1, av2 = data['items']
        self.assertEqual(av1['version'], 2)
        self.assertEqual(av2['version'], 3)

    def test_article_list_including_unpublished(self):
        "a list of published and unpublished articles are returned to an authorized response"
        resp = self.ac.get(reverse('v2:article-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/vnd.elife.articles-list+json;version=1')
        self.assertEqual(resp[settings.KONG_AUTH_HEADER], 'True')
        data = json.loads(resp.content)
        idx = {int(item['id']): item for item in data['items']}

        # valid data
        utils.validate(data, SCHEMA_IDX['list'])

        # correct data
        self.assertEqual(data['total'], 2) # two results, [msid1, msid2]
        self.assertEqual(idx[self.msid1]['version'], 3) # we get the unpublished v3 back
        self.assertEqual(idx[self.msid2]['version'], 3)

    def test_article_poa(self):
        "the latest version of the requested article is returned"
        resp = self.c.get(reverse('v2:article', kwargs={'id': self.msid2}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, "application/vnd.elife.article-poa+json;version=1")
        data = json.loads(resp.content)

        # valid data
        utils.validate(data, SCHEMA_IDX['poa'])

        # correct data
        self.assertEqual(data['version'], 2) # v3 is unpublished

    def test_article_poa_unpublished(self):
        "the latest version of the requested article is returned"
        resp = self.ac.get(reverse('v2:article', kwargs={'id': self.msid2}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, "application/vnd.elife.article-poa+json;version=1")
        data = json.loads(resp.content)

        # valid data
        utils.validate(data, SCHEMA_IDX['poa'])

        # correct data
        self.assertEqual(data['version'], 3)

    def test_article_vor(self):
        "the latest version of the requested article is returned"
        resp = self.c.get(reverse('v2:article', kwargs={'id': self.msid1}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, "application/vnd.elife.article-vor+json;version=1")

        data = json.loads(resp.content)

        # valid data
        utils.validate(data, SCHEMA_IDX['vor'])

        # correct data
        self.assertEqual(data['version'], 3)

    def test_article_unpublished_ver_not_returned(self):
        "unpublished article versions are not returned"
        self.unpublish(self.msid2, version=3)
        self.assertEqual(models.ArticleVersion.objects.filter(article__manuscript_id=self.msid2).exclude(datetime_published=None).count(), 2)
        resp = self.c.get(reverse('v2:article', kwargs={'id': self.msid2}))
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)

        # valid data
        utils.validate(data, SCHEMA_IDX['poa'])

        # correct data
        self.assertEqual(data['version'], 2) # third version was unpublished

    def test_article_does_not_exist(self):
        fake_msid = 123
        resp = self.c.get(reverse('v2:article', kwargs={'id': fake_msid}))
        self.assertEqual(resp.status_code, 404)

    def test_article_versions_list(self):
        "valid json content is returned"
        # we need some data that can only come from ejp for this
        ejp_data = join(self.fixture_dir, 'dummy-ejp-for-v2-api-fixtures.json')
        ejp_ingestor.import_article_list_from_json_path(logic.journal(), ejp_data, create=False, update=True)

        resp = self.c.get(reverse('v2:article-version-list', kwargs={'id': self.msid2}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/vnd.elife.article-history+json;version=1')
        data = json.loads(resp.content)

        # valid data
        utils.validate(data, SCHEMA_IDX['history'])

        # correct data
        self.assertEqual(len(data['versions']), 2) # this article only has two *published*

    def test_unpublished_article_versions_list(self):
        "valid json content is returned"
        # we need some data that can only come from ejp for this
        ejp_data = join(self.fixture_dir, 'dummy-ejp-for-v2-api-fixtures.json')
        ejp_ingestor.import_article_list_from_json_path(logic.journal(), ejp_data, create=False, update=True)

        resp = self.ac.get(reverse('v2:article-version-list', kwargs={'id': self.msid2}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/vnd.elife.article-history+json;version=1')
        data = json.loads(resp.content)

        # valid data
        # TODO: my unpublished PR on the api-raml isn't merged in yet
        # the null values for the 'published' value are still invalid
        #utils.validate(data, SCHEMA_IDX['history'])

        # correct data
        self.assertEqual(len(data['versions']), 3)  # this article has two *published*, one *unpublished*

    def test_article_versions_list_does_not_exist(self):
        models.Article.objects.all().delete()
        self.assertEqual(models.Article.objects.count(), 0)
        resp = self.c.get(reverse('v2:article-version-list', kwargs={'id': self.msid2}))
        self.assertEqual(resp.status_code, 404)

    def test_article_version(self):
        versions = [1, 2, 3]
        for ver in versions:
            resp = self.c.get(reverse('v2:article-version', kwargs={'id': self.msid2, 'version': ver}))
            self.assertEqual(resp.status_code, 200)

    def test_article_version_art_does_not_exist(self):
        "returns 404 when an article doesn't exist for the article-version endpoint"
        models.Article.objects.all().delete()
        self.assertEqual(models.Article.objects.count(), 0)
        resp = self.c.get(reverse('v2:article-version', kwargs={'id': '123', 'version': 1}))
        self.assertEqual(resp.status_code, 404)

    def test_article_version_artver_does_not_exist(self):
        "returns 404 when a version of the article doesn't exist for the article-version endpoint"
        resp = self.c.get(reverse('v2:article-version', kwargs={'id': self.msid2, 'version': 9}))
        self.assertEqual(resp.status_code, 404)


class V2PostContent(base.BaseCase):
    def setUp(self):
        path = join(self.fixture_dir, 'ajson', "elife-16695-v1.xml.json")
        ajson_ingestor.ingest_publish(json.load(open(path, 'r')))

        self.msid = 16695
        self.version = 1

        # layer in enough to make it validate ...
        placeholders = {
            'statusDate': '2001-01-01T00:00:00Z',
        }
        fragments.add(self.msid, 'placeholders', placeholders)
        self.av = models.ArticleVersion.objects.filter(article__manuscript_id=self.msid)[0]
        self.assertTrue(fragments.merge_if_valid(self.av))

        self.c = Client()

    def test_add_fragment(self):
        "a POST request can be sent that adds an article fragment"
        key = 'test-frag'
        url = reverse('v2:article-fragment', kwargs={'art_id': self.msid, 'fragment_id': key})
        fragment = {'title': 'pants-party'}
        q = models.ArticleFragment.objects.filter(article__manuscript_id=self.msid)

        # POST fragment into lax
        self.assertEqual(q.count(), 2) # 'xml->json', placeholder
        resp = self.c.post(url, json.dumps(fragment), content_type="application/json")
        self.assertEqual(resp.status_code, 200)

        # fragment has been added
        frag = models.ArticleFragment.objects.get(type=key)
        self.assertEqual(frag.fragment, fragment)

    def test_add_fragment_twice(self):
        key = 'test-frag'
        url = reverse('v2:article-fragment', kwargs={'art_id': self.msid, 'fragment_id': key})

        # POST fragment into lax
        fragment1 = {'title': 'pants-party'}
        resp = self.c.post(url, json.dumps(fragment1), content_type="application/json")
        self.assertEqual(resp.status_code, 200)

        # fragment has been added
        frag = models.ArticleFragment.objects.get(type=key)
        self.assertEqual(frag.fragment, fragment1)

        # do it again
        fragment2 = {'title': 'party-pants'}
        resp = self.c.post(url, json.dumps(fragment2), content_type="application/json")
        self.assertEqual(resp.status_code, 200)

        # fragment has been added
        frag = models.ArticleFragment.objects.get(type=key)
        self.assertEqual(frag.fragment, fragment2)

    def test_add_fragment_for_non_article(self):
        # POST fragment into lax
        url = reverse('v2:article-fragment', kwargs={'art_id': 99999, 'fragment_id': 'test-frag'})
        resp = self.c.post(url, json.dumps({}), content_type="application/json")
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(models.ArticleFragment.objects.count(), 2) # xml->json, placeholder

    def test_add_fragment_for_unpublished_article(self):
        # unpublish our article
        self.unpublish(self.msid, self.version)
        av = self.freshen(self.av)
        self.assertFalse(av.published())

        # post to unpublished article
        url = reverse('v2:article-fragment', kwargs={'art_id': self.msid, 'fragment_id': 'test-frag'})
        fragment = {'more-article-content': 'pants'}
        resp = self.c.post(url, json.dumps(fragment), content_type="application/json")
        self.assertEqual(resp.status_code, 200)

    def test_add_fragment_fails_unknown_content_type(self):
        url = reverse('v2:article-fragment', kwargs={'art_id': self.msid, 'fragment_id': 'test-frag'})
        resp = self.c.post(url, json.dumps({}), content_type="application/PAAAAAAANTSss")
        self.assertEqual(resp.status_code, 415) # unsupported media type

    def test_add_bad_fragment(self):
        """request with fragment that would cause otherwise validating article json
        to become invalid is refused"""
        self.assertEqual(models.ArticleFragment.objects.count(), 2) # xml->json, placeholder
        fragment = {'doi': 'this is no doi!'}
        url = reverse('v2:article-fragment', kwargs={'art_id': self.msid, 'fragment_id': 'test-frag'})
        resp = self.c.post(url, json.dumps(fragment), content_type="application/json")
        self.assertEqual(models.ArticleFragment.objects.count(), 2) # nothing was created
        self.assertEqual(resp.status_code, 400) # bad client request

class RequestArgs(base.BaseCase):
    def setUp(self):
        ingest_these = [
            #"elife-01968-v1.xml.json",

            "dummyelife-20125-v1.xml.json", # poa
            "dummyelife-20125-v2.xml.json", # poa
            "dummyelife-20125-v3.xml.json", # vor

            # NOT VALID, doesn't ingest
            #"elife-16695-v1.xml.json",
            #"elife-16695-v2.xml.json",
            #"elife-16695-v3.xml.json", # vor

            "dummyelife-20105-v1.xml.json", # poa
            "dummyelife-20105-v2.xml.json", # poa
            "dummyelife-20105-v3.xml.json" # poa
        ]
        ajson_dir = join(self.fixture_dir, 'ajson')
        for ingestable in ingest_these:
            path = join(ajson_dir, ingestable)
            ajson_ingestor.ingest_publish(json.load(open(path, 'r')))

        self.msid1 = 20125
        self.msid2 = 20105

        av = models.ArticleVersion.objects.get(article__manuscript_id=self.msid1, version=3)
        av.datetime_published = av.datetime_published + timedelta(days=1) # helps debug ordering
        av.save()

        self.c = Client()

    #
    # Pagination
    #

    def test_article_list_paginated_page1(self):
        "a list of articles are returned, paginated by 1"
        resp = self.c.get(reverse('v2:article-list') + "?per-page=1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/vnd.elife.articles-list+json;version=1')
        data = json.loads(resp.content)

        # valid data
        utils.validate(data, SCHEMA_IDX['list'])

        # correct data
        self.assertEqual(len(data['items']), 1) # ONE result, [msid1]
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['items'][0]['id'], str(self.msid1))

    def test_article_list_paginated_page2(self):
        "a list of articles are returned, paginated by 1"
        resp = self.c.get(reverse('v2:article-list') + "?per-page=1&page=2")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/vnd.elife.articles-list+json;version=1')
        data = json.loads(resp.content)

        # valid data
        utils.validate(data, SCHEMA_IDX['list'])

        # correct data
        self.assertEqual(len(data['items']), 1) # ONE result, [msid2]
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['items'][0]['id'], str(self.msid2))

    def test_article_list_page_no_per_page(self):
        "defaults for per-page and page parameters kick in when not specified"
        resp = self.c.get(reverse('v2:article-list') + "?page=2")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/vnd.elife.articles-list+json;version=1')
        data = json.loads(resp.content)

        # correct data (too few to hit next page)
        self.assertEqual(len(data['items']), 0)
        self.assertEqual(data['total'], 0)

    def test_article_list_ordering_asc(self):
        resp = self.c.get(reverse('v2:article-list') + "?order=asc")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/vnd.elife.articles-list+json;version=1')
        data = json.loads(resp.content)

        # correct data (too few to hit next page)
        self.assertEqual(len(data['items']), 2)
        self.assertEqual(data['total'], 2)

        id_list = map(lambda row: int(row['id']), data['items'])
        self.assertEqual(id_list, [self.msid2, self.msid1]) # numbers ascend -> 20105, 20125

    def test_article_list_ordering_desc(self):
        resp = self.c.get(reverse('v2:article-list') + "?order=desc")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/vnd.elife.articles-list+json;version=1')
        data = json.loads(resp.content)

        # correct data (too few to hit next page)
        self.assertEqual(len(data['items']), 2)
        self.assertEqual(data['total'], 2)

        id_list = map(lambda row: int(row['id']), data['items'])
        self.assertEqual(id_list, [self.msid1, self.msid2]) # numbers descend 20125, 20105 <-

    #
    # bad requests
    #

    def test_article_list_bad_min_max_perpage(self):
        "per-page value must be between known min and max values"
        resp = self.c.get(reverse('v2:article-list') + "?per-page=-1")
        self.assertEqual(resp.status_code, 400) # bad request

        resp = self.c.get(reverse('v2:article-list') + "?per-page=999")
        self.assertEqual(resp.status_code, 400) # bad request

    def test_article_list_negative_page(self):
        "page value cannot be zero or negative"
        resp = self.c.get(reverse('v2:article-list') + "?page=0")
        self.assertEqual(resp.status_code, 400) # bad request

        resp = self.c.get(reverse('v2:article-list') + "?page=-1")
        self.assertEqual(resp.status_code, 400) # bad request
