import configparser
import os
import sys
from UserDict import IterableUserDict

from dogapi import DogHttpApi


def report_errors(res):
    if 'errors' in res:
        for e in res['errors']:
            print('ERROR: ' + e, file=sys.stderr)
        sys.exit(1)
    return False

def report_warnings(res):
    if 'warnings' in res:
        for e in res['warnings']:
            print('WARNING: ' + e, file=sys.stderr)
        return True
    return False

class CommandLineClient(object):
    def __init__(self, config):
        self.config = config
        self._dog = None

    @property
    def dog(self):
        if not self._dog:
            self._dog = DogHttpApi(self.config['apikey'], self.config['appkey'], swallow=False, json_responses=True)
        return self._dog
        


class DogshellConfig(IterableUserDict):

    def load(self, config_file):
        config = configparser.ConfigParser()
        
        if os.access(config_file, os.F_OK):
            config.read(config_file)
            if not config.has_section('Connection'):
                report_errors({'errors': ['%s has no [Connection] section' % config_file]})
        else:
            try:
                response = input('%s does not exist. Would you like to create it? [Y/n] ' % config_file)
                if response.strip().lower() in ['', 'y', 'yes']:
                    # Read the api and app keys from stdin
                    apikey = input('What is your api key? (Get it here: https://app.datadoghq.com/account/settings) ')
                    appkey = input('What is your application key? (Generate one here: https://app.datadoghq.com/account/settings) ')
                
                    # Write the config file
                    config.add_section('Connection')
                    config.set('Connection', 'apikey', apikey)
                    config.set('Connection', 'appkey', appkey)
                
                    f = open(config_file, 'w')
                    config.write(f)
                    f.close()
                    print('Wrote %s' % config_file)
                        
                else:
                    # Abort
                    print('Exiting', file=sys.stderr)
                    sys.exit(1)
            except KeyboardInterrupt:
                # Abort
                print('\nExiting', file=sys.stderr)
                sys.exit(1)
            
        
        self['apikey'] = config.get('Connection', 'apikey')
        self['appkey'] = config.get('Connection', 'appkey')
            
