import tomllib
import os


class ConfigBuilder:
    def __init__(self, entry_config):
        self.entry_config = entry_config
        self.config_files = []

        self.files = []
        self.pacman_packages = []
        self.aur_packages = []
        self.build_scripts = []
        self.user_scripts = []
    
    def build(self):
        self.collect_config_files()
        
        for conf in self.config_files:
            try:
                with open(conf, 'rb') as f:
                    data = tomllib.load(f)
            except FileNotFoundError:
                print(f'File not found: {conf}')
                continue

            for file in data.get('files', []):
                file['src'] = self.abs_path(file['src'], conf)
                self.files.append(file)
            
            self.pacman_packages.extend(data.get('packages').get('pacman', []))
            self.aur_packages.extend(data.get('packages').get('aur', []))

            build_scripts = data.get('scripts').get('build', [])
            for script in build_scripts:
                self.build_scripts.append(self.abs_path(script, conf))
            
            user_scripts = data.get('scripts').get('user', [])
            for script in user_scripts:
                self.user_scripts.append(self.abs_path(script, conf))

        self.pacman_packages = list(set(self.pacman_packages))
        self.aur_packages = list(set(self.aur_packages))
        self.build_scripts = list(set(self.build_scripts))
        self.user_scripts = list(set(self.user_scripts))
        
        return {
            'files': self.files,
            'packages': {
                'pacman': self.pacman_packages,
                'aur': self.aur_packages
            },
            'scripts': {
                'build': self.build_scripts,
                'user': self.user_scripts
            }
        }

    
    def collect_config_files(self):
        queue = [self.entry_config]
    
        while len(queue):
            current = queue.pop(0)
            
            if current in self.config_files:
                continue
            self.config_files.append(current)

            queue.extend(
                self.abs_path(module, current) 
                for module in self.read_imports(current)
            )
    
    def abs_path(self, rel_path, parent):
        return os.path.normpath(os.path.join(os.path.dirname(parent), rel_path))

    def read_imports(self, conf):
        try:
            with open(conf, 'rb') as f:
                data = tomllib.load(f)
        except FileNotFoundError:
            print(f'File not found: {conf}')
            return []
        
        return data.get('imports', [])
