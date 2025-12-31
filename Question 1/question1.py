from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.db.models import Count

class Course(models.Model):
    titre = models.CharField(max_length=200, unique=True)
    description = models.TextField(validators=[MinLengthValidator(20)])
    duré_en_heures = models.IntegerField(validators=[MinValueValidator(1)])
    prix = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    date_de_creation = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=[('Brouillon', 'Brouillon'), ('Publié', 'Publié'), ('Archivé', 'Archivé')],
        default='Brouillon',
    )
    reference_vers_instructeur = models.ForeignKey('Instructor', on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return self.titre

    def inscrire_etudiant(self, etudiant):
        enrollment, _ = Enrollment.objects.get_or_create(
            reference_vers_cours=self,
            reference_vers_etudiant=etudiant,
        )
        return enrollment
    
class Instructor(models.Model):
    nom_complet = models.CharField(max_length=100, validators=[MinLengthValidator(2)])
    email = models.EmailField(unique=True)
    biographie = models.TextField(validators=[MinLengthValidator(30)])
    photo_de_profil = models.ImageField(upload_to='instructors/', blank=True, null=True)
    date_d_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom_complet

    def nombre_de_cours(self):
        return self.courses.filter(status='Publié').count()
    
class Enrollment(models.Model):
    reference_vers_cours = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    reference_vers_etudiant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    date_d_inscription = models.DateTimeField(auto_now_add=True)
    date_de_completion = models.DateTimeField(null=True, blank=True)
    note_finale = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    statut = models.CharField(max_length=50, choices=[('En cours', 'En cours'), ('Terminé', 'Terminé'), ('Abandonné', 'Abandonné')])

    def __str__(self):
        return f"{self.reference_vers_etudiant.username} - {self.reference_vers_cours.titre}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['reference_vers_cours', 'reference_vers_etudiant'],
                name='unique_inscription_par_cours_et_etudiant',
            )
        ]

    def marquer_comme_termine(self, note=None):
        """Marque l'inscription comme terminée et enregistre la note si fournie."""
        self.statut = 'Terminé'
        if note is not None:
            self.note_finale = note
        self.save(update_fields=['statut', 'note_finale'])



# avec les models ci-dessus, écrire les requêtes ORM pour

# 1. Récupérer tous les cours publiés triés par prix croissant.
cours_publies = Course.objects.filter(status='Publié').order_by('prix')

#2. Trouver tous les étudiants inscrits a un cours spécifique (cours avec id=5).
cours = Course.objects.get(id=5)
etudiants_inscrits = User.objects.filter(enrollments__reference_vers_cours=cours)

#3. Compter le nombre d'inscriptions complétées pour un instructeur donné 
# (instructeur avec id=3).
instructor = Instructor.objects.get(id=3)
compteur_inscriptions_terminees = Enrollment.objects.filter(
    reference_vers_cours__reference_vers_instructeur=instructor,    
    statut='Terminé'
).count()

#4 Récupérer les 3 cours avec le plus grand nombre d'inscriptions.
top_cours = Course.objects.annotate(
    num_inscrit=Count('enrollments')
).order_by('-num_inscrit')[:3]

# Partie C : Design pattern 

#1. quel design pattern Django implémente-t-il avec son ORM ? Expliquez brièvement
Django implémente le design pattern Active Record. Chaque classe de modèle dans Django représente une table de base de bdd
on peu aussi y inscrire les contraintes et des méthodes métiers liées aux données.

#2. Expliquez la différence entre le pattern MVT de Django et le pattern MVC classique.
Le pattern MVT (Model view template) de Django est une variante du pattern MVC (Model view controller) classique.
la différence se trouve dans la gestion de la vue et du contrôleur. dans MVC le contrôleur gère la logique de l'application puis la vue affiche les données.
dans MVT, la vue gère la logique de l'application et le template affiche les données.

#3. Donnez un avantage et un inconvénient du pattern Active Record utilisé par Django.
Avantage : simplicité d'utilisation, chaque modèle est responsable de sa propre persistance.
Inconvénient : peut compliquer les tests unitaires et la maintenance.