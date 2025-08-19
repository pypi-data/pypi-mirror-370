import os
import zipfile
from shutil import make_archive as shutil_make_archive
from shutil import unpack_archive as shutil_unpack_archive

from colorful_terminal import TermAct


def printProgressBar(
    iteration,
    total,
    prefix="",
    suffix="",
    decimals=1,
    length=100,
    fill="█",
    printEnd="\r",
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def make_zip_archive_with_shutil(output_filename: str, dir_name: str):
    shutil_make_archive(output_filename, "zip", dir_name)


def unpack_zip_archive_with_shutil(filename: str, extract_dir: str):
    shutil_unpack_archive(filename, extract_dir, "zip")


def zip_dir_with_zipfile(folderpath: str, zip_path: str):
    """zip a complete directory, with progress reporting

    Args:
        folderpath (str): path to folder to zip
        zip_path (str): path for zip file with name
    """
    TermAct.hide_cursor_action()

    def zipdir(path, ziph):
        # ziph is zipfile handle
        allfiles = []
        for root, dirs, files in os.walk(path):
            allfiles += files
        len_files = len(allfiles)
        printProgressBar(
            0,
            len_files,
            prefix="Progress of zip file creation:",
            suffix="Complete",
            length=50,
        )
        index = 0
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(
                    os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file), os.path.join(path, "..")),
                )
                printProgressBar(
                    index + 1,
                    len_files,
                    prefix="Progress of zip file creation:",
                    suffix="Complete",
                    length=50,
                )
                index += 1

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipdir(folderpath, zipf)
    zipf.close()
    TermAct.show_cursor_action()


def unzip_with_zipfile(extract_dir: str, zip_path: str):
    """Extract a zipfile

    Args:
        extract_dir (str): root directory for the content
        zip_path (_type_): path to zip file
    """
    zfile = zipfile.ZipFile(zip_path)
    zfile.extractall(extract_dir)
    zfile.close()
