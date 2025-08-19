import json
import os
import re
from collections import defaultdict
from fnmatch import fnmatch
from textwrap import indent, wrap

HERE = os.path.dirname(os.path.abspath(__file__))

try:
    parameter_data = json.load(
        open(os.path.join(HERE, "_mzmine2_parameter_classes.json"))
    )
except IOError:
    parameter_data = defaultdict(lambda: defaultdict(dict))


class _Parameter:
    pass


class ParameterBaseMeta:
    def __new__(cls, cls_name, bases, dict_):

        fields = parameter_data[dict_["_java_class"]]["fields"]

        # support isinstance checks below:
        bases = bases + (_Parameter,)

        doc_lines = []
        store_fields = []

        # check keys
        supported = [
            "_fields",
            "_java_class",
            "_defaults",
            "_check_*",
            "_time_in_minutes",
            "_module_combo_parameters",
        ]

        if not all(
            any(fnmatch(key, pattern) for pattern in supported)
            for key in dict_.keys()
            if not key.startswith("__")
        ):
            raise RuntimeError("found unsupported fields")

        defaults = dict_.get("_defaults", {})
        time_in_minutes = dict_.get("_time_in_minutes", [])

        all_defaults = []

        for name, entry in fields.items():
            if name not in dict_["_fields"]:
                continue

            python_field_name = _to_snake_case(name)

            default = defaults.get(python_field_name)
            if default is None:
                default = entry["default"]

            if isinstance(default, list):
                default = tuple(default)

            if name in time_in_minutes and default is not None:
                if isinstance(default, (int, float)):
                    default *= 60
                elif isinstance(default, tuple):
                    default = tuple(v * 60 for v in default)
                else:
                    raise NotImplementedError

            module_combo_parameters = dict_.get("_module_combo_parameters", {}).get(
                name
            )

            dict_[python_field_name], extra = create_descriptor(
                python_field_name, entry, default, module_combo_parameters
            )

            all_defaults.append(default)

            paragraph = _format_description(entry["description"])
            doc_lines.append(f":param {python_field_name}: {paragraph}. {extra}")
            doc_lines.append("")

            store_fields.append(python_field_name)

        for attr in dict_.keys():
            if attr.startswith("_check"):
                if not any(attr == f"_check_{field}" for field in store_fields):
                    raise RuntimeError(f"invalid attribute {attr}")

        if any(key not in store_fields for key in dict_.get("_defaults", {}).keys()):
            raise RuntimeError("invalid key in _defaults field")

        dict_["_store_fields"] = store_fields
        dict_["_check_if_all_parameters_are_set"] = _check_if_all_parameters_are_set
        dict_["_to_dict"] = _to_dict
        dict_["__doc__"] = "\n".join(doc_lines)
        dict_["__getstate__"] = __getstate__
        dict_["__setstate__"] = __setstate__
        dict_["__setattr__"] = create_setattr(store_fields)
        dict_["__str__"] = __str__

        dict_["__init__"] = create_init(store_fields, all_defaults)

        return type(cls_name, bases, dict_)


def _collect_undefined(obj):
    undefined = []
    for name, value in obj.__dict__.items():
        if value is None:
            undefined.append(name.lstrip("_"))
        elif isinstance(value, _Parameter):
            undefined.extend(_collect_undefined(value))
    return undefined


def _check_if_all_parameters_are_set(self):
    undefined = _collect_undefined(self)
    if not undefined:
        return
    msg = f"values for {', '.join(undefined)} are not defined"
    raise ValueError(msg)


def _to_dict(self):
    dd = {}
    for name in self._store_fields:
        value = getattr(self, name)
        if isinstance(value, _Parameter):
            value = value._to_dict()
        dd[name] = value
    return dd


def create_setattr(allowed_fields):
    def __setattr__(self, name, value):
        if name.lstrip("_") not in allowed_fields:
            fields = ", ".join(allowed_fields)
            raise AttributeError(f"only fields {fields} can be set")
        # with help from https://stackoverflow.com/questions/9161302:
        return object.__setattr__(self, name, value)

    return __setattr__


def create_init(store_fields, defaults):
    args = ", ".join(
        f"{arg}={default!r}" for (arg, default) in zip(store_fields, defaults)
    )
    indent = "\n    "
    setters = indent.join(f"self.{name} = {name}" for name in store_fields)
    if not setters:
        setters = "pass"

    dd = {}
    exec(f"def __init__(self, {args}): {indent}{setters}", {}, dd)
    return dd["__init__"]


def __getstate__(self):

    values = {name: getattr(self, name) for name in self._store_fields}
    return self.__dict__, values


def __setstate__(self, data):
    dd, values = data
    self.__dict__.update(dd)
    self.__init__()
    for key, value in values.items():
        setattr(self, key, value)


def __setattr__(self, name, value):
    raise ValueError()


