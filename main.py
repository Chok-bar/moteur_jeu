import time
import sys
import os
from game.server import serve
from config import logger
from db.database import init_db

if __name__ == '__main__':
    try:
        retry_count = 0
        max_retries = 5
        
        while retry_count < max_retries:
            try:
                logger.info("Initializing database...")
                init_db()
                break
            except Exception as e:
                retry_count += 1
                wait_time = retry_count * 2
                logger.warning(f"Database connection failed (attempt {retry_count}/{max_retries}): {e}")
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                
        if retry_count >= max_retries:
            logger.error("Maximum retries reached. Could not connect to the database.")
            sys.exit(1)
        
        logger.info("Starting game server...")
        server = serve()
        
        try:
            while True:
                time.sleep(86400)
        except KeyboardInterrupt:
            server.stop(0)
            
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)
