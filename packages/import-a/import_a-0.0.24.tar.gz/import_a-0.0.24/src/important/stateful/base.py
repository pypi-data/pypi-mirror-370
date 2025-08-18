import logging
from typing import (
    Dict, Any, Optional
    )
import json


from gallop.config import BaseConfig


EXAMPLE_CONF = """
classes:
  User:
    upsert_by:
      - user_name
  Order:
    upsert_by:
      # we'll update or create the order
      # by the following names of column
      - user_id
      - product_name
objects:
  order1:
    class: Order
    data:
      product_name: pepper spray
      user_id: $user1.id
  order2:
    class: Order
    data:
      product_name: paper clip
      user_id: $user2.id
  user1:
    class: User
    data:
      user_name: jason
      user_email: bourn@gmail.com
  user2:
    class: User
    data:
      user_name: ethan
      user_email: hunt@gmail.com
"""


def base_config_to_dict(config: BaseConfig):
    """
    Convert the config to dict
    """
    return config.to_dict()


FIELD_PROCESS = {
    "json.loads": json.loads,
    "json.dumps": json.dumps,
    "base_config_to_dict": base_config_to_dict,
}


class StatefulBase:
    class_room = dict()

    def __init__(
        self,
        config: BaseConfig,
        class_room: Dict[str, Any] = dict(),
        init_objects: Optional[Dict[str, Any]] = None,
    ):
        self.class_room.update(class_room)
        self.class_confs = config.classes
        self.objects_conf = config.objects
        self.class_confs = self.validate_class(self.class_confs)
        self.objects = dict() if init_objects is None else init_objects
        self.init_order = list()

    def validate_class(self, class_confs: BaseConfig):
        """
        Validate the classes in the config
        """
        for class_name, _ in class_confs.items():
            if class_name not in self.class_room:
                raise KeyError(
                    f"Class {class_name} is not defined in class_room, "
                    f"what we have is {self.class_room.keys()}"
                )
            class_confs[class_name]['class'] = self.class_room[class_name]
        return class_confs

    def __repr__(self) -> str:
        return str(self.objects_conf)

    def init_key_value(self, key: str, value: Any):
        """
        Init the key value
        """
        if type(value) == str and value.startswith('$'):
            variable_chain = value[1:].split('.')
            obj_name = variable_chain[0]
            # dead loop check
            if obj_name == key:
                raise ValueError(
                    f"❌ Cannot reference self '{key}'")
            obj = self[obj_name]
            for attr in variable_chain[1:]:
                obj = getattr(obj, attr)
            value = obj
        return key, value

    def init_value_dict(self, values: Dict[str, Any], ):
        """
        Read the value recursively
        """
        for key, value in values.items():
            key, obj = self.init_key_value(key, value)
            values[key] = obj
        return values

    def __getitem__(self, obj_name: str) -> Any:
        """
        Get the variable by name
        """
        if obj_name in self.objects:
            return self.objects[obj_name]
        if obj_name not in self.objects_conf:
            raise KeyError(
                f"❌ Object {obj_name} is not defined in the objects config, "
                f"what we have is {self.objects_conf.keys()}"
            )
        obj_conf = self.objects_conf[obj_name]
        class_name = obj_conf['class']
        class_conf = self.class_confs[class_name]

        # if there is upsert condition
        # we are going to query with the upsert fields
        if "upsert_by" in class_conf:
            upsert_by = class_conf.upsert_by

            # set up query condition
            query = dict()
            for attr in upsert_by:
                obj_val = obj_conf.data[attr]
                # incase the value is a reference
                obj_val = self.init_key_value(attr, obj_val)[1]
                query[attr] = obj_val
            obj = self.special_query(class_name, **query)
            if obj is not None:
                # update the object properties
                has_read_process = "read_process" in class_conf
                for attr in obj_conf.data:
                    if attr not in upsert_by:
                        obj_val = self.init_key_value(
                            attr, obj_conf.data[attr])[1]
                        if has_read_process:
                            if attr in class_conf.read_process:
                                process = FIELD_PROCESS[
                                    class_conf.read_process[attr]]
                                obj_val = process(obj_val)
                        setattr(obj, attr, obj_val)
                self.special_set(obj_name, obj)

                self.objects[obj_name] = obj
                return obj

        # no exist object detected
        # create new object
        cls = class_conf['class']
        obj = cls(**self.init_value_dict(
            obj_conf['data']))

        # if there is a `read_process` for the object
        if "read_process" in class_conf:
            for field_name in obj_conf.data:
                if field_name in class_conf.read_process:
                    process = FIELD_PROCESS[
                        class_conf.read_process[field_name]]
                    logging.debug(
                        f"Processing {obj_name}.{field_name} "
                        f"with {process}")
                    setattr(
                        obj,
                        field_name,
                        process(getattr(obj, field_name)))

        # we keep track of init order for save the data
        # hierarchically later
        self.init_order.append(obj_name)
        self.objects[obj_name] = obj
        self.special_set(obj_name, obj)
        return obj

    def __setitem__(self, obj_name: str, value: Any) -> None:
        self.objects[obj_name] = value

    def __len__(self) -> int:
        return len(self.objects)

    def __call__(self,) -> Dict[str, Any]:
        for obj_name in self.objects_conf.keys():
            self[obj_name] = self[obj_name]
        return self.objects

    def special_set(self, obj_name: str, obj: Any):
        """
        Set the attribute of the object
            Please override this method to implement
        """
        logging.warning(
            f"Not implemented special_set for {obj_name}")

    def special_query(self, class_name: str, **query) -> Optional[Any]:
        """
        Query the attribute of the object
            Please override this method to implement
        """
        logging.warning(
            f"Not implemented special_query for {class_name} {query}")
        return None


def build_db_stateful(
    db: "Session",
    base: "Base",
) -> StatefulBase:
    """
    Build a stateful class for database connection
    """
    class_room_db = dict(
        (i.class_.__name__, i.class_)
        for i in base.registry.mappers)

    class DBStateful(StatefulBase):
        """
        Stateful class for database
        """
        class_room = class_room_db

        def special_set(
            self,
            obj_name: str,
            obj: Any
        ):
            """
            set object to database
            """
            db.add(obj)
            db.commit()
            db.refresh(obj)

        def special_query(self, class_name: str, **query) -> Optional[Any]:
            """
            Query the object from database
            """
            cls = self.class_confs[class_name]['class']
            return db.query(cls).filter_by(**query).first()

        def delete(self, obj_name: str):
            """
            Delete the object from database
            """
            obj = self[obj_name]
            db.delete(obj)
            db.commit()
    return DBStateful
