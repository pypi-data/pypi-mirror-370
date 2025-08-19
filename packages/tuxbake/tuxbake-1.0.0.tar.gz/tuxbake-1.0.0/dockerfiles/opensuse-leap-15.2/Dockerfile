FROM opensuse/leap:15.2

ENV LANG=en_US.UTF-8
ENV PKG_DEPS="\
    python \
    makeinfo \
    python3-pexpect \
    python3-Jinja2 \
    Mesa-libEGL1 \
    libSDL-devel \
    xterm \
    rpcgen \
    Mesa-dri-devel \
    gcc \
    gcc-c++ \
    make \
    chrpath \
    python-xml \
    python-curses \
    python3-curses \
    cpio \
    curl \
    diffstat \
    file \
    gawk \
    git \
    git-lfs \
    gnupg \
    iputils \
    jq \
    less \
    openssh \
    pigz \
    python3 \
    python3-pip \
    socat \
    sudo \
    texinfo \
    unzip \
    wget \
    xz \
    xmlstarlet \
    awscli \
    openssl-devel \
    lz4 \
    zstd \
    python2 \
    patch \
    bzip2 \
    gzip \
    hostname \
    tar \
    which \
"

RUN set -e ;\
    zypper -nq update ;\
    zypper -nq dist-upgrade ;\
    zypper -nq install --no-recommends ${PKG_DEPS} ;\
    pip3 install GitPython ;\
    # Set default shell to bash
    chsh -s /usr/bin/sh ;\
    # Set Python 3 as default
    update-alternatives --install /usr/bin/python python /usr/bin/python3 50 ;\
    # Setup tuxbake user
    useradd --create-home --user-group tuxbake --shell /bin/bash ;\
    # Cleanup
    zypper clean ;\
    rm -rf /var/lib/apt/lists/* /tmp/*

USER tuxbake

RUN set -e ;\
    # Set git default config
    git config --global user.email "ci@tuxsuite.com" ;\
    git config --global user.name "Tuxsuite Bot" ;\
    git config --global color.ui "auto" ;\
    echo "progress = dot" > ${HOME}/.wgetrc ;\
    echo "dot_bytes = 10m" >> ${HOME}/.wgetrc

CMD ["/bin/bash"]
