import os
import tempfile
from pathlib import Path
import chardet


def detect_and_fix_encoding(path: str, file_name: str, target_encoding='utf-8'):
    """
    Detect and convert file encoding to target encoding, replacing the original file.
    :param path:
    :param file_name:
    :param target_encoding:
    :return: bool: True if successful, False otherwise
    """

    path = Path(path)
    file_path = path / file_name
    if not file_path.exists():
        print(f"✗ File {file_path} does not exist.")
        return False

    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            encoding_info = chardet.detect(raw_data)
            detected_encoding = encoding_info['encoding']

        if not detected_encoding:
            print(f"✗ Unable to detect encoding for file {file_path}")
            return False

        accepted_encodings = ['utf-8', 'utf-8-sig']
        if detected_encoding.lower() in accepted_encodings:
            print(f"✓ Encoding for file {file_name} is already {detected_encoding}")
            return True

        print(f"Converting {file_name} from {detected_encoding} to {target_encoding}...")

        with open(file_path, 'r', encoding=detected_encoding) as f:
            content = f.read()

        with tempfile.NamedTemporaryFile(mode='w', encoding=target_encoding,
                                         dir=path, delete=False) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        temp_path.replace(file_path)

        print(f"✓ Converted {file_name} from {detected_encoding} to {target_encoding}")
        return True

    except (UnicodeDecodeError, UnicodeEncodeError) as e:
        print(f"✗ Error converting {file_name} to {target_encoding}: {e}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            temp_path.unlink()
        return False

    except Exception as e:
        print(f"✗ Error processing {file_name}: {e}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            temp_path.unlink()
        return False