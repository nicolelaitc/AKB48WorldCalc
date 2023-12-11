member_groups = {
    "A": [
        "鈴木くるみ",
        "道枝咲",
        "田口愛佳",
        "千葉恵里",
        "西川怜",
        "篠崎彩奈",
        "山根涼羽",
        "佐藤美波",
        "向井地美音",
        "宮崎美穂",
        "加藤玲奈",
        "横山由依",
    ],
    "K": [
        "市川愛美",
        "込山榛香",
        "長友彩海",
        "武藤小麟",
        "武藤十夢",
        "茂木忍",
        "安田叶",
        "湯本亜美",
    ],
    "B": [
        "岩立沙穂",
        "大盛真歩",
        "大家志津香",
        "柏木由紀",
        "久保怜音",
        "佐々木優佳里",
        "谷口めぐ",
        "中西智代梨",
        "福岡聖菜",
    ],
    "4": [
        "浅井七海",
        "稲垣香織",
        "岡田奈々",
        "佐藤妃星",
        "馬嘉伶",
        "村山彩希",
        "山内瑞葵",
    ],
    "8": [
        "坂口渚沙",
        "横山結衣",
        "岡部麟",
        "髙橋彩音",
        "吉川七瀬",
        "小栗有以",
        "小田えりな",
        "大西桃香",
        "濵咲友菜",
        "下尾みう",
        "行天優莉奈",
        "倉野尾成美",
    ],
}

themes = [
    "海へ行こう！",
    "#今日のコーデ",
    "公演は続く",
    "Trick or Treat!",
    "初公演の衣装",
    "I want you!",
    "Please!私も見て",
    "夢にもっと近く",
    "静かな公園で",
    "桜並木の花",
    "思い出の一枚",
    "あなたとクリスマス",
    "幸せのサプライズ",
    "楽しい夜のひと時",
    "Sweet Valentine",
]


def getAllMemberList():
    return [num for sublist in member_groups.values() for num in sublist]


def getTeamMemberList(team: str):
    return member_groups[team]


def getThemeList():
    return themes