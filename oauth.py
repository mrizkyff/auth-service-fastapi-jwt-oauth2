from typing import Optional
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
# from util.util import RandomString, ValidateObjectId
# from config.config import MGDB
from config import config
# from model.register import RegisterBase
from fastapi import FastAPI, Depends, HTTPException
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth
from datetime import timedelta

# from util.util_user import CheckEmailWithCompany, CreateCredentialTemporary
# from util.util_waktu import dateTimeNow

import os
import requests_oauthlib
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

BASEURL = ''

app = FastAPI(openapi_url="/oauth/openapi.json",docs_url="/oauth/swgr")
if config.ENVIRONMENT == 'production':
    #setup Elastic APM Agent
    apm = make_apm_client({
        'SERVICE_NAME': 'ERP-MainOauth',
        'SERVER_URL': 'http://apm-server.logging:8200',
        'ELASTIC_APM_TRANSACTION_IGNORE_URLS': ['/health'],
        'METRICS_SETS': "elasticapm.metrics.sets.transactions.TransactionsMetricSet",
    })
    app.add_middleware(ElasticAPM, client=apm)
    
app.add_middleware(SessionMiddleware, secret_key='ifpeoiu83iueoi9028')

if config.ENVIRONMENT == 'production':
    BASEURL = 'http://127.0.0.1:8000'
elif config.ENVIRONMENT == 'staging':
    BASEURL = 'http://127.0.0.1:8000'
elif config.ENVIRONMENT == 'development':
    BASEURL = 'http://127.0.0.1:8000'


@app.get("/health")
async def health():
    return {"status": "ok"}

oauth = OAuth(Config('google.env'))

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.get('/oauth/')
async def home(request: Request):
    # Try to get the user
    user = request.session.get('user')
    if user is not None:
        email = user['email']
        html = (
            f'<pre>Email: {email}</pre><br>'
            '<a href="/oauth/logout">logout</a>'
        )
        return HTMLResponse(html)

    # Show the login link
    return HTMLResponse('<a href="/oauth/google_cek?companyId=6007a586406d12b2601d496e&returnUrl='+BASEURL+'/oauth">login</a>')

@app.get('/oauth/google_cek')
async def login(returnUrl:str, request: Request):
    # if ValidateObjectId(companyId):
        # redirect_uri = request.url_for('auth')
        # request.session['companyId'] = companyId
    redirect_uri = BASEURL+'/oauth/auth'
    request.session['returnUrl'] = returnUrl
    try:
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception:
        raise HTTPException(status_code=400)


@app.route('/oauth/auth')
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    request.session['user'] = dict(user)
    email = user['email']
    companyId = request.session.get('companyId')
    returnUrl = request.session.get('returnUrl')
    #jika sudah terdaftar return login
    if await CheckEmailWithCompany(email,companyId) == True:
        temporary = RandomString(30)
        CreateCredentialTemporary(email,temporary)
        #GANTI ke url front end
        return RedirectResponse(url=returnUrl+'/oauth_login?email='+email+'&companyId='+companyId+'&temporary='+temporary)
    #jika belum terdaftar return register
    else: 
        # {"regId":regId,"tempPwd":tempPwd,"email":cekOtp['email']}
        data = RegisterBase()
        data.email = email
        data.companyId = companyId
        data.createTime = dateTimeNow()
        data.expiredTime = dateTimeNow() + timedelta(minutes=5)
        data.otpStatus = True
        data.password = RandomString(10)
        reg_op = await MGDB.tbl_register_verify.insert_one(data.dict())
        reg_id = str(reg_op.inserted_id)
        #GANTI ke url front end
        return RedirectResponse(url=returnUrl+'/oauth_register?email='+email+'&regId='+reg_id+'&tempPwd='+data.password)
        

@app.get('/oauth/logout') 
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/oauth/')


#sample html utk uji coba aja, test
@app.get('/oauth/oauth_register')
async def sukses_register(email:str, regId:str, tempPwd:str):
    html = (
        f'<pre>ACTION: REGISTER</pre>'
        f'<pre>Email: {email}</pre>'
        f'<pre>Register ID: {regId}</pre>'
        f'<pre>Temporary: {tempPwd}</pre>'
        '<a href="/oauth/logout">logout</a>'
    )
    return HTMLResponse(html)

#sample html utk uji coba aja
@app.get('/oauth/oauth_login')
async def sukses_login(companyId: str, email: str, temporary: str):
    html = (
        f'<pre>ACTION: LOGIN</pre>'
        f'<pre>Email: {email}</pre>'
        f'<pre>Company ID: {companyId}</pre>'
        f'<pre>Temporary Password: {temporary}</pre>'
        '<a href="/oauth/logout">logout</a>'
    )
    return HTMLResponse(html)


