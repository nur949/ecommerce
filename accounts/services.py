from django.utils import timezone

from .models import RewardAccount, RewardTransaction


def get_or_create_reward_account(user):
    account, _ = RewardAccount.objects.get_or_create(user=user)
    return account


def add_reward_points(user, points, reason='', reference='', transaction_type='earn'):
    points = max(int(points or 0), 0)
    if points <= 0:
        return None
    account = get_or_create_reward_account(user)
    account.points_balance += points
    account.lifetime_points += points
    if account.lifetime_points >= 5000:
        account.tier = 'Radiance'
    elif account.lifetime_points >= 2000:
        account.tier = 'Luxe'
    else:
        account.tier = 'Glow'
    account.save(update_fields=['points_balance', 'lifetime_points', 'tier', 'updated_at'])
    return RewardTransaction.objects.create(
        account=account,
        transaction_type=transaction_type,
        points=points,
        reason=reason,
        reference=reference,
    )


def redeem_reward_points(user, points, reason='', reference=''):
    points = max(int(points or 0), 0)
    if points <= 0:
        return 0
    account = get_or_create_reward_account(user)
    redeemed = min(points, account.points_balance)
    if redeemed <= 0:
        return 0
    account.points_balance -= redeemed
    account.save(update_fields=['points_balance', 'updated_at'])
    RewardTransaction.objects.create(
        account=account,
        transaction_type='redeem',
        points=-redeemed,
        reason=reason,
        reference=reference,
    )
    return redeemed


def maybe_grant_birthday_offer(user):
    profile = getattr(user, 'profile', None)
    if not profile or not profile.birthday:
        return 0
    today = timezone.localdate()
    if profile.birthday.month != today.month or profile.birthday.day != today.day:
        return 0
    account = get_or_create_reward_account(user)
    if account.birthday_offer_claimed_at and account.birthday_offer_claimed_at.date() == today:
        return 0
    account.birthday_offer_claimed_at = timezone.now()
    account.save(update_fields=['birthday_offer_claimed_at', 'updated_at'])
    add_reward_points(user, 200, reason='Birthday bonus', transaction_type='birthday')
    return 200
