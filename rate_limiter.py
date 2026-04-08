from slowapi import Limiter
from utils import get_user_id


limiter = Limiter(key_func=get_user_id, default_limits=["100/minute"])



