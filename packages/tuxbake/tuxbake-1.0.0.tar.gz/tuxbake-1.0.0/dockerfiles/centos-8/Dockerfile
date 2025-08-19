FROM centos:centos8

ENV LANG=en_US.UTF-8
ENV PKG_DEPS="\
    tar \
    gzip \
    diffutils \
    cpp \
    texinfo \
    ccache \
    perl-Data-Dumper \
    perl-Text-ParseWords \
    python3-GitPython \
    python3-jinja2 \
    python3-pexpect \
    SDL-devel \
    xterm \
    rpcgen \
    mesa-libGL-devel \
    gcc \
    gcc-c++ \
    make \
    chrpath \
    cpio \
    curl \
    diffstat \
    file \
    gawk \
    git \
    git-lfs \
    gnupg \
    iputils\
    jq -y \
    less \
    openssh \
    pigz \
    python3 \
    python3-pip \
    socat \
    sudo \
    unzip \
    wget \
    xz \
    openssl-devel \
    glibc-devel \
    lz4 \
    lz4-devel \
    zstd \
    python2 \
    bzip2 \
    patch \
    which \
    perl \
    perl-Thread-Queue \
"

RUN set -e ;\
    # metadata for app stream
    cd /etc/yum.repos.d/ ;\
    sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* ;\
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-* ;\
    dnf install -y dnf-plugins-core ;\
    dnf install -y epel-release ;\
    dnf config-manager --set-enabled powertools ;\
    dnf makecache ;\
    dnf update -y -q ;\
    dnf distro-sync -y -q ;\
    dnf install -y -q ${PKG_DEPS} ;\
    pip3 install awscli --upgrade --user ;\
    # Set Python 3 as default
    alternatives --set python /usr/bin/python3;\
    # Setup tuxbake user
    useradd --create-home tuxbake --shell /bin/bash ;\
    # Cleanup
    #dnf clean ;\
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
