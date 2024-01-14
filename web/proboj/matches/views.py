import os.path
from zipfile import BadZipFile, ZipFile

from django.core.exceptions import BadRequest
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.core.signing import BadSignature, Signer
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView

from proboj.games.mixins import GameMixin
from proboj.matches.forms import MatchUploadForm
from proboj.matches.generator import generate_matches
from proboj.matches.models import Match, MatchBot


class MatchListView(GameMixin, ListView):
    template_name = "matches/list.html"
    paginate_by = 200

    def get_queryset(self):
        return (
            Match.objects.filter(game=self.game)
            .order_by("-created_at")
            .select_related("configuration")
            .prefetch_related("matchbot_set", "matchbot_set__bot_version__bot")
        )


class MatchListApiView(GameMixin, View):
    template_name = "matches/list.html"

    def get(self, request, *args, **kwargs):
        matches = (
            Match.objects.filter(game=self.game)
            .order_by("-created_at")
            .select_related("configuration")
            .prefetch_related("matchbot_set", "matchbot_set__bot_version__bot")
        )
        paginator = Paginator(matches, 200)
        page = paginator.get_page(request.GET.get("page"))
        data = []
        for match in page:
            data.append(
                {
                    "id": match.id,
                    "configuration": match.configuration.name,
                    "finished_at": match.finished_at,
                    "score": {
                        s.bot_version.bot.name: s.score
                        for s in match.matchbot_set.all()
                    },
                    "observer_log": match.observer_log.url
                    if match.observer_log
                    else None,
                    "server_log": match.server_log.url if match.server_log else None,
                }
            )
        return JsonResponse({"matches": data})


class MatchDetailView(GameMixin, DetailView):
    template_name = "matches/detail.html"

    def get_queryset(self):
        return Match.objects.filter(game=self.game).prefetch_related(
            "matchbot_set", "matchbot_set__bot_version__bot"
        )


@method_decorator(csrf_exempt, name="dispatch")
class MatchUploadView(View):
    @transaction.atomic
    def post(self, *args, **kwargs):
        signer = Signer()
        try:
            match_id = signer.unsign_object(kwargs["secret"])["match"]
        except (BadSignature, KeyError):
            raise Http404()

        match: Match = get_object_or_404(
            Match.objects.filter(is_finished=False), id=match_id
        )
        bots: dict[str, MatchBot] = {
            b.bot_version.bot.name: b
            for b in match.matchbot_set.select_related(
                "bot_version", "bot_version__bot"
            ).all()
        }

        form = MatchUploadForm(self.request.POST, self.request.FILES)
        if not form.is_valid():
            raise BadRequest()

        successful: bool = form.cleaned_data.get("successful", False)
        match.is_finished = True
        match.finished_at = timezone.now()
        match.failed = not successful

        scores: dict = form.cleaned_data.get("scores", dict())
        if scores:
            for name, score in scores.items():
                if name not in bots:
                    continue
                bots[name].score = score

        server_log = form.cleaned_data.get("server_log")
        if server_log:
            match.server_log = server_log

        observer_log = form.cleaned_data.get("observer_log")
        if observer_log:
            match.observer_log = observer_log

        bot_logs = form.cleaned_data.get("bot_logs")
        if bot_logs:
            try:
                with ZipFile(bot_logs) as zipf:
                    for file in zipf.namelist():
                        bot_name, ext = os.path.splitext(file)
                        if bot_name not in bots:
                            continue
                        bots[bot_name].log.save(file, ContentFile(zipf.read(file)))
            except BadZipFile:
                pass

        match.save()
        for b in bots.values():
            b.save()

        return HttpResponse("ok")


class MatchConfigView(GameMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            matches = generate_matches(self.game, int(request.GET.get("n", 1)))
        except ValueError:
            raise BadRequest()

        return JsonResponse([m.to_json() for m in matches], safe=False)
