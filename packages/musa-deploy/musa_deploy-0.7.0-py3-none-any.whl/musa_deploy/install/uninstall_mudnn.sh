#!/bin/bash

install_prefix=/usr/local/musa
library_prefix=lib

uninstall_mudnn_func () {
    if [ ! -d "${install_prefix}" ]; then
        echo -E "${install_prefix} does not exist"
        exit 1
    fi

    \rm -rf ${install_prefix}/${library_prefix}/cmake/mudnn
    \rm -rf ${install_prefix}/${library_prefix}/libmudnn*
    \rm -rf ${install_prefix}/bin/mudnn_version
    \rm -rf ${install_prefix}/docs/mudnn
    \rm -rf ${install_prefix}/include/mudnn*.sh
    \rm -rf ${install_prefix}/install_mudnn.sh
    echo -E "Please remove following line in ~/.bashrc if necessary"
    echo -E "export LD_LIBRARY_PATH=${install_prefix}/${library_prefix}:\${LD_LIBRARY_PATH}"
}

uninstall_mudnn_func
