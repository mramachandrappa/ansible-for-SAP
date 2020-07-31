from pyrfc import Connection
from configparser import ConfigParser
import os


def main():
    config = ConfigParser()
    try:
        config.read(os.environ["HOME"] + '/.config/sap_config.ini')
        creds = config['SAP']

        conn = Connection(user=creds['user'], passwd=creds['passwd'], ashost=creds['ashost'],
                               sysnr=creds['sysnr'], sid=creds['sid'], client=creds['client'])

        if conn:
            return True
    except KeyError:
         config.read(os.path.expanduser('~') + '\.config\sap_config.ini')
         creds = config['SAP']

         conn = Connection(user=creds['user'], passwd=creds['passwd'], ashost= creds['ashost'],
                           sysnr=creds['sysnr'], sid=creds['sid'], client=creds['client'])

         if conn:
            return True
    except Exception:
        return False

    return False


if __name__ == '__main__':
    print(main())

