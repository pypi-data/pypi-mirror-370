all: typecheck test style flake8 pylint

export PROJECT := tuxbake
TUXPKG_MIN_COVERAGE := 76
TUXPKG_BLACK_OPTIONS := --exclude=tmp/
TUXPKG_MYPY_OPTIONS := --ignore-missing-imports # FIXME while tuxmake doesn't provide typing stubs
TUXPKG_FLAKE8_OPTIONS := --exclude=tmp/

include $(shell tuxpkg get-makefile)

pylint:
	pylint --disable=all --enable=elif,exceptions,stdlib,imports,variables,string,string_constant,logging,newstyle,classes --disable=C0411,C0412,E0401,C0413,E0611,E0202,R0201,R0401,W --enable=R1707,R1714,R1715,R1716,W0235,W0404,W0611,W1401,W1402,W1403,W1505 tuxbake/

rpm-sanity-check-prepare::
	printf '[tuxmake]\nname=tuxmake\ntype=rpm-md\nbaseurl=https://tuxmake.org/packages/\ngpgcheck=1\ngpgkey=https://tuxmake.org/packages/repodata/repomd.xml.key\nenabled=1\n' > /etc/yum.repos.d/tuxmake.repo

deb-sanity-check-prepare::
	apt-get update
	apt-get install -qy ca-certificates
	/usr/lib/apt/apt-helper download-file https://tuxmake.org/packages/signing-key.gpg /etc/apt/trusted.gpg.d/tuxmake.gpg
	echo 'deb https://tuxmake.org/packages/ ./' > /etc/apt/sources.list.d/tuxmake.list
	echo 'deb http://deb.debian.org/debian bullseye contrib' > /etc/apt/sources.list.d/contrib.list
	apt-get update
