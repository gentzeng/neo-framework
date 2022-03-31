import os.path as path

from django.db.models import Model
from django.utils.encoding import force_text

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.user == request.user


class RenameFilesModel(Model):
    """
    Abstract model implementing a two-phase save in order to rename
    `FileField` and `ImageField` filenames after saving.  This allows the
    final filenames to contain information like the primary key of the model.

    Example:

        class Photo(RenameFilesModel):
            file = models.ImageField(upload_to='uploads/temp')

            RENAME_FILES = {
                'file': {'dest': 'uploads/photos', 'keep_ext': True}
            }

        >>> photo = Photo(file='uploads/temp/photo.jpg')
        >>> photo.pk

        >>> photo.save()
        >>> photo.pk
        1
        >>> photo.file
        <ImageFieldFile: uploads/photos/1.jpg>

    If the 'dest' option is a callable, it will be called with the model
    instance (guaranteed to be saved) and the currently saved filename, and
    must return the new filename.  Otherwise, the filename is determined by
    'dest' and the model's primary key.

    If a file already exists at the resulting path, it is deleted.  This is
    desirable if the filename should always be the primary key, for instance.
    To avoid this behavior, write a 'dest' handler that results in a unique
    filename.

    If 'keep_ext' is True (the default), the extension of the previously saved
    filename will be appended to the primary key to construct the filename.
    The value of 'keep_ext' is not considered if 'dest' is a callable.

    """

    RENAME_FILES = {}

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False):
        rename_files = getattr(self, "RENAME_FILES", None)
        if rename_files:
            super(RenameFilesModel, self).save(force_insert, force_update)
            force_insert, force_update = False, True

            for field_name, options in rename_files.items():
                field = getattr(self, field_name)
                file_name = force_text(field)
                name, ext = path.splitext(file_name)
                keep_ext = options.get("keep_ext", True)
                final_dest = options["dest"]
                if callable(final_dest):
                    final_name = final_dest(self, file_name)
                else:
                    final_name = path.join(final_dest, "%s" % (self.pk,))
                    if keep_ext:
                        final_name += ext
                if file_name != final_name:
                    field.storage.delete(final_name)
                    field.storage.save(final_name, field)
                    field.storage.delete(file_name)
                    setattr(self, field_name, final_name)

        super(RenameFilesModel, self).save(force_insert, force_update)
