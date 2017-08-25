import logging, json, requests, bs4
# we use bs4 to parse the HTML page

import re   # we use regexp to find IPv4 addr

from minemeld.ft.basepoller import BasePollerFT

LOG = logging.getLogger(__name__)

class IPv4(BasePollerFT):
	def configure(self):
		super(IPv4, self).configure()

		self.polling_timeout = self.config.get('polling_timeout', 20)
		self.verify_cert = self.config.get('verify_cert', True)
		self.url = self.config.get('LifeSizeCloud_URL','https://community.lifesize.com/docs/DOC-2471-lifesize-server-and-tunnel-gateway-ip-address-list')

	def _process_item(self, item):
		# called on each item returned by _build_iterator
		# it should return a list of (indicator, value) pairs
		ip = item
		m = re.match("^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", ip)
		if m is None:
			LOG.error('%s - no IPv4 found', self.name)
			return []
		
		indicator = '{}'.format(ip)
		value = {
			'type': 'IPv4',
			'confidence': 100
		}
		return [[indicator, value]]
		#~ pass

	def _build_iterator(self, now):
		# called at every polling interval
		# here you should retrieve and return the list of items

		# builds the request and retrieves the page
		rkwargs = dict(
			stream=False,
			verify=self.verify_cert,
			timeout=self.polling_timeout
		)

		r = requests.get(
			self.url,
			**rkwargs
		)

		try:
			r.raise_for_status()
		except:
			LOG.debug('%s - exception in request: %s %s',
					  self.name, r.status_code, r.content)
			raise

		# parse the page
		html_soup = bs4.BeautifulSoup(r.content, "lxml")
		search_jive_table = html_soup.find_all(
			"table",
			attrs={"jive-data-header":True}
		) # search the table from LifeSize
		
		result = []

		for x in search_jive_table:
			search_td = x.find_all(
				string=re.compile("(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)")
			) # search Cells with data LIKE IPv4 addr
			for y in search_td:
				result.append(y)
		return result
		#~ pass

