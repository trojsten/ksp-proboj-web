from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest, PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DetailView, ListView

from proboj.bots.forms import BotUploadForm, CompileUploadForm
from proboj.bots.mixins import BotMixin, BotQuerySetMixin
from proboj.bots.models import BotVersion
from proboj.games.mixins import GameMixin


class BotListView(LoginRequiredMixin, BotQuerySetMixin, GameMixin, ListView):
    template_name = "bots/list.html"


class BotDetailView(LoginRequiredMixin, BotQuerySetMixin, GameMixin, DetailView):
    template_name = "bots/detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["versions"] = self.object.botversion_set.all()
        return ctx


class BotUploadView(LoginRequiredMixin, BotMixin, CreateView):
    template_name = "bots/upload.html"
    form_class = BotUploadForm

    def get_success_url(self):
        return reverse(
            "bot_detail", kwargs={"game": self.bot.game_id, "pk": self.bot.id}
        )

    def form_valid(self, form):
        version: BotVersion = form.save(commit=False)
        version.bot = self.bot
        version.save()

        version.compile()

        self.object = version
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(csrf_exempt, name="dispatch")
class CompileUploadView(View):
    def post(self, *args, **kwargs):
        version = get_object_or_404(
            BotVersion, secret=kwargs["secret"], bot_id=kwargs["bot"]
        )
        if version.compiled:
            raise PermissionDenied()

        form = CompileUploadForm(self.request.POST, self.request.FILES)
        if not form.is_valid():
            raise BadRequest()

        if form.cleaned_data["successful"]:
            version.compiled = form.cleaned_data["output"]
        version.compile_log = form.cleaned_data["log"]
        version.save()

        return HttpResponse("ok")
