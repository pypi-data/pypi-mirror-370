from croniter import croniter
from datetime import datetime
import pytz
from typing import List, Optional


class CronParser:
    """
    Utility for parsing and validating cron expressions.
    """
    
    @staticmethod
    def validate(cron_expression: str) -> bool:
        """
        Validate a cron expression.
        
        Args:
            cron_expression: The cron expression to validate
            
        Returns:
            True if the expression is valid, False otherwise
        """
        try:
            croniter(cron_expression, datetime.now())
            return True
        except ValueError:
            return False
    
    @staticmethod
    def get_next_run_time(cron_expression: str, 
                          base_time: Optional[datetime] = None,
                          tz: str = "UTC") -> datetime:
        """
        Get the next run time for a cron expression.
        
        Args:
            cron_expression: The cron expression
            base_time: Optional base time (defaults to now)
            tz: Timezone for the cron expression
            
        Returns:
            The next run time as a datetime object
        """
        if base_time is None:
            base_time = datetime.now(pytz.timezone(tz))
        else:
            if base_time.tzinfo is None:
                base_time = pytz.timezone(tz).localize(base_time)
            else:
                base_time = base_time.astimezone(pytz.timezone(tz))
                
        cron = croniter(cron_expression, base_time)
        return cron.get_next(datetime)
    
    @staticmethod
    def get_next_n_run_times(cron_expression: str, 
                            n: int, 
                            base_time: Optional[datetime] = None,
                            tz: str = "UTC") -> List[datetime]:
        """
        Get the next n run times for a cron expression.
        
        Args:
            cron_expression: The cron expression
            n: Number of run times to get
            base_time: Optional base time (defaults to now)
            tz: Timezone for the cron expression
            
        Returns:
            List of the next n run times as datetime objects
        """
        if base_time is None:
            base_time = datetime.now(pytz.timezone(tz))
        else:
            if base_time.tzinfo is None:
                base_time = pytz.timezone(tz).localize(base_time)
            else:
                base_time = base_time.astimezone(pytz.timezone(tz))
                
        cron = croniter(cron_expression, base_time)
        return [cron.get_next(datetime) for _ in range(n)]