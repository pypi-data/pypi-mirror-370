from string import Formatter
from typing import Any

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Prompt(models.Model):
    name = models.CharField(max_length=55)
    template = models.TextField()
    input_variables = ArrayField(models.CharField(max_length=255), default=list, blank=True)

    history = HistoricalRecords(cascade_delete_history=False)

    def __str__(self):
        return self.name

    def validate_input_variables(self) -> None:
        try:
            dummy_inputs = dict.fromkeys(self.input_variables, 'foo')
            Formatter().format(self.template, **dummy_inputs)
        except ValueError as e:
            raise ValidationError(f'Invalid input variables: {e}')

    def format(self, **kwargs: Any) -> str:
        default_variables = self.get_default_input_variables()
        missing_variables = set(self.input_variables) - set(default_variables.keys()) - set(kwargs.keys())
        if missing_variables:
            raise ValidationError(f'Missing input variables: {missing_variables}')

        # Provided variables take precedence over default variables
        variables = {key: kwargs.get(key) or default_variables.get(key) for key in self.input_variables}
        return self.template.format(**variables)

    @classmethod
    def get_default_input_variables(cls) -> dict:
        return {'date': timezone.now().strftime('%Y-%m-%d')}
