from faker import Faker
from typing import Callable
import re


class Generators:
    def __init__(self, fake_gen: Faker):
        self.fake_gen = fake_gen
        self.__generators: dict[str, Callable] = {}
        self._register_default_generators()

    def _register_default_generators(self):
        default_faker_methods = [
            'name', 'first_name', 'last_name', 'email', 'phone', 'city', 'company', 'job', 'date', 'address'
        ]
        for method_name in default_faker_methods:
            if hasattr(self.fake_gen, method_name):
                def make_gen(method):
                    return lambda: getattr(self.fake_gen, method)()
                self.__generators[method_name] = make_gen(method_name)

    def get_generator(self, name: str):
        if name not in self.__generators:
            raise ValueError("Invalid generator name")
        return self.__generators.get(name)

    def has_generator(self, name: str) -> bool:
        return name in self.__generators

    # TODO: template method
    def get_all_generators(self):
        return self.__generators

    # TODO: add custom generator option


class LinesGenerator:
    def __init__(
            self,
            line_template: str,
            data_generator: Generators,
            line_count: int = 1
    ):
        self.line_template: str = line_template
        self.data_generator: Generators = data_generator
        self.line_count = line_count
        self._template_fields_list: list = self._extract_fields(self.line_template)

    def _extract_fields(self, template: str) -> list[str]:
        """
        return list of fields from template like this:
        "Hello {name}! Your city is {city}?" --> ['name', 'city']
        """
        return re.findall(r'\{\s*([^}]+?)\s*}', template)

    def one_line_generator(self):
        generated_data = {}
        for field in self._template_fields_list:
            if self.data_generator.has_generator(field):
                # TODO: add exception
                generated_data[field] = self.data_generator.get_generator(field)()
            else:
                generated_data[field] = f"UNKNOWN_field_[{field}]"

        return self.line_template.format(**generated_data)

    def lines_generator(self):
        for _ in range(self.line_count):
            yield self.one_line_generator()




# TODO: add export to file option
# TODO: add docstrings


