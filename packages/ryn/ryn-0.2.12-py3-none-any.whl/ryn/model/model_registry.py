import os
import shutil
from base64 import b64encode
from datetime import datetime
import logging
import requests
import subprocess
from dotenv import load_dotenv
from huggingface_hub import snapshot_download

load_dotenv()

from .CephS3Manager import CephS3Manager

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ProjectsAPI manages ClearML project operations
class ProjectsAPI:
    def __init__(self, post):
        self._post = post

    def create(self, name, description=""):
        response = self._post("/projects.create", {"name": name, "description": description})
        if not response or "id" not in response:
            raise ValueError("Failed to create project in ClearML")
        return response

    def get_all(self):
        response = self._post("/projects.get_all")
        if not response or "projects" not in response:
            raise ValueError("Failed to retrieve projects from ClearML")
        return response["projects"]

# ModelsAPI manages ClearML model operations
class ModelsAPI:
    def __init__(self, post):
        self._post = post

    def get_all(self, project_id=None):
        payload = {"project": project_id} if project_id else {}
        # print("$$$$$$$$$$$$$$$$$$ model get all payload", payload)
        response = self._post("/models.get_all", payload)
        # print("[DEBUG] Full response from /models.get_all:", response)

        # Check expected key in proper format
        if isinstance(response, dict):
            if "models" in response and isinstance(response["models"], list):
                return response["models"]
            if "data" in response and isinstance(response["data"], dict) and "models" in response["data"]:
                return response["data"]["models"]

        print(f"[ERROR] 'models' not found in response: {response}")
        raise ValueError("Failed to retrieve models from ClearML")
        return []

    def create(self, name, project_id, metadata=None, uri=""):
        payload = {
            "name": name,
            "project": project_id,
            "uri": uri
        }

        if isinstance(metadata, dict):
            payload["metadata"] = metadata

        response = self._post("/models.create", payload)
        if not response or "id" not in response:
            raise ValueError("Failed to create model in ClearML")
        return response

    def update(self, model_id, uri=None, metadata=None):
        payload = {"model": model_id}
        if uri:
            payload["uri"] = uri
        if isinstance(metadata, dict) or isinstance(metadata, list):
            payload["metadata"] = metadata

        # print(f"[DEBUG] Metadata Payload: {metadata}")
        # print(f"[DEBUG] Full Payload to /models.update: {payload}")

        response = self._post("/models.add_or_update_metadata", payload)
        if not response:
            raise ValueError("Failed to update model metadata in ClearML")
        return response

    def edit_uri(self, model_id, uri):
        payload = {"model": model_id, "uri": uri}
        # print(f"[DEBUG] Payload to /models.edit: {payload}")
        response = self._post("/models.edit", payload)
        if not response:
            raise ValueError("Failed to edit model URI in ClearML")
        return response

    def get_by_id(self, model_id):
        response = self._post("/models.get_by_id", {"model": model_id})
        if not response:
            raise ValueError(f"Failed to retrieve model with ID {model_id} from ClearML")
        return response

    def delete(self, model_id):
        response = self._post("/models.delete", {"model": model_id})
        if not response:
            raise ValueError(f"Failed to delete model with ID {model_id} from ClearML")
        return response

