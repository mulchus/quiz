import os
import argparse

from environs import Env


def main():
    award_parser = argparse.ArgumentParser(description='Приложение "Викторина"')
    award_parser.add_argument(
        'path',
        nargs='?',
        default=os.path.join(os.getcwd(), 'awards.xlsx'),
        help='директория с файлом awards.xlsx или awards_for_protocol.xlsx '
             '(по умолчанию - ПУТЬ_К_ПАПКЕ_СО_СКРИПТОМ/awards.xlsx)'
    )
    award_parser.add_argument(
        'task_id',
        nargs='?',
        default=1,
        help='Тип задачи: \n'
             '1 - Создание Почетных граммот и Благодарностей\n'
             '2 - Создание выписок из протоколов\n'
    )

    awards = {}
    path = award_parser.parse_args().path
    try:
        awards = get_awards_from_file(path)
    except (FileNotFoundError, ValueError) as error:
        print(f'Неверно указан путь к файлу.\nОшибка: {error}')
        print(f'Поиск в файле setup.txt в корневой папке.\n')
        environs = Env()
        try:
            environs.read_env("setup.txt", recurse=False)
            path = environs.str('PATH_TO_AWARDS_FILE')
            awards = get_awards_from_file(path)
        except (FileNotFoundError, ValueError) as error:
            exit(f'setup.txt в корневой папке не найден или в нем не указан путь к файлу награждений.\n'
                 f'Ошибка: {error}')

    print(f'Скрипт запущен с файлом данных {path}')



    with open("myfile.txt", "r", encoding="ваша кодировка") as my_file:


if __name__=='__main__':
    main()