from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
# from .models import Sith, Recruit, Planet, Test
# from .forms import RecruitForm


class ObjectDetailMixin:
    model = None
    template = None
    answers = None

    def get(self, request, slug):
        obj = get_object_or_404(self.model, slug__iexact=slug)

        if self.answers:
            return render(request, self.template, context={self.model.__name__.lower(): obj,
                                                           'answers': obj.recruitanswers.all()})
        else:
            sith_visit = request.session.get('sith_visit', slug)
            request.session['sith_visit'] = slug

            print('===SITH Seccc: {} ===: {}'.format(sith_visit, slug))
            return render(request, self.template, context={self.model.__name__.lower(): obj,
                                                           'sith_visit': sith_visit})

            # return render(request, self.template, context={self.model.__name__.lower(): obj})


class ObjectCreateMixin:
    model_form = None
    template = None

    def get(self, request):
        form = self.model_form()
        return render(request, self.template, context={'form': form})

    def post(self, request):
        bound_form = self.model_form(request.POST)

        if bound_form.is_valid():
            new_obj = bound_form.save()
            return redirect(new_obj)
        return render(request, self.template, context={'form': bound_form})


class ObjectUpdateMixin:
    model = None
    model_form = None
    template = None

    def get(self, request, slug):
        obj = get_object_or_404(self.model, slug__iexact=slug)
        bound_form = self.model_form(instance=obj)
        return render(request, self.template, context={'form': bound_form, self.model.__name__.lower(): obj})

    def post(self, request, slug):
        obj = get_object_or_404(self.model, slug__iexact=slug)
        bound_form = self.model_form(request.POST, instance=obj)

        print('== bound_form in update: ', bound_form, '== dict:', bound_form.__dict__)

        if bound_form.is_valid():
            new_obj = bound_form.save()
            return redirect(new_obj)
        return render(request, self.template, context={'form': bound_form, self.model.__name__.lower(): obj})


        # try:
        #     obj.recruitanswers.all()
        #     print('==Mixin ===: ', self.answers, self.model, obj.recruitanswers.all(), type(obj))
        #     return render(request, self.template, context={self.model.__name__.lower(): obj,
        #                                                    'answers': obj.recruitanswers.all()})


        # except AttributeError:


# --------------------------------
# sith_visit = request.session.get('sith_visit', 'You must enter under the Sith ')
# num_visits = request.session.get('num_visits', 0)
# request.session['num_visits'] = num_visits + 1
# print('===Session_info: {} --Second-: {} '.format(sith_visit, num_visits))

# -----------------------
        # if self.model == 'Sith':
        #     sith_visit = request.session.get('sith_visit', slug)
        #     print('===SITH Seccc: '.format(sith_visit))
        #     return render(request, self.template, context={self.model.__name__.lower(): obj,
        #                                                    'sith_visit': sith_visit})

# print('==Mixin ===: ', obj.recruitanswers.all())
# sith_visit = request.session.get('sith_visit', slug)
# print('===RECR Seccc: {} ===: {}'.format(sith_visit, slug))

# obj.recruitanswers.all()

# --------------------------
    # def get(self, request, slug):
    #     # recruit = Recruit.objects.get(slug__iexact=slug)
    #     recruit = get_object_or_404(Recruit, slug__iexact=slug)
    #     bound_form = RecruitForm(instance=recruit)
    #     return render(request, 'si/recruit_update.html', context={'form': bound_form, 'recruit': recruit})
    #
    # def post(self, request, slug):
    #     recruit = get_object_or_404(Recruit, slug__iexact=slug)
    #     bound_form = RecruitForm(request.POST, instance=recruit)
    #
    #     if bound_form.is_valid():
    #         new_recruit = bound_form.save()
    #         return redirect(new_recruit)
    #     return render(request, 'si/recruit_update.html', context={'form': bound_form, 'recruit': recruit})
# -----------------------------------



# recruit = Recruit.objects.get(slug__iexact=slug)
# recruit = Recruit.objects.get(slug__exact=slug)
# recruit = get_object_or_404(Recruit, slug__iexact=slug)

