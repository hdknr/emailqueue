import inspect
from django.utils.html import strip_tags
from django.utils.encoding import force_unicode


def process_docstring(app, what, name, obj, options, lines):
    # This causes import errors if left outside the function
    from django.db import models, connections
    con = connections['default']

    # Make sure we have loaded models, otherwise related fields may end up
    # as strings
    models.get_models()

    # Only look at objects that inherit from Django's base model class
    if inspect.isclass(obj) and issubclass(obj, models.Model):
        # Grab the field list from the meta class
        fields = obj._meta.fields

        for field in fields:
            # Decode and strip any html out of the field's help text
            help_text = strip_tags(force_unicode(field.help_text))

            # Decode and capitalize the verbose name, for use if there isn't
            # any help text
            verbose_name = force_unicode(field.verbose_name).capitalize()

            db_type = field.db_type(con)

            if help_text:
                # Add the model field to the end of the docstring as a param
                # using the help text as the description
                lines.append(u':param {0}: {1}({2})     [{3}]'.format(
                    field.attname, verbose_name, help_text, db_type))
            else:
                # Add the model field to the end of the docstring as a param
                # using the verbose name as the description
                lines.append(u':param {0}: {1}     [{2}]'.format(
                    field.attname, verbose_name, db_type))

            # Add the field's type to the docstring
            if isinstance(field, models.ForeignKey):
                to = field.rel.to
                lines.append(u':type {0}: {1} to :class:`~{2}.{3}`'.format(
                    field.attname, type(field).__name__,
                    to.__module__, to.__name__))
            else:
                lines.append(u':type {0}: {1}'.format(
                    field.attname, type(field).__name__))

    # Return the extended docstring
    return lines
