from loguru import logger
import json
import requests

from agentlin.core.agent_schema import generate_short_uuid, image_content, read_image_http_url


tool_server_url = "http://190.92.231.77:880/iwencai/dialog/chain/execute"
# tool_server_url = "http://127.0.0.1:8989/wencai"


def request_chain(json: dict, timeout=30):
    # curl -X POST http://190.92.231.77:880/iwencai/dialog/chain/execute \
    # -H "Host: aime-langchain-engine-server" \
    # -H "X-Arsenal-Auth: aime-reinforcement-learning-environment-access" \
    # -H "Content-Type: application/json" \
    # -d '{"chain_name":"FinQuery","req_type":"nostream","human_message":"pe","debug":"false","source":"ths_mobile_yuyinzhushou"}'
    headers = {
        "Host": "aime-langchain-engine-server",
        "X-Arsenal-Auth": "aime-reinforcement-learning-environment-access",
        "Content-Type": "application/json"
    }
    response = requests.post(tool_server_url, headers=headers, json=json, timeout=timeout)
    return response


def run_FinQuery(query: str):
    obj = """{
    "chain_name": "RawFinQuery",
    "req_type": "nostream",
    "user_id": "516341571",
    "session_id": "76aca1e22af21a8550af5998b3345997",
    "question_id": "74f72139-3a43-449b-abad-a27125c8fcfe",
    "trace_id": "20003020175249303327900000000540",
    "debug": true,
    "source": "ths_mobile_yuyinzhushou",
    "human_message": "市盈率>10",
    "question": "pe>10",
    "model_param": {},
    "history": [],
    "think_history": null,
    "add_info": {
        "input_type": "typewrite",
        "task_type": "online_user",
        "rela_trace_ids": [],
        "device_type": "android",
        "question_risk_tags": [],
        "user_lang": "",
        "urp_data_permission": "hideChargeData",
        "urp_data_permission_bit": "",
        "product_data": [],
        "component_version": "1.1.3",
        "merge_repeat": true,
        "come_from": "ShouchaoZixuanIcon",
        "ability_version": "advance",
        "txt_to_image_processing_num": 0,
        "txt_to_image_task_id": "",
        "txt_to_image_seed": "",
        "multi_media": [],
        "stock_code": "",
        "frontend_version": "3.4.1",
        "fallback": false,
        "agent": {
            "toolResults": ""
        },
        "hideChargeData": false
    },
    "nlu": {
        "underlying": [],
        "indexes": [],
        "dates": [],
        "numbers": [
            "10"
        ],
        "detail_date_time": [],
        "ner": [],
        "zhi_shu_code": []
    },
    "action_param": null,
    "result_page_info": null,
    "chain_vanish_request": null,
    "user_name": null,
    "client_ip": null,
    "action_name": "选股票",
    "thought_infos": [],
    "accept_content": null,
    "events": [],
    "agent_config": null,
    "agent_id": "",
    "transfer_question": "",
    "request_id": "c8f07304-4f60-4ad3-9468-f12311f5e132",
    "agent_chain_request": null,
    "messages": null,
    "multimodal_messages": null,
    "version": "v1",
    "stream": false,
    "client_id": ""
}"""
    obj = json.loads(obj)
    obj["human_message"] = query
    obj["question"] = query
    resp = request_chain(json=obj, timeout=10)
    resp = resp.json()
    text = ""
    query_data: dict[str, list[dict[str, str]]] = {}
    try:
        resp_result = resp["response"]["result"][0]
        text = resp_result["text"]
        query_data = resp_result.get("query_data", {})
        datas = query_data.get("datas", [])
    except Exception as e:
        logger.error(f"请求失败: {e}")
        logger.error(f"响应内容: {json.dumps(resp, indent=2, ensure_ascii=False)}")
    return text, datas


