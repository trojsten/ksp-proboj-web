from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import BadRequest, PermissionDenied
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DetailView, ListView

from proboj.bots.forms import BotForm, BotUploadForm, CompileUploadForm
from proboj.bots.mixins import BotMixin, BotQuerySetMixin
from proboj.bots.models import Bot, BotVersion
from proboj.games.mixins import GameMixin
from proboj.matches.models import Match


class BotListView(LoginRequiredMixin, BotQuerySetMixin, GameMixin, ListView):
    template_name = "bots/list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["can_create"] = len(self.object_list) < self.game.max_bots
        return ctx


class BotDetailView(LoginRequiredMixin, BotQuerySetMixin, GameMixin, DetailView):
    template_name = "bots/detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["versions"] = self.object.botversion_set.all()
        ctx["matches"] = (
            Match.objects.filter(
                matchbot__bot_version__bot=self.object, finished_at__isnull=False
            )
            .order_by("-finished_at")
            .prefetch_related(
                "matchbot_set",
                "matchbot_set__bot_version",
                "matchbot_set__bot_version__bot",
            )
            .all()[0:15]
        )
        ctx["can_upload"] = self.game.is_open
        return ctx


class BotCreateView(UserPassesTestMixin, GameMixin, CreateView):
    template_name = "bots/create.html"
    form_class = BotForm

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False

        user_bots = Bot.objects.filter(game=self.game, user=self.request.user).count()
        return user_bots < self.game.max_bots

    def get_success_url(self):
        return reverse(
            "bot_detail", kwargs={"game": self.game.id, "pk": self.object.id}
        )

    def form_valid(self, form):
        self.object: Bot = form.save(commit=False)
        self.object.user = self.request.user
        self.object.game = self.game
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


class BotUploadView(UserPassesTestMixin, BotMixin, CreateView):
    template_name = "bots/upload.html"
    form_class = BotUploadForm

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.game.is_open

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


class BotDownloadView(LoginRequiredMixin, BotMixin, View):
    def get(self, *args, **kwargs):
        version: BotVersion = get_object_or_404(
            BotVersion.objects.filter(bot=self.bot), id=kwargs["pk"]
        )
        return FileResponse(version.sources)


class BotLogView(LoginRequiredMixin, BotMixin, DetailView):
    template_name = "bots/compile_log.html"

    def get_queryset(self):
        return BotVersion.objects.filter(bot=self.bot)


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
