# routes.py
import time
# from notifications import send_msg
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from .monitoring import packet_monitor  # PacketMonitor 인스턴스 임포트
from .utils import verify_recaptcha  # 유틸리티 함수 사용

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    # 기본 페이지: reCAPTCHA 인증 페이지로 리디렉션
    session.clear()
    return redirect(url_for('main.recaptcha'))

@main_routes.route('/recaptcha', methods=['GET', 'POST'])
def recaptcha():
    # reCAPTCHA 인증 처리
    message = None

    if request.method == 'POST':
        captcha_response = request.form['g-recaptcha-response']
        if verify_recaptcha(captcha_response):
            session['authenticated'] = True
            return redirect(url_for('main.main_page'))
        else:
            session['authenticated'] = False
            message = '캡차 인증 실패! 다시 시도해주세요.'
    if packet_monitor.attack_detected:
        with packet_monitor.lock:
            message = 'DDoS공격이 감지되었습니다. 잠시 대기해주시기 바랍니다.'
            
    return render_template('recaptcha.html', alert_message=message)


@main_routes.route('/main')
def main_page():

    # 메인 페이지: 인증된 사용자만 접근 가능
    if not session.get('authenticated'):
        return redirect(url_for('main.recaptcha'))

    if packet_monitor.is_attack_detected():
        flash('DDoS 공격이 감지되었습니다! 잠시 대기해주시기 바랍니다.', 'danger')
        return redirect(url_for('main.recaptcha'))

    return render_template('index.html')

@main_routes.route('/logout')
def logout():
    """로그아웃 처리"""
    session.pop('authenticated', None)
    return redirect(url_for('main.recaptcha'))