#!/usr/bin/env python3

# Copyright (c) 2024 Institute of Software, Chinese Academy of Sciences.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import os.path
import subprocess
import multiprocessing
import shutil


# root="/home/dy/ohos6.0"
# arch="arm64"
root=sys.argv[1]
arch=sys.argv[2]

defconfig="bcm2711_oh_defconfig"
kernel_build_root = root+"/out/kernel/"

if arch=="arm":
    crosscompile=root+"/prebuilts/gcc/linux-x86/arm/gcc-linaro-7.5.0-arm-linux-gnueabi/bin/arm-linux-gnueabi-"
else:
    crosscompile=root+"/prebuilts/gcc/linux-x86/aarch64/gcc-linaro-7.5.0-2019.12-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu-"

cc=root+"/prebuilts/clang/ohos/linux-x86_64/llvm/bin/clang"

src=root+"/kernel/linux/linux-5.10/"
dst=root+"/out/kernel/linux-5.10-small/"

patch1=root+"/kernel/linux/patches/linux-5.10"
patch2=root+"/device/board/rpi/common/kernel/rpi.patch"

dtbcopylist=["bcm2711-rpi-4-b.dtb","bcm2710-rpi-3-b.dtb"]
dtbocopylist=["overlays/vc4-fkms-v3d.dtbo","overlays/rpi-ft5406.dtbo","overlays/rpi-backlight.dtbo","overlays/dwc2.dtbo"]

def copy_kernel():

    if os.path.exists(dst):
        print("exist")
    else:
        shutil.copytree(src,dst)
        patch_kernel()

def patch_kernel():
    shutil.copy(root+"/device/board/rpi/common/kernel/xhci.h",dst+"drivers/usb/host/xhci.h")
    subprocess.run(F'bash {root}/drivers/hdf_core/adapter/khdf/linux/patch_hdf.sh {root} {dst} {patch1} common', shell=True, check=True)
    subprocess.run(F'patch -d {dst} -p1 < {patch2}', shell=True, check=True)

def make_kernel():
    nproc = multiprocessing.cpu_count()
    shutil.copy(root+"/device/board/rpi/common/kernel/configs/bcm2711_oh_defconfig32",dst+"/arch/arm/configs/bcm2711_oh_defconfig")
    shutil.copy(root+"/device/board/rpi/common/kernel/configs/bcm2711_oh_defconfig64",dst+"/arch/arm64/configs/bcm2711_oh_defconfig")
    shutil.copy(root+"/device/board/rpi/common/kernel/configs/rpioh.config",dst+"/arch/arm64/configs/rpioh.config")
    subprocess.run(F'make -C {dst} ARCH=arm CC={cc} CROSS_COMPILE={root}/prebuilts/gcc/linux-x86/arm/gcc-linaro-7.5.0-arm-linux-gnueabi/bin/arm-linux-gnueabi- {defconfig}', shell=True, check=True)
    dtbs="bcm2710-rpi-3-b.dtb bcm2711-rpi-4-b.dtb overlays/vc4-fkms-v3d.dtbo overlays/rpi-ft5406.dtbo overlays/rpi-backlight.dtbo overlays/dwc2.dtbo"
    subprocess.run(F'make -C {dst} ARCH=arm CC={cc} CROSS_COMPILE={crosscompile} -j{nproc+1} {dtbs}', shell=True, check=True)

    subprocess.run(F'make -C {dst} ARCH={arch} CC={cc} CROSS_COMPILE={crosscompile} {defconfig} rpioh.config', shell=True, check=True)
    os.environ["PRODUCT_PATH"] = "vendor/iscas/rpi_small"  
    if arch=="arm":
        subprocess.run(F'make -C {dst} ARCH={arch} CC={cc} CROSS_COMPILE={crosscompile} -j{nproc+1} zImage', shell=True, check=True)
    else:
        subprocess.run(F'make -C {dst} ARCH={arch} CC={cc} CROSS_COMPILE={crosscompile} -j{nproc+1} Image.gz', shell=True, check=True)

def remove_file(name):
    try:
        os.unlink(name)
    except FileNotFoundError:
        return

def remove_directory(name):
    try:
        shutil.rmtree(name)
    except FileNotFoundError:
        pass

def make_boot_img():

    output_dir=root+"/out/rpi_small/rpi_small"
    input_dir=root+"/device/board/rpi/rpi_small/rpiboot"
    oldpwd = os.getcwd()
    os.chdir(output_dir)

    imagefile = 'boot.img'
    imagefile_tmp = imagefile + '.tmp'
    boot_dir = 'rpiboot'
    overlays_dir = 'rpiboot/overlays'
    remove_directory(boot_dir)
    remove_file(imagefile)
    shutil.copytree(input_dir, boot_dir)
    os.mkdir(overlays_dir)
    if arch=="arm":
        shutil.copy(
            os.path.join(dst, 'arch/arm/boot/zImage'),
            boot_dir
        )
    else:
        shutil.copy(
            os.path.join(dst, 'arch/arm64/boot/Image.gz'),
            boot_dir
        )
    for dtb in dtbcopylist:
        shutil.copy(
        os.path.join(dst, 'arch/arm/boot/dts/'+dtb),
        boot_dir
    )
    for dtbo in dtbocopylist:
        shutil.copy(
        os.path.join(dst, 'arch/arm/boot/dts/'+dtbo),
        overlays_dir
    )

    with open(imagefile_tmp, 'wb') as writer:
        writer.truncate(32*1024*1024)
    subprocess.run(F'mkfs.vfat -F 32 {imagefile_tmp} -n BOOT', shell=True, check=True)
    subprocess.run(F'mcopy -i {imagefile_tmp} {boot_dir}/* ::/', shell=True, check=True)
    os.rename(imagefile_tmp, imagefile)

    os.chdir(oldpwd)


command_table = {
    'copy': copy_kernel,
    'make': make_kernel,
    'makeboot': make_boot_img,
}

command_table["copy"]()
command_table["make"]()
command_table["makeboot"]()