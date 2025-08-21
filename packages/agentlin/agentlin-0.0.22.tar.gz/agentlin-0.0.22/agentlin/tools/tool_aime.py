from loguru import logger
import json
import requests

from agentlin.core.agent_schema import generate_short_uuid
from agentlin.core.multimodal import image_content, read_image_http_url


tool_server_url = "https://internal-idc-equ.ainvest.com/ind/aime-langchain-engine-server/iwencai/dialog/chain/execute"
# tool_server_url = "http://127.0.0.1:8989/aime"


def run_FinQuery(query: str):
    obj = """{
    "chain_name": "FinQueryForLinXueYuan",
    "req_type": "nostream",
    "user_id": "wangqihan",
    "session_id": "fpg9ms0oenz78m0o3ndblxpy",
    "question_id": "10e150d9-8afd-4cc6-9ee9-52cd5b38b9a6",
    "trace_id": "debug_platform_f20544ec461345d2b89c9f8271595935",
    "debug": true,
    "source": "ths_wencai_international",
    "human_message": "option with days to expiration between 15days and 45 days，implied volatility <30%; 0.3 < delta < 0.4; trading volume > 500; open interest > 1000",
    "question": "TM week low and week high",
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
                "code": "TM.N",
                "name": "Toyota Motor",
                "type": "stock",
                "word": null,
                "start_pos": null,
                "first_start_pos": -1,
                "stock_code": "TM"
            }
        ],
        "indexes": [],
        "dates": [],
        "numbers": [],
        "detail_date_time": [],
        "ner": [
            {
                "word": "tm",
                "name": "Toyota Motor",
                "code": "TM.N",
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
                "type": "stock",
                "start_pos": [
                    0
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
    "action_name": "inspect stocks",
    "thought_infos": [],
    "accept_content": null,
    "events": [],
    "agent_config": null,
    "agent_id": "",
    "transfer_question": null,
    "request_id": "2ab696df-4107-415c-8bd6-3ee8659ea278",
    "agent_chain_request": null,
    "messages": null,
    "multimodal_messages": null,
    "manual_id": "",
    "no_stream": true,
    "client_id": "",
    "stream": false,
    "token": "",
    "param_enable": false
}"""
    obj = json.loads(obj)
    obj["human_message"] = query
    obj["question"] = query
    req = requests.post(tool_server_url, json=obj, timeout=10)
    resp = req.json()
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


def run_CryptoQuery(query: str):
    obj = """{
    "chain_name": "CryptoQueryForLinXueYuan",
    "req_type": "nostream",
    "user_id": "wangqihan",
    "session_id": "fpg9ms0oenz78m0o3ndblxpy",
    "question_id": "10e150d9-8afd-4cc6-9ee9-52cd5b38b9a6",
    "trace_id": "debug_platform_f20544ec461345d2b89c9f8271595935",
    "debug": true,
    "source": "ths_wencai_international",
    "human_message": "option with days to expiration between 15days and 45 days，implied volatility <30%; 0.3 < delta < 0.4; trading volume > 500; open interest > 1000",
    "question": "TM week low and week high",
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
                "code": "TM.N",
                "name": "Toyota Motor",
                "type": "stock",
                "word": null,
                "start_pos": null,
                "first_start_pos": -1,
                "stock_code": "TM"
            }
        ],
        "indexes": [],
        "dates": [],
        "numbers": [],
        "detail_date_time": [],
        "ner": [
            {
                "word": "tm",
                "name": "Toyota Motor",
                "code": "TM.N",
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
                "type": "stock",
                "start_pos": [
                    0
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
    "action_name": "inspect stocks",
    "thought_infos": [],
    "accept_content": null,
    "events": [],
    "agent_config": null,
    "agent_id": "",
    "transfer_question": null,
    "request_id": "2ab696df-4107-415c-8bd6-3ee8659ea278",
    "agent_chain_request": null,
    "messages": null,
    "multimodal_messages": null,
    "manual_id": "",
    "no_stream": true,
    "client_id": "",
    "stream": false,
    "token": "",
    "param_enable": false
}"""
    obj = json.loads(obj)
    obj["human_message"] = query
    obj["question"] = query
    req = requests.post(tool_server_url, json=obj, timeout=10)
    resp = req.json()
    text = ""
    datas: list[dict[str, str]] = []
    try:
        resp_result = resp["response"]["result"][0]
        text = resp_result["text"]
        datas = resp_result.get("query_data", {}).get("datas", [])
    except Exception as e:
        logger.error(f"请求失败: {e}")
        logger.error(f"响应内容: {json.dumps(resp, indent=2, ensure_ascii=False)}")
    return text, datas


