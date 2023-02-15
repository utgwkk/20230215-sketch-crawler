import sys
from crawler import Crawler


def main():
    if len(sys.argv) == 1:
        print('usage: python3 main.py (url)', file=sys.stderr)
        return 1

    url = sys.argv[1]
    crawler = Crawler(url)
    crawler.crawl()

    return 0


if __name__ == "__main__":
    sys.exit(main())
