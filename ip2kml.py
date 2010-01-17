#!/usr/bin/env python
#
# IP2KML - Creates KML files from IP/URL lists using GeoIP.
#
# Copyright (C) 2010 10n1z3d <10n1z3d[at]w[dot]cn>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# To use this script you will need python-geoip and GeoLiteCity.dat
# -->
# sudo apt-get install python-geoip
# http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz

__version__ = '0.1'

import os
import sys
import GeoIP
import socket
from urllib2 import urlopen
from optparse import OptionParser

OUTPUT_FILE = 'data.kml'
GEOIP_FILE = 'GeoLiteCity.dat'

def header():
    print '\t _____ _____ ___ _____ _____ __    '
    print '\t|     |  _  |_  |  |  |     |  |   '
    print '\t|-   -|   __|  _|    -| | | |  |__ '
    print '\t|_____|__|  |___|__|__|_|_|_|_____|'
    print '\t        10n1z3d[at]w[dot]cn        '
    print '\t           Version: %s           \n' % __version__

def usage():
    print 'Usage: python ./kmlgen.py <ip_file> [options]'
    print 'Options:'
    print '      -c, --check_response            Check http response'
    print '      -o, --output_file=<file_path>   Specify output file path,'
    print '                                      the default is %s' % OUTPUT_FILE
    print '      -g, --geoip_file=<file_path>    Specify GeoIP file path,'
    print '                                      the default is %s' % GEOIP_FILE
    print '      -v, --verbose                   Verbose mode\n'

def get_ip_address(url):
    '''Gets IP addres of url.'''
    try:
        return socket.gethostbyname(url)
    except:
        return None

def get_geoip_record(ip_address):
    '''Gets geoip record of ip address.'''
    geoip_handle = GeoIP.open(GEOIP_FILE, GeoIP.GEOIP_STANDARD)

    return geoip_handle.record_by_addr(ip_address)

def get_http_response_headers(host):
    '''Gets the http response headers.'''
    try:
        return str(urlopen('http://%s/' % host).info())
    except:
        return None

def get_host_info(host, url=False, check_http_resp=False):
    '''Gets host IP address, geoip information and http_response headers'''
    (ip_address, longitude, latitude, http_headers) = None, None, None, None

    ip_address = host if not url else get_ip_address(host)
    geoip_record = get_geoip_record(ip_address)

    if check_http_resp:
        http_headers = get_http_response_headers(ip_address)

    if geoip_record:
        longitude = geoip_record['longitude']
        latitude = geoip_record['latitude']

    return (ip_address, longitude, latitude, http_headers)

def write_placemark(output_file_handle, ip_address, description, longitude,
                    latitude):
    '''Creates and writes placemark to the kml file handle.'''
    placemark = ('\t<Placemark>\n'
                 '\t\t<name>%s</name>\n'
                 '\t\t<description>\n%s\t\t</description>\n'
                 '\t\t<Point>\n'
                 '\t\t\t<coordinates>%s, %s</coordinates>\n'
                 '\t\t</Point>\n'
                 '\t</Placemark>\n') % (ip_address, description, longitude,
                                        latitude)

    output_file_handle.write(placemark)

def parse_options():
    '''Parses the command line options.'''
    try:
        ip_file = sys.argv[1]
        parser = OptionParser(add_help_option=False)
        parser.add_option('-h', '--help', action='store_true',
                          dest='help', default=False)
        parser.add_option('-c', '--check_response', action='store_true',
                          dest='check_resp', default=False)
        parser.add_option('-v', '--verbose', action='store_true',
                          dest='verbose', default=False)
        parser.add_option('-o', '--output_file', dest="output_file",
                          default=None)
        parser.add_option('-g', '--geoip_file', dest="geoip_file",
                          default=None)

        (options, args) = parser.parse_args()

        return (ip_file, options.check_resp, options.verbose,
                options.output_file, options.geoip_file, options.help)
    except:
        header()
        usage()
        exit(2)

def main():
    '''Main function'''
    global GEOIP_FILE, OUTPUT_FILE
    (ip_file, check_resp, verbose, kml_file, geoip_file, help) = parse_options()

    header()
    if help: usage(); exit(0)
    if kml_file: OUTPUT_FILE = kml_file
    if geoip_file: GEOIP_FILE = geoip_file

    if not os.path.exists(GEOIP_FILE):
        print '[-] Missing GeoIP file!'
        print ('[-] Download it from: http://geolite.maxmind.com/download'
               '/geoip/database/GeoLiteCity.dat.gz\n')
        exit(0)

    if os.path.exists(ip_file):
        with open(OUTPUT_FILE, 'w') as output_file:
            print '[+] GeoIP file: %s' % GEOIP_FILE
            print '[+] Input file: %s' % ip_file
            print '[+] Output file: %s' % kml_file
            print '[+] Check HTTP response: %s\n' % check_resp
            
            output_file.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                              '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
                              '<Document>\n')

            with open(ip_file, 'r') as input_file:
                for line in input_file:
                    host = line.split('\n')[0]

                    if verbose:
                        print '[+] Getting information for %s' % host

                    (ip_address, longitude, latitude, http_headers) = \
                    get_host_info(host, line.startswith('www.'), check_resp)

                    if verbose:
                        print '[+] Writing placemark for %s' % host

                    write_placemark(output_file, ip_address, http_headers,
                                    longitude, latitude)

            output_file.write('</Document>\n')
            output_file.write('</kml>')

        print '\n[+] Done.\n'
        exit(0)
    else:
        print '[-] "%s" does not exist!\n' % ip_file
        exit(2)

if __name__ == "__main__":
    main()