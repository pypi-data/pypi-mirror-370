import os
import shutil
import tempfile
import docker

class Cleaner:
    """Responsible for cleaning temporary files, Docker containers, images, and volumes."""

    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            print(f"Error initializing Docker client: {e}")
            self.client = None

    def cleanup(self):
        """ Responsable to clean dirs, docker images and containers after all executions,
            removes all stopped containers, unused networks, dangling images, and build cache.
        """
        try:
            client = docker.from_env()
            self.perform_cleanup()

            for container in client.containers.list(all=True):
                try:
                    container.remove()
                except Exception:
                    continue

            for image in client.images.list():
                if image.tags and any(tag.startswith("public.ecr.aws/convisoappsec/") for tag in image.tags):
                    try:
                        client.images.remove(image.id)
                    except Exception as e:
                        print(f"Error removing image {image.tags}: {e}")
                        continue

            volumes = client.volumes.list()
            for volume in volumes:
                try:
                    volume.remove()
                except Exception:
                    continue

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return

    def perform_cleanup(self):
       """Method to clean the tmp directory and remove 'conviso-output-' directories in the current directory."""

       tmp_dir = tempfile.gettempdir()

       # Clear system temp directory
       try:
           for filename in os.listdir(tmp_dir):
               file_path = os.path.join(tmp_dir, filename)
               try:
                   if os.path.isfile(file_path) or os.path.islink(file_path):
                       os.remove(file_path)
                   elif os.path.isdir(file_path):
                       shutil.rmtree(file_path)
               except Exception:
                   pass
       except Exception:
           pass

       # Clear 'conviso-output-' directories in the current directory
       try:
           for filename in os.listdir("."):
               dir_path = os.path.join(".", filename)
               if os.path.isdir(dir_path) and filename.startswith("conviso-output-"):
                   try:
                       shutil.rmtree(dir_path)
                   except Exception:
                       pass
       except Exception:
           pass
