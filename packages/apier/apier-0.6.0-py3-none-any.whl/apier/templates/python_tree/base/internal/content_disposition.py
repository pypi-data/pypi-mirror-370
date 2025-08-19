import re
from urllib.parse import unquote


def parse_content_disposition(header) -> str:
    """
    Parses the Content-Disposition header to extract the filename.

    :param header: The Content-Disposition header string.
    :return:       The extracted filename or an empty string if not found.
    """
    # Regex for filename* (e.g. filename*=UTF-8''file%20name.txt)
    filename_star_re = re.compile(
        r"filename\*\s*=\s*([^\'\";\s]+)\\?\'\\?\'([^\";\s]+)",
        re.IGNORECASE,
    )

    m_star = filename_star_re.search(header)
    if m_star:
        charset = m_star.group(1)
        encoded_filename = m_star.group(2)
        try:
            return unquote(encoded_filename, encoding=charset)
        except Exception:
            return unquote(encoded_filename)

    # Regex for filename (e.g. filename="file.txt" or filename=file.txt)
    filename_re = re.compile(
        r'filename\s*=\s*"([^"]+)"|filename\s*=\s*([^";\s]+)',
        re.IGNORECASE,
    )

    m = filename_re.search(header)
    if m:
        return m.group(1) or m.group(2)

    return ""
