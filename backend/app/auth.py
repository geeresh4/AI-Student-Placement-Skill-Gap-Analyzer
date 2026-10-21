import hashlib, hmac, base64, json, time, secrets
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .db import get_db
from .models import User
from .config import SECRET_KEY
security=HTTPBearer(auto_error=False)
def hash_password(p):
    salt=secrets.token_bytes(16); dk=hashlib.scrypt(p.encode(),salt=salt,n=2**14,r=8,p=1); return base64.b64encode(salt+dk).decode()
def verify_password(p,h):
    try:
        raw=base64.b64decode(h); return hmac.compare_digest(raw[16:],hashlib.scrypt(p.encode(),salt=raw[:16],n=2**14,r=8,p=1))
    except Exception: return False
def token(user):
    payload=json.dumps({"sub":str(user.id),"role":user.role,"exp":int(time.time())+36000},separators=(",",":")).encode(); a=base64.urlsafe_b64encode(payload).decode().rstrip('='); sig=base64.urlsafe_b64encode(hmac.new(SECRET_KEY.encode(),a.encode(),hashlib.sha256).digest()).decode().rstrip('='); return a+'.'+sig
def decode(value):
    try:
        a,s=value.split('.'); expected=base64.urlsafe_b64encode(hmac.new(SECRET_KEY.encode(),a.encode(),hashlib.sha256).digest()).decode().rstrip('=')
        if not hmac.compare_digest(s,expected): return None
        data=json.loads(base64.urlsafe_b64decode(a+'='*((4-len(a)%4)%4))); return data if data['exp']>time.time() else None
    except Exception: return None
def current_user(creds: HTTPAuthorizationCredentials|None=Depends(security), db: Session=Depends(get_db)):
    data=decode(creds.credentials) if creds else None
    if not data: raise HTTPException(401,"Valid login required")
    user=db.get(User,int(data['sub']))
    if not user: raise HTTPException(401,"User not found")
    return user
def officer(user: User=Depends(current_user)):
    if user.role!='officer': raise HTTPException(403,"Placement officer access required")
    return user
