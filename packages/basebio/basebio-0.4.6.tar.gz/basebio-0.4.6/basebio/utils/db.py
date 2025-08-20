import logging
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Enum, CheckConstraint, UniqueConstraint, DDL, inspect
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError, OperationalError, ProgrammingError
from retrying import retry

# 配置结构化日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [user:%(user_id)s] - %(message)s',
    handlers=[
        logging.FileHandler('.program_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 定义数据库模型
Base = declarative_base()

ProgramStatus = Enum(
    'not_started',
    'in_progress',
    'completed',
    'failed',
    name='program_status'
)

class Program(Base):
    """程序主表模型"""
    __tablename__ = 'programs'
    
    program_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    program_name = Column(String(255), nullable=False)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    current_status = Column(ProgramStatus, nullable=False, default='not_started')
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone(timedelta(hours=8))))
    
    stages = relationship("ProgramStage", back_populates="program", cascade="all, delete")

class ProgramStage(Base):
    """程序阶段表模型"""
    __tablename__ = 'program_stages'
    
    stage_id = Column(Integer, primary_key=True, autoincrement=True)
    program_id = Column(Integer, ForeignKey('programs.program_id', ondelete='CASCADE'), nullable=False)
    stage_name = Column(String(255), nullable=False)
    stage_status = Column(ProgramStatus, nullable=False, default='not_started')
    stage_order = Column(Integer, CheckConstraint('stage_order > 0'), nullable=False)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    program = relationship("Program", back_populates="stages")
    
    __table_args__ = (
        UniqueConstraint('program_id', 'stage_order', name='uq_program_stage_order'),
    )

def retry_if_db_error(exception):
    """重试条件判断函数"""
    return isinstance(exception, OperationalError)

