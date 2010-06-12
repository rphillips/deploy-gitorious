from fabric.api import *

# core packages
PACKAGES = """
    git-core git-svn
    build-essential libpcre3 libpcre3-dev 
    apg make
    zlib1g zlib1g-dev ssh
    ruby1.8 libbluecloth-ruby libopenssl-ruby1.8 ruby1.8-dev ri rdoc irb
    libonig-dev libyaml-dev geoip-bin libgeoip-dev libgeoip1
    imagemagick libmagickwand-dev
    mysql-client-5.1 mysql-server-5.1 libmysqlclient15-dev
    memcached
    apache2
"""

# email package
PACKAGES += "postfix"

def install_packages():
    run("sudo aptitude install -y %s" % ' '.join(PACKAGES.split()))

def deploy():
    install_packages()
