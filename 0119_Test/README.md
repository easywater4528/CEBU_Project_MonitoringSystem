# Arduino LED 웹 모니터링 시스템 Test
 아두이노 우노 사용 
 시리얼 모니터로 값 받아서 웹에 띄움 -> 웹에서 LED on off 가능 -> .py 터미널에 표시

## 기능
- 웹 브라우저에서 아두이노 LED ON/OFF 제어
- 실시간 LED 상태 그래프
- 실시간 센서 데이터 그래프
- WebSocket 기반 실시간 데이터 업데이트
- LED 상태 그래프 표시
- 통신 로그 확인 (web + py)

### 1. Python 라이브러리 설치

```bash
pip install pyserial flask flask-socketio python-socketio
```

### 2. 아두이노 코드 업로드

1. Arduino IDE - `arduino_led_web.ino` 파일
2. LED 핀을 변경하려면 코드 상단의 `LED_PIN` 값을 수정합니다
   const int LED_PIN = 13;
   const int SENSOR_PIN = A0;  // 아날로그 센서 핀

### 3. 웹 서버 실행
1. python web_server.py
   (http://localhost:5000)

## 기술 스택

### 백
- **Flask**: 웹 서버 프레임워크
- **Flask-SocketIO**: 실시간 양방향 통신
- **PySerial**: 아두이노 시리얼 통신

### 프론트엔드
- **HTML/CSS/JavaScript**: 웹 인터페이스
- **Socket.IO**: 실시간 데이터 수신
- **Chart.js**: 실시간 그래프 렌더링

### 아두이노
- **JSON 데이터 전송**: 구조화된 데이터 포맷
- **500ms 주기**: 초당 2회 데이터 업데이트

## notes

- WebSocket을 사용한 실시간 통신
- Chart.js를 사용한 부드러운 그래프 애니메이션
- 반응형 디자인으로 모바일 지원
- RESTful API 엔드포인트 제공
