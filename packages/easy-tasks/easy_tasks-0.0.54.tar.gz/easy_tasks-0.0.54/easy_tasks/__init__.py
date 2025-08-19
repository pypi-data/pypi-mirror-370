from .closest_furthest_value import (
    furthest_value_in_list,
    closest_value_in_list,
    furthest_value_in_dict,
    closest_value_in_dict,
    get_first_from_list,
)
from .dublicates import find_dublicates, remove_dublicates
from .percentage import (
    get_percentage_as_fitted_string,
    progress_printer,
    main_and_sub_progress_printer,
    ProgressBar,
)
from .sorter import sorted_dict
from .string_transformation import (
    upper_case_first_letter_of_word,
    upper_case_first_letter_of_words,
    insert_into_string,
    insert_into_file,
    replace_in_string,
    replace_in_file,
    comment_lines_in_file,
    comment_lines_by_lineno,
    remove_lines_by_lineno,
)
from .unpack import unpack_list
from .list_printer import pretty_print_list, pretty_print_nested_list, get_var_names

from .help_with_pickle import pickle_pack, pickle_unpack
from .help_with_json import dump_as_json, get_from_json

from .zipping import (
    make_zip_archive_with_shutil,
    unpack_zip_archive_with_shutil,
    zip_dir_with_zipfile,
    unzip_with_zipfile,
)

from .rounding import *
from .types import *
from .filesystem import (
    delete_empty_directories,
    get_disc_informations,
    move_file,
    copy_file,
    move_and_integrate_directory,
    copy_and_integrate_directory,
    get_all_subdir_sizes,
    get_directory_size,
    get_file_size,
    copied_paths_to_list,
    copy_with_metadata,
    copy_without_metadata,
    copy_without_metadata_using_copyfile,
    delete_path,
)
from .stoppable_thread import ThreadWithExc, StoppableThread


__version__ = "0.0.54"
