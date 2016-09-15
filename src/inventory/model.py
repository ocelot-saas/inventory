"""Model actions for the inventory service."""

import datetime

import inflection
import slugify
import sqlalchemy as sql
import sqlalchemy.dialects.postgresql as postgresql


_metadata = sql.MetaData(schema='inventory')

_org = sql.Table(
    'org', _metadata,
    sql.Column('id', sql.Integer, primary_key=True, info={'export': True}),
    sql.Column('time_created', sql.DateTime(timezone=True), info={'export': True}))

_org_user = sql.Table(
    'org_user', _metadata,
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('user_id', sql.Integer, unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.PrimaryKeyConstraint('org_id', 'user_id'))

_restaurant = sql.Table(
    'restaurant', _metadata,
    sql.Column('id', sql.Integer, primary_key=True, info={'export': True}),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True), info={'export': True}),
    sql.Column('name', sql.Text(), info={'export': True}),
    sql.Column('description', sql.Text(), info={'export': True}),
    sql.Column('keywords', postgresql.ARRAY(sql.Text), info={'export': True}),
    sql.Column('address', sql.Text(), info={'export': True}),
    sql.Column('opening_hours', postgresql.JSON(), info={'export': True}),
    sql.Column('image_set', postgresql.JSON(), info={'export': True}))

_menu_section = sql.Table(
    'menu_section', _metadata,
    sql.Column('id', sql.Integer, primary_key=True, info={'export': True}),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id)),
    sql.Column('time_created', sql.DateTime(timezone=True), info={'export': True}),
    sql.Column('time_archived', sql.DateTime(timezone=True), nullable=True),
    sql.Column('name', sql.Text(), info={'export': True}),
    sql.Column('description', sql.Text(), info={'export': True}),
    sql.UniqueConstraint('id', 'org_id', name='menu_section_uk_id_org_id'))

_menu_item = sql.Table(
    'menu_item', _metadata,
    sql.Column('id', sql.Integer, primary_key=True, info={'export': True}),
    sql.Column('section_id', sql.Integer),
    sql.Column('org_id', sql.Integer),
    sql.Column('time_created', sql.DateTime(timezone=True), info={'export': True}),
    sql.Column('time_archived', sql.DateTime(timezone=True), nullable=True),
    sql.Column('name', sql.Text(), info={'export': True}),
    sql.Column('description', sql.Text(), info={'export': True}),
    sql.Column('keywords', postgresql.ARRAY(sql.Text), info={'export': True}),
    sql.Column('ingredients', postgresql.JSON(), info={'export': True}),
    sql.Column('image_set', postgresql.JSON(), info={'export': True}),
    sql.ForeignKeyConstraint(
        ['section_id', 'org_id'], [_menu_section.c.id, _menu_section.c.org_id]),
    sql.UniqueConstraint('id', 'section_id', 'org_id'))


_platforms_website = sql.Table(
    'platforms_website', _metadata,
    sql.Column('id', sql.Integer, primary_key=True, info={'export': True}),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True), info={'export': True}),
    sql.Column('subdomain', sql.Text(), info={'export': True}))

_platforms_callcenter = sql.Table(
    'platforms_callcenter', _metadata,
    sql.Column('id', sql.Integer, primary_key=True, info={'export': True}),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True), info={'export': True}),
    sql.Column('phone_number', sql.Text(), info={'export': True}))

_platforms_emailcenter = sql.Table(
    'platforms_emailcenter', _metadata,
    sql.Column('id', sql.Integer, primary_key=True, info={'export': True}),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True), info={'export': True}),
    sql.Column('email_name', sql.Text(), info={'export': True}))


def _ec(t):
    return [c for c in t.c if 'export' in c.info and c.info['export']]


_org_columns = _ec(_org)
_restaurant_columns = _ec(_restaurant)
_menu_section_columns = _ec(_menu_section)
_menu_item_columns = _ec(_menu_item)
_platforms_website_columns = _ec(_platforms_website)
_platforms_callcenter_columns = _ec(_platforms_callcenter)
_platforms_emailcenter_columns = _ec(_platforms_emailcenter)


