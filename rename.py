import csv
import os
import os.path
import logging
import logging.config

from distutils.dir_util import copy_tree

import settings

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename=settings.LOG_FILE, filemode='w')
copy_file_count = 0

#Функция расчета кол-ва файлов
def count_files(in_directory):
    file_count = 0
    for root, dirs, files in os.walk(in_directory, topdown = False):
        file_count += len(files)
    return file_count


#Формируем список папок из существующей папки с офцилограммами
list_folders = [folders[1] for folders in os.walk(settings.SOURCE_FOLDER)][0]


#Формироуем список папок из файла совмещения
with open(settings.COMPARISON_FILE,'r', encoding='cp1251') as file_obj:
    lines_compresion_file = csv.DictReader(file_obj, delimiter=';')
    list_compresion_folders = [line['Обозначение'] for line in lines_compresion_file]


#Сравниваем два списка на разность
if list_folders != list_compresion_folders:
    difference_list = list(set(list_compresion_folders) ^ set(list_folders))
    logging.info('Обнаружена разность в количестве папок: ' + ', '.join(difference_list))


#Обрабатываем только лист пересечений
intersection_list = list(set(list_compresion_folders) & set(list_folders))
logging.info(f'Будет обработан папок: {len(intersection_list)}. Cписок: {", ".join(intersection_list)}')


#Копируем файлы 
with open(settings.COMPARISON_FILE,'r', encoding='cp1251') as file_obj:
    lines_compresion_file = csv.DictReader(file_obj, delimiter=';')
    for line in lines_compresion_file:
        if line["Обозначение"] in list_folders:
            dst_new_folder  = settings.DESTINATION_FOLDER + (f'{line["ПС"]}_{line["Напр"]}_{line["Присоединение"]}_{line["Терминал"]}').replace(" ","_")
            dst_old_folder = settings.SOURCE_FOLDER + line["Обозначение"]
            try:
                copy_tree(dst_old_folder, dst_new_folder, verbose=True)
                copy_file_count += 1
            except Exception as copy_error:
                logging.error(f'Ошибка при копировании папки {line["Обозначение"]}: {copy_error}')


logging.info(f'Скопировано папок: {copy_file_count}')
logging.info(f'Файлов в исходной директории: {count_files(settings.SOURCE_FOLDER)}')
logging.info(f'Файлов в назначенной директории : {count_files(settings.DESTINATION_FOLDER)}')

