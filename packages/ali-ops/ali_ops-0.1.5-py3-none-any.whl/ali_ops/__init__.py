

import fire 
from config import CONFIG
from vpc import VPC 
from ecs import ECS 
from decorators import MyClass

class ENTRY(object):
    """主入口类"""
    
    def __init__(self):
        # 使用装饰器创建VPC访问控制代理
        self.vpc = VPC
        self.ecs = ECS
        self.config = CONFIG() 
    

def main() -> None:
    """Main function to run the CLI."""
    fire.Fire(ENTRY)

