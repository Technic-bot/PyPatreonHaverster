import argparse
import sys
from patreon_crawler import PatreonCrawler

def proc_opts():
    parser = argparse.ArgumentParser(description="Patreon art scraper")
    parser.add_argument('url')
    parser.add_argument('outdir')
    parser.add_argument('--limit', default=0, type=int)
    parser.add_argument('--db-file', default='patreon.json')
    parser.add_argument('--cache', help='Cache file')
    parser.add_argument('--login', action='store_true', help='login to patreon for cookies')
    return parser.parse_args()

        

if __name__=="__main__":
    args = proc_opts()
        
    pc = PatreonCrawler(
            args.url, args.outdir,
            args.db_file, args.limit,
        )

    if args.login:
        pc.login()
        sys.exit(1)

    pc.crawl()
    pc.driver.quit()
