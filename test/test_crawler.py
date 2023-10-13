# import sys
# print(sys.path)
from patreonharvester.patreon_crawler import PatreonCrawler
from patreonharvester.caches import EmptyJsonCache

def test_tester():
    assert 1

def test_process_api(api_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)
    posts = api_data['data']
    crawler.process_api_response(posts)
    assert len(crawler.post_list) == 18
