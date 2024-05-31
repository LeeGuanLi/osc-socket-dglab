from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import qrcode
import websocket
import json
import threading
import time
import queue

# 设置IP和端口
ip = "127.0.0.1"
port = 9001
server_address = "ws://127.0.0.1:9999/"
message_queue = queue.Queue()

# 初始化全局变量
connectionId = ""
targetId = ""

# OSC处理函数
def print_handler(address, *args):
    global message_queue
    print(f"来自OSC{address}: {args}")
    if args[0] < 0.01:
        clear_dglab_ws()
        message_queue = queue.Queue() # 清空消息队列
    else:
        message_queue.put((address, args)) # 将消息放入队列

# 默认OSC处理函数
def default_handler(address, *args):
    print(f"DEFAULT {address}: {args}")

# 处理消息的线程函数
def process_messages():
    while True:
        if not message_queue.empty():
            address, args = message_queue.get()
            print("dglabA")
            print(f"{address}: {args}")
            dglab_ws() # 处理消息
            time.sleep(0.1) # 控制处理速度

# 启动消息处理线程
message_processor_thread = threading.Thread(target=process_messages)
message_processor_thread.start()

def dglab_up():
    data_to_send = {
        "type": 2,
        "strength": 1, # 设置强度为1
        "message": "set channel", # 设置通道
        "channel": 1, # 设置通道为1
        "targetId": targetId
    }
    json_data = json.dumps(data_to_send)
    ws.send(json_data)
    dglab_to_zero() # 将强度设置为0
def dglab_to_zero():
    data_to_send = {
        "type": 3,
        "strength": 0,
        "message": "set channel",
        "channel": 1,
        "clientId": connectionId,
        "targetId": targetId
    }
    json_data = json.dumps(data_to_send)
    ws.send(json_data)

# 清除WebSocket消息
def clear_dglab_ws():
    data_to_clear = {
        "type": 4,
        "message": "clear-1",
        "clientId": connectionId,
        "targetId": targetId
    }
    json_data_wave = json.dumps(data_to_clear)
    ws.send(json_data_wave)
def dglab_ws():
    data_to_send_wave = {
        "type": "clientMsg",
        "message": "A:[\"0A0A0A0A00000000\",\"0A0A0A0A0A0A0A0A\",\"0A0A0A0A14141414\",\"0A0A0A0A1E1E1E1E\",\"0A0A0A0A28282828\",\"0A0A0A0A32323232\",\"0A0A0A0A3C3C3C3C\",\"0A0A0A0A46464646\",\"0A0A0A0A50505050\",\"0A0A0A0A5A5A5A5A\",\"0A0A0A0A64646464\"]",
        "message2": "B:[\"0A0A0A0A00000000\",\"0A0A0A0A0A0A0A0A\",\"0A0A0A0A14141414\",\"0A0A0A0A1E1E1E1E\",\"0A0A0A0A28282828\",\"0A0A0A0A32323232\",\"0A0A0A0A3C3C3C3C\",\"0A0A0A0A46464646\",\"0A0A0A0A50505050\",\"0A0A0A0A5A5A5A5A\",\"0A0A0A0A64646464\"]",
        "time1": 1,
        "time2": 1,
        "clientId": connectionId,
        "targetId": targetId
    }
    json_data_wave = json.dumps(data_to_send_wave)
    ws.send(json_data_wave) # 通过WebSocket发送数据
    
# WebSocket回调函数
def on_message(ws, message):
    print("Received:", message)
    msg_json = json.loads(message)
    global flag
    global connectionId
    global targetId
    connectionId = msg_json["clientId"]
    targetId = msg_json["targetId"]
    if msg_json["type"] == "bind":
        img = qrcode.make('https://www.dungeon-lab.com/app-download.php#DGLAB-SOCKET#ws://10.50.147.215:9999/' + connectionId)
        type(img)  # qrcode.image.pil.PilImage
        img.save("some_file.png") # 保存二维码
        data_to_send = {
            "type": 4,
            "message":"strength-1+2+35",
            "clientId": connectionId,
            "targetId": targetId
        }
        json_data = json.dumps(data_to_send)
        ws.send(json_data) # 通过WebSocket发送数据

def on_error(ws, error): #错误
    print("Error:", error)

def on_close(ws): #关闭
    print("Connection closed")

def on_open(ws): #打开
    print("Connection opened")



ws = websocket.WebSocketApp(server_address,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open

dispatcher = Dispatcher()

# 此处dglabA为OSC传出参数，例如你模型上的一个VRCContactReceiver 如果需要运行请修改它
dispatcher.map("/avatar/parameters/dglabA", print_handler)

server = BlockingOSCUDPServer((ip, port), dispatcher)

# 启动WebSocket线程
t1 = threading.Thread(target=ws.run_forever)
t1.start()

print("OSC 服务器开始监听...")
server.serve_forever() # 启动OSC服务器