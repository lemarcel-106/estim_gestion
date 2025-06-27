from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.models import LogEntry


class HomeView(LoginRequiredMixin, View):
    template_name = 'website/home.html'

    def get(self, request):
        logs = LogEntry.objects.all().order_by('-action_time')  # Récupère les derniers logs en premier
        if not request.user.is_authenticated:
            return redirect('login')
        
        return render(request, self.template_name, {'logs': logs})

    def post(self, request):
        # Handle any form submissions or actions here if needed
        return redirect('home')