# Copyright (c) 2022 Diemit <598757652@qq.com>
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

KERNEL_CONFIG_PATH = $(PROJECT_ROOT)/device/board/iscas/rpi4/kernel/configs
export INSTALL_MOD_PATH := $(PROJECT_ROOT)/device/board/iscas/rpi4/modules
PREBUILTS_GCC_DIR := $(PROJECT_ROOT)/prebuilts/gcc
PREBUILTS_CLANG_DIR := $(PROJECT_ROOT)/prebuilts/clang
CLANG_HOST_TOOLCHAIN := $(PROJECT_ROOT)/prebuilts/clang/ohos/linux-x86_64/llvm/bin
KERNEL_HOSTCC := $(CLANG_HOST_TOOLCHAIN)/clang
CLANG_CC := $(CLANG_HOST_TOOLCHAIN)/clang

KERNEL_PREBUILT_MAKE := make

ifeq ($(KERNEL_ARCH), arm)
    KERNEL_TARGET_TOOLCHAIN := $(PREBUILTS_GCC_DIR)/linux-x86/arm/gcc-linaro-7.5.0-arm-linux-gnueabi/bin/arm-linux-gnueabi-
else ifeq ($(KERNEL_ARCH), arm64)
    KERNEL_TARGET_TOOLCHAIN := $(PREBUILTS_GCC_DIR)/linux-x86/aarch64/gcc-linaro-7.5.0-2019.12-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu-

endif

KERNEL_CROSS_COMPILE :=
KERNEL_CROSS_COMPILE += CC="$(CLANG_CC)"
KERNEL_CROSS_COMPILE += CROSS_COMPILE="$(KERNEL_TARGET_TOOLCHAIN)"

KERNEL_MAKE := \
    $(KERNEL_PREBUILT_MAKE)

$(KERNEL_IMAGE_FILE):
	echo "build kernel..."
	cp -rf $(KERNEL_CONFIG_PATH)/$(DEFCONFIG_FILE) $(KERNEL_SRC_TMP_PATH)/arch/$(KERNEL_ARCH)/configs
	$(KERNEL_MAKE) -C $(KERNEL_SRC_TMP_PATH) ARCH=$(KERNEL_ARCH) $(KERNEL_CROSS_COMPILE) $(DEFCONFIG_FILE)
# $(KERNEL_MAKE) -C $(KERNEL_SRC_TMP_PATH) ARCH=$(KERNEL_ARCH) $(KERNEL_CROSS_COMPILE) modules_prepare
	$(KERNEL_MAKE) -C $(KERNEL_SRC_TMP_PATH) ARCH=$(KERNEL_ARCH) $(KERNEL_CROSS_COMPILE) -j32 $(KERNEL_IMAGE)
#	$(KERNEL_MAKE) -C $(KERNEL_SRC_TMP_PATH) ARCH=$(KERNEL_ARCH) $(KERNEL_CROSS_COMPILE) modules modules_install

.PHONY: build-kernel
build-kernel: $(KERNEL_IMAGE_FILE)
