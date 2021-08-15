import datetime

# from accounts.models import CustomUser
from core.models import BaseModel
from core.utils import generate_uuid

from dateutil.relativedelta import relativedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import utc


class Exam(BaseModel):
    QUESTION_MIN_LIMIT = 3
    QUESTION_MAX_LIMIT = 20

    class LEVEL(models.IntegerChoices):
        BASIC = 0, 'Basic'
        MIDDLE = 1, 'Middle'
        ADVANCED = 2, 'Advanced'

    uuid = models.UUIDField(default=generate_uuid, db_index=True, unique=True)
    title = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)
    level = models.PositiveSmallIntegerField(choices=LEVEL.choices, default=LEVEL.BASIC)

    def questions_count(self):
        return self.questions.count()

    def __str__(self):
        return self.title


class Question(BaseModel):
    exam = models.ForeignKey(Exam, related_name='questions', on_delete=models.CASCADE)
    order_num = models.PositiveSmallIntegerField()
    text = models.CharField(max_length=2048)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=1024)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Result(BaseModel):
    class STATE(models.IntegerChoices):
        NEW = 0, "New"
        FINISHED = 1, "Finished"

    user = models.ForeignKey(get_user_model(), related_name='results', on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, related_name='results', on_delete=models.CASCADE)
    state = models.PositiveSmallIntegerField(default=STATE.NEW, choices=STATE.choices)
    uuid = models.UUIDField(default=generate_uuid, db_index=True, unique=True)
    current_order_number = models.PositiveSmallIntegerField(null=True)
    num_correct_answers = models.PositiveSmallIntegerField(default=0)
    num_incorrect_answers = models.PositiveSmallIntegerField(default=0)
    success_rate = models.PositiveSmallIntegerField(default=0)
    score = models.PositiveSmallIntegerField(default=0)
    time_diff = models.CharField(max_length=30, null=True)

    def update_result(self, order_number, question, selected_choices):
        correct_choice = [choice.is_correct for choice in question.choices.all()]
        correct_answer = True
        for z in zip(selected_choices, correct_choice):
            correct_answer &= (z[0] == z[1])

        self.num_correct_answers += int(correct_answer)
        self.num_incorrect_answers += 1 - int(correct_answer)
        self.success_rate = (self.num_correct_answers / (self.num_correct_answers + self.num_incorrect_answers)) * 100
        self.score = 0 if (self.num_correct_answers - self.num_incorrect_answers) <= 0 \
            else self.num_correct_answers - self.num_incorrect_answers
        time_diff = relativedelta(datetime.datetime.utcnow().replace(tzinfo=utc), self.create_timestamp)
        self.time_diff = "%dh:%dm:%ds" % (time_diff.hours, time_diff.minutes, time_diff.seconds)

        if order_number == question.exam.questions_count():
            self.state = self.STATE.FINISHED

            if (self.num_correct_answers + self.num_incorrect_answers) // 2 == 0 and self.results.rating > 0:
                self.results.rating += 1
            else:
                self.results.rating -= 1

        self.save()
