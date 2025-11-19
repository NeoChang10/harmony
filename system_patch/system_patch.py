#! /usr/bin/python
import os
import os.path
import json
import shutil
PROJECT_ROOT="/ohos"
PATCH_SRC_PATH="/ohos/device/board/rpi/system_patch"

def whitelist():
    whitelist_path='/ohos/build/compile_standard_whitelist.json'

    with open(whitelist_path, 'r') as file:
        data = json.load(file)

    addlist=["//device/soc/broadcom/bcm2711/hardware/display:display_gfx",
        "//device/soc/broadcom/bcm2711/hardware/display:libdisplay_buffer_vdi_impl",
        "//device/soc/broadcom/bcm2711/hardware/display:libdisplay_buffer_vendor",
        "//device/soc/broadcom/bcm2711/hardware/display:display_composer_vendor",
        "//device/soc/broadcom/bcm2711/hardware/display:libdisplay_composer_vdi_impl",
        "//device/soc/broadcom/common:ptgen",
        "//vendor/iscas/common/sample/nfc:nfcserver",
        "//device/board/rpi/common/camera/pipeline_core:camera_pipeline_core",
        "//device/board/rpi/common/camera:camera_host_vdi_impl_1.0"]

    for add in addlist:
        data["gn_part_or_subsystem_error"].append(add)
        data["deps_added_external_part_module"].append(add)
        data["external_deps_bundle_not_add"].append(add)
        data["third_deps_bundle_not_add"].append(add)

    with open(whitelist_path, 'w') as file:
        json.dump(data, file, indent=4)


whitelist()


# shutil.copy(PROJECT_ROOT+"/foundation/ability/ability_runtime/frameworks/native/appkit/app/main_thread.cpp",PATCH_SRC_PATH+"/foundation/main_thread.cpp")
# shutil.copy(PROJECT_ROOT+"/base/startup/appspawn/modules/common/appspawn_adapter.cpp",PATCH_SRC_PATH+"/base/appspawn_adapter.cpp")

shutil.copy(PATCH_SRC_PATH+"/foundation/main_thread.cpp",PROJECT_ROOT+"/foundation/ability/ability_runtime/frameworks/native/appkit/app/main_thread.cpp")
shutil.copy(PATCH_SRC_PATH+"/base/appspawn_adapter.cpp",PROJECT_ROOT+"/base/startup/appspawn/modules/common/appspawn_adapter.cpp")

print("finish")