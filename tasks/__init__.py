from __future__ import absolute_import
import json
from celery import shared_task
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string


@shared_task
def send_accounts_find_email(email):
    user = get_user_model().objects.filter(email=email)
    if email:
        target = user.first()
        template = render_to_string('tasks/idfinder.html', {'target': target})
        emailObject = EmailMessage("Blog에서 아이디 찾기 결과", template, to=[email])
        emailObject.content_subtype = "html"
        result = emailObject.send()
        return True
    else:
        return False


def email_wrapper(target):
    return f"""
<div style="display:flex;flex-direction:column;justify-content:center;align-items:center">
	<div style="height:10vh"></div>
	<div style="margin:auto">
		고객님의 ID는 {target}입니다.
	</div>
	<a href="react.honeycombpizza.link/accounts/Signin">로그인페이지로 이동</d>
</div>
"""
