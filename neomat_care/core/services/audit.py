from core.models import AuditLog

def log_action(user, action, referral=None, emergency_case=None, metadata=None):
    AuditLog.objects.create(
        user=user,
        action=action,
        referral=referral,
        emergency_case=emergency_case,
        metadata=metadata or {}
    )