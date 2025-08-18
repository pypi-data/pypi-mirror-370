import requests, json, re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

class Kosispy:
    def __init__(self, key=None):
        if key is not None and not isinstance(key, str):
            raise TypeError("TypeError: API_KEY를 확인하십시오")
        else:
            self.API_KEY = str(key)
        self.init_time = datetime.now()
        self.labels = {"Y": "연도별(Y)", "H": "반기별(H)", "Q": "분기별(Q)", "M": "월별(M)"}
        self.ends = {"M": 12, "Q": 4, "H": 2}

    def set_key(self, key):
        self.API_KEY = key

    def adjust_period(self):
        if self.PRD_SE in self.ends:
            ST = int(self.st * 100 + 1)
            ED = int(self.ed * 100 + self.ends[self.PRD_SE])
        else:
            ST = self.st
            ED = self.ed
        min_option, max_option = min(self.options), max(self.options)

        if ST > max_option:
            raise ValueError(
                f"입력된 시작시점 {ST} 이 자료의 최종시점 {max_option} 보다 늦습니다. 다운로드를 종료합니다."
            )
        if ED < min_option:
            raise ValueError(
                f"입력된 종료시점 {ED} 이 자료의 최초시점 {min_option} 보다 빠릅니다. 다운로드를 종료합니다."
            )
        if ST < min_option:
            print(
                f"\t WARNING: 입력된 시작시점 {ST} 이 자료의 최초시점 {min_option} 보다 빠릅니다. {min_option} 자료부터 다운로드 합니다"
            )
        if ED > max_option:
            print(
                f"\t WARNING: 입력된 종료시점 {ED} 이 자료의 최종시점 {max_option} 보다 늦습니다. {max_option} 자료까지 다운로드 합니다"
            )

        return max(ST, min_option), min(ED, max_option)

 
    def get_org_id(self):
        gbn_values = ["L", "E", "I", "B"]  # Define the possible values for gbn
        for gbn in gbn_values:
            response = requests.post(
                "https://kosis.kr/search/searchStatDBAjax.do", 
                data={"query": self.TBL_ID, "gbn": gbn}  # Add gbn parameter in the request data
            )
            
            if response.status_code != 200:
                raise ConnectionError(
                    f"기관 코드(ORG_ID)를 가지고 오지 못했습니다. \nERROR: HTTP {response.status_code}"
                )
            
            response_data = response.json()
            if response_data["resultList"] and response_data["resultList"][0].get("ORG_ID"):
                self.ORG_ID = response_data["resultList"][0]["ORG_ID"]
                return  # Exit function once ORG_ID is found
        
        # If loop completes without returning, raise error
        raise AttributeError(
            f"기관 코드(ORG_ID)를 가지고 오지 못했습니다. \nERROR: 통계표 ID(TBL_ID)를 확인하십시오."
        )

    def get_init_data(self):
        self.get_org_id()
        response = requests.get(
            f"https://kosis.kr/statHtml/statHtmlContent.do?orgId={self.ORG_ID}&tblId={self.TBL_ID}"
        )
        if response.status_code != 200:
            raise ConnectionError(
                f"자료주기(prdSe) 값를 가지고 오지 못했습니다. \nERROR: HTTP {response.status_code}"
            )

        soup = BeautifulSoup(response.text, "html.parser")
        obj_count = len(re.findall(r'var tempMaxLvl\s*=\s*"\d";', response.text))
        self.objs = "".join(f"&objL{i}=ALL" for i in range(1, obj_count + 1))
        span = soup.find("span", class_={"top"}, id={f"time{self.PRD_SE}"})

        if span is None:
            pattern = r"fn_searchPeriod\('(\w)'\);"
            matches = re.findall(pattern, response.text)
            matches_list = list(set(matches))
            remaining_options = {
                code: name for code, name in self.labels.items() if code in matches_list
            }
            raise TypeError(
                f"{', '.join(remaining_options.values())} 자료가 다운로드 가능합니다. 자료주기(prdSe)를 수정해주세요."
            )

        else:
            self.options = {int(option["value"]) for option in span.find_all("option")}

    def get_data(self, st, ed, TBL_ID, PRD_SE="Y"):
        self.TBL_ID = str(TBL_ID).upper()
        if TBL_ID[3:6].isdigit():
            self.ORG_ID = int(TBL_ID[3:6])
        else:
            self.get_org_id()

        self.PRD_SE = str(PRD_SE).upper()
        self.st = int(st)
        self.ed = int(ed)

        self.get_init_data()
        ST, ED = self.adjust_period()

        result = []
        option_list = sorted(self.options)
        for option in option_list[option_list.index(ST) : option_list.index(ED) + 1]:
            print(
                f"\t NOTICE: {option} 시점 {self.labels[self.PRD_SE]} 자료를 다운로드 받고 있습니다."
            )

            url = f"https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey={self.API_KEY}&tblId={TBL_ID}&orgId={self.ORG_ID}&startPrdDe={option}&endPrdDe={option}&itmId=ALL&format=json&jsonVD=Y&prdSe={PRD_SE}&loadGubun=2{self.objs}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                result.extend(data)

            else:
                print(
                    f"\t ERROR: {option} 시점 자료 다운로드를 실패하였습니다. \nERROR: HTTP {response.status_code}"
                )

        df = pd.DataFrame(result)
        elapsed = datetime.now() - self.init_time

        df = df.drop_duplicates()
        print(
            f"\t NOTICE: {TBL_ID} 데이터셋(N={len(df)})의 다운로드를 완료하였습니다. \n\t Elapsed Time: {elapsed}"
        )

        return df