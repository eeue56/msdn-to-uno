import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import signals
import json



class MSDNSpider(scrapy.Spider):
    name = 'msdnspider'
    start_urls = ['https://msdn.microsoft.com/en-us/library/system.drawing.drawing2d.graphicspath(v=vs.110).aspx']

    def parse(self, response):
        for title in response.css('#content .topic .title'):
            class_name = title.css("::text").extract_first().split()[0]

        namespace = response.css('#mainBody .section a ::text').extract_first()

        yield { 
            'class_name': class_name,
            'namespace': namespace
        }


def main():
    try:
        with open('out.json') as f:
            with open('old.json', 'w') as old_f:
                old_f.write(f.read())

        with open('out.json', 'w') as f:
            pass
    except:
        pass

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'out.json',
        'LOG_ENABLED': 'False'
    })


    process.crawl(MSDNSpider)
    process.start()

    with open('out.json') as f:
        items = json.load(f)

    for item in items:
        print("""
[DotNetType("{namespace}.{class_name}")]
extern(DOTNET) public class {class_name}
{{
}}
        """.format(namespace=item['namespace'], class_name=item['class_name']))

if __name__ == '__main__':
    main()