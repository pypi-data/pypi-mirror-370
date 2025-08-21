"""DNS Authenticator for Micetro."""
import logging
import requests
import zope.interface
from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)

@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Micetro

    This Authenticator uses the Micetro API to fulfill a dns-01 challenge.
    """

    description = 'Obtain certificates using a DNS TXT record (if you are using BlueCat Micetro for DNS).'
    ttl = 120

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add, **kwargs):
        super(Authenticator, cls).add_parser_arguments(add)
        add('credentials', help='Micetro credentials INI file.')

    def more_info(self):
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'the Micetro API.'

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'Micetro credentials INI file',
            {
                'username': 'Username for Micetro account',
                'password': 'Password for Micetro account',
                'url': 'Micetro API URL (e.g., https://api.micetro.com)'
            }
        )

    def _perform(self, domain, validation_name, validation):
        self._get_micetro_client().add_txt_record(domain, validation_name, validation, self.ttl)

    def _cleanup(self, domain, validation_name, validation):
        self._get_micetro_client().del_txt_record(domain, validation_name, validation)

    def _get_micetro_client(self):
        return _MicetroClient(self.credentials.conf('username'),
                              self.credentials.conf('password'),
                              self.credentials.conf('url'))


class _MicetroClient(object):
    """
    Encapsulates all communication with the Micetro API.
    """

    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.base_url = url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        self._authenticate()

    def _authenticate(self):
        """
        Authenticate with the Micetro API using username and password to get a Bearer token.
        
        :raises certbot.errors.PluginError: if authentication fails
        """
        try:
            logger.debug('Authenticating with Micetro API at %s/sessions', self.base_url)
            
            response = self.session.post(f'{self.base_url}/sessions', json={
                'loginName': self.username,
                'password': self.password
            })
            response.raise_for_status()
            
            session_data = response.json()
            token = session_data.get('session')
            
            if not token:
                raise errors.PluginError('Authentication failed: No token returned from Micetro API')
            
            # Update session headers with the Bearer token
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
            
            logger.debug('Successfully authenticated with Micetro API')
            
        except requests.exceptions.RequestException as e:
            logger.error('Authentication request failed: %s', e)
            raise errors.PluginError('Authentication failed: Unable to connect to Micetro API: {0}'.format(e))
        except Exception as e:
            logger.error('Authentication failed: %s', e)
            raise errors.PluginError('Authentication failed: {0}'.format(e))

    def add_txt_record(self, domain, record_name, record_content, record_ttl):
        """
        Add a TXT record using the supplied information.

        :param str domain: The domain to use to look up the Micetro zone (view: external).
        :param str record_name: The record name (typically beginning with '_acme-challenge.').
        :param str record_content: The record content (typically the challenge validation).
        :param int record_ttl: The record TTL (number of seconds that the record may be cached).
        :raises certbot.errors.PluginError: if an error occurs when communicating with the Micetro API
        """

        zone_id = self._find_zone_id(domain)

        try:
            logger.debug('Attempting to add record to zone %s: %s %s', zone_id, record_name, record_content)
            
            response = self.session.post(f'{self.base_url}/api/dnsRecords', json={
                'dnsZoneRef': zone_id,
                'name': record_name,
                'type': 'TXT',
                'data': record_content,
                'ttl': record_ttl
            })
            response.raise_for_status()

        except Exception as e:
            logger.error('Encountered exception adding TXT record: %d %s', e, e)
            raise errors.PluginError('Error communicating with the Micetro API: {0}'.format(e))

        record_id = self._find_txt_record_id(zone_id, record_name, record_content)
        logger.debug('Successfully added TXT record with record_id: %s', record_id)

    def del_txt_record(self, domain, record_name, record_content):
        """
        Delete a TXT record using the supplied information.

        Note that both the record's name and content are used to ensure that similar records
        created concurrently (e.g., due to concurrent invocations of this plugin) are not deleted.

        Failures are logged, but not raised.

        :param str domain: The domain to use to look up the Micetro zone.
        :param str record_name: The record name (typically beginning with '_acme-challenge.').
        :param str record_content: The record content (typically the challenge validation).
        """

        try:
            zone_id = self._find_zone_id(domain)
        except errors.PluginError as e:
            logger.debug('Encountered error finding zone_id during deletion: %s', e)
            return

        if zone_id:
            record_id = self._find_txt_record_id(zone_id, record_name, record_content)
            if record_id:
                try:
                    logger.debug('Attempting to remove txt record from zone %s: %s: %s',
                                 zone_id, record_name, record_content)
                    
                    response = self.session.delete(f'{self.base_url}/api/dnsRecords/{record_id}')
                    response.raise_for_status()

                except Exception as e:
                    logger.warning('Encountered Exception deleting TXT record: %s', e)
            else:
                logger.debug('TXT record not found; no cleanup needed.')
        else:
            logger.debug('Zone not found; no cleanup needed.')

    def _find_zone_id(self, domain):
        """
        Find the zone_id for a given domain.

        :param str domain: The domain for which to find the zone_id.
        :returns: The zone_id, if found.
        :rtype: str
        :raises certbot.errors.PluginError: if no zone_id is found.
        """

        zone_name_guesses = dns_common.base_domain_name_guesses(domain)

        for zone_name in zone_name_guesses:
            try:
                logger.debug('Attempting to find zone_id for %s using name %s', domain, zone_name)
                
                response = self.session.get(f'{self.base_url}/api/dnsZones', params={
                    'domainName': zone_name
                })
                response.raise_for_status()
                
                all_zones = response.json().get('result', [])
                
                # Prefer external zones over internal ones
                external_zones = [zone for zone in all_zones if 'external' in zone.get('view', '').lower()]
                zones = external_zones if external_zones else all_zones
                if zones:
                    zone_id = zones[0]['id']
                    logger.debug('Found zone_id of %s for %s using name %s', zone_id, domain, zone_name)
                    return zone_id
            except Exception as e:
                logger.debug('Encountered exception finding zone_id: %s', e)

        logger.debug('Unable to find zone_id for %s using zone names: %s', domain, zone_name_guesses)
        raise errors.PluginError('Unable to determine zone_id for {0} using zone names: {1}. '
                                 'Please confirm that the domain name has been entered correctly '
                                 'and is already associated with the supplied Micetro account.'
                                 .format(domain, zone_name_guesses))

    def _find_txt_record_id(self, zone_id, record_name, record_content):
        """
        Find the record_id for a TXT record with the given name and content.

        :param str zone_id: The zone_id which contains the record.
        :param str record_name: The record name (typically beginning with '_acme-challenge.').
        :param str record_content: The record content (typically the challenge validation).
        :returns: The record_id, if found.
        :rtype: str
        """

        try:
            logger.debug('Attempting to find record_id for record %s: %s in zone %s',
                         record_name, record_content, zone_id)
            
            response = self.session.get(f'{self.base_url}/api/dnsRecords', params={
                'dnsZoneRef': zone_id,
                'name': record_name,
                'type': 'TXT'
            })
            response.raise_for_status()
            
            all_records = response.json().get('result', [])
            records = [record for record in all_records 
                      if record.get('data') == record_content and record.get('name') == record_name]
        except Exception as e:
            logger.debug('Encountered Exception getting TXT record_id: %s', e)
            records = []

        if records:
            # Cleanup is returning the system to the state we found it. If, for some reason,
            # there are multiple matching records, we only delete one because we only added one.
            return records[0]['id']
        logger.debug('Unable to find TXT record.')
        return None