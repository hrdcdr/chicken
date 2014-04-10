#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import getpass
from optparse import OptionParser


class Environment(object):

    def __init__(self):
        self.sites_dir = '/home/' + getpass.getuser() + '/prj'
        self.vhosts_dir = '/etc/apache2/sites-available'
        self.hosts_file = '/etc/hosts'
        self.template = 'default'
        self.ip = '127.0.0.1'
        self.port = '80'

    def list(self):
        for filename in os.listdir(self.vhosts_dir):
            if os.path.isfile(os.path.join(self.vhosts_dir, filename)):
                print(filename)

    def init(self):
        pass


class VirtualHost(object):

    def __init__(self, domain, path, template, port):
        self.domain = domain
        self.path = path
        self.template = template
        self.port = port

    def add(self, vhosts_dir, hosts_file, ip):
        vhost = open(os.path.join(vhosts_dir, self.domain), 'w')
        vhost.write(self.get_content(self.template))
        vhost.close()
        hosts = open(hosts_file, 'a')
        hosts.write('\n' + ip + '\t' + self.domain + '\twww.' + self.domain)
        hosts.close()

    def drop(self, vhosts_dir, hosts_file):
        vhost_path = os.path.join(vhosts_dir, self.domain)
        if os.path.exists(vhost_path):
            os.remove(vhost_path)
        remove_string(hosts_file, 'www.' + self.domain)

    def get_content(self, template):
        content = ''
        if template == 'default':
            content = ('<VirtualHost *:' + self.port + '>'
                       '\n\tServerAdmin admin@localhost'
                       '\n\tServerName ' + self.domain +
                       '\n\tServerAlias www.' + self.domain +
                       '\n'
                       '\n\tDocumentRoot ' + self.path +
                       '\n\t<Directory ' + self.path + '>'
                       '\n\t\tOptions Indexes FollowSymLinks MultiViews'
                       '\n\t\tAllowOverride All'
                       '\n\t\tOrder allow,deny'
                       '\n\t\tallow from all'
                       '\n\t</Directory>'
                       '\n'
                       '\n\tLogLevel warn'
                       '\n\t#ErrorLog ${APACHE_LOG_DIR}/' + self.domain + '-error.log'
                       '\n\t#CustomLog ${APACHE_LOG_DIR}/' + self.domain + '-access.log combined'
                       '\n</VirtualHost>')
        if template == 'default24':
            content = ('<VirtualHost *:' + self.port + '>'
                       '\n\tServerAdmin admin@localhost'
                       '\n\tServerName ' + self.domain +
                       '\n\tServerAlias www.' + self.domain +
                       '\n'
                       '\n\tDocumentRoot ' + self.path +
                       '\n\t<Directory ' + self.path + '>'
                       '\n\t\tOptions Indexes FollowSymLinks MultiViews'
                       '\n\t\tAllowOverride All'
                       '\n\t\tRequire all granted'
                       '\n\t</Directory>'
                       '\n'
                       '\n\tLogLevel warn'
                       '\n\t#ErrorLog ${APACHE_LOG_DIR}/' + self.domain + '-error.log'
                       '\n\t#CustomLog ${APACHE_LOG_DIR}/' + self.domain + '-access.log combined'
                       '\n</VirtualHost>')
        return content


def main():
    if os.getuid() != 0:
        sys.exit('You must run this script as root!')
    env = Environment()
    parser = OptionParser(usage='%prog [options] [add|drop|list] domain', version='%prog 1.0')
    parser.add_option('-d', '--directory', metavar='/path/to/docroot', help='Path to docroot')
    parser.add_option('-t', '--template', default=env.template, metavar=env.template, help='Template')
    parser.add_option('-v', '--vhosts_dir', default=env.vhosts_dir, metavar=env.vhosts_dir, help='Virtual Hosts dir')
    parser.add_option('-p', '--port', default=env.port, metavar=env.port, help='Port')
    (options, args) = parser.parse_args()
    script_name = os.path.basename(__file__)
    if len(args) == 2 and args[0] in {'add': 1, 'drop': 2}:
        directory = options.directory if options.directory is not None else generate_path(env.sites_dir, args[1])
        host = VirtualHost(args[1], directory, options.template, options.port)
        if args[0] == 'add':
            host.add(env.vhosts_dir, env.hosts_file, env.ip)
        if args[0] == 'drop':
            host.drop(env.vhosts_dir, env.hosts_file)
    elif len(args) == 1 and args[0] == 'list':
        env.list()
    else:
        parser.error(script_name + ' -h')


def generate_path(sites_dir, domain):
    dirname = domain[:domain.rfind('.')] if '.' in domain else domain
    path = os.path.join(sites_dir, dirname)
    if not os.path.exists(path):
        sys.exit('Target directory ' + path + ' does not exist')
    else:
        return path


def remove_string(filepath, string):
    new_content = []
    with open(filepath) as file:
        content = file.read()
        for line in content.splitlines():
            if not string in line:
                new_content.append(line)
    with open(filepath, 'w') as file:
        file.write('\n'.join(new_content))


if __name__ == '__main__':
    main()