import argparse
from patreon_crawler import PatreonCrawler

def proc_opts():
    parser = argparse.ArgumentParser(description="Patreon art scraper")
    parser.add_argument('url')
    parser.add_argument('outdir')
    parser.add_argument('--limit', default=0, type=int)
    parser.add_argument('--json_name', default='patreon.json')
    parser.add_argument('--cache', help='Cache file')
    return parser.parse_args()

        

if __name__=="__main__":
    args = proc_opts()
        
    pc = PatreonCrawler(
            args.url, args.outdir,
            args.json_name, args.limit,
            args.cache    
        )
    pc.crawl()
    pc.driver.quit()