class Error(Exception):
    pass


class OrgAlreadyExistsError(Error):
    pass


class OrgDoesNotExist(Error):
    pass


class MenuSectionDoesNotExistError(Error):
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
                    .returning(*_org_columns) \
                    .values(time_created=right_now)

                result = conn.execute(create_org)
                org_row = result.fetchone()
                result.close()

                create_org_user = _org_user \
                    .insert() \
                    .values(org_id=org_row['id'], user_id=user_id, time_created=right_now)

                result = conn.execute(create_org_user)
                result.close()

                create_restaurant = _restaurant \
                    .insert() \
                    .values(
                        org_id=org_row['id'],
                        time_created=right_now,
                        name=restaurant_name,
                        description=restaurant_description,
                        keywords=restaurant_keywords,
                        address=restaurant_address,
                        opening_hours=restaurant_opening_hours,
                        image_set=restaurant_image_set)

                conn.execute(create_restaurant).close()

                # Create basic platforms with basic info

                create_platforms_website = _platforms_website \
                    .insert() \
                    .values(
                        org_id=org_row['id'],
                        time_created=right_now,
                        subdomain=slugify.slugify(restaurant_name))

                conn.execute(create_platforms_website).close()

                create_platforms_callcenter = _platforms_callcenter \
                    .insert() \
                    .values(
                        org_id=org_row['id'],
                        time_created=right_now,
                        phone_number='')

                conn.execute(create_platforms_callcenter).close()

                create_platforms_emailcenter = _platforms_emailcenter \
                    .insert() \
                    .values(
                        org_id=org_row['id'],
                        time_created=right_now,
                        email_name='contact')

                conn.execute(create_platforms_emailcenter).close()
            except sql.exc.IntegrityError as e:
                raise OrgAlreadyExistsError() from e

        return _i2e(org_row)

    def get_org(self, user_id):
        with self._sql_engine.begin() as conn:
            fetch_org = self._fetch_org(user_id)

            result = conn.execute(fetch_org)
            org_row = result.fetchone()
            result.close()

        if org_row is None:
            raise OrgDoesNotExistError()

        return _i2e(org_row)

    def get_restaurant(self, user_id):
        with self._sql_engine.begin() as conn:
            fetch_restaurant = self._fetch_restaurant(user_id)

            result = conn.execute(fetch_restaurant)
            restaurant_row = result.fetchone()
            result.close()

        if restaurant_row is None:
            raise OrgDoesNotExistError()

        return _i2e(restaurant_row)

    def update_restaurant(self, user_id, **kwargs):
        with self._sql_engine.begin() as conn:
            fetch_restaurant = self._fetch_restaurant(user_id, just_id=True)

            update_restaurant = _restaurant \
                .update() \
                .returning(*_restaurant_columns) \
                .where(_restaurant.c.id == fetch_restaurant.as_scalar()) \
                .values(**_e2i(kwargs))

            result = conn.execute(update_restaurant)
            restaurant_row = result.fetchone()
            result.close()

        if restaurant_row is None:
            raise OrgDoesNotExistError()

        return _i2e(restaurant_row)

    def create_menu_section(self, user_id, name, description):
        right_now = self._the_clock.now()
        
        with self._sql_engine.begin() as conn:
            fetch_org = self._fetch_org(user_id, just_id=True)
            
            create_menu_section = _menu_section \
                .insert() \
                .returning(*_menu_section_columns) \
                .values(
                    org_id=fetch_org.as_scalar(),
                    time_created=right_now,
                    name=name,
                    description=description)

            result = conn.execute(create_menu_section)
            menu_section_row = result.fetchone()
            result.close()

        if menu_section_row is None:
            raise OrgDoesNotExistError()

        return _i2e(menu_section_row)

    def get_all_menu_sections(self, user_id):
        with self._sql_engine.begin() as conn:
            fetch_menu_sections = sql \
                .select(_menu_section_columns) \
                .select_from(_org_user
                             .join(_org, _org.c.id == _org_user.c.org_id)
                             .join(_menu_section, _menu_section.c.org_id == _org_user.c.org_id)) \
                .where(sql.and_(
                    _org_user.c.user_id == user_id,
                    _menu_section.c.time_archived == None))

            result = conn.execute(fetch_menu_sections)
            menu_sections_rows = result.fetchall()
            result.close()

        return [_i2e(s) for s in menu_sections_rows]

    def get_menu_section(self, user_id, section_id):
        with self._sql_engine.begin() as conn:
            fetch_menu_section = self._fetch_menu_section(user_id, section_id)

            result = conn.execute(fetch_menu_section)
            menu_section_row = result.fetchone()
            result.close()

        if menu_section_row is None:
            raise MenuSectionDoesNotExistError()

        return _i2e(menu_section_row)

    def update_menu_section(self, user_id, section_id, **kwargs):
        with self._sql_engine.begin() as conn:
            find_menu_section = self._fetch_menu_section(user_id, section_id, True)

            update_menu_section = _menu_section \
                .update() \
                .returning(*_menu_section_columns) \
                .values(**_e2i(kwargs)) \
                .where(_menu_section.c.id == find_menu_section.as_scalar())

            result = conn.execute(update_menu_section)
            menu_section_row = result.fetchone()
            result.close()

        if menu_section_row is None:
            raise MenuSectionDoesNotExistError()

        return _i2e(menu_section_row)

    def delete_menu_section(self, user_id, section_id):
        right_now = self._the_clock.now()

        with self._sql_engine.begin() as conn:
            find_menu_section = self._fetch_menu_section(user_id, section_id, True)

            update_menu_section = _menu_section \
                .update() \
                .values(time_archived=right_now) \
                .where(_menu_section.c.id == find_menu_section.as_scalar())

            result = conn.execute(update_menu_section)
            rowcount = result.rowcount
            result.close()

        if rowcount != 1:
            raise MenuSectionDoesNotExistError()

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
        with self._sql_engine.begin() as conn:
            fetch_platforms_website = self._fetch_platforms_website(user_id)

            result = conn.execute(fetch_platforms_website)
            platforms_website_row = result.fetchone()
            result.close()

        if platforms_website_row is None:
            raise OrgDoesNotExistError()

        return _i2e(platforms_website_row)

    def update_platforms_website(self, user_id, **kwargs):
        with self._sql_engine.begin() as conn:
            find_platforms_website_id = self._fetch_platforms_website(user_id, True)
            
            update_platforms_website = _platforms_website \
                .update() \
                .returning(*_platforms_website_columns) \
                .values(**_e2i(kwargs)) \
                .where(_platforms_website.c.id == find_platforms_website_id.as_scalar())

            result = conn.execute(update_platforms_website)
            platforms_website_row = result.fetchone()
            result.close()
            
        if platforms_website_row is None:
            raise OrgDoesNotExistError()

        return _i2e(platforms_website_row)

    def get_platforms_callcenter(self, user_id):
        with self._sql_engine.begin() as conn:
            fetch_platforms_callcenter = self._fetch_platforms_callcenter(user_id)

            result = conn.execute(fetch_platforms_callcenter)
            platforms_callcenter_row = result.fetchone()
            result.close()

        if platforms_callcenter_row is None:
            raise OrgDoesNotExistError()

        return _i2e(platforms_callcenter_row)

    def update_platforms_callcenter(self, user_id, **kwargs):
        with self._sql_engine.begin() as conn:
            find_platforms_callcenter_id = self._fetch_platforms_callcenter(user_id, True)
            
            update_platforms_callcenter = _platforms_callcenter \
                .update() \
                .returning(*_platforms_callcenter_columns) \
                .values(**_e2i(kwargs)) \
                .where(_platforms_callcenter.c.id == find_platforms_callcenter_id.as_scalar())

            result = conn.execute(update_platforms_callcenter)
            platforms_callcenter_row = result.fetchone()
            result.close()
            
        if platforms_callcenter_row is None:
            raise OrgDoesNotExistError()

        return _i2e(platforms_callcenter_row)

    def get_platforms_emailcenter(self, user_id):
        with self._sql_engine.begin() as conn:
            fetch_platforms_emailcenter = self._fetch_platforms_emailcenter(user_id)

            result = conn.execute(fetch_platforms_emailcenter)
            platforms_emailcenter_row = result.fetchone()
            result.close()

        if platforms_emailcenter_row is None:
            raise OrgDoesNotExistError()

        return _i2e(platforms_emailcenter_row)

    def update_platforms_emailcenter(self, user_id, **kwargs):
        with self._sql_engine.begin() as conn:
            find_platforms_emailcenter_id = self._fetch_platforms_emailcenter(user_id, True)
            
            update_platforms_emailcenter = _platforms_emailcenter \
                .update() \
                .returning(*_platforms_emailcenter_columns) \
                .values(**_e2i(kwargs)) \
                .where(_platforms_emailcenter.c.id == find_platforms_emailcenter_id.as_scalar())

            result = conn.execute(update_platforms_emailcenter)
            platforms_emailcenter_row = result.fetchone()
            result.close()
            
        if platforms_emailcenter_row is None:
            raise OrgDoesNotExistError()

        return _i2e(platforms_emailcenter_row)

    @staticmethod
    def _fetch_org(user_id, just_id=False):
        return sql \
            .select([_org.c.id] if just_id else _org_columns) \
            .select_from(_org_user
                         .join(_org, _org.c.id == _org_user.c.org_id)) \
            .where(_org_user.c.user_id == user_id)

    @staticmethod
    def _fetch_restaurant(user_id, just_id=False):
        return sql \
            .select([_restaurant.c.id] if just_id else _restaurant_columns) \
            .select_from(_org_user
                         .join(_org, _org.c.id == _org_user.c.org_id)
                         .join(_restaurant, _restaurant.c.org_id == _org_user.c.org_id)) \
            .where(_org_user.c.user_id == user_id)

    @staticmethod
    def _fetch_menu_section(user_id, section_id, just_id=False):
        return sql \
            .select([_menu_section.c.id] if just_id else _menu_section_columns) \
            .select_from(_org_user
                         .join(_org, _org.c.id == _org_user.c.org_id)
                         .join(_menu_section, _menu_section.c.org_id == _org_user.c.org_id)) \
            .where(sql.and_(
                _org_user.c.user_id == user_id,
                _menu_section.c.id == section_id,
                _menu_section.c.time_archived == None))

    @staticmethod
    def _fetch_platforms_website(user_id, just_id=False):
        return sql \
            .select([_platforms_website.c.id] if just_id else _platforms_website_columns) \
            .select_from(_org_user
                         .join(_org, _org.c.id == _org_user.c.org_id)
                         .join(_platforms_website,
                               _platforms_website.c.org_id == _org_user.c.org_id)) \
            .where(_org_user.c.user_id == user_id)

    @staticmethod
    def _fetch_platforms_callcenter(user_id, just_id=False):
        return sql \
            .select([_platforms_callcenter.c.id] if just_id else _platforms_callcenter_columns) \
            .select_from(_org_user
                         .join(_org, _org.c.id == _org_user.c.org_id)
                         .join(_platforms_callcenter,
                               _platforms_callcenter.c.org_id == _org_user.c.org_id)) \
            .where(_org_user.c.user_id == user_id)

    @staticmethod
    def _fetch_platforms_emailcenter(user_id, just_id=False):
        return sql \
            .select([_platforms_emailcenter.c.id] if just_id else _platforms_emailcenter_columns) \
            .select_from(_org_user
                         .join(_org, _org.c.id == _org_user.c.org_id)
                         .join(_platforms_emailcenter,
                               _platforms_emailcenter.c.org_id == _org_user.c.org_id)) \
            .where(_org_user.c.user_id == user_id)


def _ec(t):
    return [c for c in t.c if 'export' in t.c.info and t.c.info['export']]


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
