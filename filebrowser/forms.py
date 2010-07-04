# coding: utf-8

# imports
import encodings
import os
import re
import sys

if __name__ == "__main__":
    # For doctest only
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

# django imports
from django import forms
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext as _

# filebrowser imports
from filebrowser.settings import MAX_UPLOAD_SIZE, FOLDER_REGEX
from filebrowser.functions import convert_filename
from filebrowser.settings import *

alnum_name_re = re.compile(FOLDER_REGEX)

class MakeDirForm(forms.Form):
    """
    Form for creating Folder.
    """

    def __init__(self, path, *args, **kwargs):
        self.path = path
        super(MakeDirForm, self).__init__(*args, **kwargs)

    dir_name = forms.CharField(widget=forms.TextInput(attrs=dict({ 'class': 'vTextField' }, max_length=50, min_length=3)), label=_(u'Name'), help_text=_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'), required=True)

    def clean_dir_name(self):
        if self.cleaned_data['dir_name']:
            # only letters, numbers, underscores, spaces and hyphens are allowed.
            if not alnum_name_re.search(self.cleaned_data['dir_name']):
                raise forms.ValidationError(_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'))
            # Folder must not already exist.
            if os.path.isdir(os.path.join(self.path, convert_filename(self.cleaned_data['dir_name']))):
                raise forms.ValidationError(_(u'The Folder already exists.'))
        return convert_filename(self.cleaned_data['dir_name'])


class RenameForm(forms.Form):
    """
    Form for renaming Folder/File.
    """

    def __init__(self, path, file_extension, *args, **kwargs):
        self.path = path
        self.file_extension = file_extension
        super(RenameForm, self).__init__(*args, **kwargs)

    name = forms.CharField(widget=forms.TextInput(attrs=dict({ 'class': 'vTextField' }, max_length=50, min_length=3)), label=_(u'New Name'), help_text=_('Only letters, numbers, underscores, spaces and hyphens are allowed.'), required=True)

    def clean_name(self):
        if self.cleaned_data['name']:
            # only letters, numbers, underscores, spaces and hyphens are allowed.
            if not alnum_name_re.search(self.cleaned_data['name']):
                raise forms.ValidationError(_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'))
            #  folder/file must not already exist.
            if os.path.isdir(os.path.join(self.path, convert_filename(self.cleaned_data['name']))):
                raise forms.ValidationError(_(u'The Folder already exists.'))
            elif os.path.isfile(os.path.join(self.path, convert_filename(self.cleaned_data['name']) + self.file_extension)):
                raise forms.ValidationError(_(u'The File already exists.'))
        return convert_filename(self.cleaned_data['name'])



class CodecChoiceField(forms.ChoiceField):
    """
    Select a sub directory in settings.MEDIA_ROOT
    
    >>> CodecChoiceField().choices # doctest: +ELLIPSIS
    [('utf8', 'utf_8'), ('ascii', 'ascii'), ... ('zlib_codec', 'zlib_codec')]
    """
    def __init__(self, *args, **kwargs):
        super(CodecChoiceField, self).__init__(*args, **kwargs)

        assert isinstance(PREFERED_CODECS, (tuple, list)), "FILEBROWSER_PREFERED_CODECS must be a tuple or list"
        self.prefered_codecs = PREFERED_CODECS
        self.choices = self._build_choices()

    def _get_codecs(self):
        return sorted(set(encodings.aliases.aliases.values()))

    def _build_choices(self):
        choices = []
        codecs = self._get_codecs()
        for prefered in self.prefered_codecs:
            prefered = prefered.replace("-", "")# FIXME
            if prefered in encodings.aliases.aliases:
                codec = encodings.aliases.aliases[prefered]
            elif prefered in codecs:
                codec = prefered
            else:
                if settings.DEBUG:
                    sys.stderr.write("Ignore unknwon codec %r\n" % prefered)
                continue

            choices.append((codec, prefered))

        existing_codec = [choice[1] for choice in choices]

        for codec in codecs:
            if codec not in existing_codec:
                choices.append((codec, codec))

        return choices



class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(), required=False)

class SelectEncodingForm(forms.Form):
    encoding = CodecChoiceField()



if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
