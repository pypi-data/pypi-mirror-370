FROM debian:buster

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV PKG_DEPS="\
    awscli \
    build-essential \
    chrpath \
    cpio \
    curl \
    debianutils \
    diffstat \
    file \
    gawk \
    gcc-multilib \
    git \
    git-lfs \
    gnupg \
    iproute2 \
    iputils-ping \
    jq \
    less \
    libc6-dev-i386 \
    libegl1-mesa \
    liblz4-tool \
    libsdl1.2-dev \
    libssl-dev \
    linux-libc-dev \
    locales \
    mesa-common-dev \
    openssh-client \
    pigz \
    pylint3 \
    python2 \
    python3 \
    python3-git \
    python3-jinja2 \
    python3-pexpect \
    python3-pip \
    python3-subunit \
    socat \
    sudo \
    texinfo \
    unzip \
    wget \
    xmlstarlet \
    xterm \
    xz-utils \
    zstd \
"

RUN set -e ;\
    echo 'locales locales/locales_to_be_generated multiselect C.UTF-8 UTF-8, en_US.UTF-8 UTF-8 ' | debconf-set-selections ;\
    echo 'locales locales/default_environment_locale select en_US.UTF-8' | debconf-set-selections ;\
    echo 'dash dash/sh boolean false' | debconf-set-selections ;\
    apt update -q=2 ;\
    apt full-upgrade -q=2 --yes ;\
    apt install -q=2 --yes --no-install-recommends ${PKG_DEPS} ;\
    # Set default shell to bash
    dpkg-reconfigure -p critical dash ;\
    # Set Python 3 as default
    update-alternatives --install /usr/bin/python python /usr/bin/python3 50 ;\
    # Setup tuxbake user
    useradd --create-home tuxbake --shell /bin/bash ;\
    # Cleanup
    apt clean ;\
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
