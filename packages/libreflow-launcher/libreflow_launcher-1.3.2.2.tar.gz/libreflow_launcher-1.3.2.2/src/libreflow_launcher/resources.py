'''
Generic file resouces repository.

This package provide a way to register some folders under a given name
(:meth:`add_folder`) and later retreive files by their basename and
registered folder name (:meth:`get`).

When registering a folder with the same name as another one, the lookup will
favorize the last one and fall back to the first one.

This way you can extend and/or override the resources available under a given
folder name.

You can deal with any kind of files, but in the case of images there are a couple
helper functions: :meth:`get_pixmap()` and :meth:`get_icon()`

Every search result is cached so disk access is minimized. You don't need to
cache your resources next to their usage code, just can keep calling
``resources.get()`` as much as you want.

You can inspect the available resources with :meth:`get_folder_names()`,
:meth:`list_folder()` and :meth:`list_folder_paths()`

.. note::

    Files starting with an underscore ``_`` are ignored.

'''

import logging
import os
import glob


_PATHS = {}
_CACHE = {}
_PIXCACHE = {}
_ICONCACHE = {}


class ResourcesError(Exception):
    '''
    Raised when the ``folder_name`` is unknown.
    '''


class NotFoundError(ResourcesError):
    '''
    Raised when the the resource was not found.
    Note that this is a :class:`ResourcesError` too.
    '''


def add_folder(name, path):
    '''
    Register a folder to the search path.

    The ``name`` will be used to access files.

    You can use :meth:`get_folder_names` to get a list of all declared names.

    The ``path`` can be a file inside the folder
    to register, or the path of the folder itself.

    If a folder with the same name was previously added, the
    files from the last one overrides the previous one but
    the previous files not available in the last one are
    still accessible.

    In other words: the last call overrides and extends the previous ones.

    Typical resource declaration:

    .. code-block:: python
        :caption: my_studio/icons/emoji/__init__.py

        # We're in a package folder containing some png files
        # Every file will be accessible, and overrides previous
        # declarations of 'icons.emoji' files
        import kabaret.app.resources
        kabaret.app.resources.add_folder('icons.emoji', __file__)

    .. code-block:: python
        :caption: my_studio/gui.py

        # Be sure to have the resource modules imported at least once
        # This is typically done in the module defining your session
        from my_studio.icons import emoji

    Typical resource access:

    .. code-block:: python
        :caption: my_studio/flows/my_dope_flow/__init__.py

        # Use anywhere
        from kabaret.app import resources
        icon = resources.get('icons.emoji', 'sunglasses')

    .. seealso::

        :meth:`get_icon()`
        :meth:`get_pixmap()`

    '''
    global _PATHS, _CACHE

    if not os.path.isdir(path):
        path = os.path.dirname(path)

    if name not in _PATHS:
        _PATHS[name] = []
    _PATHS[name].insert(0, path)

    # Remove cache for this folder name:
    if name in _CACHE:
        _CACHE.pop(name)


def get_folder_names():
    '''
    Returns a list of available folder names.
    '''
    global _PATHS
    return list(_PATHS)


def list_folder(folder_name):
    '''
    Returns a list of resource names available in ``folder_name``.
    '''
    global _PATHS

    EXCLUDE_LIST = ('Thumbs.db',)

    folder_name = folder_name.lower()

    ret = set()
    for path in _PATHS[folder_name]:
        ret.update(
            [
                name.split('.', 1)[0]
                for name in os.listdir(path)
                if not name.startswith('_')
                if not name.startswith('.')
                and name not in EXCLUDE_LIST
            ]
        )
    return sorted(ret)


def list_folder_paths(folder_name):
    '''
    Return a list of list of file_name for ``folder_name``.
    (overrides come first)
    '''
    global _PATHS

    folder_name = folder_name.lower()

    ret = []
    for path in _PATHS[folder_name]:
        ret.append(sorted(
            [
                name.split('.', 1)[0]
                for name in os.listdir(path)
                if not name.startswith('_')
            ]
        ))
    return ret


