import os.path
import subprocess

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils.data_util import DataUtil
from utils.file_util import FileUtil
from utils.random_util import RandomUtil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pid_mapper_file = "pid_mapper.json"


@app.get("/", summary="ping", deprecated=False)
async def ping():
    return "success"


class Command(BaseModel):
    command: str


@app.post("/bridge/run")
async def run_command(command: Command):
    if command.command is None or command.command is "":
        return {
            "status": "fail",
            "message": "No command provided!"
        }
    random_output_file_path = f"output/{RandomUtil.get_random_string(10)}.txt"
    with open(random_output_file_path, 'w') as file:
        # fixme: need to make it able to save to file very quick
        process = subprocess.Popen(command.command, stdout=file, shell=True)
        # don't use process.wait() here, as we need to response immediately
        # process.wait()
        DataUtil.set_data(pid_mapper_file, f"pid_{process.pid}", {
            "command": command.command,
            "output": random_output_file_path
        })
        return {
            "status": "success",
            "message": f"The command is executed~",
            "pid": process.pid
        }


@app.get("/bridge/content/all")
async def get_bridge_content_by_pid(pid):
    output_file_path = DataUtil.get_data_by_jsonpath(pid_mapper_file, f"pid_{pid}.output")
    if not output_file_path or not os.path.exists(output_file_path):
        return {
            "status": "fail",
            "message": f"Cannot find content related to your pid {pid}, please double check!"
        }
    content = FileUtil.read_lines(output_file_path)
    return {
        "status": "success",
        "content": content
    }


@app.get("/bridge/content")
async def get_bridge_content(pid, start_line=0, line_length=10):
    output_file_path = DataUtil.get_data_by_jsonpath(pid_mapper_file, f"pid_{pid}.output")
    if not output_file_path or not os.path.exists(output_file_path):
        return {
            "status": "fail",
            "message": f"Cannot find content related to your pid {pid}, please double check!",
            "content": []
        }
    start_line = int(start_line) - 1
    line_length = int(line_length)
    content = []
    with open(output_file_path, 'r') as file:
        for _ in range(start_line):
            next(file)
        for _ in range(line_length):
            line = file.readline()
            if not line:
                break
            content.append(line)
    return {
        "status": "success",
        "content": content
    }


@app.get("/bridge/pids")
async def get_pids():
    pid_mapper = DataUtil.get_data(pid_mapper_file)
    pids = []
    for pid in pid_mapper:
        pids.append(pid[4:])
    pids = pids[::-1]
    return {
        "pids": pids,
        "details": pid_mapper
    }


@app.post("/bridge/pids/clear")
async def clear_all_pids():
    output_files = FileUtil.list_all_files("output")
    file_deleted_quantity = 0
    for file in output_files:
        try:
            FileUtil.remove_if_exist(file)
            file_deleted_quantity += 1
        except PermissionError:
            pass
    # close pid
    pid_mapper = DataUtil.get_data(pid_mapper_file)
    quantity = 0
    for pid in pid_mapper:
        quantity += 1
        os.system(f"taskkill /F /PID {pid[4:]}")
    # delete pid_mapper_file
    FileUtil.clear(pid_mapper_file)
    clear_quantity = file_deleted_quantity if file_deleted_quantity < quantity else quantity
    return {
        "status": "success",
        "quantity": clear_quantity,
        "message": f"{clear_quantity} pids have been cleared~"
    }


@app.post("/bridge/pid/clear")
async def clear_pid(pid):
    os.system(f"taskkill /F /PID {pid}")

    output_file_path = DataUtil.get_data_by_jsonpath(pid_mapper_file, f"pid_{pid}.output")
    FileUtil.remove_if_exist(output_file_path)
    data = DataUtil.get_data(pid_mapper_file)
    del data[f"pid_{pid}"]
    FileUtil.clear(pid_mapper_file)
    DataUtil.write_json(pid_mapper_file, data)
    return {
        "status": "success",
        "pid": pid,
        "message": f"Clear PID: {pid}, Success~"
    }


FileUtil.makedirs_if_not_exist("output")
FileUtil.create_file_if_not_exist(pid_mapper_file)

# below is for demo usage
# app.include_router(product.router)
# app.include_router(user.router)
