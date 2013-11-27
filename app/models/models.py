from app import db
from sqlalchemy import Enum
from sqlalchemy import Column, Date, DateTime, Float, Integer, Unicode

import datetime

ROLE_USER = 0
ROLE_ADMIN = 1


class BaseMenus(db.Model):
    menu_id = db.Column(db.Integer, primary_key = True)
    rank = db.Column(db.Integer)
    description = db.Column(db.Text)
    language = db.Column(db.String(5), unique=True)
    display = db.Column(db.String(20))


class BaseUserGroup(db.Model):
    group_id = db.Column(db.Integer, primary_key = True)
    code = db.Column(db.String(10))
    description = db.Column(db.Text)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<BaseUserGroup %r>' % (self.code)

class BaseTask(db.Model):
    task_id = db.Column(db.Integer, primary_key = True)
    menu_id = db.Column(db.Integer, db.ForeignKey('base_menus.menu_id'))
    code = db.Column(db.String(10))
    description = db.Column(db.Text)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<BaseTask %r>' % (self.code)


class BaseUserGroupTask(db.Model):
    grp_task_id = db.Column(db.Integer, primary_key = True)
    task_id = db.Column(db.Integer, db.ForeignKey('base_task.task_id'))
    group_id = db.Column(db.Integer, db.ForeignKey('base_user_group.group_id'))
    code = db.Column(db.String(10))
    description = db.Column(db.Text)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<BaseTask %r>' % (self.code)





class BaseUser(db.Model):
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.Text)
    user_category = db.Column(db.Enum('API', 'FRONTEND', name='user_category_types'))
    group_id = db.Column(db.Integer, db.ForeignKey('base_user_group.group_id'))
    date_created = db.Column(db.Date)
    created_by = db.Column(db.String(50))
    last_log_in_time = db.Column(db.Date)
    user_status = db.Column(db.String(1))
    end_date = db.Column(db.Date)
    no_of_logins = db.Column(db.Integer)
    failed_log = db.Column(db.Integer)
    branch_code = db.Column(db.String(10))
    login_flag = db.Column(db.String(1))
    upload_right = db.Column(db.String(5))
    last_login_time = db.Column(db.Date)
    last_login_date = db.Column(db.Date)
    last_login_fail_time  = db.Column(db.Date)
    language = db.Column(db.String(5), db.ForeignKey('base_menus.language'))
    user_id = db.Column(db.Integer, primary_key = True)




    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<CTSUser %r>' % (self.username)






class BaseLongProcessTask(db.Model):
    process_id = db.Column(db.Integer, primary_key = True)
    code = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    expected_duration_seconds = db.Column(db.Integer)
    role_access = db.Column(db.String(10))
    country = db.Column(db.String(5)) #GHA, NGN, SLA
    task_module_name = db.Column(db.String(100))
    celery_task = db.Column(db.String(100))
    celery_task_kwargs = db.Column(db.String(500)) #Pass the paramters and the 
    application = db.Column(db.String(20))
    status = db.Column(db.String(10))
    process_type = db.Column(db.String(20)) #CELERY, NORMAL

    current_processes = db.relationship("BaseLongProcesses", backref=db.backref('owner',
                                                   lazy='dynamic'))


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<BaseLongProcessTask %r>' % (self.process_id)


class BaseLongProcesses(db.Model):
    process_running_id = db.Column(db.Integer, primary_key = True)
    process_id = db.Column(db.Integer, db.ForeignKey('base_long_process_task.process_id'))
    start_time = db.Column(db.DateTime, default=datetime.datetime.now)
    end_time = db.Column(db.DateTime)
    submitted_by = db.Column(db.String(50))
    current_status = db.Column(db.String(10))
    retry = db.Column(db.String(1))
    attempt_count = db.Column(db.Integer)
    process_result = db.Column(db.Text)


    #long_process_task = db.relationship('BaseLongProcessTask', backref=db.backref('base_long_process_task',
    #                                                     lazy='dynamic'))


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<BaseLongProcesses %r>' % (self.process_running_id)




class BaseAuditLog(db.Model):
    audit_entry_id = db.Column(db.Integer, primary_key = True)
    task = db.Column(db.Integer, db.ForeignKey('base_task.task_id'))
    operation = db.Column(db.Enum('NEW', 'UPDATE', 'DELETE', name='audit_operation_types'))
    user_id = db.Column(db.Integer, db.ForeignKey('base_user.user_id'))
    #Entity JSON structure before update
    entity_before = db.Column(db.Text)
    #Entity JSON structure after update
    entity_after = db.Column(db.Text)
    activity_start = db.Column(db.Date, default=datetime.datetime.now)
    activity_end = db.Column(db.Date)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<BaseAuditLog %r>' % (self.audit_entry_id)

class BaseExposedModels(db.Model):
    model_id = db.Column(db.Integer, primary_key = True)
    module_full_path = db.Column(db.String(100))
    module_class_name = db.Column(db.String(50))
    hidden_fields = db.Column(db.String(50))
    url_prefix = db.Column(db.String(50))
    collection_name = db.Column(db.String(50))
    http_methods = db.Column(db.String(50))

