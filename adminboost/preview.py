from django import forms

from django.conf import settings
from django.contrib.admin.options import InlineModelAdmin
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from easy_thumbnails.files import get_thumbnailer, Thumbnailer
from easy_thumbnails.exceptions import InvalidImageFormatError

# Admin classes ------------------------------------------------------------


class PreviewInline(InlineModelAdmin):
    readonly_fields = ('preview',)

    def get_fieldsets(self, request, obj=None):
        """ Move preview field to front if generating default fieldset """
        if self.declared_fieldsets:
            return self.declared_fieldsets
        form = self.get_formset(request, obj).form
        fields = list(form.base_fields) + list(
            self.get_readonly_fields(request, obj))
        # implementation identical to 1.4 ModelAdmin.get_fieldsets apart from:
        fields.remove('preview')
        fields.insert(0, 'preview')
        return [(None, {'fields': fields})]

    def preview(self, obj):
        if not(obj or obj.pk):
            return u''
        try:
            images = obj.get_preview_images()
        except AttributeError:
            raise ImproperlyConfigured(
                "PreviewInline only works with models which provide a "
                "get_preview_images method."
            )
        options = dict(size=(120, 120), crop=False)
        html = u'<div class="adminboost-preview">'
        for image in images:
            thumbnail = get_thumbnailer(image.file).get_thumbnail(options)
            if isinstance(image.file, Thumbnailer):
                image_url = default_storage.url(force_unicode(image.file.name))
            else:
                image_url = image.file.url
            html += (
                u'<div class="adminboost-preview-thumbnail">'
                u'<a href="%(image_url)s" target="_blank">'
                u'<img src="%(thumbnail_url)s"/></a></div>' % {
                    'image_url': image_url,
                    'thumbnail_url': thumbnail.url
                }
            )
        try:
            help_text = obj.get_image_preview_help_text()
        except AttributeError:
            pass
        else:
            html += u'<p class="help">%s</p>' % force_unicode(help_text)
        html += u'</div>'
        return mark_safe(unicode(html))


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
        from easy_thumbnails.files import get_thumbnailer
        from easy_thumbnails.files import Thumbnailer
        if attrs is None:
            attrs = {}

        if not self.form.preview_instance_required or self.instance is not None:
            images = self.form.get_images(self.instance)
            options = dict(size=(120, 120), crop=False)
            html = u'<div class="adminboost-preview">'
            for image in images:
                try:
                    thumbnail = get_thumbnailer(image.file).get_thumbnail(
                        options)
                except InvalidImageFormatError:
                    continue
                if isinstance(image.file, Thumbnailer):
                    image_url = default_storage.url(force_unicode(image.file.name))
                else:
                    image_url = image.file.url
                html += (
                    u'<div class="adminboost-preview-thumbnail">'
                    u'<a href="%(image_url)s" target="_blank">'
                    u'<img src="%(thumbnail_url)s"/></a></div>' % {
                        'image_url': image_url,
                        'thumbnail_url': thumbnail.url
                    }
                )
            help_text = self.form.get_preview_help_text(self.instance)
            if help_text is not None:
                html += u'<p class="help">%s</p>' % force_unicode(help_text)
            html += u'</div>'
            return mark_safe(unicode(html))
        else:
            return u''
        
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
            'all': ("%sadminboost/styles.css" % settings.STATIC_URL,)
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
