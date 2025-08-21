# -*- qrc_tools.py: python ; coding: utf-8 -*-
import os
import re


def search_files(fn_pattern, folder, sort=True, topdown=False):
    ret = []
    walk_path = folder if folder is not None else '.'
    for (this_dir, subs, files) in os.walk(walk_path, topdown=topdown):
        for fn in files:
            if re.match(fn_pattern, fn):
                ret.append((this_dir, fn))
    return sorted(ret) if sort else ret


def build_images_qrc(qrc_file_name, res_files):
    file_names = {}
    sp = '  '
    nl = '\n'
    with open(qrc_file_name, 'w') as file:
        file.write('<RCC>\n')
        for rc_prefix, files in res_files.items():
            f_names = []
            file.write(f'{sp}<qresource  prefix = "{rc_prefix}">{nl}')
            for f_dir, f_name in search_files(files[1], files[0], topdown=False):
                file.write(fr'{sp}{sp}<file alias="{f_name}">{f_dir}\{f_name}</file>{nl}')
                f_names.append(f_name)
            file.write(f'{sp}</qresource>{nl}')
            file_names[rc_prefix] = f_names
        file.write(f'</RCC>{nl}')
    return file_names


def build_enum(py_file, rc_names: dict):
    texts = []
    with open(py_file, 'w') as file:
        file.write(f'# -*- py_file.py: python ; coding: utf-8 -*-' + '\n')
        # file.write('from enum import Enum\n\n\n')
        # file.write('class PnKey(Enum):\n')
        for rc_prefix, f_names in rc_names.items():
            var_prefix = rc_prefix[1:2].upper()
            for name in f_names:
                v = f"{var_prefix}_{name.split('.')[0].upper()}"
                file.write(fr'{v} = ":{rc_prefix}/{name}"' + '\n')
                texts.append(name)
        file.write('\n')
    return texts


if __name__ == '__main__':
    qrc = build_images_qrc('images.qrc', {'/pic': ('images\\png', r'.*\.png'),
                                          '/icon': ('images\\ico', r'.*\.ico'), })
    print(qrc)
    build_enum('img.py', rc_names=qrc)