def run_Search(query):
    req = request_chain(
        json={
            "chain_name": "Search",
            "req_type": "nostream",
            "human_message": query,
            "debug": "false",
            "source": "ths_mobile_yuyinzhushou",
        },
    )
    resp = req.json()
    raw_data = []
    try:
        resp_result = resp["response"]["result"][0]
        raw_data: list[dict[str, str]] = resp_result["raw_data"]
    except Exception as e:
        logger.error(f"请求失败: {e}")
        logger.error(f"响应内容: {json.dumps(resp, indent=2, ensure_ascii=False)}")

    obs = []
    for i, x in enumerate(raw_data):
        texts = []
        texts.append(f"ID: {generate_short_uuid()}")
        if "title" in x and x["title"]:
            texts.append(f"Title: {x['title']}")
        if "url" in x and x["url"]:
            texts.append(f"URL: {x['url']}")
        if "publish_time" in x and x["publish_time"]:
            texts.append(f"Publish Time: {x['publish_time']}")
        if "summary" in x and x["summary"]:
            texts.append(f"Summary: {x['summary']}")
        # if "full_summary" in x and x["full_summary"]:
        #     texts.append(f"Content: {x['full_summary']}")
        obs.append("\n".join(texts))
    return "\n\n".join(obs)


def run_TickerChart(
    startDate: str = "2023-01-01",
    endDate: str = "2025-04-30",
    codeName: str = "MSFT",
    chartType: str = "Weekly Candlestick",
    indicator: list[str] = ["MA", "MACD", "RSI", "BOLL"],
):
    query = {
        "startDate": startDate,
        "endDate": endDate,
        "codeName": codeName,
        "chartType": chartType,
        "indicator": indicator,
    }
    query = json.dumps(query, ensure_ascii=False, separators=(",", ":"))
    # print(obj_json)
    req_json = """{
    "chain_name": "TickerChart@v1.0.2",
    "req_type": "nostream",
    "user_id": "122",
    "session_id": "143",
    "question_id": "143",
    "trace_id": "1746001144320",
    "debug": true,
    "source": "aicubes_agent_75",
    "human_message": "{\"startDate\":\"2023-01-01\",\"chartType\":\"Weekly Candlestick\",\"endDate\":\"2025-04-30\",\"codeName\":\"同花顺\",\"indicator\":[\"MA\",\"MACD\",\"RSI\",\"BOLL\"]}",
    "question": "{\"startDate\":\"2023-01-01\",\"chartType\":\"Weekly Candlestick\",\"endDate\":\"2025-04-30\",\"codeName\":\"MSFT\",\"indicator\":[\"MA\",\"MACD\",\"RSI\",\"BOLL\"]}",
    "model_param": null,
    "history": null,
    "think_history": null,
    "add_info": {},
    "nlu": null,
    "action_param": null,
    "result_page_info": null,
    "chain_vanish_request": null,
    "user_name": null,
    "client_ip": null,
    "action_name": null,
    "thought_infos": [],
    "accept_content": null,
    "events": null,
    "agent_config": null,
    "agent_id": null,
    "transfer_question": null,
    "request_id": "d9e8c04c-5c53-4a7a-9a21-3ed5661238db",
    "agent_chain_request": null,
    "messages": null,
    "multimodal_messages": null,
    "version": "v1",
    "client_id": "",
    "stream": false
}"""
    req = json.loads(req_json)
    req["human_message"] = query
    req["question"] = query
    resp = request_chain(json=req, timeout=10)
    resp = resp.json()
    url = None
    try:
        resp_result = resp["response"]["result"][0]
        url: str = resp_result["media_info"]["url"]
    except Exception as e:
        logger.error(f"请求失败: {e}")
        logger.error(f"响应内容: {json.dumps(resp, indent=2, ensure_ascii=False)}")
    # print(json.dumps(resp, indent=2, ensure_ascii=False))
    return url