# ModelRegistry integrates ClearML and Ceph S3 operations
class ModelRegistry:
    def __init__(
        self,
        CLEARML_API_SERVER_URL=None,
        CLEARML_USERNAME=None,
        CLEARML_ACCESS_KEY=None,
        CLEARML_SECRET_KEY=None
    ):
        # Load defaults from environment
        self.CLEARML_API_SERVER_URL = CLEARML_API_SERVER_URL or os.environ.get("API_URL")
        self.CLEARML_USERNAME = CLEARML_USERNAME or os.environ.get("USERNAME")
        self.CLEARML_ACCESS_KEY = CLEARML_ACCESS_KEY or os.environ.get("ACCESS_KEY")
        self.CLEARML_SECRET_KEY = CLEARML_SECRET_KEY or os.environ.get("SECRET_KEY")

        # Validate required ClearML credentials
        if not all([self.CLEARML_API_SERVER_URL, self.CLEARML_USERNAME, self.CLEARML_ACCESS_KEY, self.CLEARML_SECRET_KEY]):
            raise ValueError("Missing required ClearML configuration parameters")

        # Ceph configuration from environment
        self.CEPH_ENDPOINT_URL = os.environ.get("CEPH_ENDPOINT_URL", "")
        self.CEPH_ADMIN_ACCESS_KEY = os.environ.get("CEPH_ACCESS_KEY", "")
        self.CEPH_ADMIN_SECRET_KEY = os.environ.get("CEPH_SECRET_KEY", "")
        self.CEPH_USER_BUCKET = os.environ.get("CEPH_USER_BUCKET", "")

        # Health checks for ClearML services
        if not self.check_clearml_service():
            raise ValueError("ClearML Server down.")
        if not self.check_clearml_auth():
            raise ValueError("ClearML Authentication not correct.")

        # Initialize CephS3Manager with user-specific bucket
        self.ceph = CephS3Manager(
            self.CEPH_ENDPOINT_URL,
            self.CEPH_ADMIN_ACCESS_KEY,
            self.CEPH_ADMIN_SECRET_KEY,
            self.CEPH_USER_BUCKET
        )

        # Login to ClearML and extract token
        creds = f"{self.CLEARML_ACCESS_KEY}:{self.CLEARML_SECRET_KEY}"
        auth_header = b64encode(creds.encode("utf-8")).decode("utf-8")
        res = requests.post(
            f"{self.CLEARML_API_SERVER_URL}/auth.login",
            headers={"Authorization": f"Basic {auth_header}"}
        )
        if res.status_code != 200:
            raise ValueError("Failed to authenticate with ClearML")
        self.token = res.json()["data"]["token"]
        # print(f"[DEBUG] Bearer Token: {self.token}")

        self.projects = ProjectsAPI(self._post)
        self.models = ModelsAPI(self._post)

        # Get or create user-specific project
        projects = self.projects.get_all()
        self.project_name = f"project_{self.CLEARML_USERNAME}"
        exists = [p for p in projects if p["name"] == self.project_name]
        self.project_id = exists[0]["id"] if exists else self.projects.create(self.project_name)["id"]

    def _post(self, path, params=None):
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            res = requests.post(f"{self.CLEARML_API_SERVER_URL}{path}", headers=headers, json=params)
            res.raise_for_status()

            data = res.json()
            # print(f"[DEBUG] Response for {path}: {data}")

            if "data" not in data:
                print(f"[ERROR] No 'data' key in response: {data}")
                raise ValueError(f"Request to {path} failed: No data in response")
            return data["data"]

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request to {path} failed: {e}")
            print(f"[ERROR] Status Code: {res.status_code}, Response: {res.text}")
            raise ValueError(f"Request to {path} failed: {str(e)}")

        except ValueError as e:
            print(f"[ERROR] Failed to parse JSON from {path}: {e}")
            print(f"[ERROR] Raw response: {res.text}")
            raise ValueError(f"Failed to parse JSON from {path}: {str(e)}")

    def check_clearml_service(self):
        """
        Check if ClearML service is reachable and responding.
        """
        try:
            r = requests.get(self.CLEARML_API_SERVER_URL + "/auth.login", timeout=5)
            if r.status_code in [200, 401]:
                print("[OK] ClearML Service")
                return True
            print(f"[FAIL] ClearML Service {r.status_code}")
            raise ValueError("ClearML Service is not reachable")
        except Exception as e:
            print(f"[FAIL] ClearML Service: {str(e)}")
            raise ValueError("ClearML Service is not reachable")

    def check_clearml_auth(self):
        """
        Check if ClearML credentials are valid by attempting login.
        """
        try:
            creds = f"{self.CLEARML_ACCESS_KEY}:{self.CLEARML_SECRET_KEY}"
            auth_header = b64encode(creds.encode("utf-8")).decode("utf-8")
            r = requests.post(
                self.CLEARML_API_SERVER_URL + "/auth.login",
                headers={"Authorization": f"Basic {auth_header}"},
                timeout=5
            )
            if r.status_code == 200:
                print("[OK] ClearML Auth")
                return True
            print(f"[FAIL] ClearML Auth {r.status_code}")
            raise ValueError("ClearML Authentication failed")
        except Exception as e:
            print(f"[FAIL] ClearML Auth: {str(e)}")
            raise ValueError("ClearML Authentication failed")

    def get_model_id_by_name(self, name):
        # print(f"[DEBUG] Using project ID: {self.project_id}")
        models = self.models.get_all(self.project_id)
        for m in models:
            if m["name"] == name:
                return m["id"]
        return None

    def get_model_name_by_id(self, model_id):
        model = self.models.get_by_id(model_id)
        return model.get("name") if model else None

    def generate_random_string(self):
        import random
        import string
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

    def transfer_from_s3(self, source_endpoint_url, source_access_key, source_secret_key, source_bucket, source_path, dest_prefix, exclude=[".git", ".DS_Store"], overwrite=True):
        """
        Transfer a model from another S3 bucket to the initialized bucket.
        """
        tmp_dir = None
        try:
            tmp_dir = f"./tmp_{self.generate_random_string()}"
            os.makedirs(tmp_dir, exist_ok=True)

            src_ceph = CephS3Manager(source_endpoint_url, source_access_key, source_secret_key, source_bucket)
            print("### S3 initialized")
            src_ceph.download(source_path, tmp_dir, keep_folder=True, exclude=exclude, overwrite=overwrite)
            print("### Download done.")
            self.ceph.delete_folder(dest_prefix)  # Ensure clean state
            print("### Dest forlder deleted.")
            self.ceph.upload(tmp_dir, dest_prefix)
            print("### Model Uploaded.")

            return True
        except Exception as e:
            print(f"[FAIL] Failed to transfer model from S3: {e}")
            try:
                self.ceph.delete_folder(dest_prefix)
            except Exception as cleanup_error:
                print(f"[ERROR] Failed to clean up destination folder {dest_prefix}: {cleanup_error}")
            raise ValueError(f"Failed to transfer model from S3: {str(e)}")
        finally:
            if tmp_dir and os.path.exists(tmp_dir):
                try:
                    shutil.rmtree(tmp_dir)
                except Exception as cleanup_error:
                    print(f"[ERROR] Failed to clean up temporary directory {tmp_dir}: {cleanup_error}")

    def add_model(self, source_type, model_name=None, code_path=None, source_path=None,
                  hf_source=None, access_key=None, secret_key=None, endpoint_url=None,
                  bucket_name=None):
        """
        Add a model from various sources (local, Hugging Face, or S3) and register it in ClearML.

        Args:
            source_type (str): Type of source ('local', 'hf', or 's3').
            model_name (str): Name of the model.
            code_path (str): Path to an optional model.py file.
            source_path (str): Path to the model for local or S3 sources.
            hf_source (str): Hugging Face repository ID for 'hf' source.
            access_key (str): Access key for S3 source.
            secret_key (str): Secret key for S3 source.
            endpoint_url (str): Endpoint URL for S3 source.
            bucket_name (str): Bucket name for S3 source.

        Returns:
            str or None: Returns the model_id (str) if successful, None if failed.
        """
        # Input validation
        if not model_name or not isinstance(model_name, str):
            logger.error("Model name is required")
            print(f"[ERROR] model_name must be a non-empty string")
            return None
        if source_type not in ["local", "hf", "s3"]:
            logger.error(f"Unknown source_type: {source_type}")
            print(f"[ERROR] Unknown source_type: {source_type}")
            return None
        if source_type == "local":
            if not source_path or not os.path.exists(source_path):
                logger.error(f"Local path {source_path} does not exist")
                return None
            if not os.access(source_path, os.R_OK):
                logger.error(f"Cannot read source_path: {source_path}")
                return None
        if source_type == "hf" and (not hf_source or not isinstance(hf_source, str)):
            logger.error(f"Invalid or missing hf_source: {hf_source}")
            return None
        if source_type == "s3" and (
            not all([source_path, access_key, secret_key, endpoint_url, bucket_name])
            or not all(isinstance(x, str) for x in [source_path, access_key, secret_key, endpoint_url, bucket_name])
        ):
            logger.error("Missing required S3 parameters")
            return None
        if code_path and (not os.path.isfile(code_path) or not code_path.endswith(".py")):
            logger.error(f"Invalid code_path: {code_path}. Must be a valid .py file")
            return None

        if self.get_model_id_by_name(model_name):
            logger.warning(f"Model with name '{model_name}' already exists.")
            print(f"[WARN] Model with name '{model_name}' already exists.")
            print("[INFO] Listing existing models:")
            self.list_models(verbose=True)
            return None

        model_folder_name = os.path.basename(source_path.rstrip("/\\")) if source_path else ""
        have_model_py = False
        random_folder = self.generate_random_string()
        temp_model_id = random_folder
        dest_prefix = f"models/{temp_model_id}/"
        local_path = None
        temp_local_path = None

        try:
            if source_type == "local":
                # Create a temporary copy to protect source_path
                temp_local_path = f"./tmp_{random_folder}"
                shutil.copytree(source_path, temp_local_path, dirs_exist_ok=True)
                self.ceph.delete_folder(dest_prefix)  # Ensure clean state
                size_mb = self.ceph.upload(temp_local_path, dest_prefix)
            elif source_type == "hf":
                local_path = snapshot_download(repo_id=hf_source)
                self.ceph.delete_folder(dest_prefix)  # Ensure clean state
                size_mb = self.ceph.upload(local_path, dest_prefix)
            elif source_type == "s3":
                success = self.transfer_from_s3(
                    source_endpoint_url=endpoint_url,
                    source_access_key=access_key,
                    source_secret_key=secret_key,
                    source_bucket=bucket_name,
                    source_path=source_path,
                    dest_prefix=dest_prefix,
                    exclude=[".git", ".DS_Store"],
                    overwrite=True
                )
                if not success:
                    raise ValueError("Failed to transfer model from S3")
                uri = f"s3://{self.ceph.bucket_name}/{dest_prefix}"
                size_mb = self.ceph.get_uri_size(uri)
            else:
                raise ValueError(f"Unknown source_type: {source_type}")

            if code_path and os.path.isfile(code_path):
                self.ceph.upload(code_path, dest_prefix + "model.py")
                have_model_py = True

            # Create model in ClearML after successful upload
            model = self.models.create(
                name=model_name,
                project_id=self.project_id,
                uri="s3://dummy/uri"
            )

            model_id = model["id"]
            if model_id != temp_model_id:
                new_dest_prefix = f"models/{model_id}/"
                if self.ceph.check_if_exists(new_dest_prefix):
                    self.ceph.delete_folder(new_dest_prefix)
                self.ceph.move_folder(dest_prefix, new_dest_prefix)
                self.ceph.delete_folder(dest_prefix)
                dest_prefix = new_dest_prefix

            metadata_list = [
                {"key": "modelFolderName", "type": "str", "value": model_folder_name},
                {"key": "haveModelPy", "type": "str", "value": str(have_model_py).lower()},
                {"key": "modelSize", "type": "float", "value": str(size_mb) if size_mb is not None else "0.0"}
            ]

            uri = f"s3://{self.ceph.bucket_name}/{dest_prefix}"
            self.models.edit_uri(model_id, uri=uri)
            self.models.update(model_id, metadata=metadata_list)

            logger.info(f"Model '{model_name}' (ID: {model_id}) added successfully")
            print(f"[SUCCESS] Model '{model_name}' (ID: {model_id}) added successfully")
            return model_id

        except (Exception, KeyboardInterrupt) as e:
            logger.error(f"Upload or registration failed: {e}")
            print(f"[ERROR] Upload or registration failed: {e}")
            print("[INFO] Cleaning up partially uploaded model...")
            if 'model_id' in locals():
                try:
                    self.models.delete(model_id)
                except Exception as cleanup_error:
                    logger.error(f"Failed to clean up ClearML model {model_id}: {cleanup_error}")
                    print(f"[ERROR] Failed to clean up ClearML model {model_id}: {cleanup_error}")
            if dest_prefix:
                try:
                    self.ceph.delete_folder(dest_prefix)
                except Exception as cleanup_error:
                    logger.error(f"Failed to clean up Ceph folder {dest_prefix}: {cleanup_error}")
                    print(f"[ERROR] Failed to clean up Ceph folder {dest_prefix}: {cleanup_error}")
            return None
        finally:
            # Clean up temporary local paths
            for path in [local_path, temp_local_path]:
                if path and os.path.exists(path):
                    try:
                        shutil.rmtree(path)
                    except Exception as cleanup_error:
                        logger.error(f"Failed to clean up local directory {path}: {cleanup_error}")
                        print(f"[ERROR] Failed to clean up local directory {path}: {cleanup_error}")

    def get_model(self, model_name, local_dest):
        model_id = self.get_model_id_by_name(model_name)
        if not model_id:
            print("[FAIL] Model not found")
            raise ValueError(f"Model '{model_name}' not found")

        model_data = self.models.get_by_id(model_id)
        model = model_data.get("model") or model_data
        uri = model["uri"]
        if not uri:
            raise ValueError(f"Model '{model_name}' has no URI")

        _, remote_path = uri.replace("s3://", "").split("/", 1)
        
        # Generate timestamped folder name
        timestamp = datetime.now().strftime("DATE-%Y-%m-%d_Time-%H-%M")
        local_dest = os.path.join(local_dest, f"{model_name}_{timestamp}")

        try:
            self.ceph.download(remote_path, local_dest, keep_folder=True, exclude=[".git", ".DS_Store"], overwrite=False)
            print(f"[SUCCESS] Model '{model_name}' downloaded successfully to '{local_dest}'")
            return model
        except Exception as e:
            print(f"[FAIL] Failed to download model '{model_name}': {e}")
            raise ValueError(f"Failed to download model '{model_name}': {str(e)}")

    def get_model_info(self, identifier):
        """
        Fetch model info using either model_name or model_id.
        If `identifier` matches an existing ID, it will use it directly.
        Otherwise, it will treat it as a name and search accordingly.
        """
        all_models = self.models.get_all(self.project_id)

        def extract_model_info(model):
            print("=" * 40)
            print(f"ID: {model.get('id')}")
            print(f"Name: {model.get('name')}")
            print(f"Created: {model.get('created')}")
            print(f"Framework: {model.get('framework')}")
            print(f"URI: {model.get('uri')}")

            # Extract and show metadata (including modelSize)
            metadata = model.get("metadata", {})
            print("Metadata:")
            for key, value in metadata.items():
                print(f"  - {key}: {value}")

            # Highlight modelSize if available
            model_size = metadata.get("modelSize")
            if model_size is not None:
                try:
                    print(f"\n[Model Size] {float(model_size):.2f} MB")
                except (ValueError, TypeError):
                    print(f"\n[Model Size] Invalid value: {model_size}")

            print(f"Labels: {model.get('labels')}")
            print("=" * 40)

        # Try match by ID
        matched_by_id = [m for m in all_models if m.get("id") == identifier]
        if matched_by_id:
            extract_model_info(matched_by_id[0])
            return matched_by_id[0]

        # Try match by name
        matched_by_name = [m for m in all_models if m.get("name") == identifier]
        if matched_by_name:
            for model in matched_by_name:
                extract_model_info(model)
            return matched_by_name

        print(f"[INFO] No model found with identifier: '{identifier}'")
        raise ValueError(f"No model found with identifier: '{identifier}'")

    def list_models(self, verbose=True):
        try:
            models = self.models.get_all(self.project_id)
            if verbose:
                grouped = {}
                for m in models:
                    grouped.setdefault(m["name"], []).append(m["id"])
                for name, ids in grouped.items():
                    print(f"[Model] Name: {name}, Count: {len(ids)}")
            else:
                for m in models:
                    print(f"[Model] {m['name']} (ID: {m['id']})")
            return [(m["name"], m["id"]) for m in models]
        except Exception as e:
            print(f"[FAIL] Failed to list models: {e}")
            raise ValueError(f"Failed to list models: {str(e)}")

    def delete_model(self, model_id=None, model_name=None):
        if model_name and not model_id:
            model_id = self.get_model_id_by_name(model_name)
            if not model_id:
                print(f"[WARN] No model found with name '{model_name}'")
                raise ValueError(f"No model found with name '{model_name}'")

        model_data = self.models.get_by_id(model_id)
        if not model_data:
            print(f"[WARN] Model with ID '{model_id}' not found.")
            raise ValueError(f"Model with ID '{model_id}' not found")

        model = model_data.get("model") or model_data
        uri = model.get("uri")
        if not uri:
            print(f"[WARN] Model '{model_id}' has no 'uri'.")
            raise ValueError(f"Model '{model_id}' has no URI")

        try:
            _, remote_path = uri.replace("s3://", "").split("/", 1)
            self.ceph.delete_folder(remote_path)
            self.models.delete(model_id)
            print(f"[SUCCESS] Model '{model_id}' deleted successfully from ClearML and Ceph")
        except Exception as e:
            print(f"[FAIL] Failed to delete model '{model_id}': {e}")
            raise ValueError(f"Failed to delete model '{model_id}': {str(e)}")