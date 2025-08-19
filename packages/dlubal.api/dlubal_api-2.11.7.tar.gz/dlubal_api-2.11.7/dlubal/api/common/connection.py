''' Definition file '''
import os
import ssl
import grpc

from pathlib import Path
from configparser import ConfigParser
from pkg_resources import get_distribution, DistributionNotFound

# Enable prompt option for testing purposes
prompt = False

options = [
        ('grpc.max_send_message_length', -1),
        ('grpc.max_receive_message_length', -1),
    ]
compression = grpc.Compression.Gzip # https://grpc.io/docs/guides/compression/

class _config():
    def __init__(self):
        '''
        Read config file. It is doesn't exist, create one.
        '''
        self.config = ConfigParser()
        self.config_loc = Path(Path(__file__).parents[1], 'config.ini')
        # Parse existing file
        if os.path.isfile(self.config_loc):
            self.config.read(self.config_loc)

    def _save_to_file(self):
        '''
        Save current config file
        '''
        with open(self.config_loc, 'w', encoding="utf-8") as config_file:
            self.config.write(config_file)

    def get_name_of_default(self):
        '''
        Return first name of the API key, which was set as default
        '''
        all_items = self.config.items('api_keys')
        all_keys = self.config.options('api_keys')
        if 'default' in all_keys:
            default_value = self.config.get('api_keys', 'default')
            for i in all_items:
                if i[0] != 'default' and i[1] == default_value:
                    return i[0]
        return None

    def _set(self, section, key, value):
        '''
        Set value and save config into file
        '''
        self.config.set(section, key, value)
        self._save_to_file()

    def get_value(self, key):
        '''
        Get API key from config
        '''
        value = None
        if self.config.has_section('api_keys'):
            value = self.config.get('api_keys', key, fallback=None)
        if value and value.startswith(('AK', 'ak')):
            # Set default
            self._set('api_keys', 'default', value)
        return value

    def set_value(self, key, value):
        '''
        Set API key into config
        '''
        if self.config.has_section('api_keys'):
            self._set('api_keys', key, value)
        else:
            self.config.add_section('api_keys')
            self._set('api_keys', key, value)
        # Set default
        self._set('api_keys', 'default', value)

    def delete_value(self, section, key):
        '''
        Delete API key
        '''
        self.config.remove_option(section, key)


class _ApiKey():
    '''
    API key class to make it easy to manage API keys.
    '''
    def __init__(self, key=None , value=None):

        self.key = key
        self.value = value
        self.config = _config()

        if self.key and self.value:
            # Check if API key is saved. If not, save it to config file.
            if self.config.get_value(self.key) is None:
                self.config.set_value(self.key, self.value)
        elif self.key:
            # Check if API key is saved, get it and put into self.value
            self.value = self.config.get_value(self.key)
        elif self.value:
            # Providing value without key suggests user doesn't want to store it
            # Don't even store any default value
            pass
        else:
            # Key and value are None
            # Check if there is any default key set in config
            self.value = self.config.get_value('default')
            if self.value:
                default_key = self.config.get_name_of_default()
                if default_key:
                    # Print only if key is found
                    print(f'API key: {self.config.get_name_of_default()}')

    def get(self, key=None):
        '''
        Get API key
        '''
        if key:
            self.value = self.config.get_value(key)
        else:
            self.value = self.config.get_value('default')

        if self.value is None:
            raise ValueError("Invalid API key idenficator or missing default value.")
        return self.value

    def set(self, key, value):
        '''
        Set APi key
        '''
        self.config.set_value(key, value)


class _ClientCallDetails(grpc.ClientCallDetails):
    '''
    Client call details class to pass authorization API key
    '''
    def __init__(self, call_details, metadata):
        self.method = call_details.method
        self.timeout = call_details.timeout
        self.credentials = call_details.credentials
        self.metadata = metadata

class AuthInterceptor(grpc.UnaryUnaryClientInterceptor):
    '''
    Authorization Unary Interceptor class
    '''
    def __init__(self, value):
        self.api_key = value

    # def intercept_call(self, continuation, client_call_details, request_or_iterator):
    #     client_version = get_distribution('dlubal.api').version
    #     call_details = _ClientCallDetails(client_call_details, [("authorization", f"Bearer {self.api_key}"),("api-client-info", f"Python | {client_version}"),])
    #     return continuation(call_details, request_or_iterator)

    def intercept_call(self, continuation, client_call_details, request_or_iterator):
        try:
            client_version = get_distribution('dlubal.api').version
        except DistributionNotFound:
            # Package not installed, fallback to default version string
            client_version = "dev"

        call_details = _ClientCallDetails(
            client_call_details,
            [
                ("authorization", f"Bearer {self.api_key}"),
                ("api-client-info", f"Python | {client_version}"),
            ]
        )
        return continuation(call_details, request_or_iterator)

    def intercept_unary_unary(self, continuation, client_call_details, request):
        return self.intercept_call(continuation, client_call_details, request)

def check_ssl(_ssl, _ssl_file):
    '''
    Check SSL certificate
    Params:
        _ssl (bool): False if NOT using SSL auth. True if using SSL certificate.
        _ssl_file (str):Path to .crt/.pem certificate.
    '''
    if _ssl is False:
        pass
    elif _ssl is True:
        if isinstance(_ssl_file, str) and os.path.isfile(_ssl_file) and _ssl_file.endswith(('.crt', '.pem')):
            # Use provided file
            pass
        elif _ssl_file == '':
            # Use Windows Certification Store
            pass
        else:
            # Provided path is not correct
            exit()

    return True

def _get_ssl_credentials(_ssl_file) -> grpc.ChannelCredentials:
    '''
    Get SSL channel credentials by reading cert. file

    Params:
    path (str): Path to the SSL (.crt) certificate filepath
    '''
    if _ssl_file == '':
        certs = ssl.create_default_context().get_ca_certs(True)
        cert_string = ''
        for cert in certs:
            cert_string += ssl.DER_cert_to_PEM_cert(cert)
        return grpc.ssl_channel_credentials(root_certificates=cert_string.encode('utf-8'))
    else:
        cert_file = open(_ssl_file, 'rb')
        return grpc.ssl_channel_credentials(cert_file.read())

def init_channel(API_key, url, port, _ssl, _ssl_file):
    '''
    Initialize the gRPC channel with the provided API key.

    Params:
        API_key (str): Api key
        url (str): URL number defaults to localhost (127.0.0.1)
        port (int): Port number defaults to 9000
        _ssl (bool): True if using SSL
        _ssl_file (str): Path to SSL cert file
    '''
    channel = None
    try:
        if _ssl:
            # Create secure channel
            channel_credentials = _get_ssl_credentials(_ssl_file)
            channel = grpc.secure_channel(f"{url}:{port}", channel_credentials, options, compression)
        else:
            # Create insecure channel
            channel = grpc.insecure_channel(f"{url}:{port}", options, compression)

        #  Create gRPC interceptor
        interceptor = AuthInterceptor(API_key)
        channel = grpc.intercept_channel(channel, interceptor)

    # All exceptions are handeled at the RFEM.__exit__()
    except:
        pass

    return channel
