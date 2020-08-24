Sortable inline templatetag
===========================

Functionality
    Adding this templatetag to a ``change_form`` makes inline sortable.

Assumptions
    Inlines have integer order field. Inlines are sorted by the ``order``
    attribute by default.

Usage example
    In the ``change_form.html`` of our model which has inlines "Feature",
    "HomeFullWidthFeature" etc::

        {% load adminboost_tags %}

        {% block extrahead %}
            {{ block.super }}
            {% sortable_inlines "feature_set" %}
            {% sortable_inlines "homefullwidthfeature_set" %}
        {% endblock %}


Edit link templatetag
=====================

Functionality
    This templatetag outputs an icon which links to the Django Admin change
    page for a specific object.

Assumptions
    The object's Model is registered with Django's Admin. A user is logged-in
    and has permission to edit the object.

Arguments
    object
        The object which you wish to link to.
    label (optional)
        Text to display in a span element prepended to the edit icon.

Usage example
    ::

        {% load adminboost_tags %}

        {% edit_link object %}

        {% edit_link object 'Edit this object' %}


Image preview
=============

TODO

Custom thumbnail engine
-----------------------

Supports ``easy_thumbnails`` and ``sorl-thumbnail`` out of the box. You can
add support for custom thumbnail engines with the ``ADMINBOOST_PREVIEW_ENGINE``
setting


Settings
========

``ADMINBOOST_PREVIEW_ENGINE`` (string)
    ``adminboost.preview.ThumbnailEngine`` subclass to use when generating
    thumbnails. Should be a dotted path.

``ADMINBOOST_PREVIEW_SIZE`` (tuple)
    Default dimensions for previews when ``preview_size`` argument is not given
    to ``PreviewImageField`` field class. Should be a ``(width, height)``
    tuple.


Backward incompatible changes
=============================

01/12/2010
----------

* The syntax used to be ``{% sortable_inlines "Image" %}``. It is now
  ``{% sortable_inlines "image_set" %}``.

* If you used multiple inlines, ``{% sortable_inlines "Image","Video" %}`` is
  now ``{% sortable_inlines "image_set" "video_set" %}``.
