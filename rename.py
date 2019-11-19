import csv
import os
import os.path
from distutils.dir_util import copy_tree

import settings

#Формируем список папок из существующей папки с офцилограммами
list_folders = [folders[1] for folders in os.walk(settings.SOURCE_FOLDER)][0]

#Формироуем список папок из файла совмещения
with open(settings.COMPARISON_FILE,'r', encoding='cp1251') as file_obj:
    lines_compresion_file = csv.DictReader(file_obj, delimiter=';')
    list_compresion_folders = [line['Обозначение'] for line in lines_compresion_file]


#Сравниваем два списка на разность
if list_folders != list_compresion_folders:
    difference_list = list(set(list_compresion_folders) ^ set(list_folders))
    print('Обнаружена разность списков: ' + ', '.join(difference_list))

#Обрабатываем только лист пересечений
intersection_list = list(set(list_compresion_folders) & set(list_folders))
print('Будет обработан список: ' + ', '.join(intersection_list))

#Копируем файлы 
with open(settings.COMPARISON_FILE,'r', encoding='cp1251') as file_obj:
    lines_compresion_file = csv.DictReader(file_obj, delimiter=';')
    for line in lines_compresion_file:
        if line["Обозначение"] in list_folders:
            dst_new_folder  = settings.DESTINATION_FOLDER + (f'{line["ПС"]}_{line["Напр"]}_{line["Присоединение"]}_{line["Терминал"]}').replace(" ","_")
            dst_old_folder = settings.SOURCE_FOLDER + line["Обозначение"]
            copy_tree(dst_old_folder, dst_new_folder, verbose=True)