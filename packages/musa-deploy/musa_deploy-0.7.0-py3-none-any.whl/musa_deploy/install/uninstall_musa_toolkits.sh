#!/bin/bash

install_prefix=/usr/local

uninstall_musa_toolkits_func () {
    # 1. remove all /usr/local/musa-x.x.x dir
    for item in ${install_prefix}/*/; do
        if [[ $item =~ musa-[0-9]+\.[0-9]+\.[0-9]+/$ ]]; then
            \rm -rf ${item}
        fi
    done
    # 2. remove symlink: /usr/local/musa
    install_prefix_symlink=${install_prefix}/musa
    rm -rf ${install_prefix_symlink}
    echo -e "Please remove following line in ~/.bashrc if necessary"
    echo -e "export PATH=${install_prefix_symlink}/bin:\${PATH}"
    echo -e "export LD_LIBRARY_PATH=${install_prefix_symlink}/lib:\${LD_LIBRARY_PATH}"
}

uninstall_musa_toolkits_func
