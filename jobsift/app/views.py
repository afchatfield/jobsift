from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.forms import formset_factory
from dal import autocomplete

from .models import JobBoard, JobBoardSelector, JobBoardSearchSelector, JobProfile
from .forms import JobBoardForm, JobBoardSelectorForm, JobBoardSearchSelectorForm, JobProfileForm

# Create your views here.

def home(request):
    return render(request, 'home.html')

def index(request):
    return render(request, 'index.html')

def job_boards(request):
    job_board_entities = JobBoard.objects.all()
    JobBoardSelectorFormSet = formset_factory(JobBoardSelectorForm, extra=16)
    JobBoardSearchSelectorFormSet = formset_factory(JobBoardSearchSelectorForm, extra=5)

    if request.method == "POST":
        if 'job_board_form_submit' in request.POST:
            job_board_form = JobBoardForm(request.POST)
            if job_board_form.is_valid():
                job_board_form.save()
                return redirect('job_boards')
        elif 'job_board_selector_form_submit' in request.POST:
            formset = JobBoardSelectorFormSet(request.POST)
            job_board = JobBoard.objects.get(pk=int(request.POST.get('job-board-id')))
            if formset.is_valid():
                for form in formset:
                    if form.cleaned_data.get('css_selector'):
                        # get instance if exists, otherwise create
                        job_board_selector, created = JobBoardSelector.objects.get_or_create(
                            job_board = job_board,
                            job_field = form.cleaned_data.get('job_field'),
                            defaults = {'css_selector': form.cleaned_data.get('css_selector')}
                        )

                        if not created:
                            job_board_selector.css_selector = form.cleaned_data.get('css_selector')
                            job_board_selector.save()
                return redirect('job_boards')
        elif 'job_board_search_selector_form_submit' in request.POST:
            formset = JobBoardSearchSelectorFormSet(request.POST)
            job_board = JobBoard.objects.get(pk=int(request.POST.get('job-board-id')))
            if formset.is_valid():
                for form in formset:
                    if form.cleaned_data.get('css_selector'):
                        job_board_search_selector, created = JobBoardSearchSelector.objects.get_or_create(
                            job_board = job_board,
                            selector_type = form.cleaned_data.get('selector_type'),
                            defaults = {'css_selector': form.cleaned_data.get('css_selector')}
                        )

                        if not created:
                            job_board_search_selector.css_selector = form.cleaned_data.get('css_selector')
                            job_board_search_selector.save()
            
    job_board_form = JobBoardForm()

    selector_formset = JobBoardSelectorFormSet()
    search_selector_formset = JobBoardSearchSelectorFormSet()

    return render(request, 'job_boards.html', {
        'job_boards': job_board_entities,
        'job_board_form': job_board_form,
        'selector_formset': selector_formset,
        'search_selector_formset': search_selector_formset,
    })


@require_GET
def get_job_board_data(request, job_board_id):
    try:
        job_board = JobBoard.objects.get(id=job_board_id)
    except JobBoard.DoesNotExist:
        return JsonResponse({'error': 'Job board not found'}, status=404)
    data = job_board.get_job_board_data()
    return JsonResponse(data)

def job_profiles_view(request):
    job_profiles = JobProfile.objects.all()
    return render(request, 'job_profiles.html', {'job_profiles': job_profiles})

def job_profile_view(request, id):
    job_profile = get_object_or_404(JobProfile, id=id)
    if request.method == 'POST':
        form = JobProfileForm(request.POST, instance=job_profile)
        if form.is_valid():
            form.save()
            return redirect('job_profile', id=id)
    else:
        form = JobProfileForm(instance=job_profile)
    return render(request, 'job_profile.html', {'job_profile': job_profile, 'form': form})

def create_job_profile(request):
    if request.method == 'POST':
        form = JobProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('job_profiles')
    else:
        form = JobProfileForm()
    return render(request, 'job_profile_create.html', {'form': form})


class JobBoardAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated:
        #     return JobBoard.objects.none()

        qs = JobBoard.objects.all().order_by('name')

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
