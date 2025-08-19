
import json
from _ctypes import PyObj_FromPtr
import re

class NoIndent(object):
    """ Value wrapper. """
    def __init__(self, value, max_length=None):
        self.value = value
        self.max_length = max_length

class DocumentationEncoder(json.JSONEncoder):
    FORMAT_SPEC = '@@{}@@'
    regex = re.compile(FORMAT_SPEC.format(r'(\d+)'))

    def __init__(self, **kwargs):
        # Save copy of any keyword argument values needed for use here.
        self.__sort_keys = kwargs.get('sort_keys', None)
        super(DocumentationEncoder, self).__init__(**kwargs)

    def default(self, obj):
        return (self.FORMAT_SPEC.format(id(obj)) if isinstance(obj, NoIndent)
                else super(DocumentationEncoder, self).default(obj))

    def encode(self, obj):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.
        json_repr = super(DocumentationEncoder, self).encode(obj)  # Default JSON.

        # Replace any marked-up object ids in the JSON repr with the
        # value returned from the json.dumps() of the corresponding
        # wrapped Python object.
        for match in self.regex.finditer(json_repr):
            # see https://stackoverflow.com/a/15012814/355230
            _id = int(match.group(1))
            no_indent = PyObj_FromPtr(_id)
            if no_indent.max_length is not None and isinstance(no_indent.value, list) and len(str(no_indent.value)) > no_indent.max_length:
                truncated_value = str(no_indent.value)[0:no_indent.max_length]
                json_obj_repr = truncated_value + '...'
            else:
                json_obj_repr = json.dumps(no_indent.value, sort_keys=self.__sort_keys)

            # Replace the matched id string with json formatted representation
            # of the corresponding Python object.
            json_repr = json_repr.replace(
                            '"{}"'.format(format_spec.format(_id)), json_obj_repr)

        return '\n'+json_repr #\n to get rid of weird indent in html :)

def convert_no_indent_fields(data):
    def process_value(value):
        #Recursively process dictionaries to get turn NoIndent into its value 
        if isinstance(value, dict):
            return {k: process_value(v) for k, v in value.items()}
        #Same for any lists, prob makes it slower but maybe one day itll be needed
        elif isinstance(value, list):
            return [process_value(item) for item in value]
        #When it finds no indent convert it to value
        elif isinstance(value, NoIndent):
            return value.value
        else:
            return value
    return process_value(data)

class ExampleFormatterMixin:
    @classmethod
    def get_examples(cls, for_display=False):
        """
        Returns examples from models

        for_display returns a string of a cleaner representation for human readability.
        """
        json_schema = cls.model_config.get("json_schema_extra")
        if for_display:
            return [json.dumps(examp, cls=DocumentationEncoder, indent=2) for examp in json_schema.get("examples", []) if json_schema]
        return [convert_no_indent_fields(ex) for ex in json_schema.get("examples", [])] 
    
    @classmethod
    def get_summarized_model(cls):
        """
        Returns a summarized version of the model for display
        """
        json_schema = cls.model_config.get("json_schema_extra")
        display_examples = [json.dumps(examp, cls=DocumentationEncoder, indent=2) for examp in json_schema.get("examples", []) if json_schema]
        json_schema['examples'] = [convert_no_indent_fields(ex) for ex in json_schema.get("examples", [])]
        json_schema['display_examples'] = display_examples
        return json_schema