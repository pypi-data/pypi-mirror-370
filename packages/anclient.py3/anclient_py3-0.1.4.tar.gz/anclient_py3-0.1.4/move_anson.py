from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import shutil
import os

class CustomBuildHook(BuildHookInterface):

    def initialize(self, version, build_data):
        # Copy io/ to anclient/data/ during the build
        src = os.path.join(self.root, "src", "io")
        self.dst = os.path.join(self.root, "src", "anclient", "data", "io")
        os.makedirs(self.dst, exist_ok=True)
        # print("============= source exists: ", os.path.exists(src), src)
        if os.path.exists(src):
            print(src, " ===  ===>>> ", self.dst)
            shutil.copytree(src, self.dst, dirs_exist_ok=True)
        else:
            print("[ERROR / EMPTY] === ===>>> ", self.dst)

        # Ensure anclient/data/ is included in the wheel
        build_data["artifacts"].append("anclient/data/")

    def finalize(self, version, build_data, artifact_path):
        # Clean up any temporary files if needed
        shutil.rmtree(self.dst)