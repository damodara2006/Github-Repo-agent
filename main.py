from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
import requests
import base64
from fastapi import FastAPI , Request
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import GithubFileLoader
import json
from rich.markdown import Markdown
from rich.console import Console
app = FastAPI()
# from pathlib import Path
load_dotenv()
# print(Path.cwd())
# GithubFileLoader()
@app.post("/")
async def func(res : Request, github_username:str, repo_name:str):
    try:
        header = res.headers
        auth = header.get("authorization")
    
        auth = auth.split(" ")[1]
        loader = GithubFileLoader(
            repo=f"{github_username}/{repo_name}", 
            branch="main",  
            access_token=auth,
            github_api_url="https://api.github.com",
            file_filter=lambda file_path: file_path.endswith(
                (".js", ".jsx")
            ),  
        )
        documents = loader.load()
        code = ""
        for doc in documents:
            code+= doc.page_content
        # documents = loader.load()  # List of Document objects, each with page_content (file text) and metadata (path, etc.)
        llm = init_chat_model("groq:llama-3.3-70b-versatile")
        promt = ChatPromptTemplate.from_messages(
            [
                ("system", "you are chat bot for generating a content based on the code provided, you need to explain what that code does and that code is fetched from github repository you need to reply by explaining what that code does like a readme in simple english and make it crispy generate only what is the use of this repo"),
                ("user", "the code is : {code}")
            ]
        )
        
        promt = promt.invoke({"code" : code})
        res = llm.invoke(promt).content
        console = Console()
        console.print(Markdown(res))
        # pprint
        return {"data" : res}
    except Exception as e:
        # print(str(e))
        return str(e)
    

        
    
    
