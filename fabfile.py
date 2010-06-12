from fabric.api import *

SITE_NAME = 'git.example.com'

# core packages
PACKAGES = """
    git-core git-svn build-essential libpcre3 libpcre3-dev apg make zlib1g
    zlib1g-dev ssh ruby1.8 libbluecloth-ruby libopenssl-ruby1.8 ruby1.8-dev ri
    rdoc irb libonig-dev libyaml-dev geoip-bin libgeoip-dev libgeoip1
    imagemagick libmagickwand-dev memcached apache2 uuid uuid-dev openjdk-6-jre
"""

GEMS = """
    rails mongrel mime-types textpow chronic
    ruby-hmac daemons mime-types oniguruma textpow chronic BlueCloth
    ruby-yadis ruby-openid geoip rspec rspec-rails RedCloth echoe
    mysql rmagick 
"""

def aptitude(*packages):
    sudo('DEBIAN_FRONTEND=noninteractive aptitude -y install %s' % ' '.join(packages), shell=False)

def download_packages():
    sudo("aptitude install -d -y %s" % ' '.join(PACKAGES.split()))

def install_packages():
    aptitude(' '.join(PACKAGES.split()))
    sudo('ln -sfn /usr/bin/ruby1.8 /usr/bin/ruby')

def install_mysql():
    # http://www.muhuk.com/2010/05/how-to-install-mysql-with-fabric/
    mysql_password = prompt('Please enter MySQL root password:')
    sudo('echo "mysql-server-5.1 mysql-server/root_password password ' \
            '%s" | debconf-set-selections' % mysql_password)
    sudo('echo "mysql-server-5.1 mysql-server/root_password_again password ' \
            '%s" | debconf-set-selections' % mysql_password)
    aptitude('mysql-server-5.1 mysql-client-5.1 libmysqlclient15-dev')

def install_rubygems():
    run('mkdir -p src')
    run('cd src ; wget http://rubyforge.org/frs/download.php/60718/rubygems-1.3.5.tgz')
    run('cd src ; tar xvzf rubygems-1.3.5.tgz')
    run('cd src/rubygems-1.3.5 ; sudo ruby setup.rb')
    sudo('ln -sfn /usr/bin/gem1.8 /usr/bin/gem')

def gem(*packages):
    sudo("gem install --no-ri --no-rdoc %s" % (' '.join(packages)))

def install_gems():
    gem(GEMS)

def install_sphinx():
    run('mkdir -p src')
    run('cd src ; wget http://www.sphinxsearch.com/downloads/sphinx-0.9.8.tar.gz')
    run('cd src ; tar xvfz sphinx-0.9.8.tar.gz')
    run('cd src/sphinx-0.9.8 ; ./configure')
    run('cd src/sphinx-0.9.8 ; make')
    run('cd src/sphinx-0.9.8 ; sudo make install')
    gem('ultrasphinx')

def install_activemq():
    run('mkdir -p src')
    run('cd src ; wget http://www.powertech.no/apache/dist/activemq/apache-activemq/5.2.0/apache-activemq-5.2.0-bin.tar.gz')
    run('cd src ; sudo tar xzvf apache-activemq-5.2.0-bin.tar.gz -C /usr/local/')
    sudo('sh -c \'echo "export ACTIVEMQ_HOME=/usr/local/apache-activemq-5.2.0" \
                >> /etc/activemq.conf\'')
    sudo('sh -c \'echo "export JAVA_HOME=/usr/" >> /etc/activemq.conf\'')
    sudo('adduser --system --no-create-home activemq')
    sudo('chown -R activemq /usr/local/apache-activemq-5.2.0/data')

def configs():
    put('configs/activemq.xml', '~')
    put('configs/activemq', '~')
    sudo('mv activemq /etc/init.d/activemq')
    sudo('chmod +x /etc/init.d/activemq')
    sudo('mv activemq.xml /usr/local/apache-activemq-5.2.0/conf/activemq.xml')
    sudo('update-rc.d memcached defaults')

def install_gitorious():
    sudo('groupadd gitorious || true')
    sudo("usermod -a -G gitorious %s || true" % env.user)
    sudo("mkdir -p /var/www/%s" % SITE_NAME)
    sudo("chown %s:gitorious /var/www/%s" % (env.user, SITE_NAME))
    sudo("chmod -R g+sw /var/www/%s" % SITE_NAME)
    run("cd /var/www/%s ; mkdir -p log conf" % SITE_NAME)
    run("cd /var/www/%s ; git clone git://gitorious.org/gitorious/mainline.git gitorious" % SITE_NAME)
    run("cd /var/www/%s/gitorious ; rm -f public/.htaccess" % SITE_NAME)
    run("cd /var/www/%s/gitorious ; mkdir -p tmp/pids" % SITE_NAME)
    run("cd /var/www/%s/gitorious ; chmod ug+x script/*" % SITE_NAME)
    run("cd /var/www/%s/gitorious ; chmod -R g+w config/ log/ public/ tmp/" % SITE_NAME)
    sudo("ln -sfn /var/www/%s/gitorious/script/gitorious /usr/local/bin/gitorious" % SITE_NAME)
    sudo("ln -sfn /var/www/%s/gitorious/doc/templates/ubuntu/git-ultrasphinx /etc/init.d/git-ultrasphinx" % SITE_NAME)
    sudo("ln -sfn /var/www/%s/gitorious/doc/templates/ubuntu/git-daemon /etc/init.d/git-daemon" % SITE_NAME)
    sudo('chmod +x /etc/init.d/git-ultrasphinx')
    sudo('chmod +x /etc/init.d/git-daemon')
    sudo("sed -i s:PID_FILE=.*:PID_FILE=\"/var/www/%s/gitorious/db/sphinx/log/searchd.pid\":g /etc/init.d/git-ultrasphinx" % SITE_NAME)
    sudo("sed -i s:PID_FILE=.*:PID_FILE=\"/var/www/%s/gitorious/log/git-daemon.pid\":g /etc/init.d/git-daemon" % SITE_NAME)
    sudo("sed -i s:GIT_DAEMON=.*:GIT_DAEMON=\"/usr/bin/ruby /var/www/%s/gitorious/script/git-daemon -d:g\" /etc/init.d/git-daemon" % SITE_NAME)
    sudo('update-rc.d -f git-daemon start 99 2 3 4 5 .')
    sudo('update-rc.d -f git-ultrasphinx start 99 2 3 4 5 .')

def create_git_user():
    sudo('adduser --system git')
    sudo('usermod -a -G gitorious git')
    sudo('mkdir /var/git')
    sudo('mkdir /var/git/repositories')
    sudo('mkdir /var/git/tarballs')
    sudo('mkdir /var/git/tarball-work')
    sudo('chown -R git:gitorious /var/git')
    sudo('mkdir -p /home/git/.ssh', user='git')
    sudo('chmod 700 /home/git/.ssh', user='git')
    sudo('touch /home/git/.ssh/authorized_keys', user='git')

def deploy():
    download_packages()
    install_packages()
    install_mysql()
    install_rubygems()
    install_gems()
    install_sphinx()
    install_activemq()
    install_gitorious()
    create_git_user()
    configs()
