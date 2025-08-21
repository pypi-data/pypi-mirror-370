from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class SepaCurrentVersion(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120, blank=True)
    features = models.CharField(max_length=120, blank=True)
    fixes = models.TextField(max_length=2400, blank=True)
    fecha_creacion = models.DateTimeField(auto_now=False, auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=False, auto_now_add=True)
    eliminado = models.BooleanField(default=False)

    class Meta:
        db_table = 'api_sepa_current_version'


class SepaCompanies(models.Model):
    id = models.AutoField(primary_key=True)
    clave = models.CharField(max_length=128, blank=True)
    razonsocial = models.CharField(max_length=100)
    rfc = models.CharField(max_length=40)
    fecha_creacion = models.DateTimeField(auto_now=False, auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=False, auto_now_add=True)
    id_intelisis = models.IntegerField(blank=True)
    eliminado = models.BooleanField(default=False)

    class Meta:
        db_table = 'api_sepa_companies'


class SepaBranch(models.Model):
    id = models.AutoField(primary_key=True)
    id_company = models.ForeignKey(SepaCompanies, on_delete=models.CASCADE, related_name='branches')
    clave = models.CharField(max_length=128, blank=True)
    nombre = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=40, blank=True)
    correo = models.CharField(max_length=240, blank=True)
    fecha_creacion = models.DateTimeField(auto_now=False, auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=False, auto_now_add=True)
    conf_ip_ext = models.CharField(max_length=40, blank=True)
    conf_ip_int = models.CharField(max_length=40, blank=True, null=True)
    conf_user = models.CharField(max_length=40, blank=True)
    conf_pass = models.CharField(max_length=40, blank=True)
    conf_db = models.CharField(max_length=80, blank=True)
    conf_port = models.CharField(max_length=80, blank=True, null=True)
    id_intelisis = models.IntegerField(blank=True)
    empresa_intelisis = models.CharField(max_length=80, blank=True)
    eliminado = models.BooleanField(default=False)
    direccion = models.CharField(max_length=500, blank=True, null=True)
    latitud = models.CharField(max_length=50, blank=True, null=True)
    longitud = models.CharField(max_length=50, blank=True, null=True)
    gwmbac = models.CharField(max_length=50, blank=True, null=True)
    id_district = models.IntegerField(blank=True, null=True)
    fotos_recepcion = models.CharField(max_length=500, blank=True, null=True)
    db_recepcion = models.CharField(max_length=50, blank=True, null=True)
    ciudad = models.CharField(max_length=40, blank=True, null=True)
    id_agencia_crm = models.IntegerField(blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    allow_test = models.BooleanField(default=False)

    class Meta:
        db_table = 'api_sepa_branch'


class UserProfileManager(BaseUserManager):
    def create_user(self, id_branch, id_current_version, code_verification, correo, telefono, username, password=None):
        if not correo:
            raise ValueError('El correo es un campo obligatorio')

        correo = self.normalize_email(correo)
        user = self.model(id_branch_id=id_branch, id_current_version_id=id_current_version,
                          code_verification=code_verification, correo=correo, telefono=telefono, username=username)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, id_branch, id_current_version, code_verification, correo, telefono, username, password):
        user = self.create_user(id_branch, id_current_version, code_verification, correo, telefono, username, password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class UserAPI(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    id_branch = models.ForeignKey(SepaBranch, to_field='id', on_delete=models.CASCADE, related_name='users')
    id_current_version = models.ForeignKey(SepaCurrentVersion, on_delete=models.CASCADE, related_name='users')
    code_verification = models.CharField(max_length=20, blank=True)
    username = models.CharField(db_column='usuario', max_length=254, blank=True, unique=True)
    password = models.CharField(max_length=100, blank=True)
    nombres = models.CharField(max_length=180, blank=True)
    ap_paterno = models.CharField(max_length=100, blank=True)
    ap_materno = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=40, blank=True)
    correo = models.CharField(max_length=240, blank=True)
    fecha_creacion = models.DateTimeField(auto_now=False, auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=False, auto_now_add=True)
    id_intelisis = models.CharField(max_length=100, blank=True, null=True)
    id_ckt = models.CharField(max_length=100, blank=True, null=True)
    token_device = models.CharField(max_length=100, blank=True, null=True)
    eliminado = models.BooleanField(default=False)
    api_sctoken = models.CharField(max_length=150, blank=True)
    api_scLastLoggedIn = models.DateTimeField(auto_now=False, auto_now_add=True)
    api_scInserted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['id_branch', 'id_current_version', 'code_verification', 'correo', 'telefono', 'password']

    class Meta:
        db_table = 'api_user'


class SepaBranchUsers(models.Model):
    iduser = models.ForeignKey(UserAPI, on_delete=models.CASCADE, related_name='permissions', db_column='iduser')
    idbranch = models.ForeignKey(SepaBranch, on_delete=models.CASCADE, related_name='permissions', db_column='idbranch')
    fecharegistro = models.DateTimeField(auto_now_add=True)
    fechaactualiza = models.DateTimeField(auto_now=True)
    eliminado = models.BooleanField(default=False)

    class Meta:
        db_table = 'api_branch_users'


class ApiLogs(models.Model):
    iduser = models.IntegerField()
    tipo = models.CharField(max_length=120)
    header = models.TextField()
    request = models.TextField()
    response = models.TextField()
    status = models.IntegerField(null=True)
    url = models.TextField()
    interfaz = models.CharField(max_length=120)
    fecharegistro = models.DateTimeField(auto_now=True)
    response_time = models.IntegerField(default=0)

    class Meta:
        db_table = 'api_logs'


@receiver(post_save, sender=ApiLogs)
def delete_old_logs(sender, instance, **kwargs):
    interfaz = getattr(settings, 'INTERFAZ_NAME', '')
    max_number_logs = getattr(settings, 'MAX_NUMBER_LOGS', 500)
    if max_number_logs < ApiLogs.objects.count():
        logs_to_delete = ApiLogs.objects.filter(interfaz=interfaz).order_by('-fecharegistro')[max_number_logs:]
        list(map(lambda i: i.delete(), logs_to_delete))
