#  Host

- IOMMU

  -     SUCCESS: iommu on or (iommu off and memory < 256G)
  -     WARNING：iommu off and memory > 256GB
  -     ATTENTION: Can't get iommu info in /etc/default/grub

- pcie
  - SUCCESS: get gpu arch version
  - WARNING: get pcie info, but unknown arch version
  - FAIL: get no info by 'lspci'

- kernel
  - SUCCESS: get kernel version by 'uname -r'
  - WARNING: Can't get kernel version

- cpu

  - SUCCESS: cpu's arch is x86_64
  - Warning：cpu_arch is "arm" or "aarch64" , or Unable to get cpu info by 'lscpu'

- docker
  - SUCCESS: docker's status is ruuning
  - FAIL: docker is installed and it's active is not ruuning
  - WEAK_INSTALL: not install

- dkms and lightdm

  - SUCCESS: get package version(installed)
  - not installed

- system:

  - SUCCESS: Ubuntu system

  - ATTENTION: not Ubuntu system

  - WARNING: get not info by 'lsb_release -a'




#  Driver

- mthreads-gmi:
  - SUCCESS: mthreads-gmi outputs normally
  - STRONG_UNINSTALL：not install driver
  - FAIL: get no info by 'mthreads-gmi -q'
- MTBios:
  - SUCCESS: gmi success and get mtbios version, version is consistent
  - ATTENTION: gmi success and get mtbios version, version is not consistent
  - ATTENTION: gmi success and get no mtbios version
- gpu(gmi output nomally) :
  - WARNING: memory size is not consistent with the standard or memory size is different between gpus
  - Success: GPU memory is consistent with the standard
- clinfo:
  - WEAK_UNINSTALL: not install clinfo
  - SUCCESS: get driver version
  - WARNING: just got info 'Number of platforms'

#  ContainerToolkit

- docker_runtime
  - SUCCESS: docker_runtime check is ok(Regardless of whether mtml, sgpu-dkms is installed or not)
  - FAIL: docker_runtime check failed
- mtml, sgpu-dkms, containertoolkit(if docker_runtime validation failed)
  - SUCCESS : installed
  - FAIL: not install
