FROM fedora:33

ENV LANG=en_US.UTF-8
# setting default shell to bash
ENV SHELL /bin/bash
ENV PKG_DEPS="\
    make \
    tar \
    perl \
    diffutils \
    cpp \
    ccache \
    perl-Data-Dumper \
    perl-Text-ParseWords \
    perl-Thread-Queue \
    perl-bignum \
    python3-pexpect \
    findutils \
    python \
    python3-GitPython \
    python3-jinja2 \
    SDL-devel \
    xterm \
    mesa-libGL-devel \
    perl-FindBin \
    perl-File-Compare \
    perl-File-Copy \
    perl-locale \
    automake \
    gcc \
    gcc-c++ \
    kernel-devel \
    chrpath \
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
    openssh-server \
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
    glibc-devel \
    glibc-devel.i686 \
    lz4 \
    zstd \
    python2 \
    bzip2 \
    hostname \
    patch \
    rpcgen \
    which \
    glibc-langpack-en \
"

RUN set -e ;\
    dnf update -y -q;\
    dnf distro-sync -y -q ;\
    dnf reinstall glibc-common --assumeyes ;\
    export LANG=en_US.UTF-8 ;\
    dnf install -y -q --nobest ${PKG_DEPS} ;\
    #Set Python 3 as default
    update-alternatives --install /usr/bin/python python /usr/bin/python3 50 ;\
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
