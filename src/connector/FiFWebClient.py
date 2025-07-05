import json

from playwright.sync_api import Page, sync_playwright


class FiFWebClient:
    urls = {
        "login": "https://www.fifedu.com/iplat/fifLogin/index.html?v=5.3.3",
        "ai_task": "https://static.fifedu.com/static/fiforal/kyxl-web-static/student-h5/index.html#/pages/teaching/teaching",
        "unit_test": "https://static.fifedu.com/static/fiforal/kyxl-web-static/student-h5/index.html#/pages/webView/testWebView/testWebView?userId={}&taskId={}&unitId={}&gId={}",
    }
    api_urls = {
        "get_user_info": "https://www.fifedu.com/iplatform-zjzx/common/connect",
        "get_task_list": "https://moral.fifedu.com/kyxl-app/stu/task/teaTaskList",
        "get_task_detail": "https://moral.fifedu.com/kyxl-app/task/stu/teaTaskDetail",
        "get_unit_info": "https://moral.fifedu.com/kyxl-app/stu/column/stuUnitInfo?unitId={}&taskId={}",
        "post_test_results": "https://moral.fifedu.com/kyxl-app-challenge/evaluation/submitChallengeResults",
        "get_test_info": "https://moral.fifedu.com/kyxl-app/column/getLevelInfo",
    }
    user_auth = {"token": None, "source": None}
    user_info = None

    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,
            # args=["--use-fake-device-for-media-stream"]
        )
        self.context = self.browser.new_context(permissions=["microphone"])
        self.page = self.context.new_page()

    def __del__(self):
        self.browser.close()
        self.playwright.stop()

    def login(self, username, password):
        self.page.goto(self.urls["login"])
        self.page.fill('input[name="user"]', username)
        self.page.fill('input[name="pass"]', password)
        self.page.get_by_role("button", name="登录").click()
        self.page.wait_for_load_state("networkidle")

        with self.page.expect_popup() as fif_page:
            self.page.get_by_text("FiF口语训练系统", exact=True).click()
        page1 = fif_page.value
        page1.wait_for_load_state("networkidle")

        self.user_auth["token"] = page1.evaluate(
            "localStorage.getItem('Authorization')"
        )
        self.user_auth["source"] = page1.evaluate("localStorage.getItem('source')")
        page1.close()
        if self.user_auth["token"] is None or self.user_auth["token"] == "":
            raise Exception("登录失败")

        return self.get_user_info()

    def get_user_info(self):
        if self.user_info is not None:
            return self.user_info
        else:
            response = self.page.request.fetch(
                self.api_urls["get_user_info"], method="GET"
            )
            if response.status != 200:
                raise Exception("获取用户信息失败")
            self.user_info = json.loads(response.body())
            return self.user_info

    def get_task_list(self, page):
        response = page.request.fetch(
            self.api_urls["get_task_list"],
            method="post",
            headers={
                "Authorization": "Bearer " + self.user_auth["token"],
                "source": self.user_auth["source"],
            },
            form={
                "userId": self.get_user_info()["data"]["userId"],
                "status": 1,
                "page": 1,
            },
        )
        json = response.json()
        if json["status"] == -1:
            raise Exception("获取任务列表失败")
        return json

    def get_ttd_list(self, page, task_id):
        response = page.request.fetch(
            self.api_urls["get_task_detail"],
            method="post",
            form={
                "userId": self.get_user_info()["data"]["userId"],
                "id": task_id,
            },
            headers={
                "Authorization": "Bearer " + self.user_auth["token"],
                "source": self.user_auth["source"],
            },
        )
        json = response.json()
        if json["status"] == -1:
            raise Exception("获取任务详情失败")
        return json

    def get_unit_info(self, page, unit_id, task_id):
        response = page.request.fetch(
            self.api_urls["get_unit_info"].format(unit_id, task_id),
            method="get",
            headers={
                "Authorization": "Bearer " + self.user_auth["token"],
                "source": self.user_auth["source"],
            },
        )
        json = response.json()
        if json["status"] == -1:
            raise Exception("获取单元信息失败")
        return json

    def start_level_test(self, page: Page, speaker, unit_id, task_id, level_id, is_vocabulary: bool = False): # 增加 is_vocabulary 参数
        print("[FiFWebClient] 尝试加载{}答案。".format(level_id))
        try:
            answer = self.get_level_answer(page, level_id)
            if answer != []:
                print("已加载{}条答案。".format(len(answer)))
        except Exception:
            raise "加载答案失败。"

        page.goto(
            self.urls["unit_test"].format(
                self.get_user_info()["data"]["userId"],
                task_id,
                unit_id,
                level_id,
            )
        )

        page.wait_for_load_state("networkidle")

        page.frame_locator("iframe").get_by_role("tab", name="挑战").click()
        page.frame_locator("iframe").get_by_role("button", name="开始挑战").click()

        # 等待3秒
        page.wait_for_timeout(3000)

        for answer_index, answer_text in enumerate(answer):
            print("等待开始录音。")
            page.frame_locator("iframe").get_by_text("结束录音").is_enabled(timeout=0)

            print("正在回答第{}条。答案，内容为：\n{}".format(answer_index + 1, answer_text))
            speaker.speak(answer_text)
            print("第{}条回答完成。".format(answer_index + 1))

            page.frame_locator("iframe").get_by_text("结束录音").click()

        print("挑战完成。等待提交。")

        page.get_by_text("AI 评分").is_enabled(timeout=0)  # 阻塞

        print("当前单元结束。")

    def get_level_answer(self, page: Page, level_id):
        response = page.request.fetch(
            self.api_urls["get_test_info"],
            method="post",
            form={
                "levelId": level_id,
            },
            headers={
                "Authorization": "Bearer " + self.user_auth["token"],
                "source": self.user_auth["source"],
            },
        ).json()
        if response["status"] != 1:
            raise Exception(
                f"获取等级 {level_id} 信息失败，API返回状态码: {response.get('status', 'N/A')}, 消息: {response.get('msg', 'N/A')}")

        qcontent_list = [
            _i for _i in response["data"]["content"]["moshi"] if _i["name"] == "挑战"
        ]

        if not qcontent_list:
            print(f"[WARN] 等级 {level_id} 的 'moshi' 中未找到名为 '挑战' 的内容。")
            return []

        qcontent = qcontent_list[0]["question"]["qcontent"]

        answer = []

        # --- 优先尝试解析基于 qcontent["text"] 的对话类型题目 (例如“论文答辩”, “毕业典礼”) ---
        if "text" in qcontent and qcontent["text"]:
            print(f"[DEBUG] 检测到等级 {level_id} 包含 'text' 字段，尝试解析对话类型答案。")
            dialogue_parts = qcontent["text"].split("##")

            m1_sentences = []
            w1_sentences = []
            first_speaker = None  # 用于存储对话的第一个发言者

            for part in dialogue_parts:
                part_stripped = part.strip()
                if not part_stripped:
                    continue

                # 确定第一个发言者
                if first_speaker is None:
                    if part_stripped.startswith("m1:"):
                        first_speaker = "m1"
                    elif part_stripped.startswith("w1:"):
                        first_speaker = "w1"

                # 分类句子
                if part_stripped.startswith("m1:"):
                    sentence = part_stripped[len("m1:"):].strip()
                    if sentence:
                        m1_sentences.append(sentence)
                elif part_stripped.startswith("w1:"):
                    sentence = part_stripped[len("w1:"):].strip()
                    if sentence:
                        w1_sentences.append(sentence)

            # 根据第一个发言者来决定读取顺序
            if first_speaker == "w1":
                # 如果第一个发言者是 w1 (非用户角色)，那么用户角色 m1 的句子应该先读
                print(f"[DEBUG] 对话由 w1: 开始，按 'm1 -> w1' 顺序收集答案。")
                answer.extend(m1_sentences)
                answer.extend(w1_sentences)
            elif first_speaker == "m1":
                # 如果第一个发言者是 m1 (用户角色)，那么另一个角色 w1 的句子应该先读
                print(f"[DEBUG] 对话由 m1: 开始，按 'w1 -> m1' 顺序收集答案。")
                answer.extend(w1_sentences)
                answer.extend(m1_sentences)
            else:
                # 极端情况，如果没识别出任何发言者，可以根据默认策略或报错
                print(f"[WARN] 未能识别等级 {level_id} 对话的第一个发言者，默认按 'm1 -> w1' 顺序。")
                answer.extend(m1_sentences)
                answer.extend(w1_sentences)

            if answer:
                print(f"[DEBUG] 从 'text' 字段中成功提取到 {len(answer)} 条答案。")
                return answer
            else:
                print(f"[WARN] 从等级 {level_id} 的 'text' 字段中未能提取到有效答案。")

        # --- 如果从 'text' 字段未能获取到答案，则尝试解析常规问答和角色扮演题型 (包含 'item' 的结构) ---
        # ... (这部分保持不变，与之前版本相同) ...
        if "item" in qcontent and qcontent["item"]:
            if qcontent["item"][0] and "questions" in qcontent["item"][0] and qcontent["item"][0]["questions"]:
                if "photo" in qcontent["item"][0]["questions"][0]:
                    print(f"[DEBUG] 等级 {level_id} 未通过 'text' 结构解析，尝试解析 'photo' 角色扮演类型。")
                    answer = self.get_playrole_type_answer(qcontent)
                else:
                    print(f"[DEBUG] 等级 {level_id} 未通过 'text' 结构解析，尝试解析常规问答类型。")
                    for _i in qcontent["item"]:
                        for _j in _i["questions"]:
                            answer.append(_j["title"])
            else:
                print(f"[WARN] 等级 {level_id} 的题目内容中 'item' 下的 'questions' 结构缺失或为空。")
        else:
            print(f"[WARN] 等级 {level_id} 的题目内容中没有找到 'item' 或 'item' 为空。")

        return answer

    def get_playrole_type_answer(self, qcontent):
        answer = {}
        # count role init
        role_init_count = {}
        for _i in qcontent["item"]:
            for _j in _i["questions"]:
                locate = (
                    int(_j["recordingTime"].split("#")[0])
                    if _j["recordingTime"].strip() != ""
                    else -1
                )
                if locate != -1:
                    role_init_count[_j["photo"]] = locate
                else:
                    role_init_count[_j["photo"]] = 0

        # init answer list to role
        for _i in qcontent["item"]:
            for _j in _i["questions"]:
                if not _j["photo"] in answer:
                    answer[_j["photo"]] = [
                        "" for _ in range(role_init_count[_j["photo"]])
                    ]

        for _i in qcontent["item"]:
            for _j in _i["questions"]:
                locate = (
                    int(_j["recordingTime"].split("#")[0])
                    if _j["recordingTime"] != ""
                    else -1
                )
                answer_string = _j["title"]

                # remove string from '<' to '>' in answer_string
                while answer_string.find("<") != -1:
                    answer_string = (
                        answer_string[: answer_string.find("<")]
                        + answer_string[answer_string.find(">") + 1 :]
                    )

                if locate != -1:
                    answer[_j["photo"]][locate - 1] += answer_string
                else:
                    answer[_j["photo"]].append(answer_string)
        result = []
        sample = qcontent["sample"].split("#")
        if sample == [""]:
            sample = [_i for _i in answer.keys()]
        for role in sample:
            for answer_string in answer[role]:
                result.append(answer_string)
        return result

    def get_page(self):
        return self.page

    def get_context(self):
        return self.context

    def get_browser(self):
        return self.browser

    def get_playwright(self):
        return self.playwright

    def get_url(self):
        return self.url
