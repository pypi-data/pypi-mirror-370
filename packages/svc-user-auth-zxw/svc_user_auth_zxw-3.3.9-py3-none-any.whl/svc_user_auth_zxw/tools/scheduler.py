"""
# File       : scheduler.py
# Time       ：2024/12/20
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：定时任务调度器 - 用于自动化会员管理任务
"""
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from svc_user_auth_zxw.tools.membership_cleanup import MembershipCleanupService

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MembershipScheduler:
    """会员定时任务调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.cleanup_service = MembershipCleanupService()
        self.is_running = False
    
    async def cleanup_expired_memberships_job(self):
        """定时清理过期会员的任务"""
        try:
            logger.info("开始执行定时会员清理任务...")
            result = await self.cleanup_service.cleanup_expired_memberships(dry_run=False)
            logger.info(f"会员清理任务完成: {result}")
        except Exception as e:
            logger.error(f"会员清理任务执行失败: {str(e)}")
    
    async def membership_statistics_job(self):
        """定时统计会员信息的任务"""
        try:
            logger.info("开始执行会员统计任务...")
            stats = await self.cleanup_service.get_membership_statistics()
            logger.info(f"会员统计结果: {stats}")
        except Exception as e:
            logger.error(f"会员统计任务执行失败: {str(e)}")
    
    async def membership_expiry_reminder_job(self):
        """定时检查即将过期会员的任务"""
        try:
            logger.info("开始执行会员到期提醒任务...")
            expiring_memberships = await self.cleanup_service.get_expiring_soon_memberships(days_before=7)
            
            if expiring_memberships:
                logger.info(f"发现{len(expiring_memberships)}个即将过期的会员:")
                for membership in expiring_memberships:
                    logger.info(
                        f"  - 用户: {membership['username']}, "
                        f"会员类型: {membership['membership_type']}, "
                        f"剩余天数: {membership['days_remaining']}"
                    )
                # 这里可以添加发送邮件或推送通知的逻辑
                # await self.send_expiry_notifications(expiring_memberships)
            else:
                logger.info("没有即将过期的会员")
                
        except Exception as e:
            logger.error(f"会员到期提醒任务执行失败: {str(e)}")
    
    def setup_jobs(self):
        """设置定时任务"""
        try:
            # 每天凌晨2点清理过期会员
            self.scheduler.add_job(
                self.cleanup_expired_memberships_job,
                trigger=CronTrigger(hour=2, minute=0),
                id="cleanup_expired_memberships",
                name="清理过期会员",
                replace_existing=True
            )
            
            # 每天上午9点生成会员统计
            self.scheduler.add_job(
                self.membership_statistics_job,
                trigger=CronTrigger(hour=9, minute=0),
                id="membership_statistics",
                name="会员统计",
                replace_existing=True
            )
            
            # 每天上午10点检查即将过期的会员
            self.scheduler.add_job(
                self.membership_expiry_reminder_job,
                trigger=CronTrigger(hour=10, minute=0),
                id="membership_expiry_reminder",
                name="会员到期提醒",
                replace_existing=True
            )
            
            # 可选：每小时执行一次会员清理（用于测试或高频需求）
            # self.scheduler.add_job(
            #     self.cleanup_expired_memberships_job,
            #     trigger=IntervalTrigger(hours=1),
            #     id="hourly_cleanup",
            #     name="每小时会员清理",
            #     replace_existing=True
            # )
            
            logger.info("定时任务设置完成")
            
        except Exception as e:
            logger.error(f"设置定时任务失败: {str(e)}")
            raise
    
    async def start(self):
        """启动调度器"""
        if not self.is_running:
            try:
                self.setup_jobs()
                self.scheduler.start()
                self.is_running = True
                logger.info("会员定时任务调度器已启动")
                
                # 输出已设置的任务信息
                jobs = self.scheduler.get_jobs()
                logger.info(f"当前已设置 {len(jobs)} 个定时任务:")
                for job in jobs:
                    logger.info(f"  - 任务: {job.name}, ID: {job.id}, 下次执行: {job.next_run_time}")
                    
            except Exception as e:
                logger.error(f"启动调度器失败: {str(e)}")
                raise
    
    async def stop(self):
        """停止调度器"""
        if self.is_running:
            try:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("会员定时任务调度器已停止")
            except Exception as e:
                logger.error(f"停止调度器失败: {str(e)}")
    
    def get_job_status(self):
        """获取任务状态"""
        if not self.is_running:
            return {"status": "stopped", "jobs": []}
        
        jobs = self.scheduler.get_jobs()
        job_info = []
        for job in jobs:
            job_info.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "status": "running",
            "jobs": job_info,
            "total_jobs": len(jobs)
        }
    
    async def run_job_now(self, job_id: str):
        """立即执行指定任务"""
        try:
            job = self.scheduler.get_job(job_id)
            if not job:
                raise ValueError(f"任务不存在: {job_id}")
            
            logger.info(f"手动执行任务: {job.name}")
            
            # 根据任务ID执行对应的任务函数
            if job_id == "cleanup_expired_memberships":
                await self.cleanup_expired_memberships_job()
            elif job_id == "membership_statistics":
                await self.membership_statistics_job()
            elif job_id == "membership_expiry_reminder":
                await self.membership_expiry_reminder_job()
            else:
                raise ValueError(f"未知的任务ID: {job_id}")
                
            logger.info(f"任务执行完成: {job.name}")
            return True
            
        except Exception as e:
            logger.error(f"手动执行任务失败: {str(e)}")
            raise


# 全局调度器实例
membership_scheduler = MembershipScheduler()


# FastAPI 生命周期集成
async def start_membership_scheduler():
    """启动会员调度器（用于FastAPI生命周期）"""
    await membership_scheduler.start()


async def stop_membership_scheduler():
    """停止会员调度器（用于FastAPI生命周期）"""
    await membership_scheduler.stop()


# 独立运行的主函数
async def main():
    """独立运行调度器"""
    import signal
    import sys
    
    # 信号处理函数
    def signal_handler(signum, frame):
        logger.info("收到停止信号，正在关闭调度器...")
        asyncio.create_task(membership_scheduler.stop())
        sys.exit(0)
    
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 启动调度器
        await membership_scheduler.start()
        
        # 保持运行
        logger.info("调度器正在运行中... 按 Ctrl+C 停止")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("收到键盘中断，正在停止调度器...")
    except Exception as e:
        logger.error(f"调度器运行异常: {str(e)}")
    finally:
        await membership_scheduler.stop()


if __name__ == "__main__":
    asyncio.run(main()) 