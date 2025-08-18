# sis_system.py
import requests
import re
import random
import string
import certifi
import logging
from lxml import etree
from urllib3.contrib import pyopenssl

# 配置日志
logger = logging.getLogger(__name__)

class ValidationError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

def get_first_or_empty(tree, xpath):
        result = tree.xpath(xpath)
        return result[0] if result else ""

class SisSystem:
    """
    SisSystem 类用于与香港中文大学深圳分校的 SIS 系统交互，支持登录、获取课表、查询课程信息和成绩。
    Attributes:
        username (str): 用户名，用于登录。
        password (str): 密码，用于登录。
        session (requests.Session): HTTP 会话对象，用于保持登录态和 Cookie。
        logged_in (bool): 登录状态标志。
    """

    def __init__(self, username: str, password: str):
        """
        初始化 SisSystem 实例。
        Args:
            username (str): CUHKSZ 学号或用户名（不含前缀）。
            password (str): 对应的登录密码。
        """
        self.username = username
        self.password = password
        self.logged_in = False

        # 使用 pyopenssl 注入到 urllib3
        pyopenssl.inject_into_urllib3()
        self.session = requests.Session()
        self.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/79.0.3945.88 Safari/537.36",
        "Connection": "close",
        }
        logger.info(f"SisSystem instance created for user: {username}")

    def login(self) -> bool:
        """
        登录到 SIS 系统，分为两个阶段：
        1. 向 ADFS 授权端点发起 POST，获取 code。
        2. 使用 code 向 SIS 登录接口发起 POST，完成会话。
        Returns:
            bool: 登录成功返回 True，否则返回 False。
        """
        if self.logged_in:
            logger.info("User already logged in.")
            return True
        
        logger.info("Performing logout to clear any existing session.")
        self.session.get('https://sis.cuhk.edu.cn/psp/csprd/EMPLOYEE/HRMS/?cmd=logout', allow_redirects=True)
        self.session.get('https://sts.cuhk.edu.cn/adfs/ls/?wa=wsignout1.0', allow_redirects=True)
        self.session.get('https://sts.cuhk.edu.cn/adfs/oauth2/logout', allow_redirects=True)

        # 第一步：获取 authorization code
        logger.info("Login Step 1: Requesting authorization code from ADFS.")
        auth_url = (
            "https://sts.cuhk.edu.cn/adfs/oauth2/authorize?"
            "response_type=code"
            "&client_id=3f09a73c-33cf-49b8-8f0c-b79ea2f3e83b"
            "&redirect_uri=https://sis.cuhk.edu.cn/sso/dologin.html"
            "&client-request-id=e4ad901b-ac83-4ace-8413-0040020000e8"
        )
        data1 = {
            'UserName': f'cuhksz\\{self.username}',  # 用户名前需加前缀
            'Password': self.password,
            'Kmsi': 'true',
            'AuthMethod': 'FormsAuthentication'
        }

        # 发起 POST 请求并允许重定向
        r1 = self.session.post(auth_url, data=data1, allow_redirects=True, headers=self.headers)
        # 从重定向后的 URL 中提取 code 参数
        match = re.search(r"[&?]code=([^&]+)", r1.url)
        if not match:
            logger.error("Login Step 1 FAILED. Could not retrieve authorization code. Check credentials.")
            return False
        code = match.group(1)
        logger.info("Login Step 1 SUCCESS. Authorization code obtained.")

        # 第二步：使用 code 完成 SIS 登录
        logger.info("Login Step 2: Using authorization code to log into SIS.")
        params = {
                "cmd": 'login',
                "languageCd": "ENG",
                "code": code,
            }
        
        login_url = "https://sis.cuhk.edu.cn/psp/csprd/"
        
        # 生成随机字符串，用于第二阶段 POST 的 pwd 字段
        data2 = {
            'timezoneOffset': '-480',
            'ptmode': 'f',
            'ptlangcd': 'ENG',
            'ptinstalledlang': 'ENG,ZHT,ZHS',
            'userid': 'CUSZ_SSO_LOGIN',
            'pwd': ''.join(random.choices(string.ascii_uppercase, k=10)),
            'ptlangsel': 'ENG'
        }
        
        r2 = self.session.post(login_url, data=data2, allow_redirects=True, headers=self.headers, params=params)

        cookies = r2.cookies
        cookies.set("PS_DEVICEFEATURES",
                        "width:1728 height:1152 pixelratio:1.25 touch:0 geolocation:1 websockets:1 webworkers:1 datepicker:1 dtpicker:1 timepicker:1 dnd:1 sessionstorage:1 localstorage:1 history:1 canvas:1 svg:1 postmessage:1 hc:0")
        self.session.cookies = cookies

        start_url = "https://sis.cuhk.edu.cn/psc/csprd/EMPLOYEE/HRMS/s/WEBLIB_PTBR.ISCRIPT1.FieldFormula.IScript_StartPage?&"
        
        # 登录后跳转到学生主页的 URL
        home_url = "https://sis.cuhk.edu.cn/psp/csprd/EMPLOYEE/HRMS/h/?tab=STUDENT_HOMEPAGE"
       
        logger.info("Verifying login by accessing the start page.")
        r3 = self.session.get(start_url, headers=self.headers, allow_redirects=True)
        
        if not (home_url in r3.url):
                logger.error("Login Step 2 FAILED. Verification failed. Final URL was: %s", r3.url)
                raise ValidationError("Username or password incorrect!")
        # 判断是否进入主页
        else:
            self.logged_in = True
            logger.info("Login Step 2 SUCCESS. Successfully logged in and redirected to homepage.")
            return True

    def get_schedule(self) -> str:
        """
        获取当前用户的课程表。
        Returns:
            str: 格式化后的课程表文本。
        """
        logger.info("Attempting to get schedule.")
        if not self.login():
            return "请先登录后再获取课表。"
        # 请求课表页面
        url = (
            "https://sis.cuhk.edu.cn/psc/csprd/EMPLOYEE/HRMS/"
            "c/SA_LEARNER_SERVICES.SSR_SSENRL_SCHD_W.GBL?"
            "FolderPath=PORTAL_ROOT_OBJECT.CO_EMPLOYEE_SELF_SERVICE.HCCC_ENROLLMENT.HC_SSR_SSENRL_SCHD_W_GBL"
            "&IsFolder=false"
        )
        logger.info("Fetching schedule page...")
        r = self.session.get(url)
        html = r.text
        # 提取表格 HTML 片段，避免页面其他内容干扰
        start = html.find("<table cellspacing='0' cellpadding='2'")
        end = html.find("class='PSLEVEL3GRID'>&nbsp;</td></tr></table></div>")
        segment = html[start:end] + "class='PSLEVEL3GRID'>&nbsp;</td></tr></table></div>"
        full_html = f"<html><body>{segment}</body></html>"
        logger.info("Schedule page fetched. Parsing HTML content.")

        # 用 lxml 解析 HTML
        tree = etree.HTML(full_html.encode('utf-8'))
        # 初始化 16x8 网格，行表示时间段，列表示星期几
        table = [['' for _ in range(8)] for _ in range(16)]
        # 填写表头
        days = ["Time","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        table[0] = days
        # 填充课程和时间单元格
        for row in range(2, 17):
            for col in range(1, 9):
                cells = tree.xpath(f"//tr[{row}]/td[{col}]")
                if not cells:
                    continue
                td = cells[0]
                cls = td.get('class','')
                text = ''.join(td.xpath('.//span/text()')).strip()
                # 只取课表背景单元格
                if cls.startswith('SSSWEEKLYBACKGROUND') or cls.startswith('SSSWEEKLYTIMEBACKGROUND'):
                    table[row-1][col-1] = text
        # 格式化输出课表
        result = ''
        for d in range(1, 8):
            result += days[d] + ':\n'
            for t in range(1, 16):
                content = table[t][d]
                if content and content != '*':
                    result += self._parse_course_info(content) + '\n'
        logger.info("Schedule parsed successfully.")
        return result

    def _parse_course_info(self, info: str) -> str:
        """
        解析课表单元格里的课程信息。
        Args:
            info (str): 原始课程字符串，例如 "CSC 1001 - L1Lecture09:00AM - 10:00AMRoom101"。
        Returns:
            str: 格式化后的课程详情，包含课程代码、类型、时长和地点。
        """
        pattern = re.compile(
            r"^([A-Z]{3}\s[0-9]{4}\s-\s[LT]\d+)(Lecture|Tutorial)"
            r"(\d{1,2}:\d{2}(?:AM|PM) - \d{1,2}:\d{2}(?:AM|PM))(.+)"
        )
        m = pattern.match(info)
        if not m:
            logger.warning(f"Could not parse course info string: '{info}'")
            return ''
        course, ctype, timeslot, location = m.groups()
        return (
            f"Course: {course}\n"
            f"Type: {ctype}\n"
            f"Duration: {timeslot}\n"
            f"Location: {location}\n"
        )

    def _parse_hidden_field(self, html: str, field: str) -> str:
        """
        从页面 HTML 中解析隐藏字段值（如 ICSID, ICStateNum)。
        Args:
            html (str): HTML 文本。
            field (str): 隐藏字段的 name/id。
        Returns:
            str: 对应字段的 value 值。
        """
        match = re.search(f"name='{field}' id='{field}'.*?value='([^']+)'", html)
        return match.group(1) if match else ''

    def get_course(self, course_code: str, term: str, open_only: bool = False) -> str:
        """
        查询指定课程在指定学期的开课信息。
        Args:
            course_code (str): 课程代码，如 "CSC1001"。
            term (str): 学期字符串，如 "2510"。
            open_only (bool): 是否只显示开放课程。
        Returns:
            str: 格式化后的查询结果。
        """
        logger.info(f"Attempting to get course: code={course_code}, term={term}")
        if not self.login():
            return "请先登录后再查询课程。"
        # 初次 GET 获取 ICSID 和 ICStateNum
        search_url = (
            "https://sis.cuhk.edu.cn/psc/csprd/EMPLOYEE/HRMS/"
            "c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL"
        )
        logger.info("Fetching initial class search page to get state tokens.")
        r0 = self.session.get(search_url)
        html0 = r0.text
        tree = etree.HTML(r0.content)
        # 选中 term 下拉框的所有 option
        term_options = tree.xpath('//select[@id="CLASS_SRCH_WRK2_STRM$35$"]/option')
        terms = [opt.attrib['value'] for opt in term_options if opt.attrib['value'].strip()]
        if term not in terms:
            logger.error(f"Term '{term}' not found in available terms: {terms}")
            return f"学期 {term} 未找到。"
        icsid = self._parse_hidden_field(html0, 'ICSID')
        icstate = self._parse_hidden_field(html0, 'ICStateNum')
        logger.info(f"State tokens obtained: ICSID='{icsid}', ICStateNum='{icstate}'")
        # 准备 POST 数据并提交查询
        post_data = {
            'ICAJAX': '1',
            'ICStateNum': icstate,
            'ICSID': icsid,
            'ICAction': 'CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH',  # 按钮的 name
            'SSR_CLSRCH_WRK_SUBJECT$0': course_code[:3],
            'SSR_CLSRCH_WRK_CATALOG_NBR$1': course_code[3:],
            'CLASS_SRCH_WRK2_STRM$35$': term[:4],
            'SSR_CLSRCH_WRK_SSR_OPEN_ONLY$chk$3': 'Y' if open_only else 'N',
            # 其余隐藏字段略...
        }
        logger.info("Posting search criteria to find course sections.")
        r1 = self.session.post(search_url, data=post_data, verify=certifi.where())
        tree = etree.HTML(r1.content)
        # 提取并格式化输出
        sections    = tree.xpath("//a[starts-with(@id,'DERIVED_CLSRCH_SSR_CLASSNAME_LONG')]/text()")
        enroll_tot = tree.xpath("//span[starts-with(@id,'SSR_CLS_DTL_WRK_ENRL_TOT')]/text()")
        capacity   = tree.xpath("//span[starts-with(@id,'SSR_CLS_DTL_WRK_ENRL_CAP')]/text()")
        times      = tree.xpath("//span[starts-with(@id,'MTG_DAYTIME')]/text()")
        instructors= tree.xpath("//span[starts-with(@id,'MTG_INSTR')]/text()")
        locs       = tree.xpath("//span[starts-with(@id,'MTG_ROOM')]/text()")

        lines = [f"Search Result: code={course_code}, term={term}, open_only={open_only}"]
        for i in range(len(sections)):
            lines.append(f"Section: {sections[i]}")
            lines.append(f"Enrollment: {enroll_tot[i]}/{capacity[i]}")
            lines.append(f"Time: {times[i]}")
            lines.append(f"Instructor: {instructors[i]}")
            lines.append(f"Location: {locs[i]}")
            lines.append("")
        logger.info(f"Found {len(sections)} sections for course {course_code}.")
        return '\n'.join(lines)

    def get_grades(self, term: str) -> str:
        """
        查询指定学期的成绩。
        Args:
            term (str): 学期字符串，如 "2024-25 Term 1"。
        Returns:
            str: 格式化后的成绩单和累计 GPA。
        """
        logger.info(f"Attempting to get grades for term: {term}")
        if not self.login():
            return "请先登录后再查询成绩。"
        # 获取 ICSID 和 ICStateNum
        grades_url = (
            "https://sis.cuhk.edu.cn/psc/csprd/EMPLOYEE/HRMS/"
            "c/SA_LEARNER_SERVICES.SSR_SSENRL_GRADE.GBL"
        )
        logger.info("Fetching initial grades page to get state tokens.")
        r0 = self.session.get(grades_url)
        html0 = r0.text
        icsid = self._parse_hidden_field(html0, 'ICSID')
        icstate = self._parse_hidden_field(html0, 'ICStateNum')
        # 提取可选学期列表
        tree0 = etree.HTML(r0.content)
        terms = tree0.xpath("//span[starts-with(@id,'TERM_CAR')]//text()")
        if term not in terms:
            logger.error(f"Term '{term}' not found in available terms for grades: {terms}")
            return f"学期 {term} 未找到。"
        index = terms.index(term)
        # 构造 POST 数据提交查询
        post_data = {
            'ICAJAX': '1',
            'ICStateNum': icstate,
            'ICSID': icsid,
            'ICAction': 'DERIVED_SSS_SCT_SSR_PB_GO',  # continue button
            'SSR_DUMMY_RECV1$sels$0': str(index),    
            # 其余隐藏字段略...
        }
        logger.info("Posting selected term to get grades table.")
        r1 = self.session.post(grades_url, data=post_data, verify=certifi.where())
        tree1 = etree.HTML(r1.content)
        # 抽取成绩表字段
        courses = tree1.xpath("//a[starts-with(@id,'CLS_LINK')]/text()")
        units   = tree1.xpath("//*[starts-with(@id,'STDNT_ENRL_SSV1_UNT_TAKEN')]/text()")
        grades  = tree1.xpath("//*[starts-with(@id,'STDNT_ENRL_SSV1_CRSE_GRADE_OFF')]/text()")
        points  = tree1.xpath("//*[starts-with(@id,'STDNT_ENRL_SSV1_GRADE_POINTS')]/text()")
        # gpa     = tree1.xpath("//*[@id='STATS_CUMS$12']/text()")
        term_gpa = tree1.xpath("//span[@id='STATS_ENRL$12']/text()")
        cum_gpa  = tree1.xpath("//span[@id='STATS_CUMS$12']/text()")

        lines = [f"Grades for term: {term}"]
        for i in range(len(courses)):
            lines.append(f"{courses[i]}: Units={units[i]}, Grade={grades[i]}, Points={points[i]}")
        lines.append(f"Term GPA: {term_gpa[0]}, Cumulative GPA: {cum_gpa[0]}")
        logger.info(f"Found {len(courses)} courses in grades for term {term}.")
        return '\n'.join(lines)

    def get_course_outline(self, course_code: str) -> str:
        """
        查询指定课程的大纲
        Args:
            course_code (str): 课程代码, 如"CSC1001"
        Returns:
            格式化的课程信息
        """
        try:
            logger.info(f"Getting course outline for {course_code} with new logic.")
            if not self.login():
                return "请先登录"

            outline_url = (
                "https://sis.cuhk.edu.cn/psc/csprd/EMPLOYEE/HRMS/"
                "c/ESTABLISH_COURSES.SSS_BROWSE_CATLG.GBL"
            )
            r0 = self.session.get(outline_url)
            icsid = self._parse_hidden_field(r0.text, 'ICSID')
            icstate = self._parse_hidden_field(r0.text, 'ICStateNum')
            
            first_letter = course_code[0]
            icaction_letter = f'DERIVED_SSS_BCC_SSR_ALPHANUM_{first_letter}'
            post_data = {'ICType': 'Panel', 'ICElementNum': '0', 'ICStateNum': icstate, 'ICSID': icsid, 'ICAction': icaction_letter}
            r1 = self.session.post(outline_url, data=post_data)
            
            tree1 = etree.HTML(r1.content)
            subjects = tree1.xpath("//span[contains(@id, 'DERIVED_SSS_BCC_GROUP_BOX_1') and contains(@class, 'SSSHYPERLINKBOLD')]/text()")
            subject_idx = next((idx for idx, subj in enumerate(subjects) if subj.startswith(course_code[:3])), None)

            if subject_idx is None:
                logger.warning(f"Subject {course_code[:3]} not found.")
                return f"未找到学科: {course_code[:3]}"

            icaction_expand = f'DERIVED_SSS_BCC_SSR_EXPAND_COLLAPS${subject_idx}'
            icsid = self._parse_hidden_field(r1.text, 'ICSID')
            icstate = self._parse_hidden_field(r1.text, 'ICStateNum')
            post_data_expand = {'ICType': 'Panel', 'ICElementNum': '0', 'ICStateNum': icstate, 'ICSID': icsid, 'ICAction': icaction_expand}
            r2 = self.session.post(outline_url, data=post_data_expand)

            tree2 = etree.HTML(r2.content)
            course_ids = tree2.xpath("//span[contains(@id, 'CRSE_NBR$span$')]/text()")
            course_idx = next((idx for idx, cid in enumerate(course_ids) if cid == course_code[3:]), None)

            if course_idx is None:
                logger.warning(f"Course {course_code} not found in subject list.")
                return f"未找到课程: {course_code}"

            icaction_course = f'CRSE_TITLE${course_idx}'
            icsid = self._parse_hidden_field(r2.text, 'ICSID')
            icstate = self._parse_hidden_field(r2.text, 'ICStateNum')
            post_data_course = {'ICType': 'Panel', 'ICElementNum': '0', 'ICStateNum': icstate, 'ICSID': icsid, 'ICAction': icaction_course}
            r3 = self.session.post(outline_url, data=post_data_course)

            icaction_button = 'CUSZ_SAA_DVW_SSR_RSLT_OUTCOME'
            icsid = self._parse_hidden_field(r3.text, 'ICSID')
            icstate = self._parse_hidden_field(r3.text, 'ICStateNum')
            post_data_details_page = {'ICType': 'Panel', 'ICElementNum': '0', 'ICStateNum': icstate, 'ICSID': icsid, 'ICAction': icaction_button}
            r4 = self.session.post(outline_url, data=post_data_details_page)

            tree4 = etree.HTML(r4.content)
            title = get_first_or_empty(tree4, "//span[@id='DERIVED_CRSECAT_DESCR200']/text()")
            desc_en = get_first_or_empty(tree4, "//textarea[@id='CUSZ_OUTLIN_STU_DESCRLONG']/text()")
            prereq = get_first_or_empty(tree4, "//textarea[@id='CUSZ_OUTLIN_STU_CUSZ_PREREQUISITES']/text()")
            
            logger.info(f"Successfully fetched outline for {course_code}")

            # Format the result as a readable string
            result_str = (
                f"Course Outline for {course_code}:\n"
                f"Title: {title}\n"
                f"Description: {desc_en}\n"
                f"Prerequisites: {prereq}\n"
            )
            return result_str

        except Exception as e:
            logger.error(f"Error getting course outline for {course_code}: {e}", exc_info=True)
            return f"获取课程大纲时出错: {e}"

    def get_academic_record(self) -> str:
        """
        获取学术记录，即所有修读过的课程的相关信息，包括课程代码、课程名称、课程学期、课程学分、课程成绩等。
        """
        try:
            logger.info("Attempting to get academic record with new logic.")
            if not self.login():
                return "请先登录"

            academic_record_url = (
                "https://sis.cuhk.edu.cn/psc/csprd/EMPLOYEE/HRMS/"
                "c/SA_LEARNER_SERVICES.SSS_MY_CRSEHIST.GBL"
            )
            r = self.session.get(academic_record_url)
            tree = etree.HTML(r.content)
            
            codes = tree.xpath("//span[starts-with(@id, 'CRSE_NAME$')]/text()")
            names = tree.xpath("//span[starts-with(@id, 'CRSE_LINK$span$')]/a/text()")
            terms = tree.xpath("//span[starts-with(@id, 'CRSE_TERM$')]/text()")
            grades = tree.xpath("//span[starts-with(@id, 'CRSE_GRADE$')]/text()")
            units = tree.xpath("//span[starts-with(@id, 'CRSE_UNITS$')]/text()")
            status_imgs = tree.xpath("//div[starts-with(@id, 'win0divCRSE_STATUS$')]/div/img")
            statuses = [img.get('alt', '') for img in status_imgs]
            
            lines = ["Academic Record:\n"]
            for i in range(len(codes)):
                lines.append(f"  - Course: {codes[i]} - {names[i] if i < len(names) else ''}")
                lines.append(f"    Term: {terms[i] if i < len(terms) else ''}")
                lines.append(f"    Units: {units[i] if i < len(units) else ''}, Grade: {grades[i] if i < len(grades) else ''}, Status: {statuses[i] if i < len(statuses) else ''}\n")
            
            logger.info(f"Successfully fetched {len(codes)} courses from academic record.")
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error getting academic record: {e}", exc_info=True)
            return f"获取学术记录时出错: {e}"
