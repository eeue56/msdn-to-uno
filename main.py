import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import signals
import json
import sys



class MSDNSpider(scrapy.Spider):
    name = 'msdnspider'
    start_urls = [
        'https://msdn.microsoft.com/en-us/library/system.drawing.solidbrush(v=vs.110).aspx',
        'https://msdn.microsoft.com/en-us/library/system.drawing.drawing2d.lineargradientbrush(v=vs.110).aspx',
        'https://msdn.microsoft.com/en-us/library/system.drawing.texturebrush(v=vs.110).aspx'
    ]

    def parse(self, response):
        for title in response.css('#content .topic .title'):
            header_text = title.css("::text").extract_first().split()
            class_name = header_text[0]
            type = header_text[1]

        
        constructors = []
        is_first = True

        for constructor in response.css('#idConstructors tbody tr'):
            if is_first:
                is_first = False
                continue

            constructor_text = constructor.css("tr td a ::text").extract_first()
            constructor_args = constructor.css("tr td a span ::text").extract_first().replace('\u2002', ' ')
            constructors.append(constructor_text + constructor_args)


        properties = []
        is_first = True

        for constructor in response.css('#idProperties tbody tr'):
            if is_first:
                is_first = False
                continue

            prop_text = constructor.css("tr td a span ::text").extract_first()
            properties.append(prop_text)

        namespace = response.css('#mainBody .section a ::text').extract_first()

        yield { 
            'class_name': class_name,
            'namespace': namespace,
            'type': type,
            'constructors': constructors,
            'properties': properties
        }


TYPE_TO_TEXT = { 
    "Structure": "struct", 
    "Class": "class"
}

TYPE_TO_UNO = {
    "Single": "float"
}

def replace_types(thing):
    for original_type, new_type in TYPE_TO_UNO.items():
        thing = thing.replace(original_type, new_type)

    return thing


def main(urls):
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


    process.crawl(MSDNSpider, start_urls=urls)
    process.start()

    with open('out.json') as f:
        items = json.load(f)

    for item in items:
        constructors = '\n\t'.join(
            'public extern {constructor};'.format(
                constructor=replace_types(constructor)
            ) 
            for constructor in item['constructors']
        )

        properties = '\n\t'.join(
            'public extern {prop} {{ get; set; }}'.format(
                prop=prop
            ) 
            for prop in item['properties']
        )

        print("""
[DotNetType("{namespace}.{class_name}")]
extern(DOTNET) public {type} {class_name}
{{
\t// constructors
\t{constructors}
\n
\t// properties
\t{properties}
}}
        """.format(
                namespace=item['namespace'], 
                class_name=item['class_name'],
                type=TYPE_TO_TEXT[item['type']],
                constructors=constructors,
                properties=properties
            )
        )

if __name__ == '__main__':
    main(sys.argv[1:])