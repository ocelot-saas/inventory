"""Model actions for the inventory service."""

import datetime

import inflection
import slugify
import sqlalchemy as sql
import sqlalchemy.dialects.postgresql as postgresql


_metadata = sql.MetaData(schema='inventory')

_org = sql.Table(
    'org', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('time_created', sql.DateTime(timezone=True)))

_org_user = sql.Table(
    'org_user', _metadata,
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('user_id', sql.Integer, unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.PrimaryKeyConstraint('org_id', 'user_id'))

_restaurant = sql.Table(
    'restaurant', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.Column('name', sql.Text()),
    sql.Column('description', sql.Text()),
    sql.Column('keywords', postgresql.ARRAY(sql.Text)),
    sql.Column('address', sql.Text()),
    sql.Column('opening_hours', postgresql.JSON()),
    sql.Column('image_set', postgresql.JSON()))

_menu_section = sql.Table(
    'menu_section', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id)),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.Column('time_archived', sql.DateTime(timezone=True), nullable=True),
    sql.Column('name', sql.Text()),
    sql.Column('description', sql.Text()),
    sql.UniqueConstraint('id', 'org_id', name='menu_section_uk_id_org_id'))

_menu_item = sql.Table(
    'menu_item', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('section_id', sql.Integer),
    sql.Column('org_id', sql.Integer),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.Column('time_archived', sql.DateTime(timezone=True), nullable=True),
    sql.Column('name', sql.Text()),
    sql.Column('description', sql.Text()),
    sql.Column('keywords', postgresql.ARRAY(sql.Text)),
    sql.Column('ingredients', postgresql.JSON()),
    sql.Column('image_set', postgresql.JSON()),
    sql.ForeignKeyConstraint(
        ['section_id', 'org_id'], [_menu_section.c.id, _menu_section.c.org_id]),
    sql.UniqueConstraint('id', 'section_id', 'org_id'))

_platforms_website = sql.Table(
    'platforms_website', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.Column('subdomain', sql.Text()))

_platforms_callcenter = sql.Table(
    'platforms_callcenter', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.Column('phone_number', sql.Text()))

_platforms_emailcenter = sql.Table(
    'platforms_emailcenter', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.Column('email_name', sql.Text()))


class Error(Exception):
    pass


class OrgAlreadyExistsError(Error):
    pass


class OrgDoesNotExist(Error):
    pass


