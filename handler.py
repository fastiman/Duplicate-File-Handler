import hashlib
import os
import argparse


def argparse_init():
    parser = argparse.ArgumentParser()
    parser.add_argument("root_name", type=str, nargs='?', help="Enter directory", default=False)
    args = parser.parse_args()
    if not args.root_name:  # TODO add check for dir exists
        print("Directory is not specified")
        exit(1)
    return args.root_name


def set_search_options() -> "file_format: str, size_sorting: bool":
    file_ext = input("Enter file format:\n")
    if not file_ext:
        file_ext = 'all'

    print("Size sorting options:\n1. Descending\n2. Ascending\n")
    sorting = input("Enter a sorting option:\n")
    while sorting not in ["1", "2"]:
        print("Wrong option\n")
        print("Size sorting options:\n1. Descending\n2. Ascending\n")
        sorting = input("Enter a sorting option:\n")
    sorting = True if sorting == "1" else False

    return file_ext, sorting


def ask_for_dbl_check() -> bool:
    dbl_check = input("Check for duplicates?\n")
    if dbl_check.lower() == 'yes':
        return True
    elif dbl_check.lower() == 'no':
        return False
    else:
        print("Wrong option")
        return ask_for_dbl_check()


def check_for_dbl(files_dict: dict, sorting: bool) -> "dict files_hashed":
    files_hashed = {}
    # get the hash of files of the same size
    for size, files in sorted(files_dict.items(), reverse=sorting):
        for file in files:
            with open(file, 'rb') as f:
                hsh = hashlib.md5()
                hsh.update(f.read())
            hsh_result = hsh.hexdigest()
            sh_key = (size, hsh_result)
            if sh_key not in files_hashed:
                files_hashed[sh_key] = [file]
            else:
                files_hashed[sh_key].append(file)

    # print("DEBUG", files_hashed)
    return files_hashed


def num_and_print_hsh_list(files_hashed) -> dict:
    # group the files of the same hash
    # assign numbers to these files
    # Assign numbers to lines with files
    # Print the information about the duplicate files along with their hashes
    size = ""
    hsh_line = 1
    files_in_print = {}
    for sh_key, files in files_hashed.items():
        if len(files) == 1:
            continue
        size_key = sh_key[0]
        if size_key != size:
            size = size_key
            print(size, "bytes")
        hsh = sh_key[1]
        print("Hash:", hsh)
        for file in files:
            print(f"{hsh_line}. {file}")
            files_in_print[hsh_line, size] = file
            hsh_line += 1
    return files_in_print


def ask_for_delete() -> bool:
    delete = input("Delete files?\n")
    if delete.lower() == "yes":
        return True
    elif delete.lower() == "no":
        return False
    else:
        print("Wrong format")
        return ask_for_delete()


def ask_numbers_to_delete(files_in_list) -> list:
    available = [str(num) for num, _ in files_in_list]
    while True:
        numbers = input("Enter file numbers to delete:\n").split()
        some_error = False
        if not numbers:
            print("Wrong format")
            continue
        # возможно нужна проверка на двойной пробел
        for num in numbers:
            if num not in available:
                print("Wrong format")
                some_error = True
        if some_error:
            continue
        break
    return numbers


def delete_dbl_files(list_to_delete, files_to_delete):
    # print(files_to_delete)
    size_deleted_files = 0
    for num_size_key, file in files_to_delete.items():
        if str(num_size_key[0]) in list_to_delete:
            # print(num_size_key[1], file)
            os.remove(file)
            size_deleted_files += num_size_key[1]
    print(f"Total freed up space: {size_deleted_files} bytes")


def main(root_name, file_ext, sorting):
    files_dict = {}
    # read files from root_name to files_dict filtered by ext
    for root, dirs, files in os.walk(root_name):
        for file in files:
            if file_ext == 'all' or file.endswith(file_ext):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                if file_size not in files_dict:
                    files_dict[file_size] = [file_path]
                else:
                    files_dict[file_size].append(file_path)

    # print grouped files by size from files_dict
    for size, file_list in sorted(files_dict.items(), reverse=sorting):
        print(size, "bytes")
        if isinstance(files_dict[size], list):  # возможно нужно выводить все файлы
            for file in file_list:
                print(file)

    if ask_for_dbl_check():
        files_in_list = num_and_print_hsh_list(check_for_dbl(files_dict, sorting))
        # возможно нужно сообщить если не нашлись дубли
        if ask_for_delete():
            delete_dbl_files(ask_numbers_to_delete(files_in_list), files_in_list)


if __name__ == '__main__':
    root_path = argparse_init()
    file_format, size_sorting = set_search_options()
    main(root_path, file_format, size_sorting)
