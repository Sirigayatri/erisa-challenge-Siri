
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Claim(models.Model):
    id = models.IntegerField(primary_key=True)
    patient_name = models.CharField(max_length=200)
    billed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50)
    insurer_name = models.CharField(max_length=200)
    discharge_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)

    def underpayment(self):
        return max(self.billed_amount - self.paid_amount, 0)

    def __str__(self):
        return f"Claim {self.id} - {self.patient_name}"

    class Meta:
        ordering = ['-discharge_date']


class ClaimDetail(models.Model):
    claim = models.OneToOneField(Claim, on_delete=models.CASCADE, related_name='detail')
    denial_reason = models.TextField(blank=True)
    cpt_codes = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"Detail for Claim {self.claim.id}"


class Flag(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='flags')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Flag for Claim {self.claim.id}"


class Note(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='notes')
    text = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for Claim {self.claim.id}"
