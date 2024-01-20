import pytest
from patreonharvester.patreon_crawler import PatreonCrawler
from patreonharvester.caches import EmptyJsonCache
from patreonharvester.patreon_classes import PatreonPost

def test_tester():
    assert 1

def test_process_api(api_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)
    posts = api_data['data']
    crawler.process_api_response(posts)
    assert len(crawler.post_list) == 17

def test_process_post(api_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)
    
    post = api_data['data'][3]
    patreon_post = crawler.process_post(post)

    errors = []
    if patreon_post.title != 'Roulade Cake':
       errors.append[f'Wrong filename {patreon_post.title}'] 

    assert not errors, "\n".join(errors)
    assert patreon_post.title == 'Roulade Cake'

def test_process_post_id_is_int(api_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)
    
    post = api_data['data'][0]
    patreon_post = crawler.process_post(post)

    assert patreon_post.post_id == 96775166 

def test_process_post_tags(api_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)
    
    post = api_data['data'][1]
    patreon_post = crawler.process_post(post)

    expected_tags = ['Sunday Sketches', 'Zen']
    assert patreon_post.tags == expected_tags

def test_is_post_valid(api_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)
    
    post = api_data['data'][1]
    assert crawler.is_valid_post(post['attributes'])

def test_is_post_invalid(api_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)
    
    post = api_data['data'][0]
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

def test_single_media_process(api_multipost_data, media_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)

    post = api_multipost_data['data'][0]
    post = crawler.process_post(post)

    crawler.process_media_response(post, media_data)

    assert len(crawler.post_list) == 5

@pytest.mark.skip(reason="Disabling this feature at the moment")
def test_media_process(api_multipost_data, media_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)

    posts = api_multipost_data['data']
    posts, multiple_images = crawler.process_api_response(posts)

    assert len(multiple_images) == 8

def test_post_has_multiple_images(api_multipost_data, media_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)

    post = api_multipost_data['data'][0]

    assert crawler.has_multiple_images(post) 

def test_post_has_single_image(api_multipost_data, media_data):
    cache = EmptyJsonCache('patreon.json')
    crawler = PatreonCrawler('dummy_url','dummy_out' , cache)

    post = api_multipost_data['data'][2]

    assert not crawler.has_multiple_images(post) 
