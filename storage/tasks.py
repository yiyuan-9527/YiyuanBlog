from datetime import datetime, timezone

from celery import group, shared_task

from .models import Storage


@shared_task
def leetest():
    print('李白的 Celery 定時任務一分鐘被觸發')


@shared_task(bind=True, default_retry_delay=300, max_retries=3)
def downgrade_user_storage_plan(self, storage_id: int) -> str:
    """
    Celery子任務, 處理單個 Storage 實例的方案降級,
    每個任務只負責處理一個 storage_id
    """
    try:
        storage_instance = Storage.objects.get(id=storage_id)

        success = storage_instance.downgrade_to_free()  # 調用 Storage 模型中的降級方法
        if success:
            print(f'用戶 {storage_instance.user.email} 的方案已經降級為免費方案')
            return f'降級成功: {storage_instance.user.email}'

    except Storage.DoesNotExist:
        # 如果 Storage 不存在, 就不重試了
        print(f'儲存實例 ID {storage_id} 不存在, 跳過')
        return f'儲存實例 ID {storage_id} 不存在'

    except Exception as e:
        # 如果發生其他錯誤, 允許任務重試
        print(f'降級失敗 ID {storage_id}: {e}')
        raise self.retry(exc=e, countdown=self.default_retry_delay)


@shared_task
def storage_plan_check() -> str:
    """
    Celery主任務, 每日12點檢查用戶方案, 負責查詢所有需要降級的 Storage 實例,
    並為每個實例觸發一個獨立的 Celery 子任務
    """
    print('開始檢查用戶方案')

    # 查詢所有已經到期的 Storage 實例
    expired_storage_instances = (
        Storage.objects.filter(
            plan_expire_at__isnull=False,  # 過期時間不是 null(即有付費方案)
            plan_expire_at__lte=datetime.now(
                timezone.utc
            ),  # 過期時間 <= 現在時間(即已過期)
        )
        .exclude(
            plan_name=Storage.PlanChoices.FREE,  # 排除已經是免費方案的用戶
        )
        .select_related('user')  # 預先載入關聯的 user 資料, 避免 N+1 查詢問題
    )

    storage_ids_to_downgrade = [s.id for s in expired_storage_instances]

    if not storage_ids_to_downgrade:
        print('沒有需要降級的用戶')
        return '沒有需要降級的用戶'

    print(f'找到 {len(storage_ids_to_downgrade)} 個儲存方案需要降級')

    # 建立一個 group 任務群組, 每個 entry 是一個獨立的 downgrade_user_storage_plan 任務
    # .s() 是簽名, 用於異步呼叫任務
    job = group(
        downgrade_user_storage_plan.s(storage_id)
        for storage_id in storage_ids_to_downgrade
    )

    # 執行 group, 這會將所有子任務發送到消息佇列
    result = job.apply_async()
    print(f'已提交 {len(storage_ids_to_downgrade)} 個降級任務, 任務 ID: {result.id}')
    return f'已為 {len(storage_ids_to_downgrade)} 個儲存方案做降級處理'
