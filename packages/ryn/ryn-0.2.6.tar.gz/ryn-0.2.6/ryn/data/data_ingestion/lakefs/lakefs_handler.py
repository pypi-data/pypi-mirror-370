import requests
from requests.auth import HTTPBasicAuth
import subprocess

class lakefs_handler:
    def __init__(self,name,access_key,secret_key,lakefs_url="http://localhost:8001"):
        
        self.name=name
        self.access_key=access_key
        self.secret_key=secret_key
        self.lakefs_url=lakefs_url

        if self.repo_exist_check()==False:
            self.create_repo()
    
    

    def create_repo(self):
        repo_config = {
            "name": self.name,
            "storage_namespace": f"s3://mlops/k8s-test/{self.name}",
            "default_branch": "main"
        }

        auth = HTTPBasicAuth(self.access_key, self.secret_key)

        # Step 1: Create repo
        resp = requests.post(
            f"{self.lakefs_url}/api/v1/repositories",
            json=repo_config,
            auth=auth
        )

        if resp.status_code == 201:
            print("✅ Repository created")

            # Step 2: Upload README.md to main branch
            branch = "main"
            object_path = "README.md"
            content = "# " + self.name + "\n\nThis is a new lakeFS repository."
            url = f"{self.lakefs_url}/api/v1/repositories/{self.name}/branches/main/objects"
            params = {"path": "README.md"}

            # Fake file upload using BytesIO
            files = {
                        "content": (object_path, open(object_path, "rb"), "text/markdown")
                    }
            response = requests.post(
                url,
                params=params,
                files=files,
                auth=HTTPBasicAuth(self.access_key, self.secret_key)
            )
            # upload_resp = requests.post(
            #     f"{self.lakefs_url}/api/v1/repositories/{self.name}/branches/main/objects",
            #     auth=auth,
            #     data={"path": "README.md"},
            #     files={"content": ("README.md", "# This is a README\n", "text/markdown")}
            # )
            response.raise_for_status()

            # if upload_resp.status_code != 200:
            #     raise Exception(f"❌ Failed to upload README.md: {upload_resp.status_code} - {upload_resp.text}")

            # # Step 3: Commit the change
            # commit_resp = requests.post(
            #     f"{self.lakefs_url}/api/v1/repositories/{self.name}/branches/{branch}/commits",
            #     json={"message": "Initial commit with README.md"},
            #     auth=auth
            # )

            # if commit_resp.status_code != 201:
            #     raise Exception(f"❌ Failed to commit: {commit_resp.status_code} - {commit_resp.text}")

            print("📄 README.md added")
            return True

        elif resp.status_code == 409:
            print("⚠️ Repository already exists")
            return False
        else:
            raise ValueError("❌ Error creating repository:", resp.status_code, resp.text)

    
    
    def repo_exist_check(self):
        resp = requests.get(
        f"{self.lakefs_url}/api/v1/repositories/{self.name}",
        auth=HTTPBasicAuth(self.access_key, self.secret_key)
    )


        if resp.status_code == 200:
            return True
        elif resp.status_code == 404:
            return False
        else:
            raise ValueError("⚠️ Error:", resp.status_code, resp.text)

    def mount_repo(self,mount_point):

        # Inputs

        # create_dir_strict(mount_point)
        # Command to run
        cmd = [
            "bash",
            "/mnt/s3/mount_s3.sh",
            self.access_key,
            self.secret_key,
            self.name,
            mount_point,
            self.lakefs_url
        ]

        # Run and capture output
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Script output:\n", result.stdout)
        # result = subprocess.run([f"fusermount -u {self.mount_point}"], check=True, capture_output=True, text=True)
        # print("✅ Script output:\n", result.stdout)
        # try:
            
        # except subprocess.CalledProcessError as e:
        #     print("❌ Script failed:\n", e.stderr)
        

import os

def create_dir_strict(path):
    if os.path.exists(path):
        raise FileExistsError(f"❌ Directory already exists: {path}")
    os.makedirs(path)
    print(f"✅ Directory created: {path}")



