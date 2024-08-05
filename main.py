import os.path
import subprocess

from fastapi import FastAPI
from pydantic import BaseModel

from routers import product, user
from utils.data_util import DataUtil
from utils.file_util import FileUtil
from utils.random_util import RandomUtil

app = FastAPI()

pid_mapper_file = "pid_mapper.json"


@app.get("/", summary="ping", deprecated=False)
async def ping():
    return "success"


class Command(BaseModel):
    command: str


@app.post("/bridge/run")
async def run_command(command: Command):
    if command.command is None:
        return {
            "status": "fail",
            "message": "No command provided!"
        }
    random_output_file_path = f"output/{RandomUtil.get_random_string(10)}.txt"
    with open(random_output_file_path, 'w') as file:
        process = subprocess.Popen(command.command, stdout=file, shell=True)
        # don't use process.wait() here, as we need to response immediately
        # process.wait()
        DataUtil.set_data(pid_mapper_file, f"pid_{process.pid}", {
            "command": command.command,
            "output": random_output_file_path
        })
        return {
            "status": "success",
            "message": f"The command is executed, pid: {process.pid}"
        }


@app.get("/bridge/content/all")
async def get_bridge_content_by_pid(pid):
    output_file_path = DataUtil.get_data_by_jsonpath(pid_mapper_file, f"pid_{pid}.output")
    print(output_file_path)
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
            "message": f"Cannot find content related to your pid {pid}, please double check!"
        }
    start_line = int(start_line) - 1
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
    return {
        "pids": pids,
        "details": pid_mapper
    }


@app.post("/bridge/contents/clear")
async def clear_bridge_contents():
    output_files = FileUtil.list_all_files("output")
    for file in output_files:
        FileUtil.remove_if_exist(file)
    FileUtil.clear(pid_mapper_file)
    return {
        "status": "success",
        "quantity": len(output_files)
    }


@app.post("/bridge/content/clear")
async def clear_bridge_content_by_pid(pid):
    output_file_path = DataUtil.get_data_by_jsonpath(pid_mapper_file, f"pid_{pid}")
    print(output_file_path)
    if not output_file_path or not os.path.exists(output_file_path):
        return {
            "status": "success",
            "message": f"No need to clear content for pid {pid}"
        }
    output_files = FileUtil.list_all_files("output")
    for file in output_files:
        FileUtil.remove_if_exist(file)
    data = DataUtil.get_data(pid_mapper_file)
    del data[f"pid_{pid}"]
    FileUtil.clear(pid_mapper_file)
    FileUtil.write(pid_mapper_file, data)


FileUtil.makedirs_if_not_exist("output")
FileUtil.create_file_if_not_exist(pid_mapper_file)

# below is for demo usage
# app.include_router(product.router)
# app.include_router(user.router)
