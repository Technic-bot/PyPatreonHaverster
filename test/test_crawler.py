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

def test_process_post(api_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)
    
    post = api_data['data'][0]
    patreon_post = crawler.process_post(post)

    errors = []
    if patreon_post.filename != 'shedfurclone_color.png':
       errors.append[f'Wrong filename {patreon_post.filename}'] 

    assert not errors, "\n".join(errors)
    assert patreon_post.filename == 'shedfurclone_color.png'

def test_process_post_id_is_int(api_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)
    
    post = api_data['data'][0]
    patreon_post = crawler.process_post(post)

    assert patreon_post.post_id == 90866735 

def test_process_post_tags(api_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)
    
    post = api_data['data'][0]
    patreon_post = crawler.process_post(post)

    expected_tags = ['Color Art', 'Nora Card', 'Rose', 'Saria']
    assert patreon_post.tags == expected_tags

def test_is_post_valid(api_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)
    
    post = api_data['data'][0]
    assert crawler.is_valid_post(post['attributes'])

def test_is_post_invalid(api_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)
    
    post = api_data['data'][7]
    assert not crawler.is_valid_post(post['attributes'])

def test_limited_stop(api_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)
    posts = api_data['data']
    crawler.process_api_response(posts)
    crawler.limit = 5

    assert crawler.early_stop(2)

def test_is_no_processed(api_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)
    posts = api_data['data']
    crawler.process_api_response(posts)

    assert not crawler.is_processed(90431751)
