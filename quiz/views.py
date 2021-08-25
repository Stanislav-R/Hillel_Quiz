from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.views.generic.list import MultipleObjectMixin

from .forms import ChoicesFormSet
from .models import Exam, Question, Result


class ExamListView(LoginRequiredMixin, ListView):
    model = Exam
    template_name = 'exams/list.html'
    context_object_name = 'exams'


class ExamDetailView(LoginRequiredMixin, DetailView, MultipleObjectMixin):
    model = Exam
    template_name = 'exams/details.html'
    context_object_name = 'exam'
    pk_url_kwarg = 'uuid'
    paginate_by = 3

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        # return self.get_queryset().get(uuid=uuid)
        return self.model.objects.get(uuid=uuid)

    def get_context_data(self, **kwargs):
        # context = super().get_context_data(**kwargs)
        # context['result_list'] = Result.objects.filter(
        #     exam=self.get_object(),
        #     user=self.request.user
        # ).order_by('state')
        context = super().get_context_data(object_list=self.get_queryset(), **kwargs)

        return context

    def get_queryset(self):
        return Result.objects.filter(
            exam=self.get_object(),
            user=self.request.user
        ).order_by('state')


class ExamResultCreateView(LoginRequiredMixin, CreateView):
    def post(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        result = Result.objects.create(
            user=request.user,
            exam=Exam.objects.get(uuid=uuid),
            state=Result.STATE.NEW,
            current_order_number=0
        )

        result.save()

        return HttpResponseRedirect(reverse(
            'quizzes:question',
            kwargs={
                'uuid': uuid,
                'result_uuid': result.uuid,
                # 'order_number': 1,
            }
        ))


class ExamQuestionView(LoginRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        # order_number = kwargs.get('order_number')
        result = Result.objects.get(uuid=kwargs['result_uuid'])

        question = Question.objects.get(
            exam__uuid=uuid,
            # order_num=order_number
            order_num=result.current_order_number + 1
        )

        choices = ChoicesFormSet(queryset=question.choices.all())

        return render(
            request,
            'exams/question.html',
            context={
                'question': question,
                'choices': choices
            }
        )

    def post(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        result_uuid = kwargs.get('result_uuid')
        result = Result.objects.get(uuid=result_uuid)
        # order_number = kwargs.get('order_number')
        order_number = result.current_order_number + 1

        question = Question.objects.get(
            exam__uuid=uuid,
            order_num=order_number
        )

        choices = ChoicesFormSet(data=request.POST)
        selected_choices = ['is_selected' in form.changed_data for form in choices.forms]
        if selected_choices.count(True) == 0:
            messages.warning(request, 'Выберите один или несколько правильных ответов')
            order_number = result.current_order_number
        elif selected_choices.count(True) == len(selected_choices):
            messages.warning(request, 'Все ответы не могут быть правильными')
            order_number = result.current_order_number
        else:
            result = Result.objects.get(uuid=result_uuid)
            result.update_result(order_number, question, selected_choices)

        if result.state == Result.STATE.FINISHED:
            return HttpResponseRedirect(reverse(
                'quizzes:result_details',
                kwargs={
                    'uuid': uuid,
                    'result_uuid': result.uuid,
                }
            ))

        return HttpResponseRedirect(reverse(
            'quizzes:question',
            kwargs={
                'uuid': uuid,
                'result_uuid': result.uuid,
                # 'order_number': order_number + 1,
            }
        ))


class ExamResultDetailView(LoginRequiredMixin, DetailView):
    model = Result
    template_name = 'results/details.html'
    context_object_name = 'result'
    pk_url_kwarg = 'uuid'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('result_uuid')
        return self.get_queryset().get(uuid=uuid)


class ExamResultUpdateView(LoginRequiredMixin, UpdateView):
    # permission_required = ['accounts.view_statistics']

    def get(self, request, *args, **kwargs):
        uuid = kwargs['uuid']
        result_uuid = kwargs['result_uuid']
        user = request.user

        result = Result.objects.get(
            user=user,
            uuid=result_uuid
        )

        return HttpResponseRedirect(reverse(
            'quizzes:question',
            kwargs={
                'uuid': uuid,
                'result_uuid': result.uuid,
                # 'order_number': result.current_order_number + 1,
            }
        ))


class ExamResultDeleteView(LoginRequiredMixin, DeleteView):
    def get(self, request, *args, **kwargs):
        result_uuid = kwargs['result_uuid']
        user = request.user

        result = Result.objects.get(
            user=user,
            uuid=result_uuid
        )
        result.delete()

        return HttpResponseRedirect(reverse('quizzes:result_list'))


class ExamResultListView(LoginRequiredMixin, ListView):
    model = Result
    template_name = 'results/list.html'
    context_object_name = 'results'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        return Result.objects.filter(user=user)