class Model(object):
    def __init__(self, the_clock, sql_engine):
        self._the_clock = the_clock
        self._sql_engine = sql_engine

    def create_org(self, user_id, restaurant_name, restaurant_description, restaurant_keywords,
                   restaurant_address, restaurant_opening_hours, restaurant_image_set):
        right_now = self._the_clock.now()
        
        with self._sql_engine.begin() as conn:
            try:
                create_org = _org \
                    .insert() \
                    .values(time_created=right_now)

                result = conn.execute(create_org)
                org_id = result.inserted_primary_key[0]
                result.close()

                create_org_user = _org_user \
                    .insert() \
                    .values(org_id=org_id, user_id=user_id, time_created=right_now)

                result = conn.execute(create_org_user)
                result.close()

                create_restaurant = _restaurant \
                    .insert() \
                    .values(
                        org_id=org_id,
                        time_created=right_now,
                        name=restaurant_name,
                        description=restaurant_description,
                        keywords=restaurant_keywords,
                        address=restaurant_address,
                        opening_hours=restaurant_opening_hours,
                        image_set=restaurant_image_set)

                conn.execute(create_restaurant).close()

                # Create basic plaforms with basic info

                create_platforms_website = _platforms_website \
                    .insert() \
                    .values(
                        org_id=org_id,
                        time_created=right_now,
                        subdomain=slugify.slugify(restaurant_name))

                conn.execute(create_platforms_website).close()

                create_platforms_callcenter = _platforms_callcenter \
                    .insert() \
                    .values(
                        org_id=org_id,
                        time_created=right_now,
                        phone_number='')

                conn.execute(create_platforms_callcenter).close()

                create_platforms_emailcenter = _platforms_emailcenter \
                    .insert() \
                    .values(
                        org_id=org_id,
                        time_created=right_now,
                        email_name='contact')

                conn.execute(create_platforms_emailcenter).close()
            except sql.exc.IntegrityError as e:
                raise OrgAlreadyExistsError() from e

        return {
            'id': org_id,
            'timeCreatedTs': int(right_now.timestamp())
        }

    def get_org(self, user_id):
        with self._sql_engine.begin() as conn:
            fetch_org = sql.sql \
                .select([
                    _org.c.id,
                    _org.c.time_created
                ]) \
                .select_from(_org_user
                             .join(_org, _org.c.id == _org_user.c.org_id)) \
                .where(_org_user.c.user_id == user_id)

            result = conn.execute(fetch_org)
            org_row = result.fetchone()
            result.close()

        if org_row is None:
            raise OrgDoesNotExist()

        return _i2e(org_row)

    def get_restaurant(self, user_id):
        with self._sql_engine.begin() as conn:
            restaurant_row = self._fetch_restaurant(conn, user_id)

        if restaurant_row is None:
            raise OrgDoesNotExist()

        return _i2e(restaurant_row)

    def update_restaurant(self, user_id, **kwargs):
        with self._sql_engine.begin() as conn:
            restaurant_row = self._fetch_restaurant(conn, user_id)

            if restaurant_row is None:
                raise OrgDoesNotExist()

            update_restaurant = _restaurant \
                .update() \
                .where(_restaurant.c.id == restaurant_row['id']) \
                .values(**_e2i(kwargs))

            result = conn.execute(update_restaurant)
            result.close()

        restaurant = _i2e(restaurant_row)
        restaurant.update(kwargs)

        return restaurant

    def create_menu_section(self, user_id, name, description):
        pass

    def get_all_menu_sections(self, user_id):
        pass

    def get_menu_section(self, user_id, section_id):
        pass

    def update_menu_section(self, user_id, section_id, **kwargs):
        pass

    def delete_menu_section(self, user_id, section_id):
        pass

    def create_menu_item(self, user_id, section_id, name, description, keywords,
                         ingredients, image_set):
        pass

    def get_all_menu_items(self, user_id):
        pass

    def get_menu_item(self, user_id, item_id):
        pass

    def update_menu_item(self, user_id, item_id, **kwargs):
        pass

    def delete_menu_item(self, user_id, item_id):
        pass

    def get_platforms_website(self, user_id):
        pass

    def update_platforms_website(self, user_id, **kwargs):
        pass

    def get_platforms_callcenter(self, user_id):
        pass

    def update_platforms_callcenter(self, user_id, **kwargs):
        pass

    def get_platforms_emailcenter(self, user_id):
        pass

    def update_platforms_emailcenter(self, user_id, **kwargs):
        pass

    @staticmethod
    def _fetch_restaurant(conn, user_id):
        fetch_restaurant = sql.sql \
            .select([
                _restaurant.c.id,
                _restaurant.c.time_created,
                _restaurant.c.name,
                _restaurant.c.description,
                _restaurant.c.keywords,
                _restaurant.c.address,
                _restaurant.c.opening_hours,
                _restaurant.c.image_set,
            ]) \
            .select_from(_org_user
                         .join(_org, _org.c.id == _org_user.c.org_id)
                         .join(_restaurant, _restaurant.c.org_id == _org_user.c.org_id)) \
            .where(_org_user.c.user_id == user_id)

        result = conn.execute(fetch_restaurant)
        restaurant_row = result.fetchone()
        result.close()

        return restaurant_row


def _e2i(d):
    return {inflection.underscore(k):v for k,v in d.items()}


def _i2e(d):
    o = {}
    for k, v in d.items():
        if isinstance(v, datetime.datetime):
            o[inflection.camelize(k, False) + 'Ts'] = int(v.timestamp())
        else:
            o[inflection.camelize(k, False)] = v
    return o
