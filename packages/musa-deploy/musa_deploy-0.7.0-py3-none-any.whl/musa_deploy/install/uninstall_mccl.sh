#!/bin/bash

install_prefix=/usr/local/musa

uninstall_mccl_func () {
    if [ ! -d "${install_prefix}" ]; then
        echo -E "${install_prefix} does not exist"
        exit 1
    fi

    rm -rf ${install_prefix}/lib/libmccl*
    rm -rf ${install_prefix}/bin/mccl*
    rm -rf ${install_prefix}/include/mccl*
    rm -rf ${install_prefix}/include/mccl*
    rm -rf ${install_prefix}/cmake/FindMCCL.cmake
    echo -E "Please remove following line in ~/.bashrc if necessary"
    echo -E "export LD_LIBRARY_PATH=${install_prefix}/lib:\${LD_LIBRARY_PATH}"
}

uninstall_mccl_func
