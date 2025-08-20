from utils import exceptions

from ..model.configuration import (CMDArg, CMDBooleanArg, CMDClsArg, CMDArrayArg, CMDArgumentHelp, CMDArgDefault,
                                   CMDPasswordArgPromptInput, CMDArgPromptInput, CMDFloatArgBase, CMDIntegerArgBase,
                                   CMDStringArgBase)


class ArgumentUpdateMixin:

    @classmethod
    def _update_arg(cls, arg, **kwargs):
        if isinstance(arg, CMDArg):
            cls._update_cmd_arg(arg, **kwargs)
            cls._update_arg_enum(arg, **kwargs)
        if isinstance(arg, CMDBooleanArg):
            cls._update_boolean_arg(arg, **kwargs)
        if isinstance(arg, CMDClsArg):
            cls._update_cls_arg(arg, **kwargs)
        if isinstance(arg, CMDArrayArg):
            cls._update_array_arg(arg, **kwargs)
            cls._update_arg_enum(arg.item, **kwargs)
        return arg

    @staticmethod
    def _update_cmd_arg(arg, **kwargs):
        if 'options' in kwargs:
            arg.options = kwargs['options']
        if 'stage' in kwargs:
            arg.stage = kwargs['stage']
        if 'hide' in kwargs:
            if kwargs['hide'] and arg.required:
                raise exceptions.ResourceConflict("Cannot hide required argument")
            arg.hide = kwargs['hide']
        if 'group' in kwargs:
            arg.group = kwargs['group']
        if 'help' in kwargs:
            arg.help = CMDArgumentHelp(kwargs['help'])
        if 'default' in kwargs:
            if kwargs['default'] is None:
                arg.default = None
            else:
                arg.default = CMDArgDefault(kwargs['default'])
        if 'configurationKey' in kwargs:
            arg.configuration_key = kwargs['configurationKey']
        if 'prompt' in kwargs:
            if kwargs['prompt'] is None:
                arg.prompt = None
            elif 'confirm' in kwargs['prompt']:
                arg.prompt = CMDPasswordArgPromptInput(kwargs['prompt'])
                arg.blank = None
            else:
                arg.prompt = CMDArgPromptInput(kwargs['prompt'])
                arg.blank = None

    @staticmethod
    def _update_boolean_arg(arg, **kwargs):
        if 'reverse' in kwargs:
            arg.reverse = kwargs['reverse'] or False

    @staticmethod
    def _update_cls_arg(arg, **kwargs):
        if 'singularOptions' in kwargs:
            arg.singular_options = kwargs['singularOptions'] or None

    @staticmethod
    def _update_array_arg(arg, **kwargs):
        if 'singularOptions' in kwargs:
            arg.singular_options = kwargs['singularOptions'] or None

    @staticmethod
    def _update_arg_enum(arg, **kwargs):
        if 'supportEnumExtension' in kwargs and isinstance(arg, (CMDFloatArgBase, CMDIntegerArgBase, CMDStringArgBase)):
            if arg.enum:
                arg.enum.support_extension = kwargs['supportEnumExtension']