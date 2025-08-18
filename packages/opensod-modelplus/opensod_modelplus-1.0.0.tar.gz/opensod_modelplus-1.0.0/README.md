# opensod-modelplus

Django application `modelplus` defines reusable abstract models that can be used to quickly and consistently add common fields and their functionalities to your models.


## Installation

If using Astral's uv for virtual environment and project dependencies:

```
$ uv add opensod-modelplus
```

Or, with pip in your virtual environment:

```
$ pip install opensod-modelplus
```


## Quick setup

Add application to `settings.py`:

```
INSTALLED_APPS = [
    ...
    "modelplus",
]
```

If using abstract model `UserstampableModel`, `CurrentUserMiddleware` has be added to `settings.py` after `django.contrib.auth.middleware.AuthenticationMiddleware`:

```
MIDDLEWARE = [
    ...
    "modelplus.middleware.CurrentUserMiddleware",
]
```


## Abstract models

### ActivatableModel and ActivatableQuerySet

Frequently objects need to have some kind of *active* flag, because deleting records is not an option.

Abstract model `ActivatableModel` defines `is_active` field for this purpose, which is `True` by default.

`ActivatableQuerySet` is a corresponding QuerySet that defines filters `active` and `inactive` for models which have `ActivatableModel` as parent.

```
class MyModel(ActivatableModel):
    ...

    objects = ActivatableQueryset.as_manager()
```

or:

```
class MyQueryset(ActivatableQueryset):
    ...


class MyModel(ActivatableModel):
    ...

    objects = MyQueryset.as_manager()
```

### CancellableModel and CancellableQuerySet

Sometimes there is a need to mark some objects as cancelled.

Abstract model `CancellableModel` defines field `is_cancelled`, which is `False` by default.

`CancellableQuerySet` is a corresponding QuerySet that defines filters `cancelled` and `not_cancelled` for models which have `CancellableModel` as parent.

```
class MyModel(CancellableModel):
    ...

    objects = CancellableQueryset.as_manager()
```

or:

```
class MyQueryset(CancellableQueryset):
    ...


class MyModel(CancellableModel):
    ...

    objects = MyQueryset.as_manager()
```

### CancellationModel and CancellationQuerySet

Sometimes there is a need to provide some additional information for cancelled objects.

Abstract model `CancellationModel` defines fields `cancelled_at`, `cancelled_by` and `cancellation_reason`, while `CancellationQuerySet` is a corresponding QuerySet that defines filters `cancelled`, `not_cancelled` and `cancelled_by`.

```
class MyModel(CancellationModel):
    ...

    objects = CancellationQueryset.as_manager()
```

or:

```
class MyQueryset(CancellationQueryset):
    ...


class MyModel(CancellationModel):
    ...

    objects = MyQueryset.as_manager()
```

### LockableModel and LockableQuerySet

Sometimes there is a need to mark some objects as locked (not available for further editing).

Abstract model `LockableModel` defines field `is_locked`, which is `False` by default.

`LockableQuerySet` is a corresponding QuerySet that defines filters `locked` and `unlocked` for models which have `LockableModel` as parent.

```
class MyModel(LockableModel):
    ...

    objects = LockableQueryset.as_manager()
```

or:

```
class MyQueryset(LockableQueryset):
    ...


class MyModel(LockableModel):
    ...

    objects = MyQueryset.as_manager()
```

### TimestampableModel

Sometimes there is a need to record when are objects created and last updated.

Abstract model `TimestampableModel` defines fields `created_at` and `updated_at` which store a timestamp when the model instance was created and last updated.

Timestamps are populated using `pre_save` signal timestampable. Unfortunately, creating and updating objects in bulk doesn't update created_by and modified_by fields, since `pre_save` is not called.

```
class MyModel(TimestampableModel):
    ...

```

### UserstampableModel and UserstampableQuerySet

Sometimes there is a need to record who has created and last updated an object.

Abstract model `UserstampableModel` defines fields `created_by` and `updated_by` for storing a `User` instance which created and last updated the model instance. Deletion of the referenced created_by and modified_by objects is protected.

`UserstampableQuerySet` is a corresponding QuerySet that defines filters `created_by` and `updated_by`.

```
class MyModel(UserstampableModel):
    ...

    objects = UserstampableQueryset.as_manager()
```

or:

```
class MyQueryset(UserstampableQueryset):
    ...


class MyModel(UserstampableModel):
    ...

    objects = MyQueryset.as_manager()
```

This abstract model uses `CurrentUserMiddleware` which must be added to `settings.MIDDLEWARE` after `django.contrib.auth.middleware.AuthenticationMiddleware`.


## Translations

Package comes with translations to:

- Croatian (hr)

To create translations for new language:

```bash
$ git clone git@gitlab.com:opensod-modelplus.git
$ cd opensod-modelplus.git
$ uv sync
$ uv run django-admin makemessages -l language_code
# edit django.po file for the new language
$ make compilemessages
# build will automatically compile messages
$ uv build
```
