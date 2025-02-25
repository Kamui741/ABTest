# ---------------------- main.py ----------------------
from auth import SessionManager
from services import ServiceFactory
from config import LOGIN_URL, SESSION_FILE

def main():
    # 初始化会话（保持不变）
    session = SessionManager(LOGIN_URL, SESSION_FILE)

    # 创建服务实例（修改点）
    service = ServiceFactory.create(session)

    # 以下调用代码保持不变
    try:
        # 创建实验
        res = service.create_experiment(
            name="新用户引导优化V2",
            app_id=1001,
            metrics=["retention", "conversion"]
        )

        # 获取详情
        details = service.get_details(res['id'])
        print(f"实验详情：{details}")

    except Exception as e:
        print(f"操作失败：{str(e)}")

if __name__ == "__main__":
    main()