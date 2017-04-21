import sys, json
import os
from os.path import join
from publisher import models, logic
from publisher.utils import lmap, pad_msid
from django.core.management.base import BaseCommand
import logging

LOG = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'for snapshotting queries and uploading to s3 without celery'

    def echo(self, x):
        self.stdout.write(str(x))
        self.stdout.flush()

    def handle(self, *args, **options):
        try:

            avl = models.ArticleVersion.objects.all() \
                .select_related('article') \
                .defer('article_json_v1', 'article_json_v1_snippet') \
                .order_by('-article__manuscript_id', 'version')

            output_dir = join('/tmp', 'ajson')
            os.system('mkdir -p %s' % output_dir)

            def write_ajson(av):
                fname = "elife-%s-v%s.json" % (pad_msid(av.article.manuscript_id), av.version)
                path = join(output_dir, fname)
                if os.path.exists(path):
                    self.echo("skipping %s: path exists" % path)
                with open(path, 'w') as fh:
                    json.dump(logic.article_json(av), fh)
                    self.echo("wrote %s" % path)

            # limit here
            # avl = avl[:100]
                    
            lmap(write_ajson, avl)

        except Exception as err:
            LOG.exception(err)
            self.echo(str(err))
            sys.exit(1)

        sys.exit(0)
