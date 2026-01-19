from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import serial
import serial.tools.list_ports
import threading
import json
import time
from collections import deque
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'arduino-led-monitor'
socketio = SocketIO(app, cors_allowed_origins="*")

# 전역 변수
serial_connection = None
is_connected = False
data_buffer = deque(maxlen=100) 


def log_console(message, level="INFO"):
    """콘솔에 타임스탬프와 함께 로그를 출력합니다"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def get_available_ports():
    """사용 가능한 시리얼 포트 목록을 반환합니다"""
    ports = serial.tools.list_ports.comports()
    return [{"port": port.device, "description": port.description} for port in ports]


def read_serial_data():
    """아두이노로부터 데이터를 읽고 웹소켓으로 전송합니다"""
    global serial_connection, is_connected, data_buffer

    while is_connected:
        try:
            if serial_connection and serial_connection.in_waiting:
                line = serial_connection.readline().decode('utf-8').strip()

                if line:
                    # JSON 데이터 파싱
                    if line.startswith('{'):
                        try:
                            data = json.loads(line)
                            # 타임스탬프 추가
                            data['timestamp'] = time.time()
                            data_buffer.append(data)

                            # 콘솔 로그
                            log_console(f"데이터 수신: LED={data['led']}, Sensor={data['sensor']}", "DATA")

                            # 웹소켓으로 실시간 데이터 전송
                            socketio.emit('sensor_data', data)
                        except json.JSONDecodeError:
                            pass

                    # 상태 메시지
                    elif line.startswith('STATUS:'):
                        status = line.split(':')[1]
                        log_console(f"상태 변경: {status}", "STATUS")
                        socketio.emit('status_update', {'status': status})

                    # 일반 메시지
                    else:
                        log_console(f"메시지 수신: {line}", "MSG")
                        socketio.emit('message', {'msg': line})

            time.sleep(0.01)
        except Exception as e:
            print(f"Error reading serial: {e}")
            if is_connected:
                socketio.emit('error', {'msg': str(e)})
            break


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/api/ports')
def api_ports():
    """사용 가능한 시리얼 포트 목록"""
    return jsonify(get_available_ports())


@app.route('/api/connect', methods=['POST'])
def api_connect():
    """아두이노에 연결"""
    global serial_connection, is_connected

    data = request.json
    port = data.get('port')

    if not port:
        return jsonify({'success': False, 'message': '포트를 선택해주세요'}), 400

    try:
        serial_connection = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)  # 아두이노 리셋 대기
        is_connected = True

        log_console(f"아두이노 연결 성공: {port}", "CONNECT")

        # 데이터 수신 스레드 시작
        thread = threading.Thread(target=read_serial_data, daemon=True)
        thread.start()

        return jsonify({'success': True, 'message': f'{port}에 연결되었습니다'})
    except Exception as e:
        log_console(f"아두이노 연결 실패: {port} - {str(e)}", "ERROR")
        return jsonify({'success': False, 'message': f'연결 실패: {str(e)}'}), 500


@app.route('/api/disconnect', methods=['POST'])
def api_disconnect():
    """아두이노 연결 해제"""
    global serial_connection, is_connected

    is_connected = False
    if serial_connection:
        serial_connection.close()
        serial_connection = None

    log_console("아두이노 연결 해제", "DISCONNECT")
    return jsonify({'success': True, 'message': '연결이 해제되었습니다'})


@app.route('/api/command', methods=['POST'])
def api_command():
    """아두이노에 명령 전송"""
    global serial_connection, is_connected

    if not is_connected or not serial_connection:
        return jsonify({'success': False, 'message': '연결되지 않았습니다'}), 400

    data = request.json
    command = data.get('command')

    if not command:
        return jsonify({'success': False, 'message': '명령을 입력해주세요'}), 400

    try:
        serial_connection.write(f"{command}\n".encode())
        log_console(f"명령 전송: {command}", "COMMAND")
        return jsonify({'success': True, 'message': f'명령 전송: {command}'})
    except Exception as e:
        log_console(f"명령 전송 실패: {command} - {str(e)}", "ERROR")
        return jsonify({'success': False, 'message': f'전송 실패: {str(e)}'}), 500


@app.route('/api/data')
def api_data():
    """저장된 데이터 반환"""
    return jsonify(list(data_buffer))


@socketio.on('connect')
def handle_connect():
    """클라이언트 연결"""
    log_console('웹 클라이언트 연결됨', 'WEB')


@socketio.on('disconnect')
def handle_disconnect():
    """클라이언트 연결 해제"""
    log_console('웹 클라이언트 연결 해제됨', 'WEB')


if __name__ == '__main__':
    print("=" * 50)
    print("Arduino LED Web Monitor")
    print("http://localhost:5000")
    print("=" * 50)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
