FROM ubuntu:14.04
RUN apt-get update && apt-get install -yq curl python \
    && cd /tmp \
    && curl -q -o get-pip.py https://bootstrap.pypa.io/get-pip.py \
    && python get-pip.py \
    && curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash - \
    && apt-get install -yq nodejs build-essential supervisor \
    && npm install -g log.io --user "root" \
    && apt-get clean && rm -rf /var/lib/apt/lists/* && rm -rf /tmp/*
RUN pip install --upgrade pip \
    && pip install pygtail watchdog
RUN mkdir -p  /logs \
    && mkdir -p /var/log/supervisor
COPY files/web_server.conf /root/.log.io/web_server.conf
COPY files/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY files/watcher.py /watcher.py

VOLUME ["/logs"]
EXPOSE 28777 28778
CMD ["supervisord"]
