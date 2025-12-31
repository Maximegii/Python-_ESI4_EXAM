# Formulaire Django

from django import forms
from django.core.exceptions import ValidationError  
from Question1.question1 import Course, Enrollment  
from django.contrib.auth.models import User

class InscriptionForm(forms.Form):
    cours = forms.ModelChoiceField(
        queryset=Course.objects.filter(status='Publié'),
        label="Sélection du cours"
    )
    email_etudiant = forms.EmailField(label="Email de l'étudiant")
    motivation = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Motivation"
    )
    acceptation_conditions = forms.BooleanField(
        label="J'accepte les conditions",
        required=True
    )

    def clean_email_etudiant(self):
        email = self.cleaned_data['email_etudiant']
        if not email.endswith('@student.edu'):
            raise ValidationError("L'email doit appartenir au domaine @student.edu")
        return email

    def clean_cours(self):
        cours = self.cleaned_data['cours']
        nombre_inscriptions = Enrollment.objects.filter(reference_vers_cours=cours).count()
        if nombre_inscriptions >= 30:
            raise ValidationError("Le cours sélectionné n'a plus de places disponibles.")
        return cours

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email_etudiant')
        cours = cleaned_data.get('cours')

        if email and cours:
            
                etudiant = User.objects.get(email=email)
                inscription_existante = Enrollment.objects.filter(
                    reference_vers_cours=cours,
                    reference_vers_etudiant=etudiant
                ).exists()
                if inscription_existante:
                    raise ValidationError("L'étudiant est déjà inscrit à ce cours.")
        
        return cleaned_data
    




    #Partie B: Vue et Template
# 1.
from django.shortcuts import render, redirect
from django.contrib import messages
def inscrire_etudiant(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            cours = form.cleaned_data['cours']
            email = form.cleaned_data['email_etudiant']
            etudiant, created = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0]})
            cours.inscrire_etudiant(etudiant)
            messages.success(request, "Inscription réussie au cours.")
            return redirect('liste_cours') 
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = InscriptionForm()
    
    return render(request, 'inscription_form.html', {'form': form})
    
# 2.Écrire une vue de connexion :
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    return render(request, 'login.html')