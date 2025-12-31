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