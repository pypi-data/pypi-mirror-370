import os
import shutil
from string import ascii_uppercase

from var_print import varp
import win32api
from clipboard import paste
from colorful_terminal import *
from .rounding import round_relative_to_decimal, round_significantly_std_notation
from .percentage import get_percentage_as_fitted_string


def delete_empty_directories(
    directory: str, full_tree: bool = False, reverb: bool = False
):
    """Delete empty directories

    Args:
        directory (str): mother directory to search in
        full_tree (bool, optional): if True all subdirectories will be effected. Defaults to False.
        reverb (bool, optional): print which paths were removed. Defaults to False.

    Returns:
        list[str]: removed directory paths
    """
    removed = []
    if full_tree:
        for root, dirs, files in os.walk(directory, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    if reverb:
                        colored_print(f"Deleted empty directory: {Fore.YELLOW}{dir_path}")
                    removed.append(dir_path)
    else:
        for f in os.listdir(directory):
            fp = os.path.join(directory, f)
            if os.path.isdir(fp):
                if os.listdir(fp) == []:
                    os.rmdir(fp)
                    if reverb:
                        colored_print(f"Deleted empty directory: {Fore.YELLOW}{fp}")
                    removed.append(fp)
    return removed


def get_disc_informations(print_out: bool = True):
    """Get the information about your discs.

    Args:
        print_out (bool, optional): If True the string will be printed. Defaults to True.

    Returns:
        str: string with the information
    """
    first = True
    out = ""
    for c in ascii_uppercase:
        try:
            (
                name,
                seriennummer,
                maxfilenamelenght,
                sysflags,
                filesystemname,
            ) = win32api.GetVolumeInformation(f"{c}:\\")
            # total, used, free = shutil.disk_usage("/")
            total, used, free = shutil.disk_usage(f"{c}:\\")
            total, used, free = (
                round(total / 10**9, 2),
                round(used / 10**9, 2),
                round(free / 10**9, 2),
            )
            if not first:
                out += "\n"
            out += f"Hard disk information for {c}:\n"
            out += f"\t\tName:                " + name + "\n"
            out += f"\t\Serial number:        " + seriennummer + "\n"
            out += f"\t\tmax filename lenght: " + maxfilenamelenght + "\n"
            out += f"\t\tsys flags:           " + sysflags + "\n"
            out += f"\t\tfilesystem name:     " + filesystemname + "\n"
            out += f"\tMemory:\n"
            out += f"\t\tTotal:" + total, "GB\n"
            out += f"\t\tUsed: " + used, "GB\n"
            out += f"\t\tFree: " + free, "GB\n"
            first = False
        except:
            pass
    if print_out:
        print(out)
    return out


def move_file(
    filepath: str,
    targetpath: str,
    use_shutil_move: bool = True,
    copy_function: callable = shutil.copyfile,
    new_name: str = None,
    skip_if_exists: bool = False,
    add_missing_extension: bool = True,
    overwrite_existing: bool = False,
):
    """Move the file into the target directory. Renames the file by adding ' (counter)' just before the file extension if the filename allready exists.

    Args:
        filepath (str): File to move.
        targetpath (str): Target directory.
        use_shutil_move (bool): since shutil.move gave me trouble ... -> will use copy_function and os.remove
        copy_function (callable): used in shutil.moved or separately with os.remove
        new_name (str): Set the new filename with extension
        skip_if_exists (str): If the file already exists then None will be returned.
        add_missing_extension (bool): If your new_name doesn't contain a "." It will add the extension of the original file. Defaults to True.
    """
    if os.path.isfile(os.path.join(targetpath, os.path.basename(filepath))) and skip_if_exists:
        return
    if not os.path.isdir(targetpath):
        os.makedirs(targetpath)
    filename = os.path.basename(filepath)
    fn, fe = os.path.splitext(filename)
    fp = os.path.join(targetpath, filename)
    if overwrite_existing and os.path.isfile(fp):
        delete_path(fp)
    content = os.listdir(targetpath)
    if new_name:
        if add_missing_extension and "." not in new_name:
            new_name += fe
        filename = new_name
    else:
        counter = 2
        while filename in content:
            filename = fn + f" {counter}" + fe
            counter += 1
    nfp = os.path.join(targetpath, filename)
    if use_shutil_move:
        shutil.move(filepath, nfp, shutil.copyfile)
    else:
        copy_function(filepath, nfp)
        os.remove(filepath)
    return nfp


def copy_file(
    filepath: str,
    targetpath: str,
    copy_function: callable = shutil.copyfile,
    new_name: str = None,
    skip_if_exists: bool = False,
    add_missing_extension: bool = True,
    overwrite_existing: bool = False,
):
    """Copy the file into the target directory. Renames the file by adding ' (counter)' just before the file extension if the filename allready exists.

    Args:
        filepath (str): File to move.
        targetpath (str): Target directory.
        copy_function (callable): shutil copy function
        new_name (str): Set the new filename with extension
        skip_if_exists (str): If the file already exists then None will be returned.
        add_missing_extension (bool): If your new_name doesn't contain a "." It will add the extension of the original file. Defaults to True.
    """
    if os.path.isfile(os.path.join(targetpath, os.path.basename(filepath))) and skip_if_exists:
        return
    if not os.path.isdir(targetpath):
        os.makedirs(targetpath)
    filename = os.path.basename(filepath)
    fn, fe = os.path.splitext(filename)
    fp = os.path.join(targetpath, filename)
    if overwrite_existing and os.path.isfile(fp):
        delete_path(fp)
    content = os.listdir(targetpath)
    if new_name:
        if add_missing_extension and "." not in new_name:
            new_name += fe
        filename = new_name
    else:
        counter = 2
        while filename in content:
            filename = fn + f" {counter}" + fe
            counter += 1
    nfp = os.path.join(targetpath, filename)
    copy_function(filepath, nfp)
    return nfp


def move_and_integrate_directory(
    dirpath: str,
    targetpath: str,
):
    """Move the content of the directory (dirpath) to the target path. Removes the dirpath if empty.

    Args:
        dirpath (str): source
        targetpath (str): target / destination

    Returns
        list[str]: paths that couldn't be moved
    """
    folderpath = os.path.normpath(dirpath)
    fails = []

    def try_move(fp: str):
        rel_path = os.path.relpath(fp, folderpath)
        structure = rel_path.split("\\")
        try:
            if not os.path.isdir(fp):
                npdp = os.path.join(targetpath, *structure[: len(structure) - 1])
                if not os.path.isdir(npdp):
                    os.makedirs(npdp)
            shutil.move(fp, targetpath)
        except:
            if os.path.isdir(fp):
                for n in os.listdir(fp):
                    try_move(os.path.join(fp, n))
            else:
                fails.append(fp)

    for f in os.listdir(folderpath):
        fp = os.path.join(folderpath, f)
        try_move(fp)
    try:
        os.rmdir(folderpath)
    except:
        pass
    return fails


def copy_and_integrate_directory(
    dirpath: str,
    targetpath: str,
):
    """Copy the content of the directory (dirpath) to the target path.
    Retains the original files and directories at dirpath.

    Args:
        dirpath (str): source
        targetpath (str): target / destination

    Returns:
        list[str]: paths that couldn't be copied
    """
    folderpath = os.path.normpath(dirpath)
    fails = []

    def try_copy(fp: str):
        rel_path = os.path.relpath(fp, folderpath)
        structure = rel_path.split("\\")
        try:
            if not os.path.isdir(fp):
                npdp = os.path.join(targetpath, *structure[: len(structure) - 1])
                if not os.path.isdir(npdp):
                    os.makedirs(npdp)
            shutil.copy2(fp, os.path.join(targetpath, rel_path))
        except:
            if os.path.isdir(fp):
                for n in os.listdir(fp):
                    try_copy(os.path.join(fp, n))
            else:
                fails.append(fp)

    for f in os.listdir(folderpath):
        fp = os.path.join(folderpath, f)
        try_copy(fp)

    return fails


def get_all_subdir_sizes(
    dirpath: str,
    unit: str = "GB",
    round_to: int = 2,
    sort_for_size: bool = False,
    print_it: bool = False,
    percentages: bool = True,
    with_sum: bool = True,
    as_string: bool = True,
):
    """Get a dictionary of the sizes of all the contents of the given directory.

    Args:
        dirpath (str): Directory to get the sizes of
        unit (str, optional): Size unit. Defaults to "GB".
        round_to (int, optional): Round size to. Defaults to 2.
        sort_for_size (bool, optional): Sort the dictionary for size (ascending). Defaults to False.
        print_it (bool, optional): Immediately print the dictionary using varp form var_print. Defaults to False.
        percentages (bool, optional): Adds the percentage to the size string. Defaults to True.
        with_sum (bool, optional): Adds the sum to the dictionary. Defaults to True.

    Raises:
        ValueError: if unit is not B / MB or GB or a number representing the size like 10**9 for GB

    Returns:
        dict[str, str]: Dictionary with the file names (keys) and the size as a string with the unit (possibly with the percentage)
    """
    if print_it:
        varp(maindir)
    if unit == "B":
        u = 1
    elif unit == "MB":
        u = 10**6
    elif unit == "GB":
        u = 10**9
    else:
        raise ValueError("unit not recognized")
    mp = maindir
    summe = 0
    max_nachkomma = 0
    subdir_to_size = {}
    with ProgressBar(len(os.listdir(mp)), "Getting directory sizes: ") as prg:
        for d in os.listdir(mp):
            try:
                dp = os.path.join(mp, d)
                size = get_file_size(dp) / u
                if size / 100 > 1:
                    add_space = 0 * " "
                elif 1 > size / 100 > 0.1:
                    add_space = 1 * " "
                else:
                    add_space = 2 * " "
                summe += size
                size = std_notation(size, round_to).strip(".")
                value = f"{add_space}{size} {unit}"
                subdir_to_size[d] = value
                nachkomma = len(value.split(".")[-1])
                if nachkomma > max_nachkomma:
                    max_nachkomma = nachkomma
            except:
                pass
            prg.update()
    if sort_for_size:
        subdir_to_size = {
            k: v for (k, v) in sorted(subdir_to_size.items(), key=lambda item: item[1])
        }

    if summe / 100 > 1:
        add_space = 0 * " "
    elif 1 > summe / 100 > 0.1:
        add_space = 1 * " "
    else:
        add_space = 2 * " "
    size = std_notation(summe, round_to).strip(".")
    subdir_to_size["<Summe>"] = f"{add_space}{size} {unit}"

    if percentages:
        subdir_to_size_perc = {}
        for sd, size in subdir_to_size.items():
            if sd != "<Summe>":
                perc = get_percentage_as_fitted_string(
                    float(size.strip(" " + unit)), summe, 2
                )
                nachkomma = len(size.split(".")[-1])
                if nachkomma == len(size):
                    nachkomma = len(unit)
                spc = max_nachkomma - nachkomma + 4
                subdir_to_size_perc[sd] = size + " " * spc + perc
            else:
                subdir_to_size_perc[sd] = size
    if print_it:
        try:
            varp(subdir_to_size_perc)
        except:
            varp(subdir_to_size)
    return subdir_to_size


def get_directory_size(
    start_path=".", unit: str = None, round_to: int = 2, round_to_precision: bool = True, as_string: bool = True
):
    "unit can be none -> float or B / MB / GB -> str"
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    if round_to_precision:
        rounding = round_significantly_std_notation
    else:
        rounding = round
    if unit == None:
        total_size = total_size
    elif unit == "B":
        total_size = rounding(total_size / 1, round_to)
        if as_string:
            total_size = f"{total_size} {unit}"
    elif unit == "MB":
        total_size = rounding(total_size / 10**6, round_to)
        if as_string:
            total_size = f"{total_size} {unit}"
    elif unit == "GB":
        total_size = rounding(total_size / 10**9, round_to)
        if as_string:
            total_size = f"{total_size} {unit}"
    else:
        raise ValueError("unit not recognized")

    return total_size


def get_file_size(
    file_path: str, unit: str = None, round_to: int = 2, round_to_precision: bool = True, as_string: bool = True
):
    "unit can be none -> float or B / MB / GB -> str"
    total_size = os.path.getsize(file_path)
    if round_to_precision:
        rounding = round_significantly_std_notation
    else:
        rounding = round
    if unit == None:
        total_size = total_size
    elif unit == "B":
        total_size = rounding(total_size / 1, round_to)
        if as_string:
            total_size = f"{total_size} {unit}"
    elif unit == "MB":
        total_size = rounding(total_size / 10**6, round_to)
        if as_string:
            total_size = f"{total_size} {unit}"
    elif unit == "GB":
        total_size = rounding(total_size / 10**9, round_to)
        if as_string:
            total_size = f"{total_size} {unit}"
    else:
        raise ValueError("unit not recognized")

    return total_size


def copied_paths_to_list():
    "path copied in Windows to a list"
    urls = paste().replace("\r", "").split("\n")
    urls = [u.strip('"') for u in urls]
    return urls


def copy_with_metadata(
    src_path, dest_path, integrate_files=True, skip_existing=True, rename_existing=True
):
    # Check if the source path exists
    if not os.path.exists(src_path):
        print(f"Source path '{src_path}' does not exist.")
        return

    # Check if the source path is a file or directory
    if os.path.isfile(src_path):
        # Check if the file already exists in the destination
        if skip_existing and os.path.exists(dest_path):
            print(f"File '{src_path}' already exists in '{dest_path}'. Skipping.")
        elif rename_existing and os.path.exists(dest_path):
            base, ext = os.path.splitext(os.path.basename(dest_path))
            i = 1
            while os.path.exists(dest_path):
                new_filename = f"{base} ({i}){ext}"
                dest_path = os.path.join(os.path.dirname(dest_path), new_filename)
                i += 1
            print(
                f"File '{src_path}' already exists in '{dest_path}'. Renaming to '{os.path.basename(dest_path)}'."
            )
            shutil.copy2(src_path, dest_path)
        else:
            # Copy the file with metadata
            shutil.copy2(src_path, dest_path)
    elif os.path.isdir(src_path):
        # Check if the destination directory exists
        if os.path.exists(dest_path):
            if integrate_files:
                # Integrate files if the destination directory exists
                for item in os.listdir(src_path):
                    s = os.path.join(src_path, item)
                    d = os.path.join(dest_path, item)
                    if os.path.isdir(s):
                        # Recursively copy subdirectories
                        copy_with_metadata(
                            s, d, integrate_files, skip_existing, rename_existing
                        )
                    else:
                        # Check if the file already exists in the destination
                        if skip_existing and os.path.exists(d):
                            print(f"File '{s}' already exists in '{d}'. Skipping.")
                        elif rename_existing and os.path.exists(d):
                            base, ext = os.path.splitext(item)
                            i = 1
                            while os.path.exists(d):
                                new_filename = f"{base} ({i}){ext}"
                                d = os.path.join(dest_path, new_filename)
                                i += 1
                            print(
                                f"File '{s}' already exists in '{d}'. Renaming to '{os.path.basename(d)}'."
                            )
                            shutil.copy2(s, d)
                        else:
                            # Copy individual files with metadata
                            shutil.copy2(s, d)
            else:
                print(
                    f"Destination directory '{dest_path}' already exists. Use integrate_files=True to integrate files."
                )
        else:
            # Copy the directory with metadata
            shutil.copytree(src_path, dest_path, copy_function=shutil.copy2)
    else:
        print(f"Source path '{src_path}' is neither a file nor a directory.")


def copy_without_metadata(
    src_path, dest_path, integrate_files=True, skip_existing=True, rename_existing=True
):
    # Check if the source path exists
    if not os.path.exists(src_path):
        print(f"Source path '{src_path}' does not exist.")
        return

    # Check if the source path is a file or directory
    if os.path.isfile(src_path):
        # Check if the file already exists in the destination
        if skip_existing and os.path.exists(dest_path):
            print(f"File '{src_path}' already exists in '{dest_path}'. Skipping.")
        elif rename_existing and os.path.exists(dest_path):
            base, ext = os.path.splitext(os.path.basename(dest_path))
            i = 1
            while os.path.exists(dest_path):
                new_filename = f"{base} ({i}){ext}"
                dest_path = os.path.join(os.path.dirname(dest_path), new_filename)
                i += 1
            print(
                f"File '{src_path}' already exists in '{dest_path}'. Renaming to '{os.path.basename(dest_path)}'."
            )
            shutil.copy(src_path, dest_path)
        else:
            # Copy the file without metadata
            shutil.copy(src_path, dest_path)
    elif os.path.isdir(src_path):
        # Check if the destination directory exists
        if os.path.exists(dest_path):
            if integrate_files:
                # Integrate files if the destination directory exists
                for item in os.listdir(src_path):
                    s = os.path.join(src_path, item)
                    d = os.path.join(dest_path, item)
                    if os.path.isdir(s):
                        # Recursively copy subdirectories
                        copy_without_metadata(
                            s, d, integrate_files, skip_existing, rename_existing
                        )
                    else:
                        # Check if the file already exists in the destination
                        if skip_existing and os.path.exists(d):
                            print(f"File '{s}' already exists in '{d}'. Skipping.")
                        elif rename_existing and os.path.exists(d):
                            base, ext = os.path.splitext(item)
                            i = 1
                            while os.path.exists(d):
                                new_filename = f"{base} ({i}){ext}"
                                d = os.path.join(dest_path, new_filename)
                                i += 1
                            print(
                                f"File '{s}' already exists in '{d}'. Renaming to '{os.path.basename(d)}'."
                            )
                            shutil.copy(s, d)
                        else:
                            # Copy individual files without metadata
                            shutil.copy(s, d)
            else:
                print(
                    f"Destination directory '{dest_path}' already exists. Use integrate_files=True to integrate files."
                )
        else:
            # Copy the directory without metadata
            shutil.copytree(src_path, dest_path)
    else:
        print(f"Source path '{src_path}' is neither a file nor a directory.")


def copy_without_metadata_using_copyfile(
    src_path, dest_path, integrate_files=True, skip_existing=True, rename_existing=True
):
    # Check if the source path exists
    if not os.path.exists(src_path):
        print(f"Source path '{src_path}' does not exist.")
        return

    # Check if the source path is a file or directory
    if os.path.isfile(src_path):
        # Check if the file already exists in the destination
        if skip_existing and os.path.exists(dest_path):
            print(f"File '{src_path}' already exists in '{dest_path}'. Skipping.")
        elif rename_existing and os.path.exists(dest_path):
            base, ext = os.path.splitext(os.path.basename(dest_path))
            i = 1
            while os.path.exists(dest_path):
                new_filename = f"{base} ({i}){ext}"
                dest_path = os.path.join(os.path.dirname(dest_path), new_filename)
                i += 1
            print(
                f"File '{src_path}' already exists in '{dest_path}'. Renaming to '{os.path.basename(dest_path)}'."
            )
            shutil.copyfile(src_path, dest_path)
        else:
            # Copy the file without metadata
            shutil.copyfile(src_path, dest_path)
    elif os.path.isdir(src_path):
        # Check if the destination directory exists
        if os.path.exists(dest_path):
            if integrate_files:
                # Integrate files if the destination directory exists
                for item in os.listdir(src_path):
                    s = os.path.join(src_path, item)
                    d = os.path.join(dest_path, item)
                    if os.path.isdir(s):
                        # Recursively copy subdirectories
                        copy_without_metadata(
                            s, d, integrate_files, skip_existing, rename_existing
                        )
                    else:
                        # Check if the file already exists in the destination
                        if skip_existing and os.path.exists(d):
                            print(f"File '{s}' already exists in '{d}'. Skipping.")
                        elif rename_existing and os.path.exists(d):
                            base, ext = os.path.splitext(item)
                            i = 1
                            while os.path.exists(d):
                                new_filename = f"{base} ({i}){ext}"
                                d = os.path.join(dest_path, new_filename)
                                i += 1
                            print(
                                f"File '{s}' already exists in '{d}'. Renaming to '{os.path.basename(d)}'."
                            )
                            shutil.copyfile(s, d)
                        else:
                            # Copy individual files without metadata
                            shutil.copyfile(s, d)
            else:
                print(
                    f"Destination directory '{dest_path}' already exists. Use integrate_files=True to integrate files."
                )
        else:
            # Copy the directory without metadata
            shutil.copytree(src_path, dest_path, copy_function=shutil.copyfile)
    else:
        print(f"Source path '{src_path}' is neither a file nor a directory.")


def delete_path(path):
    try:
        shutil.rmtree(path)
    except:
        os.remove(path)
