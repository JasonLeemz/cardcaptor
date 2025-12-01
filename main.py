"""
黄历AI Agent主程序
"""

import agents.question as agent_question
import agents.calander as agent_calander
from dotenv import load_dotenv
from pkg.sqlite.sqlite import init_db

def main():
    """主函数"""
    # 加载环境变量
    load_dotenv(dotenv_path="configs/.env")

    # 初始化db
    init_db()

    try:
        question = input("\n请输入您的问题: ").strip()
        
        if not question:
            return

        # 在解析问题之前检测是否需要强制刷新（避免LLM转换时丢失关键词）
        force_refresh_keywords = ["最新", "刷新", "重新获取", "更新", "重新拉取", "强制刷新", "重新查询"]
        force_refresh = any(keyword in question for keyword in force_refresh_keywords)
        
        qs = agent_question.parse_question(question)
        answer = agent_calander.answer_question(qs, force_refresh=force_refresh)
        print(f"\n{answer}")
        print("-" * 50)
        
    except KeyboardInterrupt:
        print("\n\n程序已中断，再见！")
        return
    except Exception as e:
        print(f"\n发生错误：{str(e)}")
        print("请重试或输入 'quit' 退出")
        return
        


if __name__ == "__main__":
    main()

