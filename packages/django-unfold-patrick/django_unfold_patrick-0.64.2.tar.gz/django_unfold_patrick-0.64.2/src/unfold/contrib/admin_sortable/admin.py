import json
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_str

from adminsortable2.admin import SortableAdminMixin as BaseSortableAdminMixin

class SortableAdminMixin(BaseSortableAdminMixin):
    """
    Custom SortableAdminMixin that extends the functionality of adminsortable2's SortableAdminMixin.
    This mixin can be used to add sorting capabilities to Django admin models.
    """
    
    def update_order(self, request):
        """
        Override to log sorting actions in the admin log.
        """
        try:
            # 요청 데이터 추출
            data = json.loads(request.body)
            updated_items = data.get('updatedItems', [])
            
            # 변경 전 순서 정보 미리 저장
            old_orders = {}
            if updated_items:
                object_ids = [item[0] for item in updated_items]
                objects_before = self.model.objects.filter(id__in=object_ids)
                for obj in objects_before:
                    old_orders[str(obj.id)] = obj.order
            
            # 기본 정렬 처리 (부모 메서드 호출)
            response = super().update_order(request)
            
            # Admin Log에 변경 기록
            if updated_items and response.status_code == 200:
                content_type = ContentType.objects.get_for_model(self.model)
                
                # 변경된 항목의 IDs
                objects = self.model.objects.filter(id__in=[item[0] for item in updated_items])
                
                # 각 변경된 객체에 대한 메시지 생성
                for obj_id, new_order in updated_items:
                    obj = next((o for o in objects if str(o.id) == obj_id), None)
                    if obj:
                        # 원래 순서 확인
                        old_order = old_orders.get(obj_id, "알 수 없음")
                        
                        # 로그 메시지 생성 (원래 순서와 새 순서 모두 포함)
                        log_message = json.dumps([{
                            "changed": {
                                "fields": [f"order '{str(old_order)}' → '{str(new_order)}'"]
                            },
                        }])
                        
                        # Admin Log에 기록
                        LogEntry.objects.log_action(
                            user_id=request.user.id,
                            content_type_id=content_type.id,
                            object_id=obj_id,
                            object_repr=force_str(obj),
                            action_flag=CHANGE,
                            change_message=log_message
                        )
            
            return response
            
        except Exception as e:
            print(f"순서 변경 로깅 중 오류 발생: {e}")
            # 오류가 발생해도 기본 기능은 유지
            return super().update_order(request)