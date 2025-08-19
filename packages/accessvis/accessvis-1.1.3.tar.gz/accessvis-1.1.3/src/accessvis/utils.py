import os
import sys
from contextlib import closing
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter, Retry
from tqdm import tqdm


def is_ipython():
    """
    Detects if running within IPython environment

    Returns
    -------
    boolean
        True if IPython detected
        Does not necessarily indicate running within a browser / notebook context
    """
    try:
        if __IPYTHON__:
            return True
        else:
            return False
    except NameError:
        return False


def is_notebook():
    """
    Detects if running within an interactive IPython notebook environment

    Returns
    -------
    boolean
        True if IPython detected and browser/notebook display capability detected
    """
    if "IPython" not in sys.modules:
        # IPython hasn't been imported, definitely not
        return False
    try:
        from IPython import get_ipython
    except Exception:
        return False
    # check for `kernel` attribute on the IPython instance
    return getattr(get_ipython(), "kernel", None) is not None


class pushd:
    """
    A working directory class intended for use with contextlib.closing

    >>> from contextlib import closing
    >>> with closing(pushd('./mysubdir')):
    >>>     print(os.getcwd())
    New working directory: ./mysubdir
    /home/user/mysubdir
    Returned to:  /home/user

    Parameters
    ----------
    working_dir: str
        Path of the working directory, will be created if not existing

    """

    previous_dir = None

    def __init__(self, working_dir):
        print("New working directory:", working_dir)
        self.previous_dir = os.getcwd()
        os.makedirs(working_dir, exist_ok=True)
        os.chdir(working_dir)

    def close(self):
        os.chdir(self.previous_dir)
        print("Returned to: ", os.getcwd())


# https://gist.github.com/tobiasraabe/58adee67de619ce621464c1a6511d7d9
def downloader(url: str, filename: str, attempts: int = 5, resume_byte_pos: int = None):
    """Download url with possible resumption.
    Parameters
    ----------
    url: str
        URL to download
    filename: str
        Filename to save as
    attempts: int
        Number of retries
    resume_byte_pos: int
        Position of byte from where to resume the download
    """
    # Use a fake user agent, as some websites disallow python/urllib
    user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
    headers = {
        "User-Agent": user_agent,
    }

    retry_strategy = Retry(
        total=attempts,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    # Get size of file
    r = http.head(url, headers=headers, timeout=5)
    file_size = int(r.headers.get("content-length", 0))

    # Set configuration
    block_size = 1024
    initial_pos = 0
    mode = "wb"
    if resume_byte_pos:
        initial_pos = resume_byte_pos
        mode = "ab"
        # Append information to resume download at specific byte position
        headers["Range"] = f"bytes={resume_byte_pos}-"

    if filename is None:
        filename = url.split("/")[-1]
    file = Path(filename)

    # Establish connection with retry strategy
    r = http.get(url, stream=True, headers=headers)
    if r.status_code != 200:
        raise (requests.HTTPError(f"Download error: {r.status_code} - {url}"))

    with open(filename, mode) as f:
        with tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=file.name,
            initial=initial_pos,
            ascii=True,
            miniters=1,
        ) as pbar:
            for chunk in r.iter_content(32 * block_size):
                f.write(chunk)
                pbar.update(len(chunk))


def download(url, path=None, filename=None, overwrite=False, quiet=False, attempts=5):
    """
    Download a file from an internet URL,
    Attempts to handle transmission errors and resume partial downloads correctly

    Parameters
    ----------
    url : str
        URL to request the file from
    path : str
        Optional directory to save downloaded file, default is current directory
    filename : str
        Filename to save, default is to keep the same name as in url
    overwrite : boolean
        Always overwrite file if it exists, default is to never overwrite
    quiet : bool
        Reduce printed text
    attempts : int
        Number of attempts if exceptions occur, default = 5

    Returns
    -------
    filename : str
        Output local filename
    """
    from urllib.parse import quote, urlparse

    if filename is None:
        filename = url[url.rfind("/") + 1 :]
    file = Path(filename)

    # Encode url path
    o = urlparse(url)
    o = o._replace(path=quote(o.path))
    url = o.geturl()

    def try_download():
        if not overwrite and os.path.exists(filename):
            # Get header and file size
            # r = requests.head(url)
            # Use a fake user agent, as some websites disallow python/urllib
            user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
            r = requests.head(
                url,
                headers={
                    "User-Agent": user_agent,
                },
                timeout=5,
            )

            if r.status_code != 200:
                print(" Download error: ", url, r.status_code)
                return None
            file_size_actual = int(r.headers.get("content-length", 0))
            file_size_local = file.stat().st_size

            if file_size_local != file_size_actual:
                if not quiet:
                    print(
                        f"File {filename} is incomplete. Resume download. {file_size_local} != {file_size_actual}"
                    )
                try:
                    # Try to resume partial
                    downloader(url, filename, attempts, file_size_local)
                except requests.HTTPError:
                    # Try the full download again
                    downloader(url, filename, attempts)
            else:
                if not quiet:
                    print(f"File {filename} is complete. Skip download.")
                return filename
        else:
            if not quiet:
                print(f"File {filename} not found or overwrite set. Downloading.")
            downloader(url, filename, attempts)

        return filename

    if path is not None:
        with closing(pushd(path)):
            return try_download()
    else:
        return try_download()
