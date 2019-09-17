import hashlib


class CheckFileHash:
    FILE_HASHES = {
        'items_file': 'cache/.items_hash',
        'workflows_file': 'cache/.workflows_hash',
    }
    FILE_PATHS = {
        'items_file': 'input_files/items.csv',
        'workflows_file': 'input_files/workflow_specifications.json',
    }

    def __init__(self):
        for file_name, file_path in self.FILE_HASHES.items():
            file_hash = self._load_file(file_path)
            if file_hash:
                setattr(self, file_name, file_hash)
            else:
                self._create_file(file_name, '')
                setattr(self, file_name, None)

    def check_hash(self, file_name):
        new_hash = self._create_hash(file_path=self.FILE_PATHS.get(file_name))
        old_hash = getattr(self, file_name)
        if not old_hash:
            self._create_file(file_name, new_hash)
            return True
        if new_hash == old_hash:
            return False
        self._create_file(file_name, new_hash)
        return True

    def update(self):
        self.__init__()

    @staticmethod
    def _load_file(file_path):
        try:
            with open(file_path, 'r') as cache_file:
                file_hash = cache_file.read()
                if file_hash:
                    return file_hash
                raise IOError
        except IOError:
            return None

    def _create_file(self, file_name, input_text):
        with open(self.FILE_HASHES.get(file_name), 'w') as cache_file:
            cache_file.write(input_text)

    @staticmethod
    def _create_hash(file_path):
        try:
            with open(file_path, 'r') as file:
                file_text = file.read()
                return hashlib.sha256(str(file_text).encode('utf-8')).hexdigest()
        except FileNotFoundError:
            return None
