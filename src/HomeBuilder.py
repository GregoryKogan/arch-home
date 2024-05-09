import os, errno, subprocess
import logging


class HomeBuilder:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def build(self):
        self.link_files()
        self.link_scripts()
        self.run_build_scripts()

    def link_files(self):
        for file in self.config.get("files", []):
            destination = os.path.expanduser(f"~/{file['dest']}")

            os.makedirs(os.path.dirname(destination), mode=0o777, exist_ok=True)
            self.symlink_force(file["src"], destination)

            self.logger.info(f"Symlink: {destination} -> {file['src']}")

    def link_scripts(self):
        os.makedirs(os.path.expanduser("~/.bin/"), mode=0o777, exist_ok=True)

        user_scripts = self.config.get("scripts", {}).get("user", [])

        if len(user_scripts):
            self.logger.info("Don't forget to add ~/.bin to your PATH")

        for script in user_scripts:
            self.ensure_script_exists(script)

            os.chmod(script, 0o755)
            destination = os.path.expanduser(f"~/.bin/{os.path.basename(script)}")
            self.symlink_force(script, destination)
            self.logger.info(f"Symlink: {destination} -> {script}")

    def run_build_scripts(self):
        for script in self.config.get("scripts", {}).get("build", []):
            self.ensure_script_exists(script)

            os.chmod(script, 0o755)
            self.logger.info(f"Running build script: {script}")
            subprocess.run([script], check=True)

    def symlink_force(self, target, link_name):
        try:
            os.symlink(target, link_name)
        except OSError as e:
            if e.errno != errno.EEXIST:
                self.logger.error(f"Failed to create symlink: {link_name} -> {target}")
                raise e
            try:
                os.remove(link_name)
                os.symlink(target, link_name)
            except OSError as e:
                self.logger.error(f"Failed to update symlink: {link_name} -> {target}")
                raise e

    def ensure_script_exists(self, script):
        if not os.path.exists(script) or not os.path.isfile(script):
            self.logger.error(f"Script not found: {script}")
            raise FileNotFoundError(f"Script not found: {script}")
