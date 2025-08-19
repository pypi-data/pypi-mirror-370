from libifstate.util import logger
from libifstate.link.base import Link
from libifstate.exception import LinkCannotAdd

class PhysicalLink(Link):
    def __init__(self, ifstate, netns, name, link, ethtool, vrrp, brport):
        super().__init__(ifstate, netns, name, link, ethtool, vrrp, brport)
        self.cap_create = False
        self.cap_ethtool = True
        self.ethtool = ethtool
 
    def create(self, do_apply, sysctl, excpts, oper="add"):
        logger.warning('unable to create physical link', extra={'iface': self.settings.get('ifname'), 'netns': self.netns})