def get(folder_name, file_name):
    '''
    Returns the file named ``file_name`` in the 
    folder registered as  ``folder_name``.
    '''
    global _PATHS, _CACHE

    # avoid case sensitive look-up in order to have the same
    # behavior in win$ and Linux:
    folder_name = folder_name.lower()
    file_name = file_name.lower()

    cache_key = (folder_name, file_name)
    if cache_key in _CACHE:
        if _CACHE[cache_key]:
            return _CACHE[cache_key]
        else:
            raise NotFoundError("Resource not found: " + repr(cache_key))

    try:
        path_list = _PATHS[folder_name]
    except KeyError:
        raise ResourcesError(
            "Unknown resource folder " +
            repr(folder_name) + ". (Did you install it first?)"
        )

    files = None
    for path in path_list:
        files = glob.glob(
            os.path.join(
                path,
                file_name + ('.' not in file_name and ".*" or "")
            )
        )
        if files:
            break
    if not files:
        _CACHE[cache_key] = None
        raise NotFoundError("Resource not found: " + repr(cache_key))
    if len(files) > 1:
        logging.getLogger('kabaret.resources').warn(
            "Several resources found for: " + repr(cache_key))

    _CACHE[cache_key] = files[0]
    return files[0]


def get_pixmap(folder_name, pixmap_name):
    '''
    Same as :meth:`get()`, but returns a QPixmap
    '''
    global _PIXCACHE

    path = get(folder_name, pixmap_name)
    if path in _PIXCACHE:
        return _PIXCACHE[path]

    from qtpy import QtGui

    ret = QtGui.QPixmap(path)
    _PIXCACHE[path] = ret

    return ret


def get_icon(icon_ref, for_widget=None, disabled_ref=None, color=None):
    '''
    Same as :meth:`get_pixmap()`, but returns a QIcon

    If ``icon_ref`` is an **int**,  ``for_widget`` must not be **None**
    and its current QStyle will be used to return
    the QIcon pointed by icon_ref.

    If icon_ref is a 2D tuple, it is used to call
    :meth:`get_pixmap(*icon_ref)`

    If icon_ref is a file path, an icon is created from this file.

    if disable_ref is not None, it must be a 2D tuple suitable for
    :meth:`get_pixmap(*disabled_ref)` and will be used as the "disabled"
    state of the icon.

    Warning: calls with different disabled_ref for the same icon_ref has 
    undefined behavior.

    '''
    if isinstance(icon_ref, int):
        style = for_widget.style()
        return style.standardIcon(icon_ref)

    global _ICONCACHE
    if icon_ref in _ICONCACHE:
        if color == _ICONCACHE[icon_ref][1]:
            return _ICONCACHE[icon_ref][0]

    from qtpy import QtGui

    pix = None
    if color is not None:
        image = QtGui.QImage(get(*icon_ref))

        for x in range(image.width()):
            for y in range(image.height()):
                pcolor = image.pixelColor(x, y)
                if pcolor.alpha() > 0:
                    n_color = QtGui.QColor(color)
                    n_color.setAlpha(pcolor.alpha())
                    image.setPixelColor(x, y, n_color)
        
        pix = QtGui.QPixmap.fromImage(image)
    else:
        try:
            pix = get_pixmap(*icon_ref)
        except Exception:
            try:
                if os.path.isfile(icon_ref):
                    pix = QtGui.QPixmap(icon_ref)
            except TypeError:
                pass

    if pix is None:
        raise NotFoundError('Cannot find icon for %r' % (icon_ref,))
    
    icon = QtGui.QIcon(pix)

    if disabled_ref is not None:
        pix = get_pixmap(*disabled_ref)
        icon.addPixmap(pix, mode=icon.Disabled)

    _ICONCACHE[icon_ref] = [icon, color]
    return icon
