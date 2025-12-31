#Partie A: Système d'authentification

#1 Créez un modèle StudentProfile:

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
class StudentProfile(models.Model):
    NIVEAUX_ETUDES = [
        ('Licence', 'Licence'),
        ('Master', 'Master'),
        ('Doctorat', 'Doctorat'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    numero_etudiant = models.CharField(max_length=20, unique=True, validators=[MinLengthValidator(5)])
    date_de_naissance = models.DateField()
    niveau_d_etudes = models.CharField(max_length=10, choices=NIVEAUX_ETUDES)

    def __str__(self):
        return f"{self.user.username} - {self.numero_etudiant}"
    
# Ecrivez une vue de connexion personnalisée (function-based)

from django.shortcuts import render, redirect   
from django.contrib import messages
from django.contrib.auth import authenticate, login

def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'home'

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Connexion réussie.")
            return redirect(next_url)
        messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, 'login.html', {'next': next_url})

# Partie B : Permissions et Restrictions 
# En utilisant le système de permissions Django :
# 1. Créez deux permissions personnalisées pour le modèle Course :

@receiver(post_migrate)
def create_custom_permissions(sender, **kwargs):
    if sender.name == 'your_app_name':  
        course_content_type = ContentType.objects.get_for_model(Course)

        Permission.objects.get_or_create(
            codename='can_publish_course',
            name='Can publish course',
            content_type=course_content_type,
        )

        Permission.objects.get_or_create(
            codename='can_view_statistics',
            name='Can view statistics',
            content_type=course_content_type,
        )
#2. Écrivez une vue (CBV ou FBV) course_publish : 
@login_required
@permission_required('your_app_name.can_publish_course', raise_exception=True)
def course_publish(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return HttpResponseForbidden("Cours non trouvé.")

    if course.status != 'Brouillon':
        return HttpResponseForbidden("Le cours n'est pas en brouillon.")

    course.status = 'Publié'
    course.save(update_fields=['status'])
    return redirect('course_detail', course_id=course.id)


# Partie C : Template avec Permissions 


{% if user.is_authenticated %}
    <p>Bienvenue, {{ user.username }}!</p>

    {% if perms.your_app_name.can_publish_course %}
        <a href="{% url 'course_publish' course.id %}">Publier</a>
    {% endif %}

    {% if perms.your_app_name.can_view_statistics %}
        <a href="{% url 'course_statistics' course.id %}">Statistiques</a>
    {% endif %}

    <a href="{% url 'logout' %}">Déconnexion</a>
{% else %}
    <a href="{% url 'login' %}">Connexion</a>
{% endif %}
