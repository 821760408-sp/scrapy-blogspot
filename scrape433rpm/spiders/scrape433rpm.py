import re
import scrapy


class DownloadLinksSpider(scrapy.Spider):
    name = "cover_and_file_links"
    start_urls = [
        #'http://433rpm.blogspot.com/2018/',
        'http://433rpm.blogspot.com/2017/',
    ]

    def parse(self, response):
        for url in response.css('div.post-body a::attr(href)').extract():
            if url[-3:] == 'jpg':  # it's the album cover
                yield {
                    'image_urls': [url],
                }
            elif 'zippyshare' in url:  # it's the link to zippyshare
                yield response.follow(url, callback=self.parse_zippyshare)
            else:
                pass

        next_page = response.css('a.blog-pager-older-link::attr(href)').extract_first()
        if next_page is not None:
            stop_at = re.compile('updated-max=([0-9]+)')
            matched = re.search(stop_at, next_page)
            if matched is not None and int(matched.group(1)) >= 2017:
                yield response.follow(next_page, callback=self.parse)

    def parse_zippyshare(self, response):
        script = response.css('div.right script::text').extract_first()
        pattern = r'href.*\"(.*)\"\+.*\+\"(.*)\".*'
        urls = re.findall(pattern, script)[0]
        pattern = r'var a = (.*);'
        a = re.search(pattern, script).group(1)
        rn = str(pow(int(a), 3) + 3)
        url = response.urljoin(urls[0] + rn + urls[1])
        yield {
            'file_urls': [url],
        }