def run_BackTest(query: str):
    obj = """{
    "chain_name": "BackTest",
    "req_type": "nostream",
    "user_id": "1801861676",
    "session_id": "7xtkiy4geota2euh9l928bxo",
    "question_id": "4885c1dc-205f-44a1-8ee1-3d473f0c02e5",
    "trace_id": "23232132",
    "debug": true,
    "source": "ths_wencai_international",
    "human_message": "Backtest the impact of MACD Golden Cross on Nvidia",
    "question": "Backtest the impact of MACD Golden Cross on Nvidia",
    "model_param": null,
    "history": null,
    "think_history": null,
    "add_info": {
        "input_type": "typewrite",
        "task_type": "offline_batch_data",
        "rela_trace_ids": [],
        "user_lang": "",
        "urp_data_permission": "hideChargeData",
        "urp_data_permission_bit": "",
        "product_data": [],
        "component_version": "",
        "merge_repeat": false,
        "txt_to_image_processing_num": 0,
        "txt_to_image_task_id": "",
        "txt_to_image_seed": "",
        "multi_media": [],
        "stock_code": ""
    },
    "nlu": {
        "underlying": [
            {
                "code": "NVDA.O",
                "name": "Nvidia",
                "type": "stock",
                "word": "nvidia",
                "start_pos": [
                    44
                ],
                "stock_code": "NVDA",
                "first_start_pos": 44
            }
        ],
        "indexes": [
            "stock code",
            "macd",
            "macd record high",
            "triple golden cross",
            "triple golden cross"
        ],
        "dates": [],
        "numbers": [],
        "detail_date_time": [],
        "ner": [
            {
                "word": "nvidia",
                "name": "Nvidia",
                "code": "NVDA.O",
                "ths_industry": null,
                "fund_manager": null,
                "investment_type": null,
                "index_tracking": null,
                "skilled_in_type": null,
                "etf_secondary_classify": null,
                "index_type": null,
                "underlying_stock_name": null,
                "futures_type": null,
                "stock_attribute": null,
                "market_code": "-71",
                "type": "stock",
                "start_pos": [
                    44
                ]
            }
        ],
        "zhi_shu_code": []
    },
    "action_param": null,
    "result_page_info": null,
    "chain_vanish_request": null,
    "user_name": null,
    "client_ip": null,
    "action_name": "perform backtests",
    "thought_infos": [],
    "accept_content": null,
    "events": [],
    "agent_config": null,
    "agent_id": "",
    "transfer_question": null,
    "request_id": "7f0385d3-4906-4422-9c6d-840347bf47b6",
    "agent_chain_request": null,
    "messages": null,
    "multimodal_messages": null,
    "version": "v1",
    "stream": false,
    "no_stream": true,
    "client_id": "",
    "manual_id": "",
    "param_enable": false,
    "token": ""
}
"""
    obj = json.loads(obj)
    obj["human_message"] = query
    obj["question"] = query
    req = request_chain(json=obj, timeout=10)
    resp = req.json()
    texts = []
    try:
        resp_results = resp["response"]["result"]
        if resp_results is not None and len(resp_results) > 0:
            for resp_result in resp_results:
                text = resp_result.get("text", "")
                if text:
                    texts.append(text)
    except Exception as e:
        logger.error(f"请求失败: {e}")
        logger.error(f"响应内容: {json.dumps(resp, indent=2, ensure_ascii=False)}")
    text = "\n\n".join(texts)
    if not text:
        text = "No results found for the backtest query."
    return text


def run_Forecast(query: str):
    obj = """{
    "chain_name": "Forecast",
    "req_type": "nostream",
    "user_id": "516341571",
    "session_id": "76aca1e22af21a8550af5998b3345997",
    "question_id": "74f72139-3a43-449b-abad-a27125c8fcfe",
    "trace_id": "20003020175249303327900000000540",
    "debug": true,
    "source": "ths_mobile_yuyinzhushou",
    "human_message": "茅台",
    "question": "pe>10",
    "model_param": {},
    "history": [],
    "think_history": null,
    "add_info": {
        "input_type": "typewrite",
        "task_type": "online_user",
        "rela_trace_ids": [],
        "device_type": "android",
        "question_risk_tags": [],
        "user_lang": "",
        "urp_data_permission": "hideChargeData",
        "urp_data_permission_bit": "",
        "product_data": [],
        "component_version": "1.1.3",
        "merge_repeat": true,
        "come_from": "ShouchaoZixuanIcon",
        "ability_version": "advance",
        "txt_to_image_processing_num": 0,
        "txt_to_image_task_id": "",
        "txt_to_image_seed": "",
        "multi_media": [],
        "stock_code": "",
        "frontend_version": "3.4.1",
        "fallback": false,
        "agent": {
            "toolResults": ""
        },
        "hideChargeData": false
    },
    "nlu": {
        "underlying": [],
        "indexes": [],
        "dates": [],
        "numbers": [
            "10"
        ],
        "detail_date_time": [],
        "ner": [],
        "zhi_shu_code": []
    },
    "action_param": null,
    "result_page_info": null,
    "chain_vanish_request": null,
    "user_name": null,
    "client_ip": null,
    "action_name": "选股票",
    "thought_infos": [],
    "accept_content": null,
    "events": [],
    "agent_config": null,
    "agent_id": "",
    "transfer_question": "",
    "request_id": "c8f07304-4f60-4ad3-9468-f12311f5e132",
    "agent_chain_request": null,
    "messages": null,
    "multimodal_messages": null,
    "version": "v1",
    "stream": false,
    "client_id": ""
}"""
    obj = json.loads(obj)
    obj["human_message"] = query
    obj["question"] = query
    req = request_chain(json=obj, timeout=10)
    resp = req.json()
    texts = []
    try:
        resp_results = resp["response"]["result"]
        if resp_results is not None and len(resp_results) > 0:
            for resp_result in resp_results:
                text = resp_result.get("text", "")
                if text:
                    texts.append(text)
    except Exception as e:
        logger.error(f"请求失败: {e}")
        logger.error(f"响应内容: {json.dumps(resp, indent=2, ensure_ascii=False)}")
    text = "\n\n".join(texts)
    if not text:
        text = "No results found for the backtest query."
    return text


