# -*- coding: utf-8 -*-
"""
Created on Mar 12, 2012

@author: moloch

    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""


import xml.etree.cElementTree as ET
from builtins import str
from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy.orm import backref, relationship
from sqlalchemy.types import Boolean, String, Unicode

from libs.ValidationError import ValidationError
from models import dbsession
from models.BaseModels import DatabaseObject

from sqlalchemy import Column, String, DateTime
#Added
from models.FileUpload import FileUpload
import datetime

class Corporation(DatabaseObject):
    """Corporation definition"""

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))

    _name = Column(Unicode(32), unique=True, nullable=False)
    _description = Column(Unicode(512))
    _locked = Column(Boolean, default=False, nullable=False)
    #Added
    _start_time = Column(DateTime)
    _end_time = Column(DateTime)

    

    boxes = relationship(
        "Box",
        backref=backref("corporation", lazy="select"),
        cascade="all,delete,delete-orphan",
    )

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).all()

    @classmethod
    def count(cls):
        return dbsession.query(cls).count()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_name(cls, name):
        """Returns a the object with name of name"""
        return dbsession.query(cls).filter_by(_name=str(name)).first()

    @classmethod
    def by_uuid(cls, uuid):
        """Return an object based on uuid"""
        return dbsession.query(cls).filter_by(uuid=uuid).first()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not len(value) <= 32:
            raise ValidationError("Corporation name must be 0 - 32 characters")
        self._name = str(value)

    @property
    def description(self):
        if self._description is None:
            return ""
        return self._description

    @description.setter
    def description(self, value):
        if 512 < len(value):
            raise ValidationError("Description cannot be greater than 512 characters")
        self._description = str(value)

    @property
    def locked(self):
        """Determines if an admin has locked an corp."""
        if self._locked is None:
            return False
        return self._locked

    @locked.setter
    def locked(self, value):
        """Setter method for _lock"""
        if value is None:
            value = False
        elif isinstance(value, int):
            value = value == 1
        elif isinstance(value, str):
            value = value.lower() in ["true", "1"]
        assert isinstance(value, bool)
        self._locked = value
    #Added start_time and end_time
    @property
    def start_time(self):
        #Debug output auf die Konsole
        print("Start Time: ", self._start_time)
        if self._start_time is None:
            return None #Defualt value
        return self._start_time
    @start_time.setter
    def start_time(self, value):
        self._start_time = value
    @property
    def end_time(self):
        if self._end_time is None:
            return None #Defualt value
        return self._end_time
    @end_time.setter
    def end_time(self, value):
        self._end_time = value

    def to_dict(self):
        """Returns editable data as a dictionary"""
        return {
            "uuid": self.uuid,
            "name": self.name,
            "description": self.description,
            # "boxes": [box.uuid for box in self.boxes],
        }

    def to_xml(self, parent):
        """Add to XML dom"""
        corp_elem = ET.SubElement(parent, "corporation")
        ET.SubElement(corp_elem, "name").text = self.name
        ET.SubElement(corp_elem, "description").text = self.description
        ET.SubElement(corp_elem, "locked").text = str(self.locked)
        boxes_elem = ET.SubElement(corp_elem, "boxes")
        boxes_elem.set("count", "%s" % str(len(self.boxes)))
        for box in self.boxes:
            box.to_xml(boxes_elem)

    def __len__(self):
        return len(self.boxes)

    def __str__(self):
        return self.name
    #Added 
    def update_lock_status(self, current_time):
        """Update the lock status of the corporation"""
        if self.start_time is not None and self.end_time is not None:
            if self.start_time <= current_time and current_time <= self.end_time:
                self.locked = False
            else:
                self.locked = True

    submitted_files = relationship(
        "FileUpload",
        backref="corporation",
        cascade="all, delete, delete-orphan"
    )

    def get_submitted_files(self):
        return self.submitted_files
    
    def save_submitted_file(self, file):
        file_upload = FileUpload(
            file_name=file['filename'],
            data=file['body'],
            description="Submitted file for corporation",
            team_id=self.id,  # Assuming team_id is used to link to the corporation
            corporation_id=self.id,
            uploaded_at=datetime.datetime.utcnow()
        )
        dbsession.add(file_upload)
        dbsession.commit()