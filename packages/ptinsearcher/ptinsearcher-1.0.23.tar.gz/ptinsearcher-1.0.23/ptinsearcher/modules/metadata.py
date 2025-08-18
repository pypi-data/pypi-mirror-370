import os
import stat
import tempfile
import exiftool


class MetadataExtractor:
    def __init__(self):
        pass

    def get_metadata(self, response=None, path_to_local_file=None) -> dict:
        exif_executable = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "utils", "ExifTool", "exiftool"))
        try:
            self.is_exiftool_executable()
        except PermissionError as e:
            self.ptjsonlib.end_error(str(e), self.use_json)
            return

        if response is not None:
            tmp = tempfile.NamedTemporaryFile()
            with open(tmp.name, 'wb') as f:
                f.write(response.content)
            with exiftool.ExifTool(executable=exif_executable) as exif_tool:
                result_dict = exif_tool.execute_json(tmp.name)[0]

        elif path_to_local_file:
            with exiftool.ExifTool(executable=exif_executable) as exif_tool:
                result_dict = exif_tool.execute_json(path_to_local_file)[0]

        blacklisted_keys = ["SourceFile", "ExifTool:ExifToolVersion", "File:FileName", "File:Directory", "File:FileSize", "File:FileModifyDate", "File:FileInodeChangeDate", "File:FilePermissions", "File:FileAccessDate", "File:FileType", "File:FileTypeExtension", "File:MIMEType"]
        result_dict = {k: v for k, v in result_dict.items() if k not in blacklisted_keys and v}

        return result_dict

    def is_exiftool_executable(self) -> bool:
        """Check whether exiftool is exif_executable if not truthy raises an PermissionError"""
        exif_executable = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "utils", "ExifTool", "exiftool"))
        is_executable = os.access(exif_executable, os.X_OK)
        if not is_executable:
            try:
                os.chmod(exif_executable, os.stat(exif_executable).st_mode | stat.S_IEXEC)
                return True
            except:
                raise PermissionError(f"Cannot set execution privileges for exiftool. Please execute the following command: 'sudo chmod +x {exif_executable}'")