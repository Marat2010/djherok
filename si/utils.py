from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
# from .models import Sith, Recruit, Planet, Test


class ObjectDetailMixin:
    model = None
    template = None

    def get(self, request, slug):
        obj = get_object_or_404(self.model, slug__iexact=slug)
        return render(request, self.template, context={self.model.__name__.lower(): obj})


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

