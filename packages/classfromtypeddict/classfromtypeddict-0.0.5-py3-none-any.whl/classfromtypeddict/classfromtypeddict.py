import inspect

from types import UnionType
from typing import get_type_hints, get_origin, get_args, Optional, NamedTuple, cast
from typing import TypedDict


def _is_typeddict(a_class) -> bool:
    if not isinstance(a_class, type):
        return False
    return type(a_class).__name__ == "_TypedDictMeta"


class ClassFromTypedDict: # pylint: disable=too-few-public-methods
    """
    The Class ClassFromTypedDict allows converting a dict following
    a TypedDict schema into a class automatically.
    The resulted class needs to be a super class of ClassFromTypedDict
    At the class creation a dict is passed to the constructor.
    This dict will be used as a basis to create the parameters.
    If the TypedDict is nested, the associated ClassFromTypedDict is automatically
    created and nested to the root ClassFromTypedDict
    """

    _class_ref: TypedDict
    """
    private class attribute storing the TypedDict association.
    Shall only be used by the Super class and override as a static attribute.
    """
    _typeddict_class_association = {}
    """
    private class attribute storing association between classes and TypedDict 
    """

    _exception: dict[str, str] ={}

    class _Result(NamedTuple):
        """
        internal class to return a result able to make difference between None and nothing found
        """
        found: bool
        data: Optional[object]

    @classmethod
    def get_class_ref(cls):
        return cls._class_ref

    @classmethod
    def import_package(cls,
                       package):
        """
        This method set the association between classes and typeddict
        It goes through a package to find classes of type ClassFromTypedDict and
        record the association between the class and a typeddict
        :param package: package containing classes of type ClassFromTypedDict
        :type package: the parameter shall have a python package type
        :return: nothing
        :rtype: /
        """
        # go through all modules fo the package
        for module in inspect.getmembers(package, inspect.ismodule):
            # search all classes
            module_classes = inspect.getmembers(module[1], inspect.isclass)
            # and go through all classes
            for module_class_tuple in module_classes:
                module_class: type = module_class_tuple[1]
                # if a class is a subclass of ClassFromTypedDict
                if (issubclass(module_class, ClassFromTypedDict)
                        and module_class != ClassFromTypedDict):
                    # update the association private attribute
                    classfromtypeddict_class = cast(ClassFromTypedDict,module_class)
                    typeddict_class_ref = classfromtypeddict_class.get_class_ref()
                    cls._typeddict_class_association[typeddict_class_ref] = [ module, module_class ]

    def __init__(self,
                 data: dict):
        """

        :param data: dictionary
        :type data: dict that shall follow the schema defined by the TypedDict of the class
        """
        hints = get_type_hints(self._class_ref)  # Gather TypedDict annotations

        #correct exception
        for key, value in self._exception.items():
            if key in data:
                data[value] = data.pop(key)

        # Check there is no unexpected fields in data
        # (meaning not declared in the ref TypedDict)
        extra_fields = [field for field in data.keys() if field not in hints.keys()]
        if extra_fields:
            raise TypeError(f"Unexpected fields: {', '.join(extra_fields)}")

        # Check there is missing no field
        missing_fields = [field for field in hints.keys() if field not in data.keys()]
        if missing_fields:
            raise TypeError(f"Missing required fields: {', '.join(missing_fields)}")

        # for each field of the TypedDict
        for field, field_type in hints.items():
            # search the data in the input dict
            new_data = self.__analyze_data(data[field], type(data[field]), field_type, field)
            # if a data has been found
            if new_data is not None:
                # store it
                setattr(self, field, new_data)
                continue  # next field
            origin_type = get_origin(field_type)
            if issubclass(origin_type, UnionType):
                # for each type of the union
                types = get_args(field_type)
                if type(None) in types:
                    setattr(self, field, new_data)
                    continue # next field
            raise TypeError(f"Unexpected None value for field '{field}'. "
                            f"Expected type is '{field_type}'")

    def __analyze_data(self,
                       data,
                       data_type,
                       expected_data_type, field) -> object:
        """
        This private method analyze a data to check the coherency with
        the dict and create the value to be stored in the class
        :param data: data to analyze
        :type data: object
        :param data_type: type of the data
        :type data_type: type
        :param expected_data_type: the type expected for the data
        :type expected_data_type: type
        :param field: name of the filed (only used for error message)
        :type field: str
        :return: the data to store in the attribute
        :rtype: object
        """
        origin_type = get_origin(expected_data_type)
        # if the data is not a list or a dict or a union
        if origin_type is None:
            # check the data
            result : ClassFromTypedDict._Result = self.__check_data(data,
                                                                    data_type,
                                                                    expected_data_type)
            # if data has been converted
            if result.found:
                # return the data
                return result.data
            #otherwise raise an error
            raise TypeError(f"Analyzing field '{field}', "
                            f"unexpected type {data_type}, "
                            f"waiting {expected_data_type}")
        # if the data is a union
        if isinstance(origin_type, type) and issubclass(origin_type, UnionType):
            # for each type of the union
            for type_elem in get_args(expected_data_type):
                # check the data can be converted
                result : ClassFromTypedDict._Result = self.__check_data(data, data_type, type_elem)
                # if yes return the data
                if result.found:
                    return result.data
            # if no conversion has been possible raise an error
            raise TypeError(f"Analyzing field '{field}', "
                            f"unexpected type {data_type}, "
                            f"waiting {expected_data_type} in ")
        # if the data is a list
        if isinstance(origin_type, type) and issubclass(origin_type, list):
            # in the case of list, the case of list of TypedDict
            #       or more complex type containing TypedDict is not managed
            # at this current time, the xknx project does not contain such case
            return data
        # if the data is a dict
        if isinstance(origin_type, type) and issubclass(origin_type, dict):
            # go through the dict
            field_key_type, field_value_type = get_args(expected_data_type)
            new_data = {}
            data = cast(dict, data)
            for key, value in data.items():
                # convert the key
                new_key = self.__analyze_data(key, type(key), field_key_type, field)
                # convert the value
                new_value = self.__analyze_data(value, type(value), field_value_type, field)
                # create the new data
                new_data[new_key] = new_value
            # return the created new dict
            return new_data
        # otherwise raise an error
        raise TypeError(f"Unexpected case analyzing field '{field}")

    def __check_data(self, data, data_type, field_type) -> _Result:
        """
        This method convert the data into the data to store
        :param data: data to convert
        :type data: object
        :param data_type: type of the data to convert
        :type data_type: type
        :param field_type: target type
        :type field_type: type
        :return:
        :rtype:
        """
        if _is_typeddict(field_type):
            # if the data type is dict
            if data_type is dict:
                # convert the dict into the target field
                data=cast(dict,data)
                new_data = self.__convert_dict_to_class(field_type, data)
                #return the converted data
                return self._Result(found=True, data=new_data)
            # otherwise return a conversion has not been found
            return self._Result(found=False, data=None)
        # otherwise if the target type is the same than the data type
        if data_type == field_type:
            # return the data
            return self._Result(found=True, data=data)
        # otherwise return a conversion has not been found
        return self._Result(found=False, data=None)

    def __convert_dict_to_class(self, field_type, data) -> object:
        """
        This method convert a dict into a class if a ClassFromTypedDict exists
        :param field_type: target data type
        :type field_type: type
        :param data: data to convert
        :type data: dict
        :return: new created class or dict resulting from data conversion
        :rtype: ClassFromTypedDict | dict
        """
        # if the target field has an associated ClassFromTypedDict class
        if field_type in self._typeddict_class_association:
            # convert the data into the associated ClassFromTypedDict class
            cls = self._typeddict_class_association[field_type][1]
            new_data = cls(data)
            # return the created class
            return new_data
        # otherwise return the data as is
        return data