class ProgramMonitor:
    """
    Recode of the original program monitor code in postgreSQL.
    
    Args:
        db_url: The database URL to connect to.
        max_retries: The maximum number of retries to attempt in case of database connection errors.
        retry_interval: The time interval between retries in seconds.
        Attributes:
            engine: The SQLAlchemy engine object.
            
            Session: The SQLAlchemy sessionmaker object.
            
            max_retries: The maximum number of retries to attempt in case of database connection errors.
            
            retry_interval: The time interval between retries in seconds.
        Methods:
            create_program: Creates a new program with the given stages.
            
            update_stage_status: Updates the status of a stage in a program.
            
            get_progress: Returns the progress of a program as a dictionary of stage names and their statuses.
            
            get_all_in_progress: Returns a list of all programs that are currently in progress.
            
            get_user_progress: Returns the progress of a user's programs as a dictionary of program names and their statuses.
            
            delete_program: Deletes a program and all its stages.
    
    Example usage:
        #### initialize the program monitor
        monitor = ProgramMonitor('postgresql+psycopg2://user:password@localhost/mydb', max_retries=3, retry_interval=5)
        
        #### create a new program with stages
        program_id = monitor.create_program(1, 'Program 1', ['Stage 1', 'Stage 2', 'Stage 3'])
        
        #### update the status of a stage
        monitor.update_stage_status(program_id, 2, 'completed')
        
        #### get the progress of a program
        progress = monitor.get_progress(program_id)
        print(progress)
        
        #### get the progress of a user's programs
        user_progress = monitor.get_user_progress(user_id)
        print(user_progress)
        
        #### delete a program
        monitor.delete_program(program_id)
    """
    
    def __init__(self, db_url: str, max_retries: int = 3, retry_interval: int = 5):
        self.engine = create_engine(
            db_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.Session = sessionmaker(bind=self.engine)
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """内部方法确保表格存在"""
        inspector = inspect(self.engine)
        required_tables = {Program.__tablename__, ProgramStage.__tablename__}
        
        if not required_tables.issubset(inspector.get_table_names()):
            self.create_tables()
        else:
            logger.info("Database tables already exist")

    @retry(
        retry_on_exception=retry_if_db_error,
        stop_max_attempt_number=3,
        wait_fixed=2000
    )
    def create_tables(self):
        """创建数据库表格（带重试机制）"""
        try:
            with self.engine.begin() as conn:
                # 创建表格
                Base.metadata.create_all(bind=conn)
                
                # 创建枚举类型
                if not conn.dialect.has_type(conn, 'program_status'):
                    conn.execute(DDL("DO $$ BEGIN CREATE TYPE program_status AS ENUM ('not_started', 'in_progress', 'completed', 'failed'); EXCEPTION WHEN duplicate_object THEN null; END $$;"))
                    conn.commit()
                
            logger.info("Database tables created successfully")
        except ProgrammingError as pe:
            logger.warning(f"Tables already exist: {str(pe)}")
        except SQLAlchemyError as e:
            logger.error(f"Table creation failed: {str(e)}")
            raise

    def _log_operation(self, level: str, message: str, **kwargs):
        """结构化日志记录方法"""
        extra = {'user_id': kwargs.get('user_id', 'system')}
        log_message = f"[operation:{kwargs.get('operation')}] {message}"
        logger.log(getattr(logging, level.upper()), log_message, extra=extra)
    
    def _execute_with_retry(self, func, *args, **kwargs):
        """带重试机制的通用执行方法"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Database connection error: {str(e)}, retrying... ({attempt+1}/{self.max_retries})")
                time.sleep(self.retry_interval)
            except SQLAlchemyError as e:
                logger.error(f"Database error: {str(e)}")
                raise

    def create_program(self, user_id: int, program_name: str, stages: List[str]) -> int:
        """创建新程序（带完整日志记录）"""
        self._log_operation('info', 
            f"Creating program '{program_name}' with {len(stages)} stages",
            operation='create_program',
            user_id=user_id
        )
        
        try:
            return self._execute_with_retry(
                self._create_program, 
                user_id, 
                program_name, 
                stages
            )
        except Exception as e:
            self._log_operation('error',
                f"Create program failed: {str(e)}",
                operation='create_program',
                user_id=user_id
            )
            raise

    def _create_program(self, user_id: int, program_name: str, stages: List[str]) -> int:
        """实际创建逻辑"""
        with self.Session() as session:
            program = Program(
                user_id=user_id,
                program_name=program_name,
                current_status='not_started'
            )
            session.add(program)
            session.flush()
            
            for order, stage_name in enumerate(stages, start=1):
                session.add(ProgramStage(
                    program_id=program.program_id,
                    stage_name=stage_name,
                    stage_order=order
                ))
            
            session.commit()
            
            self._log_operation('info',
                f"Created program {program.program_id} with stages: {', '.join(stages)}",
                operation='create_program',
                user_id=user_id,
                program_id=program.program_id
            )
            return program.program_id

    def update_stage_status(self, program_id: int, stage_order: int, new_status: str):
        """更新阶段状态（带上下文日志）"""
        self._log_operation('info',
            f"Updating stage {stage_order} to {new_status}",
            operation='update_stage',
            program_id=program_id
        )
        
        try:
            return self._execute_with_retry(
                self._update_stage_status,
                program_id,
                stage_order,
                new_status
            )
        except Exception as e:
            self._log_operation('error',
                f"Update stage failed: {str(e)}",
                operation='update_stage',
                program_id=program_id
            )
            raise

    def _update_stage_status(self, program_id: int, stage_order: int, new_status: str):
        """实际更新逻辑"""
        with self.Session() as session:
            stage = session.query(ProgramStage).filter_by(
                program_id=program_id,
                stage_order=stage_order
            ).first()
            
            if not stage:
                raise ValueError(f"Stage {stage_order} not found")
            
            # 记录状态变更历史
            old_status = stage.stage_status
            stage.stage_status = new_status
            now = datetime.utcnow()
            
            if new_status == 'in_progress':
                stage.start_time = now
            elif new_status in ('completed', 'failed'):
                stage.end_time = now
                
            session.commit()
            
            self._log_operation('info',
                f"Stage {stage_order} status changed: {old_status} → {new_status}",
                operation='update_stage',
                program_id=program_id,
                stage_order=stage_order
            )

    def get_progress(self, program_id: int) -> Dict:
        """获取进度信息（带访问日志）"""
        self._log_operation('debug',
            "Fetching program progress",
            operation='get_progress',
            program_id=program_id
        )
        
        try:
            return self._execute_with_retry(
                self._get_progress,
                program_id
            )
        except Exception as e:
            self._log_operation('error',
                f"Get progress failed: {str(e)}",
                operation='get_progress',
                program_id=program_id
            )
            raise
    
    def _get_progress(self, program_id: int) -> Dict:
        """实际获取进度逻辑"""
        with self.Session() as session:
            try:
                program = session.query(Program).get(program_id)
                if not program:
                    raise ValueError(f"Program {program_id} not found")
                
                stages = session.query(ProgramStage).filter(
                    ProgramStage.program_id == program_id
                ).order_by(ProgramStage.stage_order).all()
                
                result = {
                    "program_id": program.program_id,
                    "user_id": program.user_id,  # 返回用户ID
                    "program_name": program.program_name,
                    "start_time": program.start_time,
                    "status": program.current_status,
                    "total_stages": len(stages),
                    "completed_stages": sum(1 for s in stages if s.stage_status == 'completed'),
                    "current_stage": next(
                        (s.stage_order for s in stages if s.stage_status == 'in_progress'),
                        None
                    )
                }
                
                logger.info(f"Program {program_id} progress: {result}")
                return result
            except SQLAlchemyError as e:
                logger.error(f"Error fetching program progress: {str(e)}")
                raise
    
    def get_all_in_progress(self) -> List[Dict]:
        """获取所有进行中的程序（带重试）"""
        return self._execute_with_retry(self._get_all_in_progress)

    def _get_all_in_progress(self) -> List[Dict]:
        """实际获取进行中程序逻辑"""
        with self.Session() as session:
            try:
                programs = session.query(Program).filter(
                    Program.current_status == 'in_progress'
                ).all()
                
                result = []
                for program in programs:
                    stages = session.query(ProgramStage).filter(
                        ProgramStage.program_id == program.program_id
                    ).order_by(ProgramStage.stage_order).all()
                    
                    result.append({
                        "program_id": program.program_id,
                        "user_id": program.user_id,  # 返回用户ID
                        "program_name": program.program_name,
                        "start_time": program.start_time,
                        "status": program.current_status,
                        "total_stages": len(stages),
                        "completed_stages": sum(1 for s in stages if s.stage_status == 'completed'),
                        "current_stage": next(
                            (s.stage_order for s in stages if s.stage_status == 'in_progress'),
                            None
                        )
                    })
                
                logger.info(f"Found {len(programs)} in-progress programs")
                return result
            except SQLAlchemyError as e:
                logger.error(f"Error fetching in-progress programs: {str(e)}")
                raise
    
    def get_user_progress(self, user_id: Optional[int] = None) -> List[Dict]:
        """获取进行中的程序（支持用户过滤）"""
        return self._execute_with_retry(self._get_user_progress, user_id)

    def _get_user_progress(self, user_id: Optional[int] = None) -> List[Dict]:
        """实际获取逻辑（支持用户过滤）"""
        with self.Session() as session:
            try:
                query = session.query(Program).filter(
                    Program.current_status == 'in_progress'
                )
                
                if user_id is not None:
                    query = query.filter(Program.user_id == user_id)
                
                programs = query.all()
                
                result = []
                for program in programs:
                    stages = session.query(ProgramStage).filter(
                        ProgramStage.program_id == program.program_id
                    ).order_by(ProgramStage.stage_order).all()
                    
                    result.append({
                        "program_id": program.program_id,
                        "user_id": program.user_id,  # 返回用户ID
                        "program_name": program.program_name,
                        "start_time": program.start_time,
                        "status": program.current_status,
                        "total_stages": len(stages),
                        "completed_stages": sum(1 for s in stages if s.stage_status == 'completed'),
                        "current_stage": next(
                            (s.stage_order for s in stages if s.stage_status == 'in_progress'),
                            None
                        )
                    })
                
                logger.info(f"Found {len(programs)} in-progress programs")
                return result
            except SQLAlchemyError as e:
                logger.error(f"Error fetching in-progress programs: {str(e)}")
                raise

    def delete_program(self, program_id: int):
        """删除程序记录（带重试）"""
        return self._execute_with_retry(self._delete_program, program_id)

    def _delete_program(self, program_id: int):
        """实际删除程序逻辑"""
        with self.Session() as session:
            try:
                program = session.query(Program).get(program_id)
                if not program:
                    raise ValueError(f"Program {program_id} not found")
                
                session.delete(program)
                session.commit()
                logger.info(f"Deleted program {program_id}")
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error deleting program: {str(e)}")
                raise

# 使用示例
if __name__ == "__main__":
    # 初始化监控器（自动创建表格）
    monitor = ProgramMonitor(
        "postgresql+psycopg2://user:password@localhost/mydb",
        max_retries=5
    )
    
    try:
        # 创建示例程序
        program_id = monitor.create_program(
            user_id=1001,
            program_name="Nightly Backup",
            stages=["Init", "Compress", "Upload", "Cleanup"]
        )
        
        # 更新阶段状态
        monitor.update_stage_status(program_id, 1, 'in_progress')
        monitor.update_stage_status(program_id, 1, 'completed')
        
        # 查询进度
        progress = monitor.get_progress(program_id)
        print(f"Current Progress: {progress}")
        
        # 删除程序（示例）
        # monitor.delete_program(program_id)
        
    except Exception as e:
        logger.error(f"Main process error: {str(e)}")