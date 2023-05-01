import requests
from bs4 import BeautifulSoup
import urllib3
import ssl
import xml.etree.ElementTree as ET
import sqlalchemy as db


class CustomHttpAdapter(requests.adapters.HTTPAdapter):

    def __init__(self, ssl_context=None, **kwargs):
        self.poolmanager = None
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)


def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session


def load_data(url):
    headers = {
        'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')
        xml_links = []
        for link in links:
            href = link.get('href')
            if href is not None and 'xml' in href:
                if href not in xml_links:
                    xml_links.append(href)
        second_response = get_legacy_session().get(xml_links[0], headers=headers)
        if second_response.status_code == 200:
            xml_data = second_response.content
            return xml_data
        else:
            print(f'Ошибка при запросе: {second_response.status_code}')
    else:
        print(f'Ошибка при запросе {url}: {response.status_code}')


def none_handler(find):
    if find is None:
        return ''
    else:
        return find.text


def list_to_string(find):
    empty_list = []
    for value in find:
        empty_list.append(value.text)
    filtered_list = [value for value in empty_list if value is not None]
    return ', '.join(filtered_list)


def parse_xml_individuals(xml_data):
    tree = ET.fromstring(xml_data)
    data = []
    # перебор элементов в файле
    for individual in tree.findall('./INDIVIDUALS/INDIVIDUAL'):
        dataid = individual.find('DATAID').text
        versionnum = individual.find('VERSIONNUM').text
        name_original_script = none_handler(individual.find('NAME_ORIGINAL_SCRIPT'))
        first_name = individual.find('FIRST_NAME').text
        title = list_to_string(individual.findall('.//TITLE/VALUE'))
        second_name = none_handler(individual.find('SECOND_NAME'))
        third_name = none_handler(individual.find('THIRD_NAME'))
        un_list_type = individual.find('UN_LIST_TYPE').text
        reference_number = individual.find('REFERENCE_NUMBER').text
        listed_on = individual.find('LISTED_ON').text
        comments1 = individual.find('COMMENTS1').text
        designation = list_to_string(individual.findall('.//DESIGNATION/VALUE'))
        nationality = none_handler(individual.find('.//NATIONALITY/VALUE'))
        list_type = individual.find('.//LIST_TYPE/VALUE').text
        last_day_updated = list_to_string(individual.findall('.//LAST_DAY_UPDATED/VALUE'))
        city = none_handler(individual.find('.//INDIVIDUAL_PLACE_OF_BIRTH/CITY'))
        state_province = none_handler(individual.find('.//INDIVIDUAL_PLACE_OF_BIRTH/STATE_PROVINCE'))
        country = none_handler(individual.find('.//INDIVIDUAL_PLACE_OF_BIRTH/COUNTRY'))
        from_year = none_handler(individual.find('.//INDIVIDUAL_DATE_OF_BIRTH/FROM_YEAR'))
        to_year = none_handler(individual.find('.//INDIVIDUAL_DATE_OF_BIRTH/TO_YEAR'))
        individuals_info = (dataid, versionnum, name_original_script, first_name, title, second_name, third_name,
                            un_list_type, reference_number, listed_on, comments1, designation, nationality,
                            list_type, last_day_updated, city, state_province, country, from_year, to_year)
        data.append(individuals_info)
    return data


def parse_xml_entities(xml_data):
    tree = ET.fromstring(xml_data)
    data = []
    # перебор элементов в файле
    for entity in tree.findall('./ENTITIES/ENTITY'):
        dataid = entity.find('DATAID').text
        versionnum = entity.find('VERSIONNUM').text
        first_name = entity.find('FIRST_NAME').text
        un_list_type = entity.find('UN_LIST_TYPE').text
        reference_number = entity.find('REFERENCE_NUMBER').text
        listed_on = entity.find('LISTED_ON').text
        comments1 = entity.find('COMMENTS1').text
        name_original_script = none_handler(entity.find('NAME_ORIGINAL_SCRIPT'))
        list_type = entity.find('.//LIST_TYPE/VALUE').text
        last_day_updated = list_to_string(entity.findall('.//LAST_DAY_UPDATED/VALUE'))
        entity_alias = list_to_string(entity.findall('.//ENTITY_ALIAS/ALIAS_NAME'))
        entity_address = []
        for address in entity.findall('.//ENTITY_ADDRESS'):
            country = none_handler(address.find('COUNTRY'))
            city = none_handler(address.find('CITY'))
            state_province = none_handler(address.find('STATE_PROVINCE'))
            note = none_handler(address.find('NOTE'))
            address_list = (country, city, state_province, note)
            entity_address.append(address_list)
        listed_entity_address = ', '.join([x for tpl in entity_address for x in tpl if x])
        entities_info = (dataid, versionnum, first_name, un_list_type, reference_number, listed_on, comments1,
                         name_original_script, list_type, last_day_updated, entity_alias,
                         listed_entity_address)
        data.append(entities_info)
    return data


