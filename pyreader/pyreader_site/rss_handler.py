import feedparser


def get_feed(url):
	feed=[]
	for i in range(20):
		feed.append({'title':'title'+str(i),
					'link':'link'+str(i),
					'description':'description'+str(i)})
	return feed

