'''
empostfix manager:

    argv[1] : directory path which includes "settings.py"

'''
import sys
import os


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('you need path of your django application')
        sys.exit(1)

    #  django path
    APP = os.path.basename(sys.argv[1])
    sys.argv[1] = os.path.abspath(sys.argv[1])
    sys.path.append(os.path.dirname(sys.argv[1]))

    #  argv[1] is manage.py command `empostfix`
    sys.argv[1] = 'empostfix'

    # DJANGO_SETTINGS_MODULE
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "{0}.settings".format(APP))

    # Run managemnet command
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
