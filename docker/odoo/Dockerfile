FROM debian:bullseye-slim
MAINTAINER Odoo S.A. <info@odoo.com>

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        dirmngr \
        fonts-noto-cjk \
        gnupg \
        libssl-dev \
        node-less \
        npm \
        python3-num2words \
        python3-pdfminer \
        python3-pip \
        python3-phonenumbers \
        python3-pyldap \
        python3-qrcode \
        python3-renderpm \
        python3-setuptools \
        python3-slugify \
        python3-vobject \
        python3-watchdog \
        python3-xlrd \
        python3-xlwt \
        xz-utils \
        cmake \
        libgtk2.0-dev \
        pkg-config \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        python3-dev \
        libtbb2 libtbb-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libdc1394-22-dev \
        poppler-utils \
        python3-numpy  \
        python3-wheel \
        libldap2-dev \
        libsasl2-dev \
        qpdf \
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.buster_amd64.deb \
    && echo 'ea8277df4297afc507c61122f3c349af142f31e5 wkhtmltox.deb' | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# install latest postgresql-client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && GNUPGHOME="$(mktemp -d)" \
    && export GNUPGHOME \
    && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
    && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
    && gpgconf --kill all \
    && rm -rf "$GNUPGHOME" \
    && apt-get update  \
    && apt-get install --no-install-recommends -y postgresql-client-11 \
    && rm -f /etc/apt/sources.list.d/pgdg.list \
    && rm -rf /var/lib/apt/lists/*

# Install rtlcss (on Debian buster)
RUN npm install -g rtlcss

# Install Odoo
ENV ODOO_VERSION=15.0
ARG ODOO_RELEASE=20230210
ARG ODOO_SHA=c8f3d1b3af6847c9b4e9d4750e0fc34b303911c7
RUN curl -o odoo.deb -sSL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.${ODOO_RELEASE}_all.deb \
    && echo "${ODOO_SHA} odoo.deb" | sha1sum -c - \
    && apt-get update \
    && apt-get -y install --no-install-recommends ./odoo.deb \
    && rm -rf /var/lib/apt/lists/* odoo.deb

# Install Ghostscript
# Add the bookworm repository to apt sources.list And this must be the last install
RUN echo 'deb http://deb.debian.org/debian bookworm main' > /etc/apt/sources.list.d/bookworm.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends ghostscript \
    && rm -f /etc/apt/sources.list.d/pgdg.list \
    && rm -rf /var/lib/apt/lists/*

# Copy entrypoint script and Odoo configuration file
COPY --chown=odoo ./docker/odoo/entrypoint.sh /
COPY --chown=odoo ./docker/odoo/wait-for-psql.py /usr/local/bin/wait-for-psql.py

# Copy requirements
COPY --chown=odoo exp-cognitive/requirements.txt requirements.cognitive.txt
COPY --chown=odoo exp-accounting/requirements.txt requirements.accounting.txt
COPY --chown=odoo exp-base/requirements.txt requirements.base.txt
COPY --chown=odoo odoo/requirements.txt requirements.odoo.txt
COPY --chown=odoo requirements.experio.txt requirements.experio.txt

# Install requirements
RUN python3 -m pip install --upgrade pip setuptools wheel \
    && pip3 install --no-cache-dir -r requirements.base.txt \
    && pip3 install --no-cache-dir -r requirements.cognitive.txt \
    && pip3 install --no-cache-dir -r requirements.accounting.txt \
    && pip3 install --no-cache-dir -r requirements.experio.txt

# Replace Odoo files
RUN rm -Rf /usr/lib/python3/dist-packages/odoo
COPY --chown=odoo odoo/ /usr/lib/python3/dist-packages/odoo

# Copy custom addons
COPY --chown=odoo exp-cognitive/ /mnt/exp-cognitive
COPY --chown=odoo exp-accounting/ /mnt/exp-accounting
COPY --chown=odoo exp-base/ /mnt/exp-base
COPY --chown=odoo scripts/ /mnt/scripts
COPY --chown=odoo ./odoo.conf /etc/odoo/

# Define Volutmes
VOLUME ["/var/lib/odoo", "/mnt/scripts", "/mnt/exp-cognitive", "/mnt/exp-accounting", "/mnt/exp-base"]

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default config file
ENV ODOO_RC=/etc/odoo/odoo.conf

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