def run_Reminder(query: str):
    obj = """{
    "chain_name": "Reminder",
    "req_type": "nostream",
    "user_id": "1800828950",
    "session_id": "d41a0f5f90caa89f3713e68b959d6e1a",
    "question_id": "3c02f968-1ec4-422e-8123-f85d8caf328c",
    "trace_id": "20003020174712068498600000000154",
    "debug": true,
    "source": "ths_wencai_international",
    "human_message": "Every day at 10:00 to remind—what is the weather like?",
    "question": "提醒我每天早上10点喝水",
    "model_param": {},
    "history": [],
    "think_history": null,
    "add_info": {
        "input_type": "typewrite",
        "task_type": "online_user",
        "rela_trace_ids": [],
        "device_type": "android",
        "question_risk_tags": [],
        "client_id": "",
        "token_id": "",
        "institution_id": "",
        "clear_account": "",
        "manual_id": "",
        "account_analysis_support": true,
        "to_language": "zh",
        "user_lang": "zh-hans",
        "urp_data_permission": "10000_2,10000_1",
        "urp_data_permission_bit": "",
        "product_data": [],
        "component_version": "1.1.3",
        "merge_repeat": false,
        "come_from": "AndroidAinvestOthers",
        "ability_version": "full",
        "txt_to_image_processing_num": 0,
        "txt_to_image_task_id": "",
        "txt_to_image_seed": "",
        "multi_media": [],
        "stock_code": "",
        "fallback": false
    },
    "nlu": {
        "underlying": [
            {
                "code": "",
                "name": "10",
                "type": "number",
                "word": null,
                "start_pos": null,
                "stock_code": "",
                "first_start_pos": -1
            }
        ],
        "indexes": [],
        "dates": [],
        "numbers": [
            "10"
        ],
        "detail_date_time": [],
        "ner": [
            {
                "word": "10",
                "name": "10",
                "code": "",
                "ths_industry": null,
                "fund_manager": null,
                "investment_type": null,
                "index_tracking": null,
                "skilled_in_type": null,
                "etf_secondary_classify": null,
                "index_type": null,
                "underlying_stock_name": null,
                "futures_type": null,
                "stock_attribute": null,
                "market_code": null,
                "type": "number",
                "start_pos": [
                    7
                ]
            }
        ],
        "zhi_shu_code": []
    },
    "action_param": null,
    "result_page_info": null,
    "chain_vanish_request": null,
    "user_name": null,
    "client_ip": null,
    "action_name": "set alerts",
    "thought_infos": [],
    "accept_content": null,
    "events": [
        {
            "event_type": "user_input",
            "event_name": "auto_agent",
            "content": {}
        }
    ],
    "agent_config": null,
    "agent_id": "",
    "transfer_question": "Remind me to drink water at 10:00 am every day.",
    "request_id": "0461645b-dbd7-491b-90d8-564ab283d31a",
    "agent_chain_request": null,
    "messages": null,
    "multimodal_messages": null,
    "version": "v1",
    "stream": false,
    "client_id": ""
}"""
    obj = json.loads(obj)
    obj["human_message"] = query
    obj["question"] = query
    req = request_chain(json=obj, timeout=10)
    resp = req.json()
    texts = []
    try:
        resp_results = resp["response"]["result"]
        if resp_results is not None and len(resp_results) > 0:
            for resp_result in resp_results:
                text = resp_result.get("text", "")
                if text:
                    texts.append(text)
    except Exception as e:
        logger.error(f"请求失败: {e}")
        logger.error(f"响应内容: {json.dumps(resp, indent=2, ensure_ascii=False)}")
    text = "\n\n".join(texts)
    if not text:
        text = "No results found for the backtest query."
    return text


