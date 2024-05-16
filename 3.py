#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import click
import json
from datetime import datetime
import jsonschema
from operator import itemgetter

person_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "surname": {"type": "string"},
        "date_of_birth": {"type": "string", "format": "date"},
        "zodiac_sign": {"type": "string"}
    },
    "required": ["name", "surname", "date_of_birth", "zodiac_sign"]
}


def validate_person(person_data, schema):
    try:
        jsonschema.validate(person_data, schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"Данные человека не соответствуют схеме: {e}")
        return False


def add_person(people, name, surname, date_of_birth, zodiac_sign):
    """
    Добавление нового человека в список.
    Список сортируется по знаку зодиака после добавления нового элемента.
    """
    date_of_birth = datetime.strptime(date_of_birth, '%d.%m.%Y')

    person = {
        'name': name,
        'surname': surname,
        'date_of_birth': date_of_birth,
        'zodiac_sign': zodiac_sign
    }

    people.append(person)
    people.sort(key=lambda item: item.get('zodiac_sign', ''))
    return people


def list_people(people):
    """
    Вывод таблицы людей.
    """
    line = '+-{}-+-{}-+-{}-+-{}-+-{}-+'.format(
        '-' * 4,
        '-' * 20,
        '-' * 20,
        '-' * 15,
        '-' * 13
    )
    print(line)
    print(
        '| {:^4} | {:^20} | {:^20} | {:^15} | {:^12} |'.format(
            "№",
            "Имя",
            "Фамилия",
            "Знак Зодиака",
            "Дата рождения"
        )
    )
    print(line)

    for idx, person in enumerate(people, 1):
        birth_date_str = person.get('date_of_birth').strftime('%d.%m.%Y')
        print(
            '| {:^4} | {:<20} | {:<20} | {:<15} | {:<13} |'.format(
                idx,
                person.get('name', ''),
                person.get('surname', ''),
                person.get('zodiac_sign', ''),
                birth_date_str
            )
        )

    print(line)


def select_people(people, month):
    """
    Вывести список людей, родившихся в заданном месяце.
    """
    count = 0
    for person in people:
        if person.get('date_of_birth').month == month:
            count += 1
            print('{:>4}: {} {}'.format(count, person.get(
                'name', ''), person.get('surname', '')))

    if count == 0:
        print("Люди, родившиеся в указанном месяце, не найдены.")


def save_people(file_name, staff):
    """
    Сохранить всех работников в файл JSON.
    """
    file_path = os.path.join('data', file_name)
    staff_formatted = [{**person, 'date_of_birth': person.get(
        'date_of_birth').strftime('%d.%m.%Y')} for person in staff]
    # Открыть файл с заданным именем для записи.
    with open(file_path, "w", encoding="utf-8") as fout:
        # Выполнить сериализацию данных в формат JSON.
        json.dump(staff_formatted, fout, ensure_ascii=False, indent=4)


def load_people(file_name):
    """
    Загрузить всех людей из файла JSON.
    """
    file_path = os.path.join('data', file_name)
    # Открыть файл с заданным именем для чтения.
    with open(file_path, "r", encoding="utf-8") as fin:
        staff_loaded = json.load(fin)
        result_people = []
        cnt = 0
        for person in staff_loaded:
            cnt += 1
            if validate_person(person, person_schema):
                try:
                    person['date_of_birth'] = datetime.strptime(
                        person['date_of_birth'], '%d.%m.%Y')
                    result_people.append(person)
                except:
                    print(
                        f"Ошибка при разборе даты в записи, пропуск записи {cnt}.")
            else:
                print("Неверные данные человека, пропуск записи.")
        return result_people


@click.group()
@click.argument('filename')
@click.pass_context
def cli(ctx, filename):
    """Управление списком людей."""
    ctx.ensure_object(dict)
    ctx.obj['FILENAME'] = filename

@cli.command()
@click.option('-n', '--name', required=True, help="Имя человека")
@click.option('-s', '--surname', required=True, help="Фамилия человека")
@click.option('-d', '--date_of_birth', required=True, help="Дата рождения (формат ДД.ММ.ГГГГ)")
@click.option('-z', '--zodiac_sign', required=True, help="Знак зодиака")
@click.pass_context
def add(ctx, name, surname, date_of_birth, zodiac_sign):
    """Добавить человека."""
    people = load_people(ctx.obj['FILENAME'])
    people = add_person(people, name, surname, date_of_birth, zodiac_sign)
    save_people(ctx.obj['FILENAME'], people)

@cli.command()
@click.pass_context
def list(ctx):
    """Вывести список людей."""
    people = load_people(ctx.obj['FILENAME'])
    list_people(people)

@cli.command()
@click.option('-m', '--month', required=True, type=int, help="Месяц рождения")
@click.pass_context
def select(ctx, month):
    """Выбрать людей по месяцу рождения."""
    people = load_people(ctx.obj['FILENAME'])
    select_people(people, month)

if __name__ == '__main__':
    cli(obj={})