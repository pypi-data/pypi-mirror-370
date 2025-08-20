# Original: https://github.com/musicalchemist/simple_vcs
import os
import hashlib
import json
import difflib


class VersionControl:
    def __init__(self):
        self.vc_dir = ".mc_vers_ctrl"
        self.hash = None
        os.makedirs(self.vc_dir, exist_ok=True)

    def _update_hash(self):
        snapshot_hash = hashlib.sha256()
        snapshot_hash.update(json.dumps(self.compiled, sort_keys=True).encode("utf-8"))
        self.hash = snapshot_hash.hexdigest()

    def commit(self, base="."):
        self._update_hash()
        self.hash_history.append(self.hash)
        self.save_json(filename=f"{base}/{self.vc_dir}/{self.hash}")

    def checkout(self, hash):
        checkout_path = f"{self.vc_dir}/{hash}"
        # Check if the snapshot exists; if not, print a message and exit the function
        if not os.path.exists(checkout_path):
            print("Check point does not exist.")
            return
        # Load the snapshot data from the file
        self.load_json(filename=checkout_path)
        self.hash = hash

        print(f"Successfully loaded check point {self.hash}")

    def calculate_diff(self, hash0, hash1):
        checkout_path0 = f"{self.vc_dir}/{hash0}"
        checkout_path1 = f"{self.vc_dir}/{hash1}"
        if not os.path.exists(checkout_path0) or not os.path.exists(checkout_path1):
            print("Check point does not exist.")
            return
        with open(checkout_path0, "r") as f:
            json0 = f.readlines()
        with open(checkout_path1, "r") as f:
            json1 = f.readlines()

        diff = difflib.Differ().compare(json0, json1)

        line_num = 0
        differences = []
        for line in diff:
            if line.startswith(" "):
                line_num += 1
                continue
            if line.startswith("-"):
                line_num += 1
                differences.append(f"Line {line_num}: {line.strip()}")
            elif line.startswith("+"):
                differences.append(f"Line {line_num}: {line.strip()}")
            elif line.startswith("?"):
                differences.append(f"Line {line_num}: {line.strip()}")
        differences = "\n".join(differences)
        return differences
