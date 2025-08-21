from itertools import chain

from django.db.models import Model, Field


class ModelDiff(object):
    ignore_fields = ["id"]

    def __init__(self, original: Model, new: Model = None):
        self.original_dict = to_dict(
            original, fields=[field.name for field in original._meta.fields], exclude=self.ignore_fields
        )
        if new:
            self.new_dict = to_dict(new, fields=[field.name for field in new._meta.fields], exclude=self.ignore_fields)
        else:
            self.new_dict = None
        self.diff = self._model_diff()
        self.model_diff_display = self._model_diff_display()

    def _model_diff(self):
        if self.new_dict:
            diffs = [(k, (v, self.new_dict[k])) for k, v in self.original_dict.items() if v != self.new_dict[k]]
        else:
            diffs = [(k, ("", v)) for k, v in self.original_dict.items() if v not in self.ignore_fields]
        return dict(diffs)

    def _model_diff_display(self):
        fields_display = []
        for key, value in self.diff.items():
            value_display = f"{value[0]} -> {value[1]}" if value[0] else value[1]
            fields_display.append(key + ": " + value_display)
        return "\n".join(fields_display)

    def has_changed(self):
        return bool(self.diff)

    def changed_fields(self):
        return self.diff.keys()


def to_dict(instance, fields=None, exclude=None):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        data[f.name] = str(value_from_object(f, instance))
    # for f in opts.many_to_many:
    #     data[f.name] = [str(i) for i in f.value_from_object(instance)]
    return data


def value_from_object(field: Field, instance: Model):
    return getattr(instance, field.name)