def write_to_db(individual, entity, engine):
    connection = engine.connect()
    metadata = db.MetaData()

    # Создание таблицы
    individuals = db.Table('individuals', metadata,
                           db.Column('dataid', db.String(255)),
                           db.Column('versionnum', db.String(255)),
                           db.Column('name_original_script', db.String(255)),
                           db.Column('first_name', db.String(255)),
                           db.Column('title', db.String(255)),
                           db.Column('second_name', db.String(255)),
                           db.Column('third_name', db.String(255)),
                           db.Column('un_list_type', db.String(255)),
                           db.Column('reference_number', db.String(255)),
                           db.Column('listed_on', db.String(255)),
                           db.Column('comments1', db.Text),
                           db.Column('designation', db.Text),
                           db.Column('nationality', db.String(255)),
                           db.Column('list_type', db.String(255)),
                           db.Column('last_day_updated', db.String(255)),
                           db.Column('city', db.String(255)),
                           db.Column('state_province', db.String(255)),
                           db.Column('country', db.String(255)),
                           db.Column('from_year', db.String(255)),
                           db.Column('to_year', db.String(255)),
                           )
    metadata.create_all(engine)

    # Заполнение таблицы данными
    for item in individual:
        select_query = db.select(individuals).where(individuals.c.dataid == item[0])
        result = connection.execute(select_query)
        record_exists = result.fetchone() is not None
        if not record_exists:
            query = db.insert(individuals).values(dataid=item[0],
                                                  versionnum=item[1],
                                                  name_original_script=item[2],
                                                  first_name=item[3],
                                                  title=item[4],
                                                  second_name=item[5],
                                                  third_name=item[6],
                                                  un_list_type=item[7],
                                                  reference_number=item[8],
                                                  listed_on=item[9],
                                                  comments1=item[10],
                                                  designation=item[11],
                                                  nationality=item[12],
                                                  list_type=item[13],
                                                  last_day_updated=item[14],
                                                  city=item[15],
                                                  state_province=item[16],
                                                  country=item[17],
                                                  from_year=item[18],
                                                  to_year=item[19],
                                                  )
            connection.execute(query)
    connection.commit()

    # Создание таблицы
    entities = db.Table('entities', metadata,
                        db.Column('dataid', db.String(255)),
                        db.Column('versionnum', db.String(255)),
                        db.Column('first_name', db.String(255)),
                        db.Column('un_list_type', db.String(255)),
                        db.Column('reference_number', db.String(255)),
                        db.Column('listed_on', db.String(255)),
                        db.Column('comments1', db.Text),
                        db.Column('name_original_script', db.String(255)),
                        db.Column('list_type', db.String(255)),
                        db.Column('last_day_updated', db.String(255)),
                        db.Column('entity_alias', db.Text),
                        db.Column('entity_address', db.Text),
                        )
    metadata.create_all(engine)

    # Заполнение таблицы данными
    for item in entity:
        select_query = db.select(entities).where(entities.c.dataid == item[0])
        result = connection.execute(select_query)
        record_exists = result.fetchone() is not None
        if not record_exists:
            query = db.insert(entities).values(dataid=item[0],
                                               versionnum=item[1],
                                               first_name=item[2],
                                               un_list_type=item[3],
                                               reference_number=item[4],
                                               listed_on=item[5],
                                               comments1=item[6],
                                               name_original_script=item[7],
                                               list_type=item[8],
                                               last_day_updated=item[9],
                                               entity_alias=item[10],
                                               entity_address=item[11],
                                               )
            connection.execute(query)
    connection.commit()
    connection.close()


def main():
    urls = [
        'https://www.un.org/securitycouncil/ru/sanctions/1988/materials',
        'https://www.un.org/securitycouncil/ru/sanctions/1718/materials',
        'https://www.un.org/securitycouncil/ru/sanctions/1267/aq_sanctions_list'
    ]

    engine = db.create_engine('postgresql://postgres:postgres@localhost:5432/testtask')

    # Загрузка данных из всех URL и запись в БД
    for url in urls:
        xml_data = load_data(url)
        individuals = parse_xml_individuals(xml_data)
        entities = parse_xml_entities(xml_data)
        write_to_db(individuals, entities, engine)


if __name__ == '__main__':
    main()
