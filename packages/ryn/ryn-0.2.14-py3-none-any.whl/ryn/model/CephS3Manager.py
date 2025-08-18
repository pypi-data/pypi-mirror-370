import json
import os
import random
import shutil
import string
import subprocess
import sys
import logging
import boto3
from botocore.exceptions import ClientError, EndpointConnectionError
from tqdm import tqdm
import mimetypes

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# CephS3Manager handles interaction with Ceph-compatible S3 storage
class CephS3Manager:
    def __init__(self, CEPH_ENDPOINT_URL, CEPH_ADMIN_ACCESS_KEY, CEPH_ADMIN_SECRET_KEY, CEPH_USER_BUCKET):
        if not all([CEPH_ENDPOINT_URL, CEPH_ADMIN_ACCESS_KEY, CEPH_ADMIN_SECRET_KEY, CEPH_USER_BUCKET]):
            raise ValueError("Missing required Ceph configuration parameters")
        
        self.bucket_name = CEPH_USER_BUCKET
        self.s3 = boto3.client(
            "s3",
            endpoint_url=CEPH_ENDPOINT_URL,
            aws_access_key_id=CEPH_ADMIN_ACCESS_KEY,
            aws_secret_access_key=CEPH_ADMIN_SECRET_KEY,
        )

        # Perform connection, authentication, and bucket checks
        if not self.check_connection():
            raise ValueError("Ceph connection not established.")
        if not self.check_auth():
            raise ValueError("Ceph Authentication not correct.")
        self.ensure_bucket_exists()

    def generate_random_string(self, length=12):
        """
        Generate a random string of letters and digits.
        """
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))

    def generate_key(self, length=12, characters=None):
        """
        Generate a random key for access or secret keys.
        """
        if characters is None:
            characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))

    def generate_access_key(self):
        """
        Generate a 20-character access key using uppercase letters and digits.
        """
        characters = string.ascii_uppercase + string.digits
        return "".join(random.choice(characters) for _ in range(20))

    def generate_secret_key(self):
        """
        Generate a 40-character secret key using letters and digits.
        """
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(40))

    def create_ceph_user(self, username):
        """
        Create a Ceph user using radosgw-admin.
        """
        try:
            access_key = self.generate_access_key()
            secret_key = self.generate_secret_key()
            cmd = [
                "radosgw-admin",
                "user",
                "create",
                "--uid",
                username,
                "--display-name",
                username,
                "--access-key",
                access_key,
                "--secret-key",
                secret_key,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = json.loads(result.stdout)
            print(f"[OK] Created Ceph user: {username}")
            return access_key, secret_key
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Failed to create Ceph user: {e.stderr}")
            raise ValueError(f"Failed to create Ceph user: {str(e)}")
        except Exception as e:
            print(f"[FAIL] Unexpected error creating Ceph user: {e}")
            raise ValueError(f"Unexpected error creating Ceph user: {str(e)}")

    def create_user(self, username):
        """
        Create a Ceph user using radosgw-admin in a WSL environment.
        """
        try:
            access_key = self.generate_access_key()
            secret_key = self.generate_secret_key()
            cmd = [
                "radosgw-admin",
                "user",
                "create",
                "--uid",
                username,
                "--display-name",
                username,
                "--access-key",
                access_key,
                "--secret-key",
                secret_key,
            ]
            result = self.run_in_wsl(cmd)
            output = json.loads(result.stdout)
            print(f"[OK] Created Ceph user in WSL: {username}")
            return access_key, secret_key
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Failed to create Ceph user in WSL: {e.stderr}")
            raise ValueError(f"Failed to create Ceph user in WSL: {str(e)}")
        except Exception as e:
            print(f"[FAIL] Unexpected error creating Ceph user in WSL: {e}")
            raise ValueError(f"Unexpected error creating Ceph user in WSL: {str(e)}")

    def set_user_quota(self, username, quota_gb):
        """
        Set storage quota for a Ceph user using radosgw-admin.
        """
        try:
            max_size_bytes = int(quota_gb * 1024 * 1024 * 1024)  # Convert GB to bytes
            cmd_set = [
                "radosgw-admin",
                "quota",
                "set",
                "--uid",
                username,
                "--max-size",
                str(max_size_bytes),
                "--quota-scope",
                "user",
            ]
            cmd_enable = ["radosgw-admin", "quota", "enable", "--uid", username, "--quota-scope", "user"]
            subprocess.run(cmd_set, capture_output=True, text=True, check=True)
            subprocess.run(cmd_enable, capture_output=True, text=True, check=True)
            print(f"[OK] Set quota for user {username}: {quota_gb} GB")
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Failed to set quota for user {username}: {e.stderr}")
            raise ValueError(f"Failed to set quota for user {username}: {str(e)}")
        except Exception as e:
            print(f"[FAIL] Unexpected error setting quota for user {username}: {e}")
            raise ValueError(f"Unexpected error setting quota for user {username}: {str(e)}")

    def enforce_storage_limit(self, bucket_name, storage_limit):
        """
        Simulate enforcing a storage limit on a bucket by checking its size.
        """
        try:
            size_mb = self.get_uri_size(f"s3://{bucket_name}/")
            size_gb = size_mb / 1024  # Convert MB to GB
            if size_gb > storage_limit:
                print(f"[WARN] Bucket {bucket_name} size ({size_gb:.2f} GB) exceeds limit ({storage_limit} GB)")
                return False
            print(f"[OK] Bucket {bucket_name} size ({size_gb:.2f} GB) within limit ({storage_limit} GB)")
            return True
        except ValueError as e:
            print(f"[FAIL] Bucket {bucket_name} does not exist: {e}")
            raise ValueError(f"Bucket {bucket_name} does not exist: {str(e)}")
        except Exception as e:
            print(f"[FAIL] Unexpected error enforcing storage limit for {bucket_name}: {e}")
            raise ValueError(f"Unexpected error enforcing storage limit for {bucket_name}: {str(e)}")

    def run_in_wsl(self, command_list):
        """
        Run a command inside WSL (Windows Subsystem for Linux).
        """
        try:
            cmd = ["wsl"] + command_list
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"[OK] Executed in WSL: {' '.join(cmd)}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Failed to execute in WSL: {e.stderr}")
            raise ValueError(f"Failed to execute in WSL: {str(e)}")
        except Exception as e:
            print(f"[FAIL] Unexpected error executing in WSL: {e}")
            raise ValueError(f"Unexpected error executing in WSL: {str(e)}")

    def run_cmd(self, cmd, shell=False):
        """
        Run a command and capture output.
        """
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=shell, check=True)
            print(f"[OK] Executed command: {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Command failed: {e.stderr}")
            raise ValueError(f"Command failed: {str(e)}")
        except Exception as e:
            print(f"[FAIL] Unexpected error executing command: {e}")
            raise ValueError(f"Unexpected error executing command: {str(e)}")

    def run_radosgw_admin(self, args, use_wsl=False):
        """
        Run a radosgw-admin command, optionally in WSL.
        """
        try:
            cmd = ["radosgw-admin"] + args
            if use_wsl:
                cmd = ["wsl"] + cmd
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"[OK] Executed radosgw-admin: {' '.join(cmd)}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Failed to execute radosgw-admin: {e.stderr}")
            raise ValueError(f"Failed to execute radosgw-admin: {str(e)}")
        except Exception as e:
            print(f"[FAIL] Unexpected error executing radosgw-admin: {e}")
            raise ValueError(f"Unexpected error executing radosgw-admin: {str(e)}")

    def check_wsl(self):
        """
        Check if WSL is installed and operational.
        """
        try:
            result = subprocess.run(["wsl", "--version"], capture_output=True, text=True, check=True)
            print(f"[OK] WSL is installed: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError:
            print("[FAIL] WSL is not installed or not operational")
            return False
        except Exception as e:
            print(f"[FAIL] Unexpected error checking WSL: {e}")
            return False

    def check_radosgw_admin(self, use_wsl=False):
        """
        Check if radosgw-admin is installed, optionally in WSL.
        """
        try:
            cmd = ["wsl", "which", "radosgw-admin"] if use_wsl else ["which", "radosgw-admin"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if result.stdout.strip():
                print(f"[OK] radosgw-admin is installed at: {result.stdout.strip()}")
                return True
            print("[FAIL] radosgw-admin is not installed")
            return False
        except subprocess.CalledProcessError:
            print("[FAIL] radosgw-admin is not installed")
            return False
        except Exception as e:
            print(f"[FAIL] Unexpected error checking radosgw-admin: {e}")
            return False

    def check_s5cmd(self):
        """
        Check if s5cmd is installed.
        """
        try:
            cmd = ["s5cmd", "--version"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"[OK] s5cmd is installed: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError:
            print("[FAIL] s5cmd is not installed")
            return False
        except Exception as e:
            print(f"[FAIL] Unexpected error checking s5cmd: {e}")
            return False

    def check_command_exists(self, cmd_name, path=None):
        """
        Check if a command is available in the system PATH or at a specified path.
        """
        try:
            if path:
                return os.path.isfile(path) and os.access(path, os.X_OK)
            result = shutil.which(cmd_name)
            if result:
                print(f"[OK] Command {cmd_name} found at: {result}")
                return True
            print(f"[FAIL] Command {cmd_name} not found")
            return False
        except Exception as e:
            print(f"[FAIL] Unexpected error checking command {cmd_name}: {e}")
            return False

    def check_aws_credentials_folder(self):
        """
        Ensure the ~/.aws/credentials folder exists.
        """
        try:
            aws_dir = os.path.expanduser("~/.aws")
            os.makedirs(aws_dir, exist_ok=True)
            print(f"[OK] AWS credentials folder exists: {aws_dir}")
            return True
        except Exception as e:
            print(f"[FAIL] Failed to create AWS credentials folder: {e}")
            return False

    def _list_all_files(self):
        # Retrieve all object keys in the bucket for finding close matches
        response = self.s3.list_objects_v2(Bucket=self.bucket_name)
        return [obj["Key"] for obj in response.get("Contents", [])] if "Contents" in response else []

    def _find_closest_match(self, target_name, file_list):
        # Find the closest matching file or folder name using difflib
        import difflib

        matches = difflib.get_close_matches(target_name, file_list, n=1, cutoff=0.5)
        return matches[0] if matches else None

    def get_local_path(self, key):
        # Generate a local file path that preserves the S3 folder structure
        return os.path.join("./downloads", self.bucket_name, key)

    def print_file_info(self, file_key, response):
        # Print detailed metadata for a downloaded file
        metadata = response.get("ResponseMetadata", {}).get("HTTPHeaders", {})
        file_size = metadata.get("content-length", "Unknown Size")
        file_type = metadata.get("content-type", "Unknown Type")
        last_modified = response.get("LastModified", "Unknown Date")
        print("\nDownloaded File Information:")
        print(f"File Name: {file_key}")
        print(f"File Size: {file_size} bytes")
        print(f"File Type: {file_type}")
        print(f"Last Modified: {last_modified}")

    def read_file_from_s3(self, key):
        # Read a file from S3 and process it based on its MIME type
        try:
            # Check if the file exists
            if not self.check_if_exists(key):
                file_list = self._list_all_files()
                closest_match = self._find_closest_match(key, file_list)
                if closest_match:
                    raise ValueError(f"File '{key}' not found. Similar file found: '{closest_match}'")
                raise ValueError(f"File '{key}' does not exist in bucket '{self.bucket_name}'.")

            # Detect file type
            file_type, _ = mimetypes.guess_type(key)
            file_type = file_type if file_type else "Unknown file type"

            # Read the file content
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            body = response["Body"].read()

            # Process based on file type
            if file_type and ("text" in file_type or file_type in ["application/json", "application/xml"]):
                content = body.decode("utf-8")
                if file_type == "application/json":
                    content = json.dumps(json.loads(content), indent=4)
                print(f"\nFile Content:\n{content}")
                return content
            if file_type and "image" in file_type:
                local_path = "downloaded_image.jpg"
                with open(local_path, "wb") as f:
                    f.write(body)
                print(f"Image saved as '{local_path}'")
                return local_path
            if file_type and "audio" in file_type:
                local_path = "downloaded_audio.mp3"
                with open(local_path, "wb") as f:
                    f.write(body)
                print(f"Audio file saved as '{local_path}'")
                return local_path
            if file_type and "pdf" in file_type:
                local_path = "downloaded_file.pdf"
                with open(local_path, "wb") as f:
                    f.write(body)
                print(f"PDF file saved as '{local_path}'")
                return local_path
            local_path = "downloaded_file.bin"
            with open(local_path, "wb") as f:
                f.write(body)
            print(f"Binary file saved as '{local_path}'")
            return local_path
        except ClientError as e:
            print(f"[FAIL] Failed to read file '{key}': {e.response['Error']['Code']}")
            raise ValueError(f"Failed to read file '{key}': {e.response['Error']['Code']}")
        except Exception as e:
            print(f"[FAIL] Unexpected error reading file '{key}': {e!s}")
            raise ValueError(f"Unexpected error reading file '{key}': {str(e)}")

    def get_identity(self):
        """
        Retrieve AWS caller identity using STS.
        """
        try:
            sts_client = boto3.client(
                "sts",
                endpoint_url=self.s3.meta.endpoint_url,
                aws_access_key_id=self.s3.meta.client._request_signer._credentials.access_key,
                aws_secret_access_key=self.s3.meta.client._request_signer._credentials.secret_key,
            )
            identity = sts_client.get_caller_identity()
            print(f"[OK] Caller Identity: {identity}")
            return identity
        except ClientError as e:
            print(f"[FAIL] Failed to get caller identity: {e.response['Error']['Code']}")
            raise ValueError(f"Failed to get caller identity: {e.response['Error']['Code']}")
        except Exception as e:
            print(f"[FAIL] Unexpected error getting caller identity: {e}")
            raise ValueError(f"Unexpected error getting caller identity: {str(e)}")

    def get_user_info(self):
        """
        Retrieve IAM user information.
        """
        try:
            iam_client = boto3.client(
                "iam",
                endpoint_url=self.s3.meta.endpoint_url,
                aws_access_key_id=self.s3.meta.client._request_signer._credentials.access_key,
                aws_secret_access_key=self.s3.meta.client._request_signer._credentials.secret_key,
            )
            user_info = iam_client.get_user()
            print(f"[OK] User Info: {user_info['User']}")
            return user_info["User"]
        except ClientError as e:
            print(f"[FAIL] Failed to get user info: {e.response['Error']['Code']}")
            raise ValueError(f"Failed to get user info: {e.response['Error']['Code']}")
        except Exception as e:
            print(f"[FAIL] Unexpected error getting user info: {e}")
            raise ValueError(f"Unexpected error getting user info: {str(e)}")

    def ensure_bucket_exists(self):
        try:
            buckets = self.s3.list_buckets()
            names = [b["Name"] for b in buckets.get("Buckets", [])]
            if self.bucket_name not in names:
                self.s3.create_bucket(Bucket=self.bucket_name)
                print(f"[OK] Ceph S3 Bucket Created: {self.bucket_name}")
            else:
                print(f"[OK] Ceph S3 Bucket Exists: {self.bucket_name}")
        except ClientError as e:
            print(f"[FAIL] Failed to ensure bucket exists: {e.response['Error']['Code']}")
            raise ValueError(f"Failed to ensure bucket exists: {e.response['Error']['Code']}")
        except Exception as e:
            print(f"[FAIL] Unexpected error ensuring bucket exists: {e}")
            raise ValueError(f"Unexpected error ensuring bucket exists: {str(e)}")

    def check_connection(self):
        try:
            self.s3.list_buckets()
            print("[OK] Ceph S3 Connection")
            return True
        except EndpointConnectionError:
            print("[FAIL] Ceph S3 Connection")
            raise ValueError("Ceph S3 Connection failed")
        except ClientError as e:
            print(f"[FAIL] Ceph S3 ClientError: {e.response['Error']['Code']}")
            raise ValueError(f"Ceph S3 ClientError: {e.response['Error']['Code']}")
        except Exception:
            print("[FAIL] Ceph S3 Unknown")
            raise ValueError("Ceph S3 Connection failed")

    def check_auth(self):
        try:
            self.s3.list_buckets()
            print("[OK] Ceph S3 Auth")
            return True
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code in ["InvalidAccessKeyId", "SignatureDoesNotMatch"]:
                print("[FAIL] Ceph S3 Auth Invalid")
            else:
                print(f"[FAIL] Ceph S3 Auth: {code}")
            raise ValueError(f"Ceph S3 Authentication failed: {code}")
        except Exception:
            print("[FAIL] Ceph S3 Auth Unknown")
            raise ValueError("Ceph S3 Authentication failed")

    def check_if_exists(self, key):
        try:
            resp = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=key)
            return resp.get("Contents", []) if "Contents" in resp else None
        except ClientError as e:
            print(f"[FAIL] Failed to check if key '{key}' exists: {e.response['Error']['Code']}")
            raise ValueError(f"Failed to check if key '{key}' exists: {e.response['Error']['Code']}")
        except Exception as e:
            print(f"[FAIL] Unexpected error checking if key '{key}' exists: {e}")
            raise ValueError(f"Unexpected error checking if key '{key}' exists: {str(e)}")

    def get_uri_size(self, uri):
        import re

        pattern = r"^s3://([^/]+)/(.+)$"
        match = re.match(pattern, uri)
        if not match:
            raise ValueError(f"Invalid S3 URI: {uri}")
        bucket, key = match.groups()
        if bucket != self.bucket_name:
            raise ValueError(f"URI bucket '{bucket}' does not match initialized bucket '{self.bucket_name}'")
        try:
            response = self.s3.head_object(Bucket=self.bucket_name, Key=key)
            size = response["ContentLength"] / (1024**2)
            print(f"[OK] Found file: {key} ({size:.2f} MB)")
            return size
        except self.s3.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                if not key.endswith("/"):
                    key += "/"
            else:
                raise ValueError(f"Failed to get size for {uri}: {e.response['Error']['Code']}")
        paginator = self.s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=key)
        total_size = 0
        found = False
        for page in tqdm(pages, desc=f"Scanning {uri}"):
            contents = page.get("Contents", [])
            if contents:
                found = True
                for obj in contents:
                    total_size += obj["Size"]
        if not found:
            print(f"[WARN] No objects found at URI '{uri}'.")
            return 0.0
        size_mb = total_size / (1024**2)
        size_mb = str(round(size_mb, 2))
        print(f"[OK] Folder total size: {size_mb} MB")
        return size_mb

    def list_buckets(self):
        try:
            response = self.s3.list_buckets()
            buckets = response.get("Buckets", [])
            bucket_data = [{"Name": b["Name"], "CreationDate": str(b["CreationDate"])} for b in buckets]
            if not buckets:
                print("No buckets found.")
            else:
                print("Available S3 buckets:")
                for bucket in buckets:
                    print(f" - {bucket['Name']} (Created: {bucket['CreationDate']})")
            return bucket_data
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            raise ValueError(f"Failed to list buckets: {error_code}")
        except Exception as e:
            raise ValueError(f"Unexpected error while listing buckets: {str(e)}")

    def list_folder_contents(self, folder_prefix):
        try:
            if not folder_prefix.endswith("/"):
                folder_prefix += "/"
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=folder_prefix)
            if "Contents" not in response:
                all_files = self._list_all_files()
                closest_match = self._find_closest_match(folder_prefix, all_files)
                if closest_match:
                    print(f"Folder '{folder_prefix}' was not found.")
                    print(f"However, a similar folder was found: '{closest_match}'")
                    folder_prefix = closest_match
                    response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=folder_prefix)
                else:
                    print(f"Folder '{folder_prefix}' does not exist in bucket '{self.bucket_name}'.")
                    raise ValueError(f"Folder '{folder_prefix}' does not exist in bucket '{self.bucket_name}'.")
            print(f"\nFiles in folder: {folder_prefix}\n")
            for obj in response.get("Contents", []):
                print(f" - {obj['Key']} (Last Modified: {obj['LastModified']})")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            raise ValueError(f"Failed to list folder contents: {error_code}")
        except Exception as e:
            raise ValueError(f"Unexpected error while listing folder contents: {str(e)}")

    def list_available_buckets(self):
        try:
            response = self.s3.list_buckets()
            buckets = [bucket["Name"] for bucket in response.get("Buckets", [])]
            if not buckets:
                print("No buckets found in Ceph S3.")
            return buckets
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            raise ValueError(f"Failed to list buckets: {error_code}")
        except Exception as e:
            raise ValueError(f"Unexpected error while listing buckets: {str(e)}")

    def print_bucket_full_detail(self):
        try:
            import json

            response = self.s3.list_buckets()
            print(json.dumps(response, indent=4, default=str))
            return response
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            raise ValueError(f"Failed to retrieve bucket details: {error_code}")
        except Exception as e:
            raise ValueError(f"Unexpected error while retrieving bucket details: {str(e)}")

    def print_bucket_short_detail(self):
        try:
            from tabulate import tabulate

            response = self.s3.list_buckets()
            buckets = response.get("Buckets", [])
            bucket_data = [[b["Name"], b["CreationDate"]] for b in buckets]
            if bucket_data:
                print("\nAvailable S3 Buckets:")
                print(tabulate(bucket_data, headers=["Bucket Name", "Creation Date"], tablefmt="fancy_grid"))
            else:
                print("No buckets found.")
        except ImportError:
            raise ValueError("Tabulate library is not installed. Please install it using 'pip install tabulate'.")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            raise ValueError(f"Failed to retrieve bucket details: {error_code}")
        except Exception as e:
            raise ValueError(f"Unexpected error while printing bucket details: {str(e)}")

    def find_file(self, file_or_folder_name):
        try:
            import difflib
            import mimetypes

            def list_all_files():
                response = self.s3.list_objects_v2(Bucket=self.bucket_name)
                return [obj["Key"] for obj in response.get("Contents", [])] if "Contents" in response else []

            def find_closest_match(target, file_list):
                matches = difflib.get_close_matches(target, file_list, n=1, cutoff=0.5)
                return matches[0] if matches else None

            def check_if_exists(key):
                response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=key)
                return "Contents" in response

            def list_folder_contents(prefix):
                if not prefix.endswith("/"):
                    prefix += "/"
                response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
                if "Contents" not in response:
                    closest_match = find_closest_match(prefix, list_all_files())
                    if closest_match:
                        raise ValueError(f"Folder '{prefix}' not found. Similar folder found: '{closest_match}'")
                    raise ValueError(f"Folder '{prefix}' does not exist in bucket '{self.bucket_name}'.")
                results = []
                for obj in response.get("Contents", []):
                    results.append((obj["Key"], obj["LastModified"]))
                return results

            def read_file(key):
                file_list = list_all_files()
                if not check_if_exists(key):
                    closest_match = find_closest_match(key, file_list)
                    if closest_match:
                        raise ValueError(f"File '{key}' not found. Similar file found: '{closest_match}'")
                    raise ValueError(f"File '{key}' does not exist in bucket '{self.bucket_name}'.")
                file_type, _ = mimetypes.guess_type(key)
                return [(key, file_type or "Unknown file type")]

            if file_or_folder_name.endswith("/") or "." not in file_or_folder_name:
                results = list_folder_contents(file_or_folder_name)
                print(f"\nFiles in folder: {file_or_folder_name}\n")
                for key, last_modified in results:
                    print(f"- {key} (Last Modified: {last_modified})")
                return results
            results = read_file(file_or_folder_name)
            print(f"\nFile Type Detected: {results[0][1]}\n")
            return results
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            raise ValueError(f"Failed to find file/folder: {error_code}")
        except Exception as e:
            raise ValueError(f"Unexpected error while finding file/folder: {str(e)}")

    def list_model_classes(self):
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix="models/", Delimiter="/")
            if "CommonPrefixes" not in response:
                print(f"No models found in bucket '{self.bucket_name}'.")
                return []
            model_classes = [prefix["Prefix"].split("/")[1] for prefix in response["CommonPrefixes"]]
            return model_classes
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchBucket":
                raise ValueError(f"Bucket '{self.bucket_name}' does not exist.")
            raise ValueError(f"Failed to list model classes: {error_code}")
        except Exception as e:
            raise ValueError(f"Unexpected error while listing model classes: {str(e)}")

    def list_buckets_and_model_classes(self):
        try:
            result = {}
            buckets = self.s3.list_buckets()
            bucket_names = [bucket["Name"] for bucket in buckets.get("Buckets", [])]
            for bucket in bucket_names:
                try:
                    response = self.s3.list_objects_v2(Bucket=bucket, Prefix="models/", Delimiter="/")
                    if "CommonPrefixes" in response:
                        model_classes = [prefix["Prefix"].split("/")[1] for prefix in response["CommonPrefixes"]]
                    else:
                        model_classes = []
                    result[bucket] = model_classes
                    print(f"Bucket: {bucket}")
                    if model_classes:
                        print(f"  Model Classes: {model_classes}")
                    else:
                        print("  No model classes found")
                    print("-" * 40)
                except ClientError as e:
                    error_code = e.response["Error"]["Code"]
                    if error_code == "NoSuchBucket":
                        print(f"Bucket '{bucket}' does not exist.")
                        continue
                    raise ValueError(f"Failed to list model classes for bucket '{bucket}': {error_code}")
            return result
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            raise ValueError(f"Failed to list buckets: {error_code}")
        except Exception as e:
            raise ValueError(f"Unexpected error while listing buckets and model classes: {str(e)}")

    def list_models_and_versions(self):
        try:
            all_models = {}
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix="models/", Delimiter="/")
            if "CommonPrefixes" not in response:
                print(f"No models found in bucket '{self.bucket_name}'.")
                return all_models
            model_classes = [prefix["Prefix"].split("/")[1] for prefix in response["CommonPrefixes"]]
            for model_class in model_classes:
                all_models[model_class] = {}
                response = self.s3.list_objects_v2(
                    Bucket=self.bucket_name, Prefix=f"models/{model_class}/", Delimiter="/"
                )
                if "CommonPrefixes" not in response:
                    continue
                models = [prefix["Prefix"].split("/")[2] for prefix in response["CommonPrefixes"]]
                for model in models:
                    version_response = self.s3.list_objects_v2(
                        Bucket=self.bucket_name, Prefix=f"models/{model_class}/{model}/", Delimiter="/"
                    )
                    if "CommonPrefixes" in version_response:
                        versions = [prefix["Prefix"].split("/")[-2] for prefix in version_response["CommonPrefixes"]]
                        numeric_versions = sorted(
                            [v for v in versions if v.startswith("model_v") and v[7:].isdigit()],
                            key=lambda v: int(v[7:]),
                        )
                        non_numeric_versions = [v for v in versions if v not in numeric_versions]
                        all_models[model_class][model] = numeric_versions + non_numeric_versions
                    else:
                        all_models[model_class][model] = []
                    print(f"\nCategory: {model_class}")
                    print(f"  Model: {model}")
                    print(
                        f"    Versions: {', '.join(all_models[model_class][model]) if all_models[model_class][model] else 'No versions found'}"
                    )
                    print("-" * 50)
            return all_models
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchBucket":
                raise ValueError(f"Bucket '{self.bucket_name}' does not exist.")
            raise ValueError(f"Failed to list models and versions: {error_code}")
        except Exception as e:
            raise ValueError(f"Unexpected error while listing models and versions: {str(e)}")

    def is_folder(self, key):
        contents = self.check_if_exists(key)
        return bool(contents) and any(obj["Key"] != key for obj in contents)

    def _download_file_with_progress_bar(self, remote_path, local_path):
        try:
            meta_data = self.s3.head_object(Bucket=self.bucket_name, Key=remote_path)
            total_length = int(meta_data.get("ContentLength", 0))
        except Exception as e:
            print(f"[ERROR] Failed to fetch metadata for '{remote_path}': {e}")
            total_length = None
        with tqdm(
            total=total_length,
            desc=os.path.basename(remote_path),
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            leave=False,
            dynamic_ncols=True,
            ncols=100,
            file=sys.stdout,
            ascii=True,
        ) as pbar:
            with open(local_path, "wb") as f:
                self.s3.download_fileobj(self.bucket_name, remote_path, f, Callback=pbar.update)

    def download_file(self, remote_path, local_path):
        if os.path.isdir(local_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        try:
            self._download_file_with_progress_bar(remote_path, local_path)
            print(f"Downloaded '{remote_path}' to '{local_path}'")
        except Exception as e:
            print(f"Error downloading file '{remote_path}': {e}")
            raise ValueError(f"Error downloading file '{remote_path}': {str(e)}")

    def download_folder(self, remote_folder, local_folder, keep_folder=False, exclude=[], overwrite=False):
        if not remote_folder.endswith("/"):
            remote_folder += "/"
        resp = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=remote_folder)
        if "Contents" not in resp:
            print(f"[FAIL] Folder {remote_folder} not found")
            raise ValueError(f"Folder {remote_folder} not found")
        print(f"Downloading folder '{remote_folder}' to '{local_folder}'...")
        if keep_folder:
            local_folder = os.path.join(local_folder, remote_folder.split("/")[-2])
        os.makedirs(local_folder, exist_ok=True)
        with tqdm(total=len(resp["Contents"]), desc="Downloading") as pbar:
            for obj in resp["Contents"]:
                file_key = obj["Key"]
                relative_path = file_key[len(remote_folder) :]
                if any(x in relative_path for x in exclude):
                    print(f"Skipped file {file_key}. File matches excluded pattern.")
                    continue
                local_file_path = os.path.join(local_folder, relative_path)
                if not overwrite and os.path.exists(local_file_path):
                    print(f"Skipped file {file_key}. File already exists.")
                else:
                    self.download_file(file_key, local_file_path)
                pbar.update(1)

    def download(self, remote_path, local_path, keep_folder=False, exclude=[], overwrite=False):
        if os.path.isfile(local_path) and self.is_folder(remote_path):
            raise ValueError("Cannot download folder to file path")
        if os.path.isdir(local_path) and not self.is_folder(remote_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))
        if self.is_folder(remote_path):
            self.download_folder(remote_path, local_path, keep_folder=keep_folder, exclude=exclude, overwrite=overwrite)
        else:
            self.download_file(remote_path, local_path)

    def upload_file(self, local_file_path, remote_path):
        try:
            self.s3.upload_file(local_file_path, self.bucket_name, remote_path)
            print(f"[Upload] {local_file_path} -> s3://{self.bucket_name}/{remote_path}")
        except Exception as e:
            raise ValueError(f"Failed to upload file {local_file_path} to {remote_path}: {str(e)}")

    def upload(self, local_path, remote_path):
        """
        Upload a file or folder to S3 and return the size of the uploaded content.

        Args:
            local_path (str): Path to the local file or folder.
            remote_path (str): Destination path in S3.

        Returns:
            float: Size of the uploaded content in MB, or None if calculation fails.

        Raises:
            ValueError: If paths are invalid or upload fails.
        """
        logger = logging.getLogger(__name__)
        if os.path.isfile(local_path) and self.is_folder(remote_path):
            logger.error("Cannot upload file to folder path")
            print(f"[ERROR] Cannot upload file to folder path")
            raise ValueError("Cannot upload file to folder path")
        if os.path.isdir(local_path):
            if self.check_if_exists(remote_path) and not self.is_folder(remote_path):
                logger.error("Cannot upload folder to file path")
                print(f"[ERROR] Cannot upload folder to file path")
                raise ValueError("Cannot upload folder to file path")

        try:
            uploaded_files = []
            # Use s5cmd if available for faster upload
            if self.check_s5cmd() and os.path.isdir(local_path):
                cmd = ["s5cmd", "cp", f"{local_path}/*", f"s3://{self.bucket_name}/{remote_path}"]
                self.run_cmd(cmd)
            else:
                if os.path.isdir(local_path):
                    for root, _, files in os.walk(local_path):
                        for file in files:
                            local_file = os.path.join(root, file)
                            s3_key = os.path.join(remote_path, os.path.relpath(local_file, local_path)).replace("\\", "/")
                            self.upload_file(local_file, s3_key)
                            print(f"[Upload] {local_file} -> s3://{self.bucket_name}/{s3_key}")
                            uploaded_files.append(s3_key)
                else:
                    self.upload_file(local_path, remote_path)
                    print(f"[Upload] {local_path} -> s3://{self.bucket_name}/{remote_path}")
                    uploaded_files.append(remote_path)

            # Calculate the size of the uploaded content
            uri = f"s3://{self.bucket_name}/{remote_path}"
            try:
                size_mb = self.get_uri_size(uri)
                logger.info(f"Uploaded {local_path} to {uri}, size: {size_mb} MB")
                return size_mb
            except Exception as e:
                logger.warning(f"Failed to calculate size for {uri}: {e}")
                print(f"[WARN] Failed to calculate size for {uri}: {e}")
                return None
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            print(f"[FAIL] Upload failed: {e}")
            for s3_key in uploaded_files:
                try:
                    self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
                    logger.info(f"Cleaned up partially uploaded file: {s3_key}")
                    print(f"[INFO] Cleaned up partially uploaded file: {s3_key}")
                except Exception as cleanup_error:
                    logger.error(f"Failed to clean up {s3_key}: {cleanup_error}")
                    print(f"[ERROR] Failed to clean up {s3_key}: {cleanup_error}")
            raise ValueError(f"Upload failed: {str(e)}")

    def delete_folder(self, prefix):
        try:
            objects = self.check_if_exists(prefix)
            if objects:
                for obj in objects:
                    self.s3.delete_object(Bucket=self.bucket_name, Key=obj["Key"])
                print(f"[Delete] s3://{self.bucket_name}/{prefix}")
        except Exception as e:
            print(f"[FAIL] Failed to delete folder {prefix}: {e}")
            raise ValueError(f"Failed to delete folder {prefix}: {str(e)}")

    def move_folder(self, src_prefix, dest_prefix):
        try:
            objects = self.check_if_exists(src_prefix)
            if not objects:
                raise ValueError(f"Source folder {src_prefix} does not exist")
            for obj in objects:
                src_key = obj["Key"]
                dest_key = src_key.replace(src_prefix, dest_prefix, 1)
                self.s3.copy_object(Bucket=self.bucket_name, CopySource={'Bucket': self.bucket_name, 'Key': src_key}, Key=dest_key)
                self.s3.delete_object(Bucket=self.bucket_name, Key=src_key)
            print(f"[Move] s3://{self.bucket_name}/{src_prefix} -> s3://{self.bucket_name}/{dest_prefix}")
        except Exception as e:
            print(f"[FAIL] Failed to move folder from {src_prefix} to {dest_prefix}: {e}")
            raise ValueError(f"Failed to move folder from {src_prefix} to {dest_prefix}: {str(e)}")