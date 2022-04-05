from django.db import models
from django.utils import timezone

class SoftDeleteManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True,status=0)
    
    
class SoftDeleteModel(models.Model):
    
    deleted_at = models.DateTimeField('삭제일', null=True, default=None)
    status = models.PositiveIntegerField('상태코드',default=0)
    class Meta:
        abstract = True  # 상속 할수 있게 

    objects = SoftDeleteManager()  # 커스텀 매니저 

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):  # 삭제된 레코드를 복구한다.
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])
        
class TimeMixin(SoftDeleteModel):
    reg_date=models.DateTimeField('등록날짜',auto_now_add=True)
    update_date=models.DateTimeField('수정날짜',auto_now=True,null=True)
    
    class Meta:
        abstract = True
    
    def since(self):
        time = timezone.now()-self.reg_date
        return str(time)
    