def FinQuery(args: dict):
    query = args["query"]
    result = run_FinQuery(query)
    return {
        "type": "text",
        "text": result,
    }


def Search(args: dict):
    query = args["query"]
    result = run_Search(query)
    return {
        "type": "text",
        "text": result,
    }


def TickerChart(args: dict):
    startDate = args["startDate"]
    endDate = args["endDate"]
    codeName = args["codeName"]
    chartType = args["chartType"]
    indicator = args["indicator"]
    url = run_TickerChart(
        startDate,
        endDate,
        codeName,
        chartType,
        indicator,
    )
    img = read_image_http_url(url)
    img_id = generate_short_uuid()
    return image_content(img, img_id)


tool_map = {
    "FinQuery": FinQuery,
    "Search": Search,
    "TickerChart": TickerChart,
}
tools = [
    {
        "type": "function",
        "function": {
            "name": "FinQuery",
            "description": ("通过 FinQuery API 查询金融数据。" "当知识无法回答用户提出的问题，或用户请求联网搜索时调用此工具。"),
            "parameters": {
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "要查询的文本内容。",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Search",
            "description": "通过搜索引擎搜索互联网上的内容。当知识无法回答用户提出的问题，或用户请求联网搜索时调用此工具。",
            "parameters": {
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "要搜索的文本内容。",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "TickerChart",
            "description": "Get a chart to better understand the technical situation of the financial asset",
            "strict": True,
            "parameters": {
                "type": "object",
                "required": ["startDate", "codeName", "chartType", "indicator", "endDate"],
                "properties": {
                    "startDate": {"type": "string", "description": "Start date in the format YYYY-MM-DD"},
                    "endDate": {"type": "string", "description": "End date in the format YYYY-MM-DD"},
                    "codeName": {"type": "string", "description": "Stock code or ticker symbol"},
                    "chartType": {"type": "string", "description": "Type of chart to retrieve, maximum 1. Enumerate value: Intraday,Daily Candlestick,Weekly Candlestick,Monthly Candlestick"},
                    "indicator": {"type": "array", "items": {"type": "string"}, "description": "List of indicators to display on the chart, maximum 5. Enumerate value: MA,EMA,BIAS,VR,BRAR,WR,SMA,CCI,MTM,BBI,DMI,EMV,VOL,CR,SAR,PSY,AO,DMA,ROC,TRIX,PVT,RSI,OBV,VWAP,BOLL,MACD,KDJ"},
                },
                "additionalProperties": False,
            },
        },
    },
]

if __name__ == "__main__":
    
    def test_forecast():
        query = "茅台"
        response = run_Forecast(query)
        print(response)
        
    test_forecast()

    # def test_search():
    #     query = "同花顺最新新闻"
    #     response = run_Search(query)
    #     print("Query:", query)
    #     print()
    #     print("Result:")
    #     print(response)
    #     assert isinstance(response, str), "Search result should be a string"
    #     assert len(response) > 0, "Search result should not be empty"

    # test_search()


    def test_FinQuery():
        query = "同花顺和东方财富近 3 天股票价格"
        response, query_data = run_FinQuery(query)
        # columns = query_data.get("columns", [])
    #         {
    #   "id": null,
    #   "unit": "$",
    #   "domain": null,
    #   "source": "index",
    #   "label": "NoIndent",
    #   "type": "DOUBLE",
    #   "key": "Closing Price[20250530]",
    #   "timestamp": "20250530",
    #   "subtype": null,
    #   "index_name": "国际美股@Closing Price",
    #   "feKey": "Closing Price[20250530]",
    #   "mx_index": null,
    #   "foldedMxColumns": null,
    #   "sort_info": "desc",
    #   "empty_default_value": null
    # },
        # datas = query_data.get("data", [])

        print(json.dumps(query_data, indent=2, ensure_ascii=False))
        print("Query:", query)
        print()
        print("Result:\n", response)
        assert isinstance(response, str), "FinQuery result should be a string"
        assert len(response) > 0, "FinQuery result should not be empty"
    test_FinQuery()
    print("Test passed!")