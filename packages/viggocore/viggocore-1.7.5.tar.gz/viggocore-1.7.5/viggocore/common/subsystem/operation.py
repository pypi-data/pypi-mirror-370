from typing import Optional
import uuid
import flask
import sqlalchemy

# TODO this import here is so strange
from datetime import datetime
from viggocore.common import exception
from viggocore.common.operation_after_post import \
    operation_after_post_registry
from viggocore.common.subsystem.driver import Driver


class Operation(object):

    def __init__(self, manager):
        self.manager = manager
        self.driver: Optional[Driver] = (
            manager.driver if hasattr(manager, 'driver') else None)

    def pre(self, **kwargs):
        return True

    def do(self, **kwargs):
        return True

    def post(self):
        pass

    def __call__(self, **kwargs):
        session = kwargs.pop(
            'session', self.driver.transaction_manager.session)

        if not self.pre(session=session, **kwargs):
            raise exception.PreconditionFailed()

        try:
            self.driver.transaction_manager.begin()

            result = self.do(session, **kwargs)

            self.driver.transaction_manager.commit()

            self.post()

            key = (self.manager.__class__, self.__class__)
            fn_after_post = operation_after_post_registry.get(key, None)
            if fn_after_post is not None:
                fn_after_post(self)

        except sqlalchemy.exc.IntegrityError as e:
            self.driver.transaction_manager.rollback()
            msg_info = ''.join(e.args)
            raise exception.DuplicatedEntity(msg_info)
        except Exception as e:
            self.driver.transaction_manager.rollback()
            raise e
        return result


class Create(Operation):

    def pre(self, session, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = uuid.uuid4().hex
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.now()
        if 'created_by' not in kwargs:
            if flask.has_request_context():
                token_id = flask.request.headers.get('token')
                if token_id is not None:
                    self.token = self.manager.api.tokens().get(id=token_id)
                    kwargs['created_by'] = self.token.user_id

        self.entity = self.driver.instantiate(**kwargs)

        return self.entity.is_stable()

    def do(self, session, **kwargs):
        self.driver.create(self.entity, session=session)
        return self.entity


class Get(Operation):

    def pre(self, session, id, **kwargs):
        self.id = id
        return True

    def do(self, session, **kwargs):
        entity = self.driver.get(self.id, session=session)
        return entity


class List(Operation):

    def _att_kwargs_with_query(self, session, **kwargs):
        if 'order_by' in kwargs.keys():
            order_by = kwargs.get('order_by', '')
            if '.' in order_by:
                kwargs['query'] = self.manager.init_query(
                    session, order_by, self.driver.resource)
        return kwargs

    def do(self, session, **kwargs):
        kwargs = self._att_kwargs_with_query(session=session, **kwargs)
        entities = self.driver.list(session=session, **kwargs)
        return entities


class Update(Operation):

    def pre(self, session, id, **kwargs):
        if id is None:
            raise exception.BadRequest

        self.entity = self.driver.get(id, session=session)

        self.entity.updated_at = datetime.now()
        if 'updated_by' not in kwargs:
            if flask.has_request_context():
                token_id = flask.request.headers.get('token')
                if token_id is not None:
                    self.token = self.manager.api.tokens().get(id=token_id)
                    self.entity.updated_by = self.token.user_id

        return self.entity.is_stable()

    def do(self, session, **kwargs):
        self.driver.update(self.entity, kwargs, session=session)
        return self.entity


class Delete(Operation):

    def pre(self, session, id, **kwargs):
        self.entity = self.driver.get(id, session=session)
        return True

    def do(self, session, **kwargs):
        self.driver.delete(self.entity, session=session)


class Count(Operation):

    def do(self, session, **kwargs):
        rows = self.driver.count(session=session, **kwargs)
        return rows


class ListMultipleSelection(Operation):

    def do(self, session, **kwargs):
        entities = self.driver.list_multiple_selection(
            session=session, **kwargs)
        return entities


class ActivateOrDeactivateMultipleEntities(Operation):

    def pre(self, session, **kwargs):
        domain_id = kwargs.get('domain_id', None)
        if domain_id is None:
            raise exception.BadRequest('domain_id is required.')

        active = kwargs.get('active', None)
        if active is None:
            raise exception.PreconditionFailed('active is required.')

        multiple_selection = kwargs.get('multiple_selection', None)
        if multiple_selection is None:
            raise exception.PreconditionFailed(
                'multiple_selection is required.')

        return True

    def do(self, session, **kwargs):
        # atualiza o updated_at e o updated_by
        kwargs['updated_at'] = datetime.now()
        if flask.has_request_context():
            token_id = flask.request.headers.get('token')
            if token_id is not None:
                token = self.manager.api.tokens().get(id=token_id)
                kwargs['updated_by'] = token.user_id

        result = self.driver.activate_or_deactivate_multiple_entities(
            session=session, **kwargs)
        return result
