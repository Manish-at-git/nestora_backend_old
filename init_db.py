import asyncio
from server import init_pool, setup_schema, seed_database, seed_demo_codes, seed_demo_content, pool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_init():
    logger.info("Initializing database pool...")
    await init_pool()
    
    logger.info("Setting up schema...")
    await setup_schema()
    
    logger.info("Seeding database...")
    await seed_database()
    
    logger.info("Seeding demo codes...")
    await seed_demo_codes()
    
    logger.info("Seeding demo content...")
    await seed_demo_content()
    
    if pool:
        pool.close()
        await pool.wait_closed()
        
    logger.info("Database initialization complete.")

if __name__ == "__main__":
    asyncio.run(run_init())
