import feedparser

# url='http://feeds.feedburner.com/euronews/en/news?format=xml'	

class Rss_Handler(object):

	def get_feed(self,url):
		d=feedparser.parse(url)	
		rss_contents=[]
		for entry in d['entries']:
			summary=entry['summary']
			title=entry['title']
			rss_contents.append({'summary':summary,'title':title})
		return rss_contents
	
	def get_feeds(self,urls):
		content=[]
		for rss_url in urls:
			url_feed=self.get_feed(rss_url.url)
			content+=url_feed
		return content