def run_Search(query):
    req = requests.post(
        tool_server_url,
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
        if "title" in x and x["title"]:
            if "url" in x and x["url"]:
                texts.append(f"[{x['title']}]({x['url']})")
            else:
                texts.append(f"Title: {x['title']}")
        texts.append(f"ID: {generate_short_uuid()}")
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
    obj = {
        "startDate": startDate,
        "endDate": endDate,
        "codeName": codeName,
        "chartType": chartType,
        "indicator": indicator,
    }
    obj_json = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    # print(obj_json)
    req = requests.post(
        tool_server_url,
        json={
            "chain_name": "TickerChart",
            "req_type": "nostream",
            "user_id": "122",
            "session_id": "143",
            "question_id": "143",
            "trace_id": "1746001144320",
            "debug": True,
            "source": "aicubes_agent_75",
            "human_message": obj_json,
            "question": obj_json,
            "model_param": None,
            "history": None,
            "think_history": None,
            "add_info": {},
            "nlu": None,
            "action_param": None,
            "result_page_info": None,
            "chain_vanish_request": None,
            "user_name": None,
            "client_ip": None,
            "action_name": None,
            "thought_infos": [],
            "accept_content": None,
            "events": None,
            "agent_config": None,
            "agent_id": None,
            "transfer_question": None,
            "request_id": "d9e8c04c-5c53-4a7a-9a21-3ed5661238db",
            "agent_chain_request": None,
            "messages": None,
            "multimodal_messages": None,
            "version": "v1",
            "client_id": "",
            "stream": False,
        },
    )
    resp = req.json()
    url = None
    try:
        resp_result = resp["response"]["result"][0]
        url: str = resp_result["media_info"]["url"]
    except Exception as e:
        logger.error(f"请求失败: {e}")
        logger.error(f"响应内容: {json.dumps(resp, indent=2, ensure_ascii=False)}")
    # print(json.dumps(resp, indent=2, ensure_ascii=False))
    return url


def run_Visual(query: str):
    obj = r"""{
    "chain_name": "visual",
    "req_type": "nostream",
    "user_id": "shiweiwei",
    "session_id": "54b37c52f079e57b02d7635ac4ae757e",
    "question_id": "cc2650c9-690b-4ca7-9b14-77c9a2cb41e7",
    "trace_id": "debug_platform_bba1e0e959244e549d25ccda57863f7a",
    "debug": true,
    "source": "ths_wencai_international",
    "human_message": "aapl net income",
    "question": "aapl net income",
    "model_param": {},
    "history": [
        {
            "time": 0,
            "query": "AAPL net income CUM in the past ten years",
            "answer": "Apple's net income has steadily increased from $45.69 billion in 2016 to $99.8 billion in 2022, showing a strong and consistent growth pattern over the past decade:\n\n",
            "input_media_info": null,
            "output_media_info": null,
            "enable": true
        }
    ],
    "think_history": null,
    "add_info": {
        "input_type": "typewrite",
        "task_type": "offline_batch_data",
        "rela_trace_ids": [],
        "account_analysis_support": false,
        "user_lang": "en",
        "urp_data_permission": "hideChargeData",
        "urp_data_permission_bit": "",
        "product_data": [],
        "component_version": "",
        "merge_repeat": false,
        "txt_to_image_processing_num": 0,
        "txt_to_image_task_id": "",
        "txt_to_image_seed": "",
        "multi_media": [],
        "stock_code": "",
        "fallback": false,
        "agent": {
            "noReference": "",
            "referenceNow": "Number: 1\nQuery: AAPL Net Income (Cum) in the past two years\nResults: 2 results found:\n|stock code|stock name|Last Price|Last Change|Net Income (Cum)|Report End Date|Report Period|\n|---|---|---|---|---|---|---|\n|AAPL|Apple|$235.33|-0.17%|$97 billion|20230930|2023Q4|\n|AAPL|Apple|$235.33|-0.17%|$93.74 billion|20240928|2024Q4|\n",
            "reference": "Number: 1\nQuery: AAPL Net Income (Cum) in the past two years\nResults: 2 results found:\n|stock code|stock name|Last Price|Last Change|Net Income (Cum)|Report End Date|Report Period|\n|---|---|---|---|---|---|---|\n|AAPL|Apple|$235.33|-0.17%|$97 billion|20230930|2023Q4|\n|AAPL|Apple|$235.33|-0.17%|$93.74 billion|20240928|2024Q4|\n\n\nNumber: 2\nQuery: AAPL Net Income (Cum) in the past ten years\nResults: 10 results found:\n|stock code|stock name|Last Price|Last Change|Net Income (Cum)|Report End Date|Report Period|\n|---|---|---|---|---|---|---|\n|AAPL|Apple|$235.33|-0.17%|$99.8 billion|20220924|2022Q4|\n|AAPL|Apple|$235.33|-0.17%|$97 billion|20230930|2023Q4|\n|AAPL|Apple|$235.33|-0.17%|$94.68 billion|20210925|2021Q4|\n|AAPL|Apple|$235.33|-0.17%|$93.74 billion|20240928|2024Q4|\n|AAPL|Apple|$235.33|-0.17%|$59.53 billion|20180929|2018Q4|\n|AAPL|Apple|$235.33|-0.17%|$57.41 billion|20200926|2020Q4|\n|AAPL|Apple|$235.33|-0.17%|$55.26 billion|20190928|2019Q4|\n|AAPL|Apple|$235.33|-0.17%|$53.39 billion|20150926|2015Q4|\n|AAPL|Apple|$235.33|-0.17%|$48.35 billion|20170930|2017Q4|\n|AAPL|Apple|$235.33|-0.17%|$45.69 billion|20160924|2016Q4|\n",
            "dialogHistory": "Human: AAPL net income CUM in the past ten years\nAssistant: Apple's net income has steadily increased from $45.69 billion in 2016 to $99.8 billion in 2022, showing a strong and consistent growth pattern over the past decade:\n\n",
            "outline": "",
            "allUserProfile": "The user is interested in the US Tech sector, particularly Artificial Intelligence, MAG7 index, Wearable Technology, and Metaverse. His investment focus includes GICS Sector, Interval Average Trading Volume, P/E ratio, and Pre Market Percentage Change. Recently, he clicked on NVDA 141 times, GOOGL 82 times, and BABA 79 times. He also inquired about the impact of the Greensill collapse on UBS's financial performance and the effect of Japanese debt issuance reduction on JGB yields and global markets. In a previous conversation, he discussed AMD's future valuation, noting that the average price target is $188.44 and analysts are optimistic about its growth prospects.",
            "referenceHistory": "Number: 2\nQuery: AAPL Net Income (Cum) in the past ten years\nResults: 10 results found:\n|stock code|stock name|Last Price|Last Change|Net Income (Cum)|Report End Date|Report Period|\n|---|---|---|---|---|---|---|\n|AAPL|Apple|$235.33|-0.17%|$99.8 billion|20220924|2022Q4|\n|AAPL|Apple|$235.33|-0.17%|$97 billion|20230930|2023Q4|\n|AAPL|Apple|$235.33|-0.17%|$94.68 billion|20210925|2021Q4|\n|AAPL|Apple|$235.33|-0.17%|$93.74 billion|20240928|2024Q4|\n|AAPL|Apple|$235.33|-0.17%|$59.53 billion|20180929|2018Q4|\n|AAPL|Apple|$235.33|-0.17%|$57.41 billion|20200926|2020Q4|\n|AAPL|Apple|$235.33|-0.17%|$55.26 billion|20190928|2019Q4|\n|AAPL|Apple|$235.33|-0.17%|$53.39 billion|20150926|2015Q4|\n|AAPL|Apple|$235.33|-0.17%|$48.35 billion|20170930|2017Q4|\n|AAPL|Apple|$235.33|-0.17%|$45.69 billion|20160924|2016Q4|\n"
        },
        "visual_info": "AAPL net income CUM in the past ten years"
    },
    "nlu": {
        "underlying": [
            {
                "code": "",
                "name": "past two years",
                "type": "time",
                "word": "past two years",
                "start_pos": [
                    29
                ],
                "first_start_pos": 29,
                "stock_code": ""
            },
            {
                "code": "AAPL.O",
                "name": "Apple",
                "type": "stock",
                "word": "aapl",
                "start_pos": [
                    0
                ],
                "first_start_pos": 0,
                "stock_code": "AAPL"
            }
        ],
        "indexes": [
            "net income (cum)",
            "net income",
            "net investment income (cum)",
            "stock code",
            "total revenue (cum)",
            "net profit",
            "gross profit (cum)",
            "net income(quarter)",
            "total comprehensive income (cum)",
            "basic eps (cum)",
            "net interest income (cum)",
            "net investment income",
            "net investment income(quarter)",
            "other comprehensive income (cum)",
            "other net income (cum)",
            "net income (non-gaap) (cum)",
            "accumulated net profit",
            "other net income",
            "net income(quarter)(gaap)",
            "insurance income (cum)",
            "other revenue (cum)"
        ],
        "dates": [
            "past two years"
        ],
        "numbers": [],
        "detail_date_time": [
            {
                "text": "past two years",
                "type": "time",
                "start_date_time": "2023-03-07 00:00:00",
                "end_date_time": "2025-03-06 23:59:59",
                "start_date_time_with_day_str": "2023-03-07 00:00:00",
                "end_date_time_with_day_str": "2025-03-06 23:59:59"
            }
        ],
        "ner": [
            {
                "word": "past two years",
                "name": "past two years",
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
                "market_code": "",
                "type": "time",
                "start_pos": [
                    29
                ]
            },
            {
                "word": "aapl",
                "name": "Apple",
                "code": "AAPL.O",
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
                    0
                ]
            }
        ],
        "zhi_shu_code": []
    },
    "action_param": {
        "subject": {
            "stock": [
                "AAPL.O"
            ],
            "fund": [],
            "zhishu": [],
            "first_stock": "AAPL.O",
            "first_fund": null,
            "first_zhishu": null
        },
        "dimension": {
            "dim": [],
            "one_dim": null
        },
        "attribute": {
            "index": [
                "net income (cum)",
                "net income",
                "net investment income (cum)",
                "stock code",
                "total revenue (cum)",
                "net profit",
                "gross profit (cum)",
                "net income(quarter)",
                "total comprehensive income (cum)",
                "basic eps (cum)",
                "net interest income (cum)",
                "net investment income",
                "net investment income(quarter)",
                "other comprehensive income (cum)",
                "other net income (cum)",
                "net income (non-gaap) (cum)",
                "accumulated net profit",
                "other net income",
                "net income(quarter)(gaap)",
                "insurance income (cum)",
                "other revenue (cum)"
            ],
            "event": [],
            "kg_label": null,
            "first_index": "net income (cum)",
            "first_event": null,
            "first_kg_label": null
        },
        "command": {
            "param": ""
        },
        "slots": [
            {
                "desc": "select one of the following skills to generate answer for user's query: [paragraph visualization, query visualization]",
                "importance": "no",
                "values": [
                    "query visualization"
                ],
                "name_en": "skill",
                "clarify_text": "",
                "extra_msg": null,
                "name": "skill",
                "type": "string",
                "default_value": "",
                "normalize_type": null,
                "normalized": false,
                "ner_types": null,
                "ner_type": null
            }
        ]
    },
    "result_page_info": null,
    "chain_vanish_request": null,
    "user_name": null,
    "client_ip": null,
    "action_name": "inspect stocks",
    "thought_infos": [],
    "accept_content": null,
    "events": [],
    "agent_config": null,
    "agent_id": "",
    "transfer_question": "",
    "request_id": "8f7e2155-e06a-4177-9e9c-c879123f4e8c",
    "agent_chain_request": {
        "tool_results": [
            {
                "text": "2 results found:\n|stock code|stock name|Last Price|Last Change|Net Income (Cum)|Report End Date|Report Period|\n|---|---|---|---|---|---|---|\n|AAPL|Apple|$235.33|-0.17%|$97 billion|20230930|2023Q4|\n|AAPL|Apple|$235.33|-0.17%|$93.74 billion|20240928|2024Q4|\n",
                "mark_down": null,
                "result_page": null,
                "raw_data": null,
                "query_data": {
                    "condition": "",
                    "title": "AAPL Net Income (Cum) in the past two years",
                    "query_type": "intusstock",
                    "model_sql": "select   stock_code,   net_income_cum from   ustock_fin_data where   report_end_date = recent('2y')   and report_period like '%q4'   and stock_code = 'aapl'",
                    "data_ext_params": {
                        "expand_index": true,
                        "merge_repeat": false,
                        "add_index": 0,
                        "data_add": 1
                    },
                    "url": null
                },
                "query_data_list": null,
                "model_info": null,
                "media_info": null
            },
            {
                "text": "10 results found:\n|stock code|stock name|Last Price|Last Change|Net Income (Cum)|Report End Date|Report Period|\n|---|---|---|---|---|---|---|\n|AAPL|Apple|$235.33|-0.17%|$99.8 billion|20220924|2022Q4|\n|AAPL|Apple|$235.33|-0.17%|$97 billion|20230930|2023Q4|\n|AAPL|Apple|$235.33|-0.17%|$94.68 billion|20210925|2021Q4|\n|AAPL|Apple|$235.33|-0.17%|$93.74 billion|20240928|2024Q4|\n|AAPL|Apple|$235.33|-0.17%|$59.53 billion|20180929|2018Q4|\n|AAPL|Apple|$235.33|-0.17%|$57.41 billion|20200926|2020Q4|\n|AAPL|Apple|$235.33|-0.17%|$55.26 billion|20190928|2019Q4|\n|AAPL|Apple|$235.33|-0.17%|$53.39 billion|20150926|2015Q4|\n|AAPL|Apple|$235.33|-0.17%|$48.35 billion|20170930|2017Q4|\n|AAPL|Apple|$235.33|-0.17%|$45.69 billion|20160924|2016Q4|\n",
                "mark_down": null,
                "result_page": null,
                "raw_data": null,
                "query_data": {
                    "condition": "",
                    "title": "AAPL Net Income (Cum) in the past ten years",
                    "query_type": "intusstock",
                    "model_sql": "select   stock_code,   net_income_cum from   ustock_fin_data where   report_end_date = recent('10y')   and report_period like '%q4'   and stock_code = 'aapl'",
                    "data_ext_params": {
                        "expand_index": true,
                        "merge_repeat": false,
                        "add_index": 0,
                        "data_add": 1
                    },
                    "url": null
                },
                "query_data_list": null,
                "model_info": null,
                "media_info": null
            }
        ],
        "page": null,
        "visual_async": true,
        "media_requests": null,
        "role_info": null,
        "llm_context": "",
        "fallback": false,
        "deep_research_answer_prompt_word": null
    },
    "messages": null,
    "multimodal_messages": null,
    "version": "v1",
    "client_id": "",
    "stream": false
}"""
    obj = json.loads(obj)
    obj["human_message"] = query
    obj["question"] = query
    obj["add_info"]["visual_info"] = query
    req = requests.post(tool_server_url, json=obj, timeout=10)
    resp = req.json()
    result_page = None
    try:
        resp_result = resp["response"]["result"][0]
        result_page = resp_result["result_page"]
        result_page = result_page[0] if isinstance(result_page, list) else result_page
    except Exception as e:
        logger.error(f"请求失败: {e}")
        logger.error(f"响应内容: {json.dumps(resp, indent=2, ensure_ascii=False)}")
    component = result_page["components"][0] if "components" in result_page else {}
    # datas = component.get("data", {}).get("datas", [])
    return component


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
    req = requests.post(tool_server_url, json=obj, timeout=10)
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


def run_Forcast(query: str):
    obj = """{
    "chain_name": "Forecast",
    "req_type": "nostream",
    "user_id": "1802946616",
    "session_id": "15adff11d3cfd9809929adffb094e0c5",
    "question_id": "dd0b8813-6240-42ff-a98c-9f6e4edbdf1b",
    "trace_id": "debug_platform_02fc1d21b10847c1abb148d851447923",
    "debug": true,
    "source": "ths_wencai_international",
    "human_message": "Forecast whether TSLA will rise tomorrow",
    "question": "Will TSLA go up tomorrow?",
    "model_param": {},
    "history": [],
    "think_history": null,
    "add_info": {
        "input_type": "typewrite",
        "task_type": "offline_batch_data",
        "rela_trace_ids": [],
        "account_analysis_support": false,
        "user_lang": "en",
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
                "code": "",
                "name": "tomorrow",
                "type": "time",
                "word": "tomorrow",
                "start_pos": [
                    32
                ],
                "first_start_pos": 32,
                "stock_code": ""
            },
            {
                "code": "TSLA.O",
                "name": "Tesla",
                "type": "stock",
                "word": "tsla",
                "start_pos": [
                    17
                ],
                "first_start_pos": 17,
                "stock_code": "TSLA"
            }
        ],
        "indexes": [
            "stock code",
            "the effective date of security code change",
            "securities code before change",
            "stock recommend"
        ],
        "dates": [
            "tomorrow"
        ],
        "numbers": [],
        "detail_date_time": [
            {
                "text": "tomorrow",
                "type": "time",
                "start_date_time": "2025-01-21 00:00:00",
                "end_date_time": "2025-01-21 23:59:59",
                "start_date_time_with_day_str": "2025-01-21 00:00:00",
                "end_date_time_with_day_str": "2025-01-21 23:59:59"
            }
        ],
        "ner": [
            {
                "word": "tomorrow",
                "name": "tomorrow",
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
                "market_code": "",
                "type": "time",
                "start_pos": [
                    32
                ]
            },
            {
                "word": "tsla",
                "name": "Tesla",
                "code": "TSLA.O",
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
                    17
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
    "action_name": "predict stocks",
    "thought_infos": [],
    "accept_content": null,
    "events": [],
    "agent_config": null,
    "agent_id": "",
    "transfer_question": "",
    "request_id": "b25d07de-a816-493e-94aa-97329c109020",
    "agent_chain_request": null,
    "messages": null,
    "multimodal_messages": null,
    "version": "v1",
    "no_stream": true,
    "token": "",
    "param_enable": false,
    "stream": false,
    "manual_id": "",
    "client_id": ""
}"""
    obj = json.loads(obj)
    obj["human_message"] = query
    obj["question"] = query
    req = requests.post(tool_server_url, json=obj, timeout=10)
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
    req = requests.post(tool_server_url, json=obj, timeout=10)
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

    def test_search():
        query = "AAPL news"
        response = run_Search(query)
        print("Query:", query)
        print()
        print("Result:\n", response)
        assert isinstance(response, str), "Search result should be a string"
        assert len(response) > 0, "Search result should not be empty"


    def test_FinQuery():
        query = "TSLA and AAPL stock price in 20 days"
        response, query_data = run_FinQuery(query)
        columns = query_data.get("columns", [])
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
        datas = query_data.get("data", [])

        print(json.dumps(query_data, indent=2, ensure_ascii=False))
        print("Query:", query)
        print()
        print("Result:\n", response)
        assert isinstance(response, str), "FinQuery result should be a string"
        assert len(response) > 0, "FinQuery result should not be empty"
    test_FinQuery()
    print("Test passed!")