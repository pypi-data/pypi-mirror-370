# coding: utf-8


import random
import os
import zipfile
from pathlib import Path

from ksupk import gen_random_string, mkdir_with_p, rm_folder_content

from KanvasObjectKlick.assets import (get_html_mode_a_part_one, get_html_mode_a_part_two,
                                      get_html_mode_b_part_one, get_html_mode_b_part_two,
                                      create_black_image)
from KanvasObjectKlick.common import KOKEntity


def build_a(KOKEntitys: list[KOKEntity], out_file_path: os.PathLike | str | None = None, zip_need: bool = False) -> tuple[str, str | None]:
    """
    build html text.
    if out_file_path == None, then html file will not saved.
    Returns tuple of 1) html text and 2) saved path

    :param KOKEntitys: list of KOKEntity
    :param out_file_path: path to save html text without extension
    :param zip_need: if True, then output file fill be zip-archive
    :return: 1 - html text, 2 - saved path or None
    """
    to_join = []
    for i in range(len(KOKEntitys)):
        KOKEntity_i_str = KOKEntitys[i].get_dict_str()
        if i != len(KOKEntitys)-1:
            KOKEntity_i_str += ",\n"
        to_join.append(KOKEntity_i_str)
    res = "[\n" + "".join(to_join) + "]"
    res = get_html_mode_a_part_one() + res + get_html_mode_a_part_two()
    if out_file_path is None:
        return res, None
    else:
        if not zip_need:
            out_path = str(out_file_path) + ".html"
            with open(out_path, "w", encoding="utf-8") as fd:
                fd.write(res)
                fd.flush()
            return res, out_path
        else:
            out_path = str(out_file_path) + ".zip"
            with zipfile.ZipFile(out_path, 'w') as zipf:
                with zipf.open('index.html', 'w') as file:
                    file.write(res.encode('utf-8'))
                    file.flush()
            return res, out_path


def build_b(KOKEntitys: list[KOKEntity], out_file_path: os.PathLike, working_dir: os.PathLike | None = None) -> str:
    """
    Do same as build_a, but not all in one file. It may be usefull if too much KOKEntity objects to visualize.

    :param KOKEntitys:
    :param out_file_path: path to out zip file
    :param working_dir: dir, where build_b will be worked. build_b clean after process end
    :return: return result output zip file name
    """
    out_file_path = Path(out_file_path)
    if working_dir is None:
        buff = out_file_path.parent
    else:
        working_dir = Path(working_dir)
        buff = working_dir
    while True:
        work_dir = buff / f"{out_file_path.name}_{gen_random_string()}"
        if not work_dir.exists():
            break
    work_dir.mkdir(parents=True, exist_ok=True)

    # to_join = []
    # for i in range(len(KOKEntitys)):
    #     KOKEntity_i_str = KOKEntitys[i].get_dict_str(path_to_work_dir_if_mode_b=Path(work_dir))
    #     if i != len(KOKEntitys)-1:
    #         KOKEntity_i_str += ",\n"
    #     to_join.append(KOKEntity_i_str)
    # res = "[\n" + "".join(to_join) + "]"
    # res = get_html_mode_b_part_one() + res + get_html_mode_b_part_two()

    res_path = os.path.join(work_dir, "index.html")
    with open(res_path, "w", encoding="utf-8") as fd:
        fd.write(get_html_mode_b_part_one())
        fd.write("[\n")
        for i in range(len(KOKEntitys)):
            KOKEntity_i_str = KOKEntitys[i].get_dict_str(path_to_work_dir_if_mode_b=Path(work_dir))
            if i != len(KOKEntitys)-1:
                KOKEntity_i_str += ",\n"
            fd.write(KOKEntity_i_str)
        fd.write("]")
        fd.write(get_html_mode_b_part_two())
        fd.flush()

    zip_filename = f"{out_file_path}"

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, dirs, files in os.walk(work_dir):
            zip_dir_name = os.path.basename(work_dir)
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=work_dir)
                zipf.write(file_path, os.path.join(zip_dir_name, arcname))
    rm_folder_content(str(work_dir), root_dir_too=True)

    return zip_filename


def test_it():
    keks = []
    for _ in range(random.randint(3, 50)):
        name_i = gen_random_string()
        coord_i = (random.randint(-1000, 1000)+random.random(), random.randint(-1000, 1000)+random.random())
        color_i = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        img_i = create_black_image()
        kok = KOKEntity(name_i, coord_i, color_i, img_i)
        keks.append(kok)

    build_a(keks, Path("test_a"), zip_need=False)
    build_a(keks, Path("test_a"), zip_need=True)
    build_b(keks, Path("test_b_1.zip"), Path("."))
    build_b(keks, Path("test_b_2.zip"))


if __name__ == "__main__":
    test_it()
