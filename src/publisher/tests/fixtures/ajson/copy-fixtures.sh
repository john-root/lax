#!/bin/bash
set -xuv
for fname in elife-16695- patched/elife-01968- patched/elife-20125- patched/elife-20105-v1 patched/elife-12215-v1 patched/elife-00353-v1 patched/elife-00385-v1 patched/elife-01328-v1 patched/elife-02619-v1 patched/elife-03401-v patched/elife-03665-v1 patched/elife-06250-v patched/elife-07301-v1 patched/elife-08025-v patched/elife-09571-v1
do
   cp "/home/luke/dev/python/bot-lax-adaptor/article-json/$fname"* ./
done

