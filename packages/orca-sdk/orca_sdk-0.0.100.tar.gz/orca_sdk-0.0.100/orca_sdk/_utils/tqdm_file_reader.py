class TqdmFileReader:
    def __init__(self, file_obj, pbar):
        self.file_obj = file_obj
        self.pbar = pbar

    def read(self, size=-1):
        data = self.file_obj.read(size)
        self.pbar.update(len(data))
        return data

    def __getattr__(self, attr):
        return getattr(self.file_obj, attr)
