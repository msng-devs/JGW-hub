from django.db import models

from djongo import models


class MultiSelectSurvey(models.Model):
    _id = models.ObjectIdField()

    class Meta:
        db_table = 'multi_select_survey'

class SingleSelectSurvey(models.Model):
    _id = models.ObjectIdField()

    class Meta:
        db_table = 'single_select_survey'

class ShortAnswerSurvey(models.Model):
    _id = models.ObjectIdField()

    class Meta:
        db_table = 'short_answer_survey'

