import csv
import logging
import logging.config
import os
import os.path
from shutil import copy2

import settings


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename=settings.LOG_FILE, filemode='w')


#Функция расчета кол-ва файлов
def count_files(in_directory):
    file_count = 0
    for root, dirs, files in os.walk(in_directory, topdown = False):
        file_count += len(files)

    return file_count


def file_defference(source_folder: str, destination_folder: str) -> list:
    #Формируем данные по папке источнику(диск,папка, файл)
    source_folder_data = [folder for folder in os.walk(source_folder)]
    #Формируем данные по папке назначению(диск,папка, файл)
    destination_folder_data = [folder for folder in os.walk(destination_folder)]
    
    #Формируем список ФАЙЛОВ в исходной папке
    source_files_list = [filename for root, dirs, files in source_folder_data for filename in files]
    #Формируем список ФАЙЛОВ в папке назначения
    destination_files_list = [filename for root, dirs, files in destination_folder_data for filename in files]

    #Сравниваем два списка файлов  и если элемент списка разности входит в исходную папку, то добавляем его в список
    difference_files_list = [file_name  for file_name in list(set(source_files_list) ^ set(destination_files_list)) if file_name in source_files_list]
    if len(difference_files_list) != 0:
        logging.info('Обнаружена разность файлов:' + str(difference_files_list) + 'в папке:{}'.format(source_folder))
        
    else:
        logging.info('В папке:{}'.format(source_folder) + ' все файлы совпадают.')
    return difference_files_list

#Формируем список папок из существующей папки с офцилограммами
def list_folders_of_source_folders(folder_path: str) -> list:
    list_folders = [folders[1] for folders in os.walk(folder_path)][0]

    return list_folders


#Формироуем список папок из файла совмещения
def list_folders_of_compresion_file(file_path: str) -> list:
    with open(file_path,'r', encoding='cp1251') as file_obj:
        lines_compresion_file = csv.DictReader(file_obj, delimiter=';')
        list_compresion_folders = [line['Обозначение'] for line in lines_compresion_file]

    return list_compresion_folders


#Сравниваем два списка на разность
def differents_between_file_and_folder(list_folder: list, list_file: list) -> list:
    difference_list = []
    if list_folder != list_file:
        difference_list = list(set(list_folder) ^ set(list_file))
        logging.info('Обнаружена разность в количестве папок между файлом и папкой источником:' + ', '.join(difference_list))
    return difference_list



#Обрабатываем только лист пересечений
def list_of_crossings_file_and_folders(list_folder: list, list_file: list) -> list:
    intersection_list = list(set(list_folder) & set(list_file))
    logging.info('Будет обработано папок: {}. Cписок:'.format(len(intersection_list)) + ', '.join(intersection_list))

    return intersection_list


def copy_file(file_path: str, source_folder: str, destination_folder: str) -> None:
    copy_file_count = 0

    #Запрашиваем список папок в папке назначения
    source_list_folders = list_folders_of_source_folders(source_folder)
    #Запрашиваем список папок в файле сопоставления
    source_list_file = list_folders_of_compresion_file(file_path)
    #Проверяем расхождение между списком папок в файле и списком папок в папке назначения
    differents_between_file_and_folder(source_list_folders, source_list_file)
    #Формируем лист пересечений
    intersection_list = list_of_crossings_file_and_folders(source_list_folders, source_list_file)
    #Считываем файл сопоставления
    with open(file_path,'r', encoding='cp1251') as file_obj:
        lines_compresion_file = csv.DictReader(file_obj, delimiter=';')
        for line in lines_compresion_file:
            #Проверяем, входит ли название папки в файле в список разности
            if line["Обозначение"] in intersection_list:
                #Формируем путь до папки назначения
                dst_new_folder  = (destination_folder + ('{}'.format(line['ПС']))).replace(" ","_")
                #Формируем путь до папки источника
                dst_old_folder = source_folder + line["Обозначение"]
                #Формируем разность ФАЙЛОВ в каталоге назначения и источникап
                files_list = file_defference(dst_old_folder, dst_new_folder)
                #Проверяем, что есть разность файлов
                if len(files_list) != 0:
                    #logging.info('Выявлена разность в файлах: ' + ', '.join(files_list))
                    #Для всех файлов в списоке разности файлов производим копирование
                    for file_c_name in files_list:
                        #Путь куда копируем
                        dst_new_file = dst_new_folder + '/' + file_c_name
                        #Путь к исходному файлу
                        dst_old_file = dst_old_folder + '/' + file_c_name
                        #Проверяем существует ли путь до папки назначения
                        if not os.path.exists(dst_new_folder):
                            os.makedirs(dst_new_folder)
                        #Пытаемся скопировать
                        try:
                            copy2(dst_old_file, dst_new_file)
                            copy_file_count += 1
                        #Если не получается, формируем ошибку
                        except Exception as copy_error:
                            logging.error('Ошибка при копировании папки {}: {}'.format(line['Обозначение'],copy_error))    

    logging.info('Скопировано файлов: {}'.format(copy_file_count))
    logging.info('Файлов в исходной директории:{}'.format(count_files(source_folder)))
    logging.info('Файлов в назначенной директории :{}'.format(count_files(destination_folder)))


if __name__ == "__main__":
    copy_file(settings.COMPARISON_FILE, settings.SOURCE_FOLDER, settings.DESTINATION_FOLDER)