def __str__(self):
    rows = []
    max_field_length = 0
    for field in self._store_fields:
        value = getattr(self, field)
        rows.append((field, value))
        max_field_length = max(max_field_length, len(field))

    lines = [self.__class__.__qualname__ + ":"]
    for field, value in rows:
        field = field.ljust(max_field_length)
        if value is None:
            value = "<undef>"
        lines.append(f"    {field}: {value}")
    return "\n".join(lines)


class ParameterField:
    def __init__(self, python_field_name, checker, default_value, value_range):
        self._checker = checker
        self._python_field_name = python_field_name
        self._default_value = default_value
        self._value_range = value_range

    def __get__(self, instance, owner):
        return getattr(instance, "_" + self._python_field_name, self._default_value)

    def __set__(self, instance, value):
        if value is not None:
            ok, message = self._checker(value, self._value_range)
            if not ok:
                raise ValueError(f"setting {self._python_field_name}: {message}")
            check_method_name = "_check_" + self._python_field_name
            if hasattr(instance, check_method_name):
                checker = getattr(instance, check_method_name)
                ok, message = checker(value)
                if not ok:
                    raise ValueError(f"setting {self._python_field_name}: {message}")
        setattr(instance, "_" + self._python_field_name, value)


def double_checker(value, value_range):
    return isinstance(value, (float, int)), "floating point number required"


def integer_checker(value, value_range):
    return isinstance(value, int), "integer number required"


def string_checker(value, value_range):
    return isinstance(value, str), "string required"


def bool_checker(value, value_range):
    return value in (True, False), "boolean value required"


def double_range_checker(value, value_range):
    return (
        (
            isinstance(value, tuple)
            and len(value) == 2
            and isinstance(value[0], (float, int))
            and isinstance(value[1], (float, int))
        ),
        "tuple of two numbers required",
    )


def percent_checker(value, value_range):
    return (
        isinstance(value, (int, float)) and value_range[0] <= value <= value_range[1],
        f"value between {value_range[0]} and {value_range[1]} required",
    )


def mz_tolerance_checker(value, value_range):
    return (
        (
            isinstance(value, tuple)
            and len(value) == 2
            and isinstance(value[0], (int, float))
            and isinstance(value[1], (int, float))
        ),
        "tuple (abs_tolerance, ppm_tolerance)",
    )


def rt_tolerance_checker(value, value_range):
    return (
        (
            isinstance(value, tuple)
            and len(value) == 2
            and isinstance(value[0], (bool, int))
            and isinstance(value[1], (int, float))
        ),
        "tuple (is_abs_tolerance, rt_tolerance)",
    )


def adducts_checker(adducts, value_range):
    return (
        (
            isinstance(adducts, (tuple, list))
            and all(len(adduct) == 2 for adduct in adducts)
            and all(isinstance(adduct[0], str) for adduct in adducts)
            and all(isinstance(adduct[1], float) for adduct in adducts)
        ),
        "list of tuples (str, float)",
    )


def create_combo_checker(choices):
    def combo_checker(value, value_range):
        return value in choices, f"allowed values are {choices!r}"

    return combo_checker


def create_module_combo_checker(choice_types):
    def combo_checker(value, value_range):
        choice_types_str = ", ".join(t.__qualname__ for t in choice_types)
        return (
            any(isinstance(value, choice_type) for choice_type in choice_types),
            f"allowed values are among type(s) {choice_types_str}",
        )

    return combo_checker


_checkers = {
    "DoubleParameter": double_checker,
    "IntegerParameter": integer_checker,
    "StringParameter": string_checker,
    "BooleanParameter": bool_checker,
    "MZToleranceParameter": mz_tolerance_checker,
    "RTToleranceParameter": rt_tolerance_checker,
    "DoubleRangeParameter": double_range_checker,
    "PercentParameter": percent_checker,
}


def create_descriptor(python_field_name, entry, default_value, module_combo_parameters):
    java_type = entry["type"]
    choices = entry["choices"]
    value_range = entry["value_range"]

    checker = _checkers.get(java_type)
    if checker is not None:
        return (
            ParameterField(python_field_name, checker, default_value, value_range),
            "",
        )
    elif java_type == "ComboParameter":
        extra = "allowed values: {}".format(", ".join(map(repr, choices)))
        return (
            ParameterField(
                python_field_name, create_combo_checker(choices), default_value, None
            ),
            extra,
        )
    elif java_type == "ModuleComboParameter":
        extra = "allowed types: {}".format(
            ", ".join(p.__name__ for p in module_combo_parameters)
        )
        return (
            ParameterField(
                python_field_name,
                create_module_combo_checker(module_combo_parameters),
                default_value,
                None,
            ),
            extra,
        )

    elif java_type == "AdductsParameter":
        return (
            ParameterField(python_field_name, adducts_checker, default_value, None),
            "",
        )
    raise NotImplementedError(f"java type {java_type} not supported")


def _format_description(description):
    lines = wrap(description, 60)
    return indent("\n".join(lines), "        ").lstrip().rstrip(".")


def _to_snake_case(txt):
    # from https://stackoverflow.com/questions/1175208
    txt = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", txt)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", txt).lower()
