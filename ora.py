#! /usr/bin/env python3

import json
from pprint import pprint
from datetime import datetime

import click


@click.group()
def cli():
    pass


@click.command()
@click.option('-u', '--user', help='user''s name')
@click.option('-r', '--retailer', help='retailer''s name')
@click.option('-d', '--date', 'search_date_str', help='receipt date (selling date)')
@click.option('-e', '--email', help='seller''s email address')
@click.option('-i', '--inn', help='seller''s INN')
@click.argument('source', type=click.File('rt', encoding='utf8'))
def search(user, retailer, search_date_str, email, inn, source):
    def get_date(d):
        return datetime.fromisoformat(d).date()

    for receipt_data in json.load(source):
        ticket = receipt_data['ticket']
        document = ticket['document']
        receipt = document.get('receipt', None)

        if not receipt:
            continue

        if user and user.upper() in receipt.get('user', '').upper() \
                or retailer and retailer.upper() in receipt.get('retailPlace', '').upper() \
                or search_date_str and get_date(search_date_str) == get_date(receipt['dateTime']) \
                or email and email.upper() in receipt.get('sellerAddress', '').upper() \
                or inn and inn in receipt.get('userInn', ''):
            pprint(receipt)


@click.command()
@click.argument('source', type=click.File('rt', encoding='utf8'))
def stat(source):
    def update_statistic(statistic, data, r, i):
        for key, value in data.items():
            if not value:
                continue

            if isinstance(value, list):
                simple_type = True
                for item in value:
                    if isinstance(item, dict):
                        if isinstance(statistic.setdefault(key, [dict()]), dict):
                            statistic[key] = [statistic]
                        simple_type = False
                        update_statistic(statistic[key][0], item, r, i)
                if simple_type and value:
                    if isinstance(statistic, list):
                        statistic[0][key] = statistic[0].get(key, 0) + 1
                    else:
                        statistic[key] = statistic.get(key, 0) + 1
            elif isinstance(value, dict):
                update_statistic(statistic.setdefault(key, dict()), value, r, i)
            else:
                if isinstance(statistic, list):
                    statistic = statistic[0]

                statistic[key] = statistic.get(key, 0) + 1

    info = {}
    total_items = 0
    for receipt_data in json.load(source):
        update_statistic(info, receipt_data, receipt_data, info)
        total_items += 1

    pprint(info)
    print(f'total receipts: {total_items}')


cli.add_command(search)
cli.add_command(stat)

if __name__ == '__main__':
    cli()
