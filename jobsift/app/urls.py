from django.urls import path, include
from . import views as v

urlpatterns = [
    path('', v.home, name='home'),
    path('index', v.index, name='index'),
    path('job_boards', v.job_boards, name='job_boards'),
    path('api/job_board/<int:job_board_id>/', v.get_job_board_data, name='get_job_board_data'),
    path('job_profiles/', v.job_profiles_view, name='job_profiles'),
    path('job_profile/<int:id>/', v.job_profile_view, name='job_profile'),
    path('job_profiles/create/', v.create_job_profile, name='create_job_profile'),
    path('job_board-autocomplete/', v.JobBoardAutocomplete.as_view(), name='job_board-autocomplete'),
]