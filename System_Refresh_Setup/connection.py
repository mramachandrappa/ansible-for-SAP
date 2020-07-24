from pyrfc import Connection
from configparser import ConfigParser
import os

os.chdir('../')


def main():
    config = ConfigParser()
    try:
        config.read(os.getcwd() + '/sap_config.ini')
        creds = config['SAP']

        Connection(user=creds['user'], passwd=creds['passwd'], ashost=creds['ashost'],
                   sysnr=creds['sysnr'], sid=creds['sid'], client=creds['client'])

        return True
    except KeyError:
        config.read(os.getcwd() + '/sap_config.ini')
        creds = config['SAP']

        Connection(user=creds['user'], passwd=creds['passwd'], ashost= creds['ashost'],
                   sysnr=creds['sysnr'], sid=creds['sid'], client=creds['client'])

        return True
    except Exception as e:
        return False


if __name__ == '__main__':
    print(main())

