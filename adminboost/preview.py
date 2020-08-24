from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.contrib.admin.options import InlineModelAdmin
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.encoding import force_text

from easy_thumbnails.files import get_thumbnailer, Thumbnailer
from easy_thumbnails.exceptions import InvalidImageFormatError

# Admin classes ------------------------------------------------------------


class PreviewInline(InlineModelAdmin):
    """
    The 'preview' "field" should be present in the ModelForm used
    (see ModelForm classes below), but won't be actually rendered unless
    picked up via django.contrib.admin.helpers.InlineAdminFormSet.fields.

    Injecting it via get_fieldsets is a relatively straightforward way of
    enabling this, and bypasses Django's validation system for checking
    field names that actually exist.
    """

    def get_fieldsets(self, request, obj=None):
        """ Identical to standard code apart from inserting ['preview'] """
        if self.declared_fieldsets:
            return self.declared_fieldsets
        form = self.get_formset(request, obj).form
        fields = ['preview'] + list(form.base_fields) + list(
            self.get_readonly_fields(request, obj)
        )
        return [(None, {'fields': fields})]


class PreviewStackedInline(PreviewInline):
    template = 'admin/edit_inline/stacked.html'


class PreviewTabularInline(PreviewInline):
    template = 'admin/edit_inline/tabular.html'


# Form classes ------------------------------------------------------------


class PreviewWidget(forms.widgets.Input):
    is_hidden = False
    input_type = 'text'

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        self.form = kwargs.pop('form', None)
        super(PreviewWidget, self).__init__(*args, **kwargs)


class ImagePreviewWidget(PreviewWidget):

    def render(self, name, data, attrs=None):

        if not self.form.preview_instance_required or self.instance is not None:
            images = self.form.get_images(self.instance)
            options = dict(size=(120, 120), crop=False)
            html = '<div class="adminboost-preview">'
            for image in images:
                try:
                    thumbnail = get_thumbnailer(image.file).get_thumbnail(options)
                except InvalidImageFormatError:
                    continue
                if isinstance(image.file, Thumbnailer):
                    image_url = default_storage.url(force_text(image.file.name))
                else:
                    image_url = image.file.url
                html += (
                    '<div class="adminboost-preview-thumbnail">'
                    '<a href="%(image_url)s" target="_blank">'
                    '<img src="%(thumbnail_url)s"/></a></div>' % {
                        'image_url': image_url,
                        'thumbnail_url': thumbnail.url
                    }
                )
            help_text = self.form.get_preview_help_text(self.instance)
            if help_text is not None:
                html += '<p class="help">%s</p>' % force_text(help_text)
            html += '</div>'
            return mark_safe(str(html))
        else:
            return ''
        
class PreviewField(forms.Field):
    """ Dummy "field" to provide preview thumbnail. """
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        self.form = kwargs.pop('form', None)
        kwargs['widget'] = self.form.preview_widget_class(
            instance=self.instance, form=self.form)
        super(PreviewField, self).__init__(*args, **kwargs)


class PreviewInlineForm(forms.ModelForm):
    # If True, the widget will only be displayed if an
    # instance of the model exists (i.e. the object
    # has already been saved at least once).
    preview_instance_required = True

    def __init__(self, *args, **kwargs):
        super(PreviewInlineForm, self).__init__(*args, **kwargs)
        preview_field = PreviewField(
            label = _('Preview'), required=False,
            instance = kwargs.get('instance', None), form=self)
        self.fields.insert(0, 'preview', preview_field)
        self.base_fields.insert(0, 'preview', preview_field)

    class Media:
        css = {
            'all': ("%sadminboost/styles.css" % django_settings.STATIC_URL,)
        }


class ImagePreviewInlineForm(PreviewInlineForm):

    preview_widget_class = ImagePreviewWidget

    def get_preview_help_text(self, instance):
        """
        Returns text that should be displayed under
        the image(s). Useful for example to display a
        disclaimer about the preview
        """

    def get_images(self, instance): # TODO: Rename to get_preview_images
        """
        This needs to be specified by the child
        form class, as we cannot anticipate the name of the image model field
        """
        raise NotImplementedError()
