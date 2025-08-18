from datetime import timedelta

from django.http import HttpRequest
from django.utils.timezone import now

from .models import Settings as HideAdminSettings
from .storage import CachedStorage
from .utils import get_client_ip, is_blacklisted, is_whitelisted


class LimitLoginAttempts:
    def __init__(self, request: HttpRequest):
        self.request = request
        self.settings = HideAdminSettings.load()
        self.ip = get_client_ip(request, self.settings)
        self.storage = CachedStorage(f"login_throttle:{self.ip}")
        self.now = now()

    def is_enabled(self) -> bool:
        return self.settings.throttling_login_enabled

    def is_locked_out(self) -> bool:
        if not self.is_enabled() or is_whitelisted(self.ip, self.settings):
            return False
        if is_blacklisted(self.ip, self.settings):
            return True
        return self.storage.exists(self._lockout_key())

    def register_failed_attempt(self):
        if not self.is_enabled():
            return

        if is_whitelisted(self.ip, self.settings):
            return

        if is_blacklisted(self.ip, self.settings):
            return

        self._increment_failed_count()

        if not self._has_reached_attempt_limit():
            return

        self._record_lockout()

    # ───────────── Internal Logic ─────────────

    def _increment_failed_count(self):
        attempts = self.storage.get(self._failed_key(), default=0) + 1
        self.storage.set(self._failed_key(), attempts, timeout=self._window_seconds())
        self._failed_attempts = attempts

    def _has_reached_attempt_limit(self) -> bool:
        return self._failed_attempts >= self.settings.throttle_attempt_limit

    def _record_lockout(self):
        history = self._pruned_lockout_history()
        history.append(self.now)
        self.storage.set(self._history_key(), history, timeout=self._window_seconds())

        duration = self._get_lockout_duration(len(history))
        self.storage.set(self._lockout_key(), True, timeout=int(duration.total_seconds()))
        self.storage.delete(self._failed_key())  # Reset failed count

    def _pruned_lockout_history(self) -> list:
        history = self.storage.get(self._history_key(), default=[])
        return [ts for ts in history if (self.now - ts) <= self._window()]

    def _get_lockout_duration(self, history_count: int) -> timedelta:
        if history_count >= self.settings.throttle_escalation_threshold:
            return timedelta(minutes=self.settings.throttle_escalated_duration)
        return timedelta(minutes=self.settings.throttle_lockout_duration)

    def _window(self) -> timedelta:
        return timedelta(minutes=self.settings.throttle_window)
    
    def _window_seconds(self) -> int:
        return int(self._window().total_seconds())

    def _failed_key(self) -> str:
        return f"failed_login:{self.ip}"

    def _lockout_key(self) -> str:
        return f"lockout:{self.ip}"

    def _history_key(self) -> str:
        return f"lockout_history:{self.ip}"